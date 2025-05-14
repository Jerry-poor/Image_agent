import os, json
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def parse_requirement(caption: str, requirement: str) -> dict:
    system = "你是图像编辑策略规划助手，输入图像描述和用户需求，输出 JSON，包括：mask_type、action、style、其他参数。"
    user = (
        f"图像描述：{caption}\n"
        f"用户需求：{requirement}\n"
        "请严格返回 JSON，不要多余文本。"
    )
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role":"system","content":system},
                  {"role":"user","content":user}],
        temperature=0
    )
    return json.loads(resp.choices[0].message.content)
