from pathlib import Path
from PIL import Image
import torch
from diffusers import StableDiffusionInpaintPipeline

# 1. 计算出 sibling 目录的路径
#    __file__ = .../my-image-agent/src/06_diffusion_pipeline/pipeline.py
repo_root = Path(__file__).resolve().parents[3]             # .../my-image-agent
sibling_model_dir = repo_root.parent / "stable-diffusion-v1-5"  # .../<parent>/stable-diffusion-v1-5

# 2. 从本地加载 inpainting 模型
pipe = StableDiffusionInpaintPipeline.from_pretrained(
    str(sibling_model_dir),
    torch_dtype=torch.float16,
    safety_checker=None,      # 如不需要安全检查器可以禁用
).to("cuda")

def run_inpainting(
    image_path: str,
    mask_path: str,
    prompt: str,
    out_path: str
) -> str:
    """
    image_path: 原图路径
    mask_path: 二值 mask 图路径
    prompt:     替换/修复文本提示
    out_path:   输出图像保存路径
    """
    img  = Image.open(image_path).convert("RGB")
    mask = Image.open(mask_path).convert("RGB")
    result = pipe(
        prompt=prompt,
        image=img,
        mask_image=mask,
        guidance_scale=7.5,    # 可以根据需要调整
        num_inference_steps=50
    ).images[0]
    result.save(out_path)
    return out_path
