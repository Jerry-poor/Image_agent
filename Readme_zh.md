# 智能图像编辑 Agent

> 一个基于 Gemini 多模态大模型和 Stable Diffusion 的自动化图像处理工作流系统，支持去背景、掩码、降噪、修复、合成、生成等多种操作，并通过大模型验证结果。

---

## 功能概述

* **自然语言驱动**：用户上传图片并以自然语言描述需求，Agent 自动理解并分解任务。
* **多步骤编排**：自动生成并执行包含去背景、目标提取、降噪、Inpaint、生成、合成等在内的图像处理计划。
* **自动验证**：使用 Gemini 大模型判断生成结果是否符合用户意图，不符合则重试（最多 3 次）。
* **前端交互**：React 实现拖拽/粘贴上传、文本输入、轮询展示结果弹窗。

---

## 目录结构

```
Image_agent/
├── .git/
├── .vscode/
├── config/                  # API key 和模型配置
│   └── api.json
├── src/                     # 后端源码
│   ├── agent.py             # 主流程：解析、执行、验证
│   ├── return.py            # 结果服务：/upload, /latest-image
│   ├── data/                # 运行时数据及日志
│   │   ├── log/
│   │   ├── work/
│   │   └── return/          # 输出结果目录
│   └── tools/               # 各类图像处理工具封装
│       ├── mask.py
│       ├── bg_remove.py
│       ├── denoise.py
│       ├── fg_remove.py
│       ├── inpaint.py
│       ├── generate.py
│       ├── compose.py
│       ├── caption_image.py
│       ├── parse.py
│       └── verify.py
├── testcases/               # 测试用例
└── user/                    # 前端交互代码
    └── src/                 # React 应用入口
        ├── App.jsx
        ├── index.js
        ├── App.css
        └── ...
```

---

## 环境与依赖

* **Python 3.8+**
* **Node.js 14+**
* **CUDA 与可用 GPU（推荐加速 Stable Diffusion）**

### Python 依赖

```bash
pip install fastapi uvicorn langchain requests pillow rembg torch diffusers
```

### 前端依赖

```bash
cd user
npm install
```

---

## 配置

1. 在 `config/api.json` 填入你的 Gemini API Key：

```json
{
  "api_key": "YOUR_GEMINI_API_KEY",
  "base_url": "https://generativelanguage.googleapis.com/v1beta",
  "model_name": "gemini-2.0-flash",
  "parameters": {"temperature": 0.7, "max_output_tokens": 512},
  "timeout": 60
}
```

2. 确保 `base_url` 与 Google Cloud 控制台一致。

---

## 启动流程

### 1. 启动后端 Agent 服务

```bash
cd Image_agent/src
uvicorn agent:app --host 0.0.0.0 --port 9527 --reload
```

### 2. 启动结果服务（Upload & Poll）

```bash
cd Image_agent/src
uvicorn return:app --host 0.0.0.0 --port 2333 --reload
```

### 3. 启动前端 React 应用

```bash
cd Image_agent/user
npm start
```

打开浏览器访问 `http://localhost:3000`，即可使用拖拽或粘贴上传图片并输入描述进行体验。

---

## 工作流原理

1. **接收请求**：Agent `/process/` 接口接收用户上传的图片和需求。
2. **解析计划**：调用 `parse` 工具（基于 Gemini）生成多步骤处理 plan。
3. **执行步骤**：依次使用 `mask_tool`、`bg_remove_tool`、`denoise_tool`、`inpaint_tool`、`generate_tool`、`compose_tool` 等工具完成任务。
4. **验证结果**：调用 `verify_image_match` 工具判断是否符合需求，符合则结束，不符合则重试（最多3次）。
5. **上传 & 展示**：将最终图像 POST 到结果服务，并由前端轮询 `/latest-image` 接口自动弹窗展示。

---

## 示例伪代码

```python
user_query = {"text": requirement, "image_path": original_img, "request_id": request_id}
for attempt in range(3):
    plan = parse({"params": user_query})
    current = original_img
    for step in plan:
        current = run_tool(step, current)
    if verify({"image_path": current, "plan_prompt": str(plan)}):
        deliver(current)
        break
```

---

## 致谢

* Google Gemini API 提供多模态理解与生成能力
* Hugging Face Diffusers 支持 Stable Diffusion 图像生成流程

---

## License

MIT License
