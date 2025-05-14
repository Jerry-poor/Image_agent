from pathlib import Path

def save_user_input(image_bytes: bytes, filename: str, requirement: str) -> str:
    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)
    img_path = raw_dir / filename
    with open(img_path, "wb") as f:
        f.write(image_bytes)
    #原文存储在data/raw
    with open(raw_dir / f"{filename}.req.txt", "w", encoding="utf-8") as f:
        f.write(requirement)
    return str(img_path)
