from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json, shutil, os, requests
from pathlib import Path

# 工具全部导入，全部为 dict 单参数！
from tools.mask import mask_tool
from tools.caption_image import caption_tool
from tools.bg_remove import bg_remove_tool
from tools.denoise import denoise_tool
from tools.fg_remove import fg_remove_tool
from tools.inpaint import inpaint_tool
from tools.generate import generate_tool
from tools.compose import compose_tool
from tools.verify import verify_image_match
from tools.parse import parse

PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.chdir(PROJECT_ROOT)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_ATTEMPTS = 3

def safe_filename(name: str) -> str:
    return Path(name).name

def get_work_path(work_dir, filename, subdir="output"):
    fname = safe_filename(filename)
    full_path = work_dir / subdir / fname
    full_path.parent.mkdir(parents=True, exist_ok=True)
    return str(full_path)

@app.post("/process/")
async def process(
    file: UploadFile = File(...),
    requirement: str = Form(...),
    userId: str        = Form(...),
    timestamp: str     = Form(...),
    target: str        = Form("")
):
    print("收到/process请求", userId, timestamp, file.filename)
    request_id = f"{userId}_{timestamp}"
    logs_dir = Path("data/log") / request_id

    for sub in ["prompts", "images", "captions", "evaluations", "errors", "status"]:
        (logs_dir / sub).mkdir(parents=True, exist_ok=True)

    # ---- 1. 保存一次原始图片（只保存一次！） ----
    work_dir = Path("data/work") / request_id
    if work_dir.exists():
        shutil.rmtree(work_dir, ignore_errors=True)
    (work_dir / "raw").mkdir(parents=True, exist_ok=True)
    (work_dir / "output").mkdir(parents=True, exist_ok=True)
    (work_dir / "masks").mkdir(parents=True, exist_ok=True)

    img_path = work_dir / "raw" / safe_filename(file.filename)
    with open(img_path, "wb") as f:
        f.write(await file.read())

    # ---- 2. 只在外部生成一次原始 query dict ----
    user_query = {
        "text": requirement,
        "image_path": str(img_path),
        "request_id": request_id
    }
    if target:
        user_query["target"] = target

    with open(work_dir / "query.json", "w", encoding="utf-8") as f:
        json.dump(user_query, f, ensure_ascii=False)

    # ---- 3. MAX_ATTEMPTS 循环只复用 user_query，永不更改 ----
    attempts = 0
    success = False
    final_out = None
    verify_result = False

    while attempts < MAX_ATTEMPTS:
        attempts += 1

        # 1. 调用 Parse 永远只用 user_query
        try:
            raw_plan = parse({"params": user_query})
            plan_obj = json.loads(raw_plan)
            if isinstance(plan_obj, dict):
                style = plan_obj.get("style", "")
                plan = plan_obj.get("plan", [])
            elif isinstance(plan_obj, list):
                style = ""
                plan = plan_obj
            else:
                raise ValueError("Unknown plan_obj structure from parse.")

            (logs_dir / "prompts" / f"attempt_{attempts}_plan.json").write_text(raw_plan, encoding="utf-8")
            (logs_dir / "prompts" / f"attempt_{attempts}_style.txt").write_text(style, encoding="utf-8")
        except Exception as e:
            print("parse调用异常:", e)
            (logs_dir / "errors" / f"attempt_{attempts}_error.txt").write_text(f"parse: {e}", encoding="utf-8")
            break

        current_image = str(img_path)
        final_image = None

        try:
            for idx, step in enumerate(plan):
                op = step["operation"]
                args = step.get("args", {})
                print(f"执行第{idx+1}步: {op}")

                if op == "mask":
                    out_name = safe_filename(args.get("output_path", f"mask_{idx+1}.png"))
                    mask_input = {
                        "image_path": str(Path(current_image)),
                        "target": args.get("target", ""),
                        "request_id": request_id,
                        "output_path": get_work_path(work_dir, out_name, "masks")
                    }
                    mask_path = mask_tool({"params": mask_input})
                    shutil.copy(str(mask_path), logs_dir / "images" / Path(mask_path).name)
                    current_image = str(mask_path)

                elif op == "caption":
                    cap = caption_tool({"params": {"image_path": str(Path(current_image))}})
                    (logs_dir / "captions" / f"{attempts:02d}_{idx+1:02d}_caption.txt").write_text(cap, encoding="utf-8")
                    continue

                elif op == "bg_remove":
                    out_name = safe_filename(args.get("output_path", f"bg_removed_{idx+1}.png"))
                    out = bg_remove_tool({"params": {
                        "image_path": str(Path(current_image)),
                        "output_path": get_work_path(work_dir, out_name, "output")
                    }})
                    shutil.copy(str(out), logs_dir / "images" / Path(out).name)
                    current_image = str(out)

                elif op == "denoise":
                    out_name = safe_filename(args.get("output_path", f"denoised_{idx+1}.png"))
                    strength = args.get("strength", 0.5)
                    out = denoise_tool({"params": {
                        "image_path": str(Path(current_image)),
                        "output_path": get_work_path(work_dir, out_name, "output"),
                        "strength": strength
                    }})
                    shutil.copy(str(out), logs_dir / "images" / Path(out).name)
                    current_image = str(out)

                elif op == "fg_remove":
                    out_name = safe_filename(args.get("output_path", f"fg_removed_{idx+1}.png"))
                    out = fg_remove_tool({"params": {
                        "image_path": str(Path(current_image)),
                        "output_path": get_work_path(work_dir, out_name, "output")
                    }})
                    shutil.copy(str(out), logs_dir / "images" / Path(out).name)
                    current_image = str(out)

                elif op == "inpaint":
                    out_name = safe_filename(args.get("output_path", f"inpainted_{idx+1}.png"))
                    mask_p = get_work_path(work_dir, safe_filename(args["mask_path"]), "masks") if "mask_path" in args else ""
                    prompt = args["prompt"]
                    if style and style not in prompt:
                        prompt = f"{prompt}, {style}"
                    (logs_dir / "prompts" / f"{attempts:02d}_{idx+1:02d}_inpaint.txt").write_text(prompt, encoding="utf-8")
                    out = inpaint_tool({"params": {
                        "image_path": str(Path(current_image)),
                        "mask_path": mask_p,
                        "prompt": prompt,
                        "output_path": get_work_path(work_dir, out_name, "output")
                    }})
                    shutil.copy(str(out), logs_dir / "images" / Path(out).name)
                    current_image = str(out)

                elif op == "generate":
                    out_name = safe_filename(args.get("output_path", f"gen_{idx+1}.png"))
                    prompt = args["prompt"]
                    if style and style not in prompt:
                        prompt = f"{prompt}, {style}"
                    (logs_dir / "prompts" / f"{attempts:02d}_{idx+1:02d}_generate.txt").write_text(prompt, encoding="utf-8")
                    out = generate_tool({"params": {
                        "prompt": prompt,
                        "output_path": get_work_path(work_dir, out_name, "output")
                    }})
                    shutil.copy(str(out), logs_dir / "images" / Path(out).name)
                    current_image = str(out)

                elif op == "compose":
                    fg = get_work_path(work_dir, safe_filename(args["foreground"]), "output")
                    bg = get_work_path(work_dir, safe_filename(args["background"]), "output")
                    output = get_work_path(work_dir, safe_filename(args["output_path"]), "output")
                    out = compose_tool({"params": {
                        "foreground": fg,
                        "background": bg,
                        "output_path": output
                    }})
                    shutil.copy(str(out), logs_dir / "images" / Path(out).name)
                    current_image = str(out)

                else:
                    print(f"未知操作: {op}")
                    continue

                final_image = current_image

        except Exception as e:
            print("执行步骤出错:", e)
            (logs_dir / "errors" / f"attempt_{attempts}_error.txt").write_text(str(e), encoding="utf-8")
            break

        # === 验证环节 ===
        plan_desc = f"User requirement: {requirement}\nStyle: {style}\nPlan: {json.dumps(plan, ensure_ascii=False)}"
        try:
            verify_result = verify_image_match({"params": {
                "image_path": final_image,
                "plan_prompt": plan_desc
            }})
        except Exception as e:
            verify_result = False
            (logs_dir / "evaluations" / f"attempt_{attempts}_verify.txt").write_text(f"验证报错:{e}", encoding="utf-8")
        else:
            (logs_dir / "evaluations" / f"attempt_{attempts}_verify.txt").write_text(str(verify_result), encoding="utf-8")

        if verify_result:
            final_out = logs_dir / "images" / Path(final_image).name
            shutil.copy(final_image, final_out)
            (logs_dir / "status" / "success.txt").write_text(f"Success on attempt {attempts}", encoding="utf-8")
            with open(final_out, "rb") as f:
                files = {'file': (str(final_out.name), f, 'image/png')}
                try:
                    requests.post("http://localhost:2333/upload", files=files, timeout=5)
                except Exception as err:
                    print("POST到2333端口失败:", err)
            success = True
            break

        shutil.rmtree(work_dir, ignore_errors=True)

    if not success:
        raise HTTPException(status_code=500, detail=f"No satisfactory workflow found after {MAX_ATTEMPTS} attempts. Last verify result: {verify_result}")

    return {
        "request_id": request_id,
        "final_image": str(final_out),
        "attempts": attempts,
        "verify": verify_result
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "agent:app",
        host="0.0.0.0",
        port=9527,
        reload=True
    )
