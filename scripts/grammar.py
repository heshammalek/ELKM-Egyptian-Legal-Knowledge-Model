"""
scripts/grammar.py
ELKM - استخراج المواد والأبواب والفصول من النص القانوني العربي

هذا الملف مسؤول فقط عن "استخراج البنية الهيكلية" (structure extraction)
بالـ Regex — فصل المستند إلى مواد/أبواب/فصول.

هو غير مسؤول عن "فهم الصياغة اللغوية" داخل كل مادة (الجملة الشرطية،
الإحالات، التعريفات) — ده مكانه ملف منفصل يستخدم Lark (شوف sentence_parse.py
وgrammar/legal_arabic.lark لاحقاً).

الإصلاحات في هذه النسخة مقارنة بالنسخة السابقة:
  1. فصل قسم "المحتوى" (الفهرس) عن متن الوثيقة قبل أي تحليل — كان هذا هو
     السبب الجذري لتلوث استخراج الأبواب/الفصول ولفقدان آخر مادة في المستند.
  2. تقييد "الباب"/"الفصل" بعدد ترتيبي معروف + بداية سطر، بدل أي ظهور
     للكلمتين في نص عادي (مثل "نغلق به الباب أمام الفساد" أو
     "الفصل بين السلطات").
  3. إزالة الحد الأقصى المُثبّت بالكود (num > 246) — كان يفترض خطأً أن كل
     مستند لن يتجاوز عدد مواد الدستور تحديداً، وكان يستبعد المادة 247 بشكل
     صريح ومتعمّد. الحد الأقصى الآن مبني على البيانات نفسها، لا على افتراض
     مسبق.
  4. تثبيت استخراج المواد على بداية السطر (^) بدل أي ظهور للنمط في أي مكان
     من النص — لتفادي التقاط إحالات داخلية مثل "طبقاً لأحكام المادة (5) من
     هذا القانون"، والتي ستكون شائعة جداً في قوانين أخرى غير الدستور.
  5. دالة تحقق (validate_articles) تُرجع تحذيرات صريحة عن أي فجوات في
     ترقيم المواد بدل الصمت عن المشكلة.
"""

import re
from pathlib import Path


# ════════════════════════════════════════════════════════
# قائمة الأعداد الترتيبية العربية المستخدمة في عناوين الأبواب/الفصول
# ════════════════════════════════════════════════════════

ORDINALS = [
    "الأول", "الاول",
    "الثاني", "الثالث", "الرابع", "الخامس",
    "السادس", "السابع", "الثامن", "التاسع", "العاشر",
    "الحادي عشر", "الثاني عشر", "الثالث عشر", "الرابع عشر", "الخامس عشر",
    "السادس عشر", "السابع عشر", "الثامن عشر", "التاسع عشر", "العشرون",
]
ORDINALS_PATTERN = "|".join(sorted(ORDINALS, key=len, reverse=True))


# ════════════════════════════════════════════════════════
# 1. تنظيف النص من تنسيق Markdown
# ════════════════════════════════════════════════════════

