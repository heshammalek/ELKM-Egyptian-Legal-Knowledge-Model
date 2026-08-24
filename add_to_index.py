"""
scripts/add_to_index.py
ELKM - إضافة وثيقة إلى فهرس الميتاداتا
"""

import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
INDEX_PATH = BASE_DIR / "corpus" / "metadata" / "documents_index.json"


def load_index() -> list:
    """تحميل الفهرس الحالي"""
    if INDEX_PATH.exists():
        with open(INDEX_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_index(index: list):
    """حفظ الفهرس"""
    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def add_document(metadata: dict):
    """
    إضافة وثيقة إلى الفهرس (أو تحديثها لو موجودة)
    """
    index = load_index()
    doc_id = metadata.get("doc_id")
    
    # البحث عن وثيقة موجودة
    for i, doc in enumerate(index):
        if doc.get("doc_id") == doc_id:
            index[i] = metadata
            save_index(index)
            print(f"✅ تحديث: {doc_id}")
            return
    
    # إضافة جديدة
    index.append(metadata)
    save_index(index)
    print(f"✅ إضافة: {doc_id}")


def get_document(doc_id: str) -> dict:
    """جلب وثيقة من الفهرس"""
    index = load_index()
    for doc in index:
        if doc.get("doc_id") == doc_id:
            return doc
    return None


def list_documents(doc_type: str = None) -> list:
    """قائمة الوثائق (مع فلترة حسب النوع)"""
    index = load_index()
    if doc_type:
        return [doc for doc in index if doc.get("doc_type") == doc_type]
    return index


if __name__ == "__main__":
    # اختبار
    print(f"📂 الفهرس: {INDEX_PATH}")
    index = load_index()
    print(f"📊 عدد الوثائق: {len(index)}")
    
    if index:
        print("\nآخر 3 وثائق:")
        for doc in index[-3:]:
            print(f"  - {doc.get('doc_id')}: {doc.get('title')[:50]}...")