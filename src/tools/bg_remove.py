from pathlib import Path
from rembg import remove
from PIL import Image
from langchain.tools import tool

@tool("bg_remove_tool", return_direct=True, description=(
    "移除图像背景，保留前景并输出带透明通道的 PNG。"
    "参数：image_path, output_path。返回：处理后图像路径。"
))
def bg_remove_tool(params: dict) -> str:
    """
    params: {
        "image_path": "xxx.png",
        "output_path": "yyy.png"
    }
    """
    image_path = params["image_path"]
    output_path = params["output_path"]
    img = Image.open(image_path).convert("RGBA")
    result = remove(img)
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    result.save(out_path)
    return str(out_path)
