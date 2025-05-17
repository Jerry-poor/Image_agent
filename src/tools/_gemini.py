import os
import json
import requests
import base64
from pathlib import Path

# 1. 读取配置文件
cfg_path = Path(__file__).resolve().parents[2] / "config" / "api.json"
cfg = json.loads(cfg_path.read_text(encoding="utf-8"))

API_KEY = cfg.get("api_key") or os.getenv(cfg.get("api_key_env_var") or "")
if not API_KEY:
    raise RuntimeError("请在环境变量或 api.json 填写你的 Gemini API Key")

BASE_URL = cfg["base_url"].rstrip("/")
MODEL_NAME = cfg["model_name"].replace("models/", "")  # 只保留 gemini-2.0-flash

def gemini_generate_text(
    prompt: str,
    temperature: float = None,
    max_output_tokens: int = None,
    top_k: int = None,
    top_p: float = None
) -> str:
    """
    调用 Gemini 2.0+ 文本生成接口，返回生成的 text。
    """
    url = f"{BASE_URL}/models/{MODEL_NAME}:generateContent?key={API_KEY}"
    headers = {"Content-Type": "application/json; charset=utf-8"}

    # 取默认参数（可被函数参数覆盖）
    params = cfg.get("parameters", {})
    gen_cfg = {
        "temperature": temperature if temperature is not None else params.get("temperature"),
        "maxOutputTokens": max_output_tokens if max_output_tokens is not None else params.get("max_output_tokens"),
        "topK": top_k if top_k is not None else params.get("top_k"),
        "topP": top_p if top_p is not None else params.get("top_p"),
    }
    # 只保留有效参数
    gen_cfg = {k: v for k, v in gen_cfg.items() if v is not None}

    body = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }
    if gen_cfg:
        body["generationConfig"] = gen_cfg

    resp = requests.post(url, headers=headers, json=body, timeout=cfg.get("timeout", 60))
    resp.raise_for_status()
    data = resp.json()
    # 兼容 Gemini 返回格式
    return data["candidates"][0]["content"]["parts"][0]["text"]

def gemini_generate_caption(prompt: str, image_path: str, **gen_kwargs) -> str:
    with open(image_path, "rb") as f:
        img_bytes = f.read()
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")

    url = f"{BASE_URL}/models/{MODEL_NAME}:generateContent?key={API_KEY}"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    # Gemini 多模态格式
    body = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": "image/png", "data": img_b64}}
                ]
            }
        ]
    }
    if gen_kwargs:
        body["generationConfig"] = gen_kwargs
    resp = requests.post(url, headers=headers, json=body, timeout=cfg.get("timeout", 60))
    resp.raise_for_status()
    data = resp.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]
