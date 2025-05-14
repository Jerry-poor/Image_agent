from pathlib import Path

# Directories to create
dirs = [
    "my-image-agent/config",
    "my-image-agent/data/raw",
    "my-image-agent/data/processed",
    "my-image-agent/src/01_user_input",
    "my-image-agent/src/02_multimodal_analysis",
    "my-image-agent/src/03_llm_parsing",
    "my-image-agent/src/04_strategy_generation",
    "my-image-agent/src/05_prompt_construction",
    "my-image-agent/src/06_diffusion_pipeline/model_weights",
    "my-image-agent/src/07_output",
    "my-image-agent/scripts",
    "my-image-agent/notebooks",
    "my-image-agent/logs",
    "my-image-agent/tests",
]

# Files to create (empty content)
files = [
    "my-image-agent/README.md",
    "my-image-agent/config/model_config.yaml",
    "my-image-agent/config/pipeline_config.yaml",
    "my-image-agent/src/01_user_input/upload.py",
    "my-image-agent/src/01_user_input/parse_requirements.py",
    "my-image-agent/src/02_multimodal_analysis/embedder.py",
    "my-image-agent/src/02_multimodal_analysis/captioner.py",
    "my-image-agent/src/03_llm_parsing/llm_client.py",
    "my-image-agent/src/03_llm_parsing/parser.py",
    "my-image-agent/src/04_strategy_generation/strategy.py",
    "my-image-agent/src/05_prompt_construction/prompt_builder.py",
    "my-image-agent/src/06_diffusion_pipeline/pipeline.py",
    "my-image-agent/src/07_output/result_saver.py",
    "my-image-agent/scripts/run_full_pipeline.sh",
    "my-image-agent/scripts/start_server.sh",
    "my-image-agent/notebooks/demo.ipynb",
    "my-image-agent/tests/test_multimodal.py",
    "my-image-agent/requirements.txt",
]

# Create directories
for d in dirs:
    Path(d).mkdir(parents=True, exist_ok=True)

# Create empty files
for f in files:
    Path(f).parent.mkdir(parents=True, exist_ok=True)
    Path(f).touch()
