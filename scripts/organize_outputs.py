"""
scripts/organize_outputs.py
ترتيب الملفات في normalized/ حسب النوع
"""

import json
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
NORMALIZED_DIR = BASE_DIR / "corpus" / "normalized"
ORGANIZED_DIR = BASE_DIR / "corpus" / "organized"

# خريطة النوع ← المجلد
TYPE_MAP = {
    "constitution": "constitutions",
    "law": "laws",
    "regulation": "regulations",
    "judgment": "jurisprudence",
    "fatwa": "fatwas",
}

def organize_files():
    """ينقل الملفات من normalized/ إلى organized/ حسب النوع"""
    
    for json_path in NORMALIZED_DIR.glob("*.json"):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        doc_type = data.get("doc_type", "unknown")
        folder = TYPE_MAP.get(doc_type, "other")
        
        # مجلد الوجهة
        dest_dir = ORGANIZED_DIR / folder
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # نقل JSON
        dest_json = dest_dir / json_path.name
        shutil.copy2(json_path, dest_json)
        
        # نقل TXT (لو موجود)
        txt_path = json_path.with_suffix('') / f"{json_path.stem}_normalized.txt"
        # الصيغة الصحيحة: json_path.stem + "_normalized.txt"
        txt_path = NORMALIZED_DIR / f"{json_path.stem}_normalized.txt"
        if txt_path.exists():
            dest_txt = dest_dir / txt_path.name
            shutil.copy2(txt_path, dest_txt)
        
        print(f"  {json_path.name} → {folder}/")

if __name__ == "__main__":
    organize_files()