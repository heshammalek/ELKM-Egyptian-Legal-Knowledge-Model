'''
تم تصميم السكريبت لسحب البيانات من الموقع المجاني أولاً (manshurat.org)، مع إضافة الموقعين الآخرين (alamiria.laalaws.com و ccl.gov.eg) كخيارات مستقبلية مع تعليمات تسجيل الدخول.
'''
import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ==================================================
# 1. الإعدادات والمسارات
# ==================================================
BASE_DIR = Path(__file__).parent.parent
RAW_DIR = BASE_DIR / "corpus" / "raw"
METADATA_DIR = BASE_DIR / "corpus" / "metadata"
METADATA_INDEX = METADATA_DIR / "documents_index.json"

RAW_DIR.mkdir(parents=True, exist_ok=True)
METADATA_DIR.mkdir(parents=True, exist_ok=True)

# ==================================================
# 2. إدارة الفهرس (للتكرار)
# ==================================================
def load_index() -> Dict:
    if METADATA_INDEX.exists():
        with open(METADATA_INDEX, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"documents": []}

def save_index(index: Dict):
    with open(METADATA_INDEX, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

def generate_doc_id(title: str, year: int) -> str:
    """معرف فريد من الاسم والسنة."""
    clean_title = title.replace(" ", "_").replace("/", "-")
    return f"{clean_title}-{year}"

def is_duplicate(doc_id: str, index: Dict) -> bool:
    return any(doc["doc_id"] == doc_id for doc in index["documents"])

# ==================================================
# 3. تحميل الملفات
# ==================================================
def download_pdf(url: str, save_path: Path) -> bool:
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, stream=True, headers=headers, timeout=60)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"❌ فشل التحميل: {e}")
        return False

# ==================================================
# 4. المصدر الأول: منشورات (مجاني - بدون تسجيل دخول)
# ==================================================
def scrape_manshurat():
    """سحب البيانات من manshurat.org (مجاني)."""
    print("\n🌐 [1] جلب البيانات من manshurat.org...")
    base_url = "https://manshurat.org"
    try:
        response = requests.get(base_url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # مثال: استخراج عناوين الوثائق من القسم الرئيسي
        doc_elements = soup.select("article h2 a")  # حدد المحددات بدقة
        found = 0
        for el in doc_elements[:5]:  # حدد العدد للتجربة
            title = el.text.strip()
            link = el.get('href')
            if link and not link.startswith('http'):
                link = base_url + link
            
            # استخراج السنة من النص أو الرابط (مثال)
            year = 2025 if "2025" in title else datetime.now().year
            
            doc_info = {
                "title": title,
                "year": year,
                "doc_type": "legal_draft",  # حدد نوع الوثيقة
                "source_url": link,
                "source": {
                    "type": "website",
                    "url": base_url,
                    "retrieved_date": datetime.now().isoformat()
                },
                "fidelity_level": "compiled"  # مستوى الاكتمال
            }
            process_document(doc_info)
            found += 1
        
        print(f"✅ تم العثور على {found} وثيقة من منشورات.")
    except Exception as e:
        print(f"⚠️ خطأ في منشورات: {e}")

# ==================================================
# 5. المصدر الثاني: المطبعة الأميرية (يتطلب تسجيل دخول)
# ==================================================
def scrape_alamiria(username: str, password: str):
    """
    سحب البيانات من alamiria.laalaws.com.
    يتطلب تسجيل دخول (تم إيقافها مؤقتاً).
    """
    print("\n🔐 [2] الوصول إلى alamiria.laalaws.com (معلق).")
    print("   ⚠️ يتطلب اشتراكاً مدفوعاً وتفعيل حساب.")
    # TODO: تفعيل عند توفر الاشتراك
    # driver = webdriver.Chrome()
    # driver.get("https://alamiria.laalaws.com/Sections/Login")
    # driver.find_element(By.ID, "username").send_keys(username)
    # driver.find_element(By.ID, "password").send_keys(password)
    # driver.find_element(By.XPATH, "//button[@type='submit']").click()
    # ... استكمال الاستخراج ...
    pass

# ==================================================
# 6. المصدر الثالث: مكتبة التشريعات (يتطلب تسجيل دخول)
# ==================================================
def scrape_ccl(username: str, password: str):
    """
    سحب البيانات من ccl.gov.eg.
    يتطلب تسجيل دخول (تم إيقافها مؤقتاً).
    """
    print("\n🔐 [3] الوصول إلى ccl.gov.eg (معلق).")
    print("   ⚠️ يتطلب اشتراكاً وتفعيل حساب.")
    # TODO: تفعيل عند توفر الاشتراك
    pass

# ==================================================
# 7. المعالج الرئيسي للوثائق
# ==================================================
def process_document(doc_info: Dict):
    doc_id = generate_doc_id(doc_info["title"], doc_info["year"])
    
    index = load_index()
    if is_duplicate(doc_id, index):
        print(f"⏩ مكرر: {doc_id} - تم التخطي.")
        return
    
    doc_type = doc_info.get("doc_type", "other")
    target_dir = RAW_DIR / doc_type
    target_dir.mkdir(parents=True, exist_ok=True)
    
    file_name = f"{doc_id}.pdf"
    save_path = target_dir / file_name
    
    # تحميل الملف (إذا كان رابط PDF)
    if doc_info.get("source_url", "").endswith('.pdf'):
        print(f"⬇️  تحميل: {doc_info['title']}")
        if not download_pdf(doc_info["source_url"], save_path):
            return
    else:
        # إذا كان رابط صفحة، نضيفه كملف HTML أو ننتظر
        print(f"📄 رابط صفحة (ليس PDF مباشر): {doc_info['source_url']}")
        # يمكن حفظ الرابط في metadata للرجوع إليه لاحقاً
    
    new_doc_entry = {
        "doc_id": doc_id,
        "doc_type": doc_type,
        "title_ar": doc_info["title"],
        "year": doc_info["year"],
        "source": doc_info.get("source", {}),
        "file_path": str(save_path.relative_to(BASE_DIR)) if save_path.exists() else None,
        "fidelity_level": doc_info.get("fidelity_level", "official"),
        "status": "extracted",
        "added_to_index": datetime.now().isoformat()
    }
    
    index["documents"].append(new_doc_entry)
    save_index(index)
    print(f"✅ تم حفظ الفهرس: {doc_id}")

# ==================================================
# 8. التشغيل الرئيسي
# ==================================================
if __name__ == "__main__":
    print("="*50)
    print("🚀 بدء تشغيل سكريبت سحب البيانات")
    print("="*50)
    
    # 1. المصدر المجاني (مباشر)
    scrape_manshurat()
    
    # 2. المصادر المدفوعة (معلقة لحين توفر بيانات الدخول)
    # scrape_alamiria("USERNAME_HERE", "PASSWORD_HERE")
    # scrape_ccl("USERNAME_HERE", "PASSWORD_HERE")
    
    print("\n✅ اكتملت العملية.")