def build_inpainting_prompt(strategy: dict) -> str:
    # 示例：在背景区域进行 inpainting，风格为 XXX
    return f"{strategy['action']} on {strategy['mask_type']} area, style: {strategy['style']}."
