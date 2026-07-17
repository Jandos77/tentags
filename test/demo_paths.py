from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEMO_OUTPUT_DIR = PROJECT_ROOT / "demo_output"


def demo_output_path(filename: str) -> Path:
    DEMO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return DEMO_OUTPUT_DIR / filename
