"""
scripts/build_corpus_structure.py
ELKM - بناء هيكل corpus/ بالكامل
"""

import os
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
CORPUS_DIR = BASE_DIR / "corpus"

# ── المجلدات المطلوبة ────────────────────────────────────
FOLDERS = {
    "raw": [
        "constitutions",
        "laws",
        "regulations",
        "jurisprudence/cassation",
        "jurisprudence/constitutional",
        "jurisprudence/administrative",
        "fatwas",
    ],
    "normalized": [
        "constitutions",
        "laws",
        "regulations",
        "jurisprudence",
        "fatwas",
    ],
    "exports": [
        "akn",
        "neo4j",
        "elasticsearch",
    ],
    "metadata": [],
}


def build_structure():
    """يبني هيكل corpus/ بالكامل"""
    
    print("📁 بناء هيكل corpus/...")
    print("=" * 50)
    
    for base, folders in FOLDERS.items():
        for folder in folders:
            path = CORPUS_DIR / base / folder
            path.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ {path.relative_to(BASE_DIR)}")
    
    # ── إنشاء ملف الميتاداتا الرئيسي ────────────────────
    metadata_dir = CORPUS_DIR / "metadata"
    metadata_dir.mkdir(parents=True, exist_ok=True)
    
    index_path = metadata_dir / "documents_index.json"
    if not index_path.exists():
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        print(f"  ✅ {index_path.relative_to(BASE_DIR)}")
    
    print("=" * 50)
    print("✅ هيكل corpus/ جاهز")


if __name__ == "__main__":
    build_structure()