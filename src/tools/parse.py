import re 
import json
from langchain.tools import tool
from tools._gemini import gemini_generate_text
from tools.caption_image import caption_tool  # 函数式版本

@tool("parse_tool", return_direct=True, description="解析用户需求和图像,生成编辑计划。参数：包含 text, image_path, target 的字典。返回：JSON字符串。")
def parse(params: dict) -> str:
    """
    解析用户文字与图像，生成包含 style 和 plan 的 JSON 对象。LLM返回所有 output_path/mask_path 仅允许文件名（不带路径）。
    """
    # 1. 解析输入
    user_text = params.get("text", "")
    image_path = params.get("image_path", "")
    target = params.get("target", "").strip()

    # 2. 生成图像描述（一定要用 {"params": ...} 包一层）
    image_desc = caption_tool({"params": {"image_path": image_path}}).strip()

    # 3. 构建 prompt（以下内容不变）
    plan_prompt = (
        "You are an advanced image editing workflow planner (zero-shot, fully autonomous). "
        "Your job is to output a JSON object with two fields: 'style' and 'plan'.\n\n"
        f"User requirement: {user_text}\n"
        f"Image description: {image_desc}\n"
        f"Target (if provided): {target if target else 'None'}\n"
        "\n"
        "First, analyze the image description and summarize the image's style in a short English phrase or 3-5 keywords (e.g., 'anime, cyberpunk, vibrant colors').\n"
        "Second, decompose the editing task into atomic image editing steps, each as an object with:\n"
        "  - operation: one of [\"mask\",\"bg_remove\",\"denoise\",\"inpaint\",\"generate\",\"compose\",\"caption\"]\n"
        "  - args: dictionary of parameters for the operation\n"
        "  - All output_path, mask_path, foreground, background etc. must be FILE NAMES ONLY, without any slashes or directories. Do NOT include any path, only file names like 'mask1.png', 'foreground.png'.\n"
        "  - Example: {\"operation\": \"bg_remove\", \"args\": {\"output_path\": \"foreground.png\"}}\n"
        "If the requirement involves:\n"
        "  - removing background and generating a new one, you must plan at least three steps: background removal, background generation, and front-background composition.\n"
        "  - If a mask or denoising is required, insert those steps accordingly.\n"
        "  - Always use 'compose' as the last step if the foreground needs to be placed onto a generated background.\n"
        "When using previous outputs as inputs, refer to them with FILE NAME only, do not use any path or slash. (e.g. foreground.png, background.png, mask.png).\n"
        "For any step that has a prompt parameter (such as generate or inpaint), automatically append the style description or keywords to the prompt to maintain style consistency.\n"
        "If you are unsure about a step, still decompose it as best as possible.\n"
        "\n"
        "Return ONLY a valid JSON object of the following format (no explanations, no markdown, no extra text):\n"
        "{\n"
        "  \"style\": \"<style keywords>\",\n"
        "  \"plan\": [\n"
        "    {\"operation\": \"bg_remove\", \"args\": {\"output_path\": \"foreground.png\"}},\n"
        "    {\"operation\": \"generate\", \"args\": {\"prompt\": \"a futuristic city at night, anime, vibrant colors\", \"output_path\": \"background.png\"}},\n"
        "    {\"operation\": \"compose\", \"args\": {\"foreground\": \"foreground.png\", \"background\": \"background.png\", \"output_path\": \"final.png\"}}\n"
        "  ]\n"
        "}\n"
    )

    # 4. 调用 Gemini 生成 plan
    raw_plan = gemini_generate_text(plan_prompt)
    if not raw_plan or not isinstance(raw_plan, str) or raw_plan.strip() == "":
        raise ValueError(f"gemini_generate_text 输出为空，无法解析：{repr(raw_plan)}")

    # 5. 尝试从返回内容中抽取JSON对象
    json_str = None
    try:
        plan_obj = json.loads(raw_plan)
        json_str = raw_plan
    except Exception:
        match = re.search(r'{\s*"style"\s*:.*"plan"\s*:\s*\[.*?\]\s*}', raw_plan, re.DOTALL)
        if match:
            json_str = match.group(0)
        else:
            print("Gemini返回原文:", raw_plan)
            raise ValueError("未能从Gemini输出中提取有效JSON对象。")

    # 6. 校验格式、只允许文件名
    try:
        plan_obj = json.loads(json_str)
        assert isinstance(plan_obj, dict)
        assert "style" in plan_obj
        assert "plan" in plan_obj
        assert isinstance(plan_obj["plan"], list)
        for step in plan_obj["plan"]:
            args = step.get("args", {})
            for k, v in args.items():
                if "path" in k or k in ("foreground", "background"):
                    if "/" in v or "\\" in v:
                        raise ValueError(f"路径参数 {k}='{v}' 不允许包含斜杠，请仅返回文件名。")
    except Exception as e:
        print("Gemini返回原文:", raw_plan)
        raise ValueError(f"解析LLM输出失败或格式不对: {e}")

    # 7. 返回标准化JSON字符串
    return json.dumps(plan_obj, ensure_ascii=False)
