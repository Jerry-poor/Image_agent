from fastapi import FastAPI, UploadFile, File, Form
import uvicorn
from src.user_input.upload import save_user_input
from src.multimodal_analysis.captioner import generate_caption
from src.llm_parsing.llm_client import parse_requirement
from src.strategy_generation.strategy import generate_strategy
from src.prompt_construction.prompt_builder import build_inpainting_prompt
from src.diffusion_pipeline.pipeline import run_inpainting

app = FastAPI()

@app.post("/process/")
async def process(
    file: UploadFile = File(...),
    requirement: str = Form(...)
):
    # 1. 保存输入
    img_path = save_user_input(await file.read(), file.filename, requirement)
    # 2. Caption
    caption = generate_caption(img_path)
    # 3. 结构化解析
    parsed = parse_requirement(caption, requirement)
    # 4. 策略
    strat = generate_strategy(parsed)
    # 5. Prompt
    prompt = build_inpainting_prompt(strat)
    # 6. Inpainting
    out_file = f"data/processed/out_{file.filename}"
    run_inpainting(img_path, strat["mask_path"], prompt, out_file)
    # 7. 返回结果路径
    return {"result": out_file}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