def clean_text(text: str) -> str:
    """
    ينظف النص من تنسيق Markdown الذي قد يتسرب أحياناً من مخرجات Gemini
    رغم تعليمات الـ prompt الصريحة بعدم استخدامه.
    """
    text = re.sub(r"\*\*", "", text)
    text = re.sub(r"__", "", text)
    text = re.sub(r"###?\s*", "", text)
    text = re.sub(r"---+\s*", "", text)
    text = re.sub(r"___+\s*", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


# ════════════════════════════════════════════════════════
# 2. فصل قسم "المحتوى" (الفهرس) عن متن الوثيقة
# ════════════════════════════════════════════════════════

def strip_toc(text: str) -> tuple[str, str]:
    """
    يفصل قسم الفهرس (المحتوى) الموجود عادة في نهاية الوثيقة عن المتن
    الفعلي، لأن الفهرس يكرر عناوين الأبواب/الفصول ونطاقات أرقام المواد
    (مثل "الباب الأول - الدولة (مادة 1 - مادة 6)")، وهذا التكرار كان يلوّث
    كل عملية استخراج هيكلي لاحقة.

    يرجع: (متن الوثيقة بدون الفهرس, نص الفهرس منفصلاً)
    """
    marker = re.search(r"\n\s*المحتوي[ةى]?\s*\n", text)
    if not marker:
        return text, ""
    return text[:marker.start()].strip(), text[marker.start():].strip()


# ════════════════════════════════════════════════════════
# 3. استخراج الأبواب والفصول (مقيّد بعدد ترتيبي + بداية سطر)
# ════════════════════════════════════════════════════════

def extract_headings(text: str, keyword: str) -> list[dict]:
    """
    يستخرج عناوين الأبواب أو الفصول، بشرط:
      - الكلمة المفتاحية (الباب/الفصل) في بداية السطر
      - متبوعة مباشرة بعدد ترتيبي معروف (الأول، الثاني...)
    هذا يمنع التقاط الكلمة في استخدامها العادي داخل جملة
    (مثل "نغلق به الباب أمام الفساد" أو "الفصل بين السلطات").
    """
    pattern = rf"^\s*{keyword}\s+({ORDINALS_PATTERN})\s*[-–—]?\s*([^\n]*)"
    items = []
    for m in re.finditer(pattern, text, re.MULTILINE):
        ordinal = m.group(1).strip()
        extra_title = m.group(2).strip()
        full_title = f"{ordinal} - {extra_title}" if extra_title else ordinal
        items.append({
            "type": "chapter" if keyword == "الباب" else "section",
            "title": full_title,
            "ordinal": ordinal,
            "position": m.start(),
            "end": 0,
        })
    for i, item in enumerate(items):
        item["end"] = items[i + 1]["position"] if i + 1 < len(items) else len(text)
    return items


# ════════════════════════════════════════════════════════
# 4. استخراج المواد (مقيّد ببداية السطر، بدون حد أقصى مُثبّت)
# ════════════════════════════════════════════════════════

ARTICLE_PATTERN = r"^\s*ماده?\s*\(?\s*([٠-٩\d]+)\s*\)?\s*[:.\-]?\s*$"

ARABIC_DIGIT_MAP = {'٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
                     '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'}


def _to_int(num_str: str) -> int | None:
    for a, b in ARABIC_DIGIT_MAP.items():
        num_str = num_str.replace(a, b)
    try:
        return int(num_str)
    except ValueError:
        return None


def extract_articles(text: str, chapters: list[dict], sections: list[dict]) -> list[dict]:
    """
    يستخرج المواد بشرط أن يكون نمط "مادة (رقم)" وحده في بداية السطر —
    ما يفرّق بين عنوان مادة حقيقي وبين إحالة داخلية مثل
    "طبقاً لأحكام المادة (5) من هذا القانون" التي تظهر عادة وسط جملة
    وليست وحدها على سطر مستقل.

    لا يوجد هنا أي حد أقصى مُثبّت بالكود لعدد المواد — العدد الحقيقي
    يُكتشف من البيانات نفسها، ويُتحقق منه لاحقاً بدالة validate_articles.
    """
    matches = list(re.finditer(ARTICLE_PATTERN, text, re.MULTILINE))

    seen = set()
    articles = []

    for i, m in enumerate(matches):
        num = _to_int(m.group(1))
        if num is None or num < 1:
            continue
        if num in seen:
            # أول ظهور للرقم هو الأصح دائماً (المستند يُقرأ من أوله)
            continue
        seen.add(num)

        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

        chapter_title = next(
            (c["title"] for c in chapters if c["position"] <= start < c["end"]),
            None,
        )
        section_title = next(
            (s["title"] for s in sections if s["position"] <= start < s["end"]),
            None,
        )

        articles.append({
            "article_number": num,
            "text": text[start:end].strip(),
            "chapter": chapter_title,
            "section": section_title,
        })

    return sorted(articles, key=lambda a: a["article_number"])


# ════════════════════════════════════════════════════════
# 5. التحقق من سلامة ترقيم المواد
# ════════════════════════════════════════════════════════

def validate_articles(articles: list[dict]) -> list[str]:
    """
    يرجع قائمة تحذيرات نصية بدل الصمت عن أي مشكلة في الترقيم.
    لا يحذف أو يستبعد أي شيء — القرار النهائي للمراجعة البشرية.
    """
    warnings = []
    if not articles:
        warnings.append("لم يتم استخراج أي مادة على الإطلاق — تحقق من نمط الـ regex أو من النص المصدر.")
        return warnings

    numbers = [a["article_number"] for a in articles]
    expected = set(range(1, max(numbers) + 1))
    missing = sorted(expected - set(numbers))
    if missing:
        warnings.append(f"مواد مفقودة من التسلسل: {missing}")

    if numbers[0] != 1:
        warnings.append(f"أول مادة مستخرجة رقمها {numbers[0]} وليس 1 — تحقق من بداية المستند.")

    return warnings


# ════════════════════════════════════════════════════════
# 6. الدالة الرئيسية
# ════════════════════════════════════════════════════════

def parse_legal_text(text: str) -> dict:
    """
    يستخرج المواد والأبواب والفصول من النص القانوني.
    """
    text = clean_text(text)
    body, toc = strip_toc(text)

    chapters = extract_headings(body, "الباب")
    sections = extract_headings(body, "الفصل")
    articles = extract_articles(body, chapters, sections)
    warnings = validate_articles(articles)

    return {
        "preamble": [],
        "chapters": chapters,
        "sections": sections,
        "articles": articles,
        "toc_stripped": bool(toc),
        "warnings": warnings,
        "statistics": {
            "total_articles": len(articles),
            "total_chapters": len(chapters),
            "total_sections": len(sections),
            "preamble_lines": 0,
        },
    }


if __name__ == "__main__":
    test_file = Path(__file__).parent.parent / "corpus" / "normalized" / "EG-CONST-2014_normalized.txt"
    if test_file.exists():
        with open(test_file, encoding="utf-8") as f:
            raw_text = f.read()
        result = parse_legal_text(raw_text)

        print("=" * 50)
        print(f"المواد: {result['statistics']['total_articles']}")
        print(f"الأبواب: {result['statistics']['total_chapters']}")
        print(f"الفصول: {result['statistics']['total_sections']}")
        print(f"تم فصل الفهرس: {'نعم' if result['toc_stripped'] else 'لا'}")
        print("=" * 50)

        if result["warnings"]:
            print("\n⚠ تحذيرات:")
            for w in result["warnings"]:
                print(f"  - {w}")
        else:
            print("\n✅ لا توجد تحذيرات — ترقيم المواد متسلسل بدون فجوات.")

        if result["chapters"]:
            print(f"\nالأبواب المستخرجة ({len(result['chapters'])}):")
            for ch in result["chapters"]:
                print(f"  - {ch['title']}")

        if result["articles"]:
            print("\nأول 3 مواد:")
            for art in result["articles"][:3]:
                print(f"  مادة {art['article_number']} [{art['chapter']}]: {art['text'][:60]}...")
            print("\nآخر 3 مواد:")
            for art in result["articles"][-3:]:
                print(f"  مادة {art['article_number']} [{art['chapter']}]: {art['text'][:60]}...")
    else:
        print("❌ ملف النص غير موجود")