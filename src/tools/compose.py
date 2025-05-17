from PIL import Image
from pathlib import Path
from langchain.tools import tool

@tool("compose_tool", return_direct=True, description="""
将前景 PNG（支持透明）和背景图片合成。
参数：foreground, background, output_path。
返回：合成后图像路径。
""")
def compose_tool(params: dict) -> str:
    """
    params: {
        "foreground": "fg.png",
        "background": "bg.png",
        "output_path": "out.png"
    }
    """
    foreground_path = params["foreground"]
    background_path = params["background"]
    output_path = params["output_path"]

    foreground = Image.open(foreground_path).convert("RGBA")
    background = Image.open(background_path).convert("RGBA")

    # 尺寸对齐（以背景为主）
    fg_resized = foreground.resize(background.size, resample=Image.LANCZOS)

    # 透明叠加
    composed = Image.alpha_composite(background, fg_resized)

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    composed.save(out_path)

    return str(out_path)
