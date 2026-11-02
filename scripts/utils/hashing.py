import hashlib
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATE_FILE = os.path.join(BASE_DIR, "scripts", "incremental_state.json")

def get_file_hash(filepath):
    """بيحسب الـ MD5 hash للملف"""
    hasher = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()
    except Exception as e:
        print(f"⚠️ مشكلة في قراءة الملف {filepath}: {e}")
        return None

def load_state():
    """بيقرا حالة الملفات اللي اتعالجت قبل كده"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_state(state):
    """بيحفظ حالة الملفات"""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=4, ensure_ascii=False)
