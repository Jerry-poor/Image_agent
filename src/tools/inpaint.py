from pathlib import Path
from PIL import Image
import torch
from diffusers import StableDiffusionInpaintPipeline
from langchain.tools import tool
import os

diff_root = Path(__file__).resolve().parents[3]
model_path = diff_root / "stable-diffusion-v1-5"

pipe = StableDiffusionInpaintPipeline.from_pretrained(
    str(model_path),
    local_files_only=True,
    torch_dtype=torch.float16
).to("cuda")

@tool("inpaint_tool", return_direct=True, description="""
对指定区域进行 Inpainting。
参数：image_path, mask_path, prompt, output_path。返回：处理后图像路径。
""")
def inpaint_tool(params: dict) -> str:
    image_path = params["image_path"]
    mask_path = params["mask_path"]
    prompt = params["prompt"]
    output_path = params["output_path"]
    img = Image.open(str(Path(image_path).resolve())).convert("RGB")
    mask = Image.open(str(Path(mask_path).resolve())).convert("RGB")
    result = pipe(
        prompt=prompt,
        image=img,
        mask_image=mask,
        guidance_scale=7.5,
        num_inference_steps=50
    ).images[0]
    out_path = Path(output_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    result.save(out_path)
    return str(out_path)
