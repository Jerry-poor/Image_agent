import base64
from pathlib import Path
from tools._gemini import gemini_generate_text
from langchain.tools import tool

@tool("verify_image_match", return_direct=True, description="验证图片是否符合意图，参数：包含 image_path, plan_prompt 的字典，返回 True/False。")
def verify_image_match(params: dict) -> bool:
    image_path = params["image_path"]
    plan_prompt = params["plan_prompt"]

    with open(str(Path(image_path).resolve()), "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")

    system_prompt = (
        "You are an image verification expert. "
        "Given a user intent description and the AI plan (prompt/caption/style),"
        " please judge whether the provided image matches the described intent and plan."
        " Respond only with 'True' or 'False'."
        "\n\n"
        f"User plan/caption:\n{plan_prompt}\n"
        "Below is the generated image (base64-encoded):\n"
        f"{image_b64}\n"
        "Does the image match the description/plan? Reply with only 'True' or 'False'."
    )
    res = gemini_generate_text(system_prompt)
    answer = res.strip().lower()
    if answer == "true":
        return True
    elif answer == "false":
        return False
    else:
        print(f"[verify_image_match] 非法LLM回答: {res!r}")
        return False
