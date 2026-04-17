from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_DIR = BASE_DIR / "data" / "input"
INPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_DIR = BASE_DIR / "data" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)