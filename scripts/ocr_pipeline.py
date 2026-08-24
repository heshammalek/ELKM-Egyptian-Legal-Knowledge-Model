"""
================================================================================
ELKM - OCR Pipeline
scripts/ocr_pipeline.py

المحرك: Gemini API (نظيف ودقيق)
المحركات المعلّقة: EasyOCR, Google Document AI

الاستخدام:
  python -m scripts.ocr_pipeline --file "دستور_جمهورية_مصر_العربية_المعدل_لسنة_2014.pdf"

التعديلات في هذه النسخة:
  1. المخرجات تُكتب في corpus/normalized/_pending_review/ وليس مباشرة في
     corpus/normalized/ — لأن المراجعة البشرية اليدوية لازم تحصل قبل الاعتماد.
  2. حد أقصى لمحاولات انتظار حالة "PROCESSING" من Gemini.
  3. طباعة تحذيرات grammar.py الجديدة بوضوح في نهاية كل تشغيل.
  4. تقسيم تلقائي للملفات الكبيرة عند مواجهة خطأ RECITATION/SAFETY.
  5. استخدام gemini-1.5-flash (النموذج الأصلي الذي يعمل معك).
================================================================================
"""

import os
import re
import json
import time
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
from typing import Tuple, Dict, Any, Optional, List

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


# ════════════════════════════════════════════════════════
# 1. إعداد البيئة
# ════════════════════════════════════════════════════════

