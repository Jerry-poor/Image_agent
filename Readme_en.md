# Intelligent Image Editing Agent

> An automated image processing workflow powered by Google Gemini multimodal large model and Stable Diffusion, supporting background removal, masking, denoising, inpainting, composition, generation, and result verification.

---

## Features

* **Natural Language Driven**
  Users upload an image and describe their requirements in plain English or Chinese. The Agent automatically interprets and decomposes the task.
* **Multi-Step Workflow**
  Automatically plans and executes a sequence of operations such as background removal, target extraction, denoising, inpainting, generation, and composition.
* **Result Verification**
  Uses Gemini to verify that the final image matches the original user intent. If verification fails, it retries up to three times.
* **Interactive Frontend**
  A React application supports drag-and-drop or paste image upload, text input, and real-time result polling with modal display.

---

## Project Structure

```
Image_agent/
├── .git/
├── .vscode/
├── config/                  # API keys and model configuration
│   └── api.json
├── src/                     # Backend source code
│   ├── agent.py             # Main agent: parse, execute, verify
│   ├── return.py            # Result service: /upload, /latest-image
│   ├── data/                # Runtime data and logs
│   │   ├── log/
│   │   ├── work/
│   │   └── return/          # Output images served to frontend
│   └── tools/               # Image processing tools
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
├── testcases/               # Automated test cases
└── user/                    # Frontend code (React)
    └── src/
        ├── App.jsx
        ├── index.js
        ├── App.css
        └── ...
```

---

## Prerequisites

* **Python 3.8+**
* **Node.js 14+**
* **CUDA-enabled GPU** (optional, recommended for Stable Diffusion acceleration)

### Python Dependencies

```bash
pip install fastapi uvicorn langchain requests pillow rembg torch diffusers
```

### Frontend Dependencies

```bash
cd user
npm install
```

---

## Configuration

1. Edit `config/api.json` and insert your Google Gemini API credentials:

```json
{
  "api_key": "YOUR_GEMINI_API_KEY",
  "base_url": "https://generativelanguage.googleapis.com/v1beta",
  "model_name": "gemini-2.0-flash",
  "parameters": {"temperature": 0.7, "max_output_tokens": 512},
  "timeout": 60
}
```

2. Ensure the `base_url` matches your Google Cloud setup.

---

## Running the Services

### 1. Start the Agent Backend

```bash
cd Image_agent/src
uvicorn agent:app --host 0.0.0.0 --port 9527 --reload
```

### 2. Start the Result Service

```bash
cd Image_agent/src
uvicorn return:app --host 0.0.0.0 --port 2333 --reload
```

### 3. Start the Frontend

```bash
cd Image_agent/user
npm start
```

Open your browser to `http://localhost:3000` to access the React UI. Drag-and-drop or paste an image, enter your description, and see results in a modal popup.

---

## Core Workflow

1. **Receive Request**: The `/process/` endpoint accepts the uploaded image and user requirement.
2. **Plan Generation**: The `parse` tool (Gemini) returns a JSON plan with style and steps.
3. **Step Execution**: Sequentially run each tool (`mask_tool`, `bg_remove_tool`, `denoise_tool`, `inpaint_tool`, `generate_tool`, `compose_tool`, etc.).
4. **Verification**: Use `verify_image_match` to check if the output matches the plan; retry if necessary (max 3 times).
5. **Result Delivery**: POST the final image to the result service. The frontend polls `/latest-image` and displays the image when available.

---

## Example Pseudocode

```python
user_query = {"text": requirement, "image_path": original_img, "request_id": request_id}
for attempt in range(3):
    plan = parse({"params": user_query})
    current_img = original_img
    for step in plan:
        current_img = run_tool(step["operation"], step["args"], current_img)
    if verify({"image_path": current_img, "plan_prompt": str(plan)}):
        upload_result(current_img)
        break
```

---

## Acknowledgements

* **Google Gemini API** for multimodal understanding and generation.
* **Hugging Face Diffusers** for Stable Diffusion pipelines.

---

## License

This project is licensed under the MIT License.
