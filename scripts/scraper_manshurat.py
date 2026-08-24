"""
ELKM - Web Scraper for Manshurat.org
سكريبت سحب البيانات من موقع منشورات (التصنيفات المتعددة)
"""

import os
import json
import re
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List
from bs4 import BeautifulSoup

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
# 2. تعريف التصنيفات (Term IDs) وأسمائها
# ==================================================
CATEGORIES = {
    # --- التصنيفات المؤكدة (تعمل حالياً) ---
    
    "2": "وثائق دستورية",
    "3": "أحكام ووثائق قضائية",
    "4": "فتاوى",
    "5": "قرارات  ",
    "6": "قرارات وزارية",
    "7": "قرارات رئاسية",
    "8": "قرارات محافظين",
    "9": "قرارات إدارية أخرى",
    "10": "تقارير وبيانات ",
    "11": "تقارير حكومية أجنبية وجهات دولية  ",
    "12": "تقارير حكومية مصرية ",
    "13": "تقارير غير حكومية مصرية ودولية ",
    "14": "لجان تقصي الحقائق",
    "15": "أحكام ووثائق قضائية ",
    "16": "أحكام ",
    "17": "تبليغات قسم التشريع",
    "18": "تقارير هيئة المفوضين  ",
    "19": "فتاوى  ",
    "20": "قرارات نيابة    ",
    "21": "قوانين ولوائح",
    "22": "مذكرات إيضاحية / أعمال تحضيرية / مشروعات قوانين  ",
    "23": "قوانين",
    "24": " اتفاقيات ومعاهدات دولية  ",
    "25": "لوائح",
    "26": "الدولة ونظام الحكم ",
    "27": "المجالات و القطاعات",
    "28": "الانتخابات  ",
    "29": "البرلمان  ",
    "30": "الجهات الرقابية والمجالس  ",
    "31": "الشئون الدستورية",
    "32": "الشئون العسكرية",
    "33": "تنظيم السلطة التنفيذية ",
    "34": "تنظيم السلطة القضائية ",
    "35": "حقوق مدنية وسياسية",
    "36": "الأحزاب",
    "37": " ",
    "38": "التظاهر والاحتجاج ",
    "39": "الجمعيات الأهلية والتعاونية ",
    "40": "الشئون الدينية  ",
    "41": "النقابات ",
    "42": "الهجرة والجنسية ",
    "43": "حرية التعبير وتداول المعلومات",
    "44": "سياسات اقتصادية ومالية",
    "45": "الإدارة المحلية",
    "46": "التعاون الدولي",
    "47": "الزراعة",
    "48": " السياحة",
    "49": "الطاقة",
    "50": "القطاع المصرفي وسوق المال",
    "51": "المالية العامة ",
    "52": "بنية تحتية و مرافق عامة",
    "53": "مكافحة الفساد والتصالح ",
    "54": "شئون اجتماعية وثقافية ",
    "55": "الآثار",
    "56": "البيئة",
    "57": "التعليم ",
    "58": "الثقافة",
    "59": "السكن ",
    "60": "الصحة العامة",
    "61": "الضمان الاجتماعي ",
    "62": "العمل ",
    "63": "الرياضة",
    "64": "قضايا الطفل ",
    "65": "قضايا المرأة ",
    "66": " عدالة جنائية وشئون أمنية  ",
    "67": "  ",
    "68": " الإجراءات الجنائية ",
    "69": "السجون والعفو عن السجناء ",
    "70": "الشرطة والأجهزة الأمنية ",
    "71": "   ",
    "72": "الطوارئ والقضاء الاستثنائي",
    "73": " ",
    "74": "القضاء العسكري  ",
    "75": "المحاسبة وتقصي الحقائق ",
    "76": "المخدرات ",
    "77": "الإرهاب وجرائم العنف ",
    "78": "25 يناير ",
    "79": " 3 يوليو ",
    "80": "30 يونيو ",
    "81": "6 أبريل ",
    "82": " ",
    "83": "أبناء الأم المصرية ",
    "85": "أجهزة اتصالات ",




    "4786": "الجهات الرقابية والمجالس",
    "4092": "الأحوال الشخصية  ",

    
    # --- تصنيفات محتملة (معلقة لحين التحقق) ---
 
    # 
    # 
    #
    #
    #"63": "السكن ",
    #"64": "السكن ",
    #"65": "السكن ",
}

