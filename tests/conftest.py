import sys
from pathlib import Path

# src/ をカレントにして実行する前提のimport（from pokemon import Pokemon 等）になっているため、src/ をパスに通す
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
