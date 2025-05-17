from langchain.tools import tool
from tools._gemini import gemini_generate_caption

@tool("caption_tool", return_direct=True, description="使用 Gemini 生成图像英文描述。参数：image_path。返回英文描述字符串。")
def caption_tool(params: dict) -> str:
    """
    params: {
        "image_path": "xxx.png"
    }
    """
    image_path = params["image_path"]
    prompt = "Please provide a concise, fluent English description of the image."
    caption = gemini_generate_caption(prompt, image_path)
    return caption.strip()
