from pathlib import Path
from rembg import remove
from PIL import Image, ImageOps
from langchain.tools import tool

@tool("fg_remove_tool", return_direct=True, description="""
移除图像前景（主体），保留背景。
参数：image_path, output_path。返回：处理后图像路径。
""")
def fg_remove_tool(params: dict) -> str:
    image_path = params["image_path"]
    output_path = params["output_path"]
    img = Image.open(image_path).convert("RGBA")
    # 提取前景
    fg = remove(img)
    # 得到前景 alpha 通道
    mask = fg.split()[-1]
    # 反转 mask，用于抠出背景
    inv_mask = ImageOps.invert(mask)
    # 在透明背景上粘贴原图，只保留背景部分
    bg = Image.new("RGBA", img.size)
    bg.paste(img, mask=inv_mask)
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    bg.save(out_path)
    return str(out_path)
