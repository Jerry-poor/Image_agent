from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import shutil
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],         
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
RETURN_DIR = Path("data/return")
IMAGES_DIR = RETURN_DIR / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
LATEST_IMAGE = IMAGES_DIR / "latest.png"

# 1. 提供 /upload 接口，agent POST 图片用
@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    with open(LATEST_IMAGE, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"msg": "ok", "image_url": f"/images/latest.png"}

# 2. 静态图片服务
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")

# 3. 提供 /latest-image，返回图片URL，前端用于轮询
@app.get("/latest-image")
def latest_image():
    if LATEST_IMAGE.exists():
        # 前端通过 /images/latest.png 访问图片
        return JSONResponse(content={
            "imageUrl": f"http://localhost:2333/images/latest.png"
        })
    else:
        return JSONResponse(content={"imageUrl": None})

# 可选：直接下载图片接口（如果你需要）
@app.get("/download-latest")
def download_latest():
    if LATEST_IMAGE.exists():
        return FileResponse(LATEST_IMAGE)
    else:
        return {"msg": "No image found."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("return:app", host="0.0.0.0", port=2333, reload=True)
