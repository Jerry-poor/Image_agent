from pathlib import Path
from PIL import Image
import torch
from diffusers import StableDiffusionImg2ImgPipeline
from langchain.tools import tool
import os

# 动态定位本地 Stable-Diffusion v1.5 模型目录
diff_root = Path(__file__).resolve().parents[3]
os.chdir(str(diff_root))

pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
    "stable-diffusion-v1-5",
    local_files_only=True,
    torch_dtype=torch.float16
).to("cuda")

@tool("denoise_tool", return_direct=True, description="""
对输入图像进行降噪。
参数：image_path（原图路径），output_path（保存路径），strength（降噪强度，0~1，可选，默认0.5）。
返回：去噪后图像路径。
""")
def denoise_tool(params: dict) -> str:
    image_path = params["image_path"]
    output_path = params["output_path"]
    strength = params.get("strength", 0.5)
    img = Image.open(image_path).convert("RGB")
    img = img.resize((512, 512))  # 调整到管道输入尺寸

    result = pipe(
        prompt="",
        image=img,
        strength=strength,
        guidance_scale=7.5,
        num_inference_steps=50
    ).images[0]

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    result.save(out_path)
    return str(out_path)