def load_env(env_path: str = ".env") -> dict:
    env = {}
    env_file = Path(env_path)
    if not env_file.exists():
        raise FileNotFoundError(f"ملف .env غير موجود في: {env_file.absolute()}")
    with open(env_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                value = value.strip().strip('"').strip("'")
                env[key.strip()] = value
    return env


ENV = load_env(".env")
GEMINI_API_KEY = ENV.get("GEMINI_API_KEY", "")

BASE_DIR = Path(__file__).parent.parent
RAW_DIR = BASE_DIR / "corpus" / "raw"
NORMALIZED_DIR = BASE_DIR / "corpus" / "normalized"
PENDING_REVIEW_DIR = NORMALIZED_DIR / "_pending_review"
RAW_DIR.mkdir(parents=True, exist_ok=True)
NORMALIZED_DIR.mkdir(parents=True, exist_ok=True)
PENDING_REVIEW_DIR.mkdir(parents=True, exist_ok=True)


# ════════════════════════════════════════════════════════
# 2. الملف المستهدف — غيّر المسار ده قبل كل تشغيل
# ════════════════════════════════════════════════════════

TARGET_FILE = "constitutions/دستور_جمهورية_مصر_العربية_المعدل_لسنة_2014.pdf"


# ════════════════════════════════════════════════════════
# 2.1 تحديد النوع تلقائياً من اسم الفولدر
# ════════════════════════════════════════════════════════

FOLDER_TO_DOC_TYPE = {
    "constitutions": "constitutions",
    "law": "law",
    "regulation": "regulation",
    "decree": "decree",
    "judgment": "judgment",
    "fatwa": "fatwa",
    "treaty": "treaty",
    "draft": "draft",
    "report": "report",
    "jurisprudence": "jurisprudence",
}

DOC_TYPE_PREFIX = {
    "constitution": "EG-CONST",
    "law": "EG-LAW",
    "regulation": "EG-REG",
    "decree": "EG-DECREE",
    "judgment": "EG-JUDG",
    "fatwa": "EG-FATWA",
    "treaty": "EG-TREATY",
    "draft": "EG-DRAFT",
    "report": "EG-REPORT",
    "jurisprudence": "EG-JURIS",
    "other": "EG-OTHER",
}

# ════════════════════════════════════════════════════════
# 2.2 معرّفات يدوية دقيقة (اختياري)
# ════════════════════════════════════════════════════════

KNOWN_DOC_IDS = {
    "دستور_جمهورية_مصر_العربية_المعدل_لسنة_2014.pdf": "EG-CONST-2014",
    "دستور_جمهورية_مصر_العربية_لسنة_2012.pdf": "EG-CONST-2012",
    "قانون_العمل_رقم_14_لسنة_2025.pdf": "EG-LAW-2025-014",
    "قانون_رقم_155_لسنة_2024_باصدار_قانون_التامين_الموحد.txt": "EG-LAW-2024-155",
}


def slugify_filename(stem: str) -> str:
    """يحوّل اسم الملف لمعرّف مختصر صالح للاستخدام كـ doc_id."""
    ascii_slug = re.sub(r"[^A-Za-z0-9]+", "-", stem).strip("-")
    if len(ascii_slug) >= 3:
        return ascii_slug.upper()
    return hashlib.sha1(stem.encode("utf-8")).hexdigest()[:8].upper()


def resolve_target(relative_path: str) -> Tuple[Path, str, str]:
    """
    يحدد المسار الكامل، ونوع الوثيقة، ومعرّفها من مسار نسبي.
    يرجع: (المسار الكامل, doc_type, doc_id)
    """
    rel = Path(relative_path)
    full_path = RAW_DIR / rel
    parts = rel.parts

    folder = parts[0] if len(parts) > 1 else None
    doc_type = FOLDER_TO_DOC_TYPE.get(folder)
    if doc_type is None:
        print(f"  ⚠ الفولدر '{folder}' مش من التصنيفات المعروفة "
              f"({', '.join(FOLDER_TO_DOC_TYPE)}) — هيتسجل كـ 'other'.")
        doc_type = "other"

    filename = rel.name
    if filename in KNOWN_DOC_IDS:
        doc_id = KNOWN_DOC_IDS[filename]
    else:
        prefix = DOC_TYPE_PREFIX.get(doc_type, "EG-OTHER")
        doc_id = f"{prefix}-{slugify_filename(rel.stem)}"
        print(f"  ⚠ '{filename}' مش مسجّل في KNOWN_DOC_IDS — "
              f"تم توليد معرّف تلقائي: {doc_id}")

    return full_path, doc_type, doc_id


# ════════════════════════════════════════════════════════
# 3. استخراج النص من Gemini
# ════════════════════════════════════════════════════════

# النموذج الأصلي الذي كان يعمل معك
MODEL_NAME = "gemini-1.5-flash"

def _extract_text_or_raise(response, pdf_path: Path) -> str:
    """استخراج النص مع تشخيص دقيق للأخطاء"""
    if response.text:
        return response.text.strip()

    candidate = response.candidates[0] if response.candidates else None
    finish_reason = getattr(candidate, "finish_reason", None)
    safety_ratings = getattr(candidate, "safety_ratings", None)

    # محاولة استخراج النص من الأجزاء يدوياً
    manual_text = ""
    if candidate and candidate.content and candidate.content.parts:
        for part in candidate.content.parts:
            if getattr(part, "text", None) and not getattr(part, "thought", False):
                manual_text += part.text

    if manual_text.strip():
        print("  ⚠ response.text كانت فاضية، لكن تم استخراج نص من الأجزاء يدوياً.")
        return manual_text.strip()

    print(f"  ❌ فشل استخراج النص من {pdf_path.name}")
    print(f"     finish_reason : {finish_reason}")
    print(f"     safety_ratings: {safety_ratings}")
    
    # رفع الخطأ مع التفاصيل
    error_msg = f"لم يُرجع Gemini أي نص لملف {pdf_path.name} — finish_reason={finish_reason}."
    raise RuntimeError(error_msg)


def split_pdf(pdf_path: Path, pages_per_part: int = 20) -> List[Path]:
    """يقسم ملف PDF إلى أجزاء صغيرة ويعيد مسارات الملفات المؤقتة"""
    try:
        import fitz
    except ImportError:
        raise ImportError("pip install PyMuPDF")
    
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    parts = []
    
    # إذا كان الملف صغيراً، لا نقسمه
    if total_pages <= pages_per_part:
        return [pdf_path]
    
    for start in range(0, total_pages, pages_per_part):
        end = min(start + pages_per_part, total_pages)
        temp_path = pdf_path.parent / f"{pdf_path.stem}_part_{start+1}_{end}.pdf"
        
        new_doc = fitz.open()
        for page_num in range(start, end):
            new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
        new_doc.save(temp_path)
        new_doc.close()
        parts.append(temp_path)
    
    doc.close()
    return parts


def process_single_part(pdf_path: Path, max_wait_attempts: int = 30) -> Tuple[str, int]:
    """معالجة جزء واحد من PDF"""
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        raise ImportError("pip install google-genai")

    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY غير موجود في .env")

    client = genai.Client(api_key=GEMINI_API_KEY)

    with open(pdf_path, "rb") as f:
        uploaded = client.files.upload(
            file=f,
            config=types.UploadFileConfig(
                mime_type="application/pdf",
                display_name=pdf_path.name
            )
        )

    attempts = 0
    while uploaded.state.name == "PROCESSING":
        if attempts >= max_wait_attempts:
            raise TimeoutError(
                f"انتظار معالجة الملف تجاوز {max_wait_attempts} محاولة"
            )
        time.sleep(2)
        uploaded = client.files.get(name=uploaded.name)
        attempts += 1

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            types.Part.from_uri(
                file_uri=uploaded.uri,
                mime_type="application/pdf"
            ),
            """استخرج النص الكامل من هذا المستند القانوني المصري.
قواعد صارمة:
- استخرج النص كما هو بدون أي تعديل أو تلخيص
- احتفظ بأرقام المواد وعناوين الأبواب والفصول كما هي
- لا تضف أي نص من عندك
- النص فقط"""
        ],
        config=types.GenerateContentConfig(
            temperature=0,
        )
    )

    client.files.delete(name=uploaded.name)

    text = _extract_text_or_raise(response, pdf_path)
    
    # حساب عدد الصفحات
    try:
        import fitz
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
    except:
        total_pages = max(1, pdf_path.stat().st_size // 50_000)

    return text, total_pages


def process_with_gemini_safe(pdf_path: Path) -> Tuple[str, int]:
    """يستخرج النص من PDF باستخدام Gemini مع تقسيم تلقائي إذا لزم الأمر"""
    # نبدأ بتقسيم الملف إلى أجزاء صغيرة مباشرة (20 صفحة لكل جزء)
    # لأن الملف كبير والمشكلة كانت في RECITATION
    print(f"  ↑ تقسيم الملف إلى أجزاء (20 صفحة لكل جزء) لتجنب مشاكل RECITATION...")
    
    parts = split_pdf(pdf_path, pages_per_part=20)
    
    # إذا كان الملف أصغر من 20 صفحة، parts سيكون [pdf_path] فقط
    if len(parts) == 1 and parts[0] == pdf_path:
        print(f"  ↳ الملف صغير (أقل من 20 صفحة)، نعالجه كاملاً...")
        return process_single_part(pdf_path)
    
    full_text_parts = []
    total_pages = 0
    
    for i, part_path in enumerate(parts):
        print(f"  ↳ معالجة الجزء {i+1}/{len(parts)}: {part_path.name}")
        try:
            text, pages = process_single_part(part_path)
            full_text_parts.append(text)
            total_pages += pages
            print(f"    ✓ تم استخراج {len(text):,} حرف من الجزء {i+1}")
        except Exception as e:
            print(f"  ❌ فشل الجزء {i+1}: {e}")
            # إذا فشل جزء، نحاول تقسيمه إلى أجزاء أصغر (10 صفحات)
            if "RECITATION" in str(e) or "SAFETY" in str(e):
                print(f"  ↳ نحاول مرة أخرى بـ 10 صفحات...")
                smaller_parts = split_pdf(part_path, pages_per_part=10)
                for j, small_path in enumerate(smaller_parts):
                    try:
                        text, pages = process_single_part(small_path)
                        full_text_parts.append(text)
                        total_pages += pages
                        print(f"    ✓ تم استخراج {len(text):,} حرف من الجزء الصغير {j+1}")
                    except Exception as e3:
                        print(f"  ❌ فشل الجزء الصغير {small_path.name}: {e3}")
                    finally:
                        # تنظيف الملف الصغير
                        if small_path.exists() and small_path != pdf_path:
                            small_path.unlink()
        
        # تنظيف الملف المؤقت
        if part_path.exists() and part_path != pdf_path:
            part_path.unlink()
    
    if not full_text_parts:
        raise RuntimeError("فشل استخراج النص من جميع أجزاء الملف")
    
    final_text = "\n\n".join(full_text_parts)
    print(f"  ✓ تم دمج {len(full_text_parts)} جزء بنجاح")
    return final_text, total_pages


# ════════════════════════════════════════════════════════
# 4. استخراج المواد (Grammar)
# ════════════════════════════════════════════════════════

def parse_legal_text(text: str) -> Dict[str, Any]:
    """يستخرج المواد والأبواب والفصول من النص القانوني"""
    from scripts.grammar import parse_legal_text as grammar_parse
    return grammar_parse(text)


# ════════════════════════════════════════════════════════
# 5. تطبيع النص
# ════════════════════════════════════════════════════════

def normalize_arabic(text: str) -> str:
    text = re.sub(r"[إأآ]", "ا", text)
    text = re.sub(r"ى", "ي", text)
    text = re.sub(r"ة", "ه", text)
    text = re.sub(r"[\u064B-\u065F\u0670]", "", text)
    text = re.sub(r"ـ+", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ════════════════════════════════════════════════════════
# 6. بناء المستند
# ════════════════════════════════════════════════════════

def build_document(
    pdf_path: Path,
    law_id: str,
    law_type: str,
    full_text: str,
    total_pages: int,
    engine: str
) -> Dict[str, Any]:
    """يبني المستند النهائي"""
    from scripts.grammar import parse_legal_text

    normalized_text = normalize_arabic(full_text)

    print("  📊 تحليل النص بالـ Grammar...")
    parsed = parse_legal_text(normalized_text)
    print(f"    ✅ استخرج {parsed['statistics']['total_articles']} مادة "
          f"| {parsed['statistics']['total_chapters']} باب "
          f"| {parsed['statistics']['total_sections']} فصل")

    if parsed["warnings"]:
        print("    ⚠ تحذيرات تحتاج مراجعة يدوية قبل الاعتماد:")
        for w in parsed["warnings"]:
            print(f"      - {w}")
    else:
        print("    ✅ لا توجد تحذيرات في ترقيم المواد.")

    return {
        "doc_id": law_id,
        "doc_type": law_type,
        "ocr_engine": engine,
        "source_file": pdf_path.name,
        "processed_at": datetime.now().isoformat(),
        "review_status": "pending_review",
        "total_pages": total_pages,
        "total_chars": len(full_text),
        "total_articles": parsed["statistics"]["total_articles"],
        "full_text_display": full_text,
        "full_text_normalized": normalized_text,
        "structure": {
            "chapters": parsed["chapters"],
            "sections": parsed["sections"]
        },
        "articles": parsed["articles"],
        "grammar_stats": parsed["statistics"],
        "grammar_warnings": parsed["warnings"],
    }


# ════════════════════════════════════════════════════════
# 7. حفظ النتيجة — في مجلد المراجعة المعلّقة أولاً
# ════════════════════════════════════════════════════════

def save_document(doc: Dict[str, Any]):
    """يحفظ في corpus/normalized/_pending_review/"""
    doc_id = doc["doc_id"]
    json_path = PENDING_REVIEW_DIR / f"{doc_id}.json"
    txt_path = PENDING_REVIEW_DIR / f"{doc_id}_normalized.txt"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(doc["full_text_normalized"])

    print(f"  ✅ {json_path.relative_to(BASE_DIR)}")
    print(f"  ✅ {txt_path.relative_to(BASE_DIR)}")
    print(f"  📊 مواد: {doc['total_articles']}")
    print(f"  📊 أبواب: {len(doc['structure']['chapters'])}")
    print(f"  📊 فصول: {len(doc['structure']['sections'])}")
    print(f"  🔎 الحالة: {doc['review_status']} — راجع الملف يدوياً قبل نقله لـ corpus/normalized/")


# ════════════════════════════════════════════════════════
# 8. المعالجة الرئيسية
# ════════════════════════════════════════════════════════

def process_file(relative_path: str, engine: str = "gemini", dry_run: bool = False):
    """
    relative_path: مسار نسبي داخل corpus/raw/، مثل:
                    'constitution/دستور_....pdf' أو 'law/قانون_العمل....pdf'
    """
    pdf_path, doc_type, doc_id = resolve_target(relative_path)

    if not pdf_path.exists():
        print(f"✗ الملف غير موجود: {pdf_path.absolute()}")
        print(f"  تأكد إن TARGET_FILE مطابق تماماً لمسار الملف داخل corpus/raw/")
        return

    print(f"\n{'='*52}")
    print(f"  📄 الملف   : {pdf_path.name}")
    print(f"  📁 المسار  : {relative_path}")
    print(f"  🆔 المعرّف : {doc_id}")
    print(f"  📂 النوع   : {doc_type}")
    print(f"  ⚙️ المحرك  : {engine}")
    print(f"  🤖 النموذج : {MODEL_NAME}")
    print(f"{'='*52}\n")

    if dry_run:
        print("  [DRY RUN] لا يُرسل طلب للـ API")
        return

    text, pages = process_with_gemini_safe(pdf_path)
    doc = build_document(pdf_path, doc_id, doc_type, text, pages, engine)
    save_document(doc)
    print(f"\n✅ {doc_id} — اكتمل بنجاح (بانتظار المراجعة اليدوية)\n")


def process_all(engine: str = "gemini", dry_run: bool = False):
    """يعالج كل ملفات PDF داخل corpus/raw/ وكل الفولدرات الفرعية بداخله."""
    pdfs = list(RAW_DIR.rglob("*.pdf"))
    if not pdfs:
        print(f"لا توجد ملفات PDF في {RAW_DIR} (بحث متضمن كل الفولدرات الفرعية)")
        return
    print(f"وجدت {len(pdfs)} ملف PDF")
    for p in pdfs:
        relative_path = str(p.relative_to(RAW_DIR))
        process_file(relative_path, engine=engine, dry_run=dry_run)


# ════════════════════════════════════════════════════════
# 9. CLI
# ════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ELKM OCR Pipeline - Gemini")

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("--file", "-f",
                       help="مسار الملف نسبياً لـ corpus/raw/ (مثل: constitution/الملف.pdf). "
                            "لو معملتش تمرير، السكريبت هيستخدم TARGET_FILE المحدد أعلى الملف.")
    group.add_argument("--all", "-a", action="store_true",
                       help="معالجة كل ملفات PDF في raw/ وكل الفولدرات الفرعية")

    parser.add_argument("--dry-run", action="store_true",
                        help="اختبار بدون إرسال للـ API")

    args = parser.parse_args()

    print("─" * 45)
    print(f"المحرك : Gemini")
    print(f"النموذج: {MODEL_NAME}")
    print(f"API Key: {'✓ موجود' if GEMINI_API_KEY else '❌ غير محدد'}")
    print("─" * 45)

    if args.all:
        process_all(dry_run=args.dry_run)
    else:
        target = args.file or TARGET_FILE
        process_file(target, dry_run=args.dry_run)


# ════════════════════════════════════════════════════════
# 10. المحركات المعلّقة (كومنتات)
# ════════════════════════════════════════════════════════

'''
المحرك المعلّق: EasyOCR
----------------------------
import easyocr

def ocr_with_easyocr(pdf_path: Path) -> str:
    reader = easyocr.Reader(['ar'], gpu=False)
    doc = fitz.open(pdf_path)
    full_text = []
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=150)
        img_path = f"temp_page_{i}.png"
        pix.save(img_path)
        result = reader.readtext(img_path, detail=0, paragraph=True)
        full_text.append("\n".join(result))
    return "\n\n".join(full_text)

المحرك المعلّق: Google Document AI
----------------------------
from google.cloud import documentai

def process_with_document_ai(pdf_path: Path) -> Tuple[str, int]:
    client = documentai.DocumentProcessorServiceClient()
    result = client.process_document(...)
    return result.document.text, len(result.document.pages)
'''