# ==================================================
# 3. دوال إدارة الفهرس
# ==================================================
def load_index() -> Dict:
    """تحميل الفهرس، وإعادة تعيينه إذا كان تالفاً"""
    if METADATA_INDEX.exists():
        try:
            with open(METADATA_INDEX, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
        except:
            print("⚠️ ملف الفهرس تالف، سيتم إعادة إنشائه.")
    return {"documents": []}

def save_index(index: Dict):
    """حفظ الفهرس في ملف JSON"""
    with open(METADATA_INDEX, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

def download_pdf(url: str, save_path: Path) -> bool:
    """تحميل ملف PDF من الرابط"""
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

def extract_doc_id_from_title(title: str) -> tuple:
    """استخراج رقم القانون وسنته من العنوان"""
    number_match = re.search(r'رقم\s*(\d+)', title)
    number = number_match.group(1) if number_match else None
    
    year_match = re.search(r'(\d{4})', title)
    year = year_match.group(1) if year_match else None
    
    return number, year

def extract_pdf_link(soup: BeautifulSoup) -> Optional[str]:
    """استخراج رابط PDF من الصفحة"""
    # البحث عن زر التحميل
    download_link = soup.find('a', string=re.compile(r'Download|تحميل'))
    if download_link and download_link.get('href'):
        return download_link['href']
    
    # البحث عن أي رابط ينتهي بـ .pdf
    for link in soup.find_all('a', href=True):
        if link['href'].endswith('.pdf'):
            return link['href']
    
    return None

def get_document_type_from_title(title: str) -> str:
    """تحديد نوع الوثيقة من العنوان"""
    if "قانون" in title and "رقم" in title:
        return "law"
    elif "مشروع" in title:
        return "draft"
    elif "لائحة" in title:
        return "regulation"
    elif "تقرير" in title:
        return "report"
    elif "فتوى" in title:
        return "fatwa"
    elif "حكم" in title or "قضائي" in title:
        return "judgment"
    elif "قرار" in title and "رئاسي" in title:
        return "presidential_decree"
    elif "قرار" in title and "وزاري" in title:
        return "ministerial_decree"
    else:
        return "other"

def generate_unique_doc_id(title: str, number: Optional[str], year: Optional[str], category: str, index: int) -> str:
    """إنشاء معرف فريد للوثيقة"""
    if number and year:
        return f"LAW-{number}-{year}"
    
    # إنشاء معرف من النوع والعنوان
    clean_title = re.sub(r'[^\\w\\s]', '', title)
    # إزالة الكلمات الشائعة الطويلة
    clean_title = re.sub(r'(تعديل بعض أحكام|إصدار|قانون|اللائحة التنفيذية لـ?|تقرير اللجنة البرلمانية المختصة بمراجعة مشروع|مشروع)', '', clean_title)
    keywords = re.findall(r'[\\w]{3,}', clean_title)
    if keywords:
        short_title = '_'.join(keywords[:3])
    else:
        short_title = clean_title[:20].replace(' ', '_')
    
    if not year:
        year_match = re.search(r'(\d{4})', title)
        year = year_match.group(1) if year_match else "unknown"
    
    doc_id = f"{category.upper()}-{short_title}-{year}"
    # تنظيف المعرف من الأحرف الغريبة
    doc_id = re.sub(r'[^\\w\\-]', '', doc_id)
    doc_id = re.sub(r'-+', '-', doc_id)
    if len(doc_id) < 5:
        doc_id = f"{category.upper()}-{index:03d}-{year}"
    return doc_id

# ==================================================
# 4. سحب البيانات من صفحة تصنيف معين
# ==================================================
def scrape_category(category_id: str, category_name: str, max_pages: int = 5, start_page: int = 0):
    """سحب البيانات من تصنيف معين"""
    print(f"\n{'='*50}")
    print(f"📂 معالجة التصنيف: {category_name} (ID: {category_id})")
    print(f"{'='*50}")
    
    base_list_url = f"https://manshurat.org/taxonomy/term/{category_id}"
    all_doc_links = []
    
    for page_num in range(start_page, start_page + max_pages):
        page_url = f"{base_list_url}?page={page_num}"
        print(f"   📄 معالجة الصفحة {page_num + 1}: {page_url}")
        
        try:
            response = requests.get(page_url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            doc_links_page = []
            for item in soup.find_all('div', class_='views-row'):
                link_elem = item.find('a')
                if link_elem and link_elem.get('href'):
                    url = link_elem['href']
                    if not url.startswith('http'):
                        url = 'https://manshurat.org' + url
                    doc_links_page.append({
                        'title': link_elem.text.strip(),
                        'url': url
                    })
            
            if not doc_links_page:
                print(f"      ⚠️ لا توجد وثائق في الصفحة {page_num + 1}. قد تكون هذه آخر صفحة.")
                break
                
            print(f"      ✅ تم العثور على {len(doc_links_page)} وثيقة في الصفحة {page_num + 1}.")
            all_doc_links.extend(doc_links_page)
            time.sleep(1)
        except Exception as e:
            print(f"      ⚠️ فشل في معالجة الصفحة {page_num + 1}: {e}")
            break
    
    if not all_doc_links:
        print(f"⚠️ لم يتم العثور على أي وثائق في التصنيف {category_name}")
        return
    
    print(f"✅ إجمالي الوثائق في التصنيف: {len(all_doc_links)}")
    
    # تحميل الفهرس والتحقق من التكرار
    index = load_index()
    existing_ids = {doc.get('doc_id', '') for doc in index['documents']}
    new_docs_count = 0
    
    for i, doc in enumerate(all_doc_links):
        print(f"\n📄 معالجة ({i+1}/{len(all_doc_links)}): {doc['title'][:60]}...")
        
        # استخراج رقم القانون وسنته من العنوان
        number, year = extract_doc_id_from_title(doc['title'])
        
        # تحديد نوع الوثيقة
        doc_type = get_document_type_from_title(doc['title'])
        
        # إنشاء معرف فريد
        doc_id = generate_unique_doc_id(doc['title'], number, year, category_id, i+1)
        print(f"   📌 المعرف: {doc_id}")
        
        # التحقق من التكرار
        if doc_id in existing_ids:
            print(f"   ⏩ مكرر: {doc_id} - تم التخطي.")
            continue
        
        # فتح صفحة الوثيقة للحصول على رابط PDF
        try:
            page_response = requests.get(doc['url'], timeout=30)
            page_response.raise_for_status()
            page_soup = BeautifulSoup(page_response.text, 'html.parser')
            pdf_link = extract_pdf_link(page_soup)
        except Exception as e:
            print(f"   ⚠️ فشل فتح صفحة الوثيقة: {e}")
            continue
        
        if not pdf_link:
            print(f"   ⚠️ لا يوجد رابط PDF للتحميل.")
            # تسجيل الوثيقة في الفهرس بدون ملف
            new_entry = {
                "doc_id": doc_id,
                "doc_type": doc_type,
                "category_id": category_id,
                "category_name": category_name,
                "title_ar": doc['title'],
                "year": year or "unknown",
                "doc_number": number or "0",
                "source": {
                    "type": "website",
                    "url": doc['url'],
                    "retrieved_date": datetime.now().isoformat()
                },
                "file_path": None,
                "status": "no_pdf",
                "added_to_index": datetime.now().isoformat()
            }
            index['documents'].append(new_entry)
            existing_ids.add(doc_id)
            save_index(index)
            new_docs_count += 1
            continue
        
        # تحويل الرابط النسبي إلى كامل
        if pdf_link and not pdf_link.startswith('http'):
            if pdf_link.startswith('/'):
                pdf_link = 'https://manshurat.org' + pdf_link
            else:
                pdf_link = 'https://manshurat.org/' + pdf_link
        
        # تحديد مسار الحفظ
        target_dir = RAW_DIR / doc_type
        target_dir.mkdir(parents=True, exist_ok=True)
        
        file_name = f"{doc_id}.pdf"
        save_path = target_dir / file_name
        
        # تحميل الملف
        print(f"   ⬇️  تحميل: {doc['title'][:50]}...")
        if download_pdf(pdf_link, save_path):
            # حفظ في الفهرس
            new_entry = {
                "doc_id": doc_id,
                "doc_type": doc_type,
                "category_id": category_id,
                "category_name": category_name,
                "title_ar": doc['title'],
                "year": year or "unknown",
                "doc_number": number or "0",
                "source": {
                    "type": "website",
                    "url": doc['url'],
                    "retrieved_date": datetime.now().isoformat()
                },
                "file_path": str(save_path.relative_to(BASE_DIR)),
                "status": "extracted",
                "added_to_index": datetime.now().isoformat()
            }
            index['documents'].append(new_entry)
            existing_ids.add(doc_id)
            save_index(index)
            new_docs_count += 1
            print(f"   ✅ تم الحفظ: {save_path}")
        else:
            print(f"   ❌ فشل تحميل الملف.")
        
        # تأخير بسيط
        time.sleep(1)
    
    print(f"\n✅ اكتمل سحب التصنيف {category_name} (تمت إضافة {new_docs_count} وثيقة جديدة)")

# ==================================================
# 5. دالة سحب جميع التصنيفات
# ==================================================
def scrape_all_categories(max_pages_per_category: int = 5):
    """سحب جميع التصنيفات المؤكدة"""
    print("="*50)
    print("🚀 بدء سحب جميع التصنيفات من منشورات")
    print(f"📊 عدد التصنيفات: {len(CATEGORIES)}")
    print("="*50)
    
    total_docs = 0
    for category_id, category_name in CATEGORIES.items():
        try:
            scrape_category(category_id, category_name, max_pages_per_category)
            # إحصائيات مؤقتة
            index = load_index()
            total_docs = len(index['documents'])
            print(f"📊 إجمالي الوثائق حتى الآن: {total_docs}")
        except Exception as e:
            print(f"⚠️ فشل في سحب التصنيف {category_name} (ID: {category_id}): {e}")
            continue
    
    print("\n" + "="*50)
    print("✅ اكتمل سحب جميع التصنيفات")
    print(f"📊 إجمالي الوثائق: {total_docs}")
    print("="*50)

# ==================================================
# 6. دالة إعادة تعيين الفهرس
# ==================================================
def reset_index():
    """إعادة تعيين الفهرس بالكامل"""
    confirm = input("⚠️ هل أنت متأكد من حذف الفهرس بالكامل؟ (اكتب 'yes' للتأكيد): ")
    if confirm.lower() == 'yes':
        index = {"documents": []}
        save_index(index)
        print("✅ تم إعادة تعيين الفهرس.")
    else:
        print("❌ تم إلغاء العملية.")

# ==================================================
# 7. التشغيل الرئيسي
# ==================================================
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ELKM Web Scraper - Manshurat.org")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--category", "-c", help="معرف التصنيف (مثل 21 للقوانين)")
    group.add_argument("--all-categories", "-a", action="store_true", help="سحب جميع التصنيفات")
    parser.add_argument("--pages", "-p", type=int, default=5, help="عدد الصفحات لكل تصنيف (افتراضي: 5)")
    parser.add_argument("--reset-index", action="store_true", help="إعادة تعيين الفهرس بالكامل")
    
    args = parser.parse_args()
    
    print("="*50)
    print("🚀 ELKM - Web Scraper for Manshurat.org")
    print("="*50)
    
    if args.reset_index:
        reset_index()
        exit()
    
    if args.all_categories:
        scrape_all_categories(args.pages)
    elif args.category:
        category_name = CATEGORIES.get(args.category, f"تصنيف غير معروف (ID: {args.category})")
        scrape_category(args.category, category_name, args.pages)
    
    print("\n✅ اكتملت العملية.")