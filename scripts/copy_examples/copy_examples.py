"""Script to copy the examples folder into the docs.
"""

import shutil
from pathlib import Path

docs_path = Path("docs", "examples")

for notebook in Path("examples").glob("*.ipynb"):
    shutil.copy(notebook, docs_path)
