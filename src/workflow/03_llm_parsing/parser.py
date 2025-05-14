def generate_strategy(parsed: dict) -> dict:
    # parsed 里可能有 mask_type、action、style 等字段
    # 这里只做简单 passthrough，也可加业务逻辑校验
    strategy = {
        "mask_type": parsed["mask_type"],
        "action": parsed["action"],
        "style": parsed.get("style", ""),
        # 比如如果 mask_type="background"，我们默认用整图 mask
        "mask_path": "data/processed/mask.png"
    }
    return strategy
