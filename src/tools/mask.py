from langchain.tools import tool
from pathlib import Path
from PIL import Image
from rembg import remove

@tool("mask_tool", return_direct=True, description="""
生成图像的二值掩码。参数：包含 image_path, target, request_id, output_path 的字典。返回：掩码图像路径。
""")
def mask_tool(params: dict) -> str:
    image_path = params["image_path"]
    target = params["target"]
    request_id = params["request_id"]
    img = Image.open(str(Path(image_path).resolve())).convert("RGBA")
    removed = remove(img)
    mask = removed.split()[-1]
    work_targets_dir = (Path("data/work") / request_id / "targets").resolve()
    work_targets_dir.mkdir(parents=True, exist_ok=True)
    output_path = params.get("output_path")
    if output_path:
        mask_path = Path(output_path).resolve()
        mask_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        safe_target = target.replace(" ", "_") or "mask"
        mask_path = (work_targets_dir / f"{safe_target}_mask.png").resolve()
    mask.save(mask_path)
    return str(mask_path)
