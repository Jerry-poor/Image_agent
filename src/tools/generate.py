import os
from pathlib import Path
import torch
from diffusers import StableDiffusionPipeline
from langchain.tools import tool

diff_root = Path(__file__).resolve().parents[3]
model_path = diff_root / "stable-diffusion-v1-5"

pipe = StableDiffusionPipeline.from_pretrained(
    str(model_path),
    local_files_only=True,
    torch_dtype=torch.float16
).to("cuda")

@tool("generate_tool", return_direct=True, description="""
根据纯文本 prompt 生成新图。
参数：prompt, output_path。返回：生成图像的文件路径。
""")
def generate_tool(params: dict) -> str:
    prompt = params["prompt"]
    output_path = params["output_path"]
    result = pipe(
        prompt=prompt,
        num_inference_steps=50
    ).images[0]
    out_path = Path(output_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    result.save(out_path)
    return str(out_path)
