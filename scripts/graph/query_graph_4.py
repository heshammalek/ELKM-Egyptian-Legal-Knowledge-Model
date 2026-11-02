#بيحاول يستخدم Gemini عشان يحول السؤال لـ Cypher.  - لو Gemini رد (نجح)، بينفذ الـ Cypher.- لو Gemini فشل (زي ما بيحصل دلوقتي)، بيرجع تلقائياً للبحث التقليدي (زي query_graph_3) عشان ميسيبكش من غير إجابة.


import os
import json
import sys
from dotenv import load_dotenv
from google import genai

# إضافة مسار الجذر
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from scripts.utils.db import get_driver

# تحميل المتغيرات
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ مفتاح GEMINI_API_KEY مش موجود في ملف .env")
    sys.exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)

# =========================================================
# 1. محاولة استخدام Gemini (لو شغال)
# =========================================================
def try_gemini(question):
    prompt = f"""
    أنت خبير في Neo4j Cypher. عندك جراف قانوني بالهيكل ده:
    - (:Document {{doc_id, title_ar}})
    - (:Article {{doc_id, article_number}})
    - (:Article)-[r:RELATION {{type_name}}]->(:Article)
    - (:Document)-[:HAS_ARTICLE]->(:Article)

    **المهمة:** حول السؤال ده لـ Cypher Query.
    استخدم `CONTAINS` للبحث في `title_ar`.

    أرجع الكود بس، بدون أي شرح أو علامات مارك داون.
    السؤال: {question}
    """
    try:
        response = client.models.generate_content(model='gemini-3.8-flash', contents=prompt)
        cypher = response.text.strip()
        if cypher.startswith("```"): cypher = cypher.split("\n", 1)[1]
        if cypher.endswith("```"): cypher = cypher.rsplit("\n", 1)[0]
        return cypher.strip()
    except Exception as e:
        # لو فشل، بنرجع None عشان نروح للبحث التقليدي
        return None

# =========================================================
# 2. البحث التقليدي (Rule-based) - زي query_graph_3
# =========================================================
def search_traditional(keyword):
    print(f"🔍 جاري البحث التقليدي عن: {keyword} ...")
    driver = get_driver()
    try:
        with driver.session() as session:
            query = "MATCH (d:Document) WHERE d.title_ar CONTAINS $kw RETURN d.doc_id, d.title_ar"
            result = session.run(query, kw=keyword)
            docs = list(result)
            
            if not docs:
                print(f"📭 مفيش مستند اسمه فيه '{keyword}'")
                return

            for doc in docs:
                doc_id = doc["d.doc_id"]
                print(f"\n✅ تم العثور على المستند: {doc['d.title_ar']} ({doc_id})")

                query_rel = """
                MATCH (src:Article)-[r:RELATION]->(tgt)
                WHERE (src.doc_id = $doc_id OR tgt.doc_id = $doc_id)
                RETURN 
                    CASE WHEN src.doc_id = $doc_id THEN 'Source' ELSE 'Target' END AS direction,
                    src.doc_id AS src_doc, src.article_number AS src_art,
                    r.type_name AS rel_type,
                    tgt.doc_id AS tgt_doc, tgt.article_number AS tgt_art,
                    r.reference_text AS ref_text
                """
                result_rel = session.run(query_rel, doc_id=doc_id)
                records = list(result_rel)
                
                if not records:
                    print("📭 مفيش علاقات مرتبطة.")
                    continue

                print(f"✅ تم العثور على {len(records)} علاقة:\n")
                for i, rec in enumerate(records, 1):
                    print(f"--- العلاقة {i} ({rec['direction']}) ---")
                    print(f"المصدر: {rec['src_doc']} (مادة {rec['src_art']})")
                    print(f"نوع العلاقة: {rec['rel_type']}")
                    print(f"الهدف: {rec['tgt_doc']} (مادة {rec['tgt_art']})")
                    print()

    except Exception as e:
        print(f"❌ خطأ في البحث: {e}")
    finally:
        driver.close()

# =========================================================
# 3. الدالة الرئيسية اللي بتنسق بينهم
# =========================================================
def ask_graph(question):
    print(f"🤔 جاري تحليل السؤال: {question}")
    
    # 1. محاولة استخدام AI
    cypher = try_gemini(question)
    
    if cypher:
        print(f"\n📝 الاستعلام المترجم (من AI):\n{cypher}\n")
        driver = get_driver()
        try:
            with driver.session() as session:
                result = session.run(cypher)
                records = list(result)
                if records:
                    print(f"✅ تم العثور على {len(records)} نتيجة.")
                    for rec in records:
                        print(rec.data())
                    return
                else:
                    print("📭 مفيش نتايج. جاري التجربة بالبحث التقليدي...")
        except Exception as e:
            print(f"❌ فشل الاستعلام (AI): {e}. جاري التجربة بالبحث التقليدي...")
        finally:
            driver.close()

    # 2. لو AI فشل أو مفيش نتايج، بنروح للبحث التقليدي
    print("\n⚠️ استخدام البحث التقليدي (Rule-based).")
    
    # بنستخرج الكلمات المفتاحية من السؤال (أبسط طريقة: ناخد أطول كلمة أو اللي بعد "عن")
    keywords = ["الإجراءات الجنائية", "قانون العقوبات", "الضمان الاجتماعي"] # ممكن نزود
    found_kw = None
    for kw in keywords:
        if kw in question:
            found_kw = kw
            break
    
    if found_kw:
        search_traditional(found_kw)
    else:
        # لو ملقاش كلمة من القايمة، يدور على أطول كلمة في السؤال
        words = question.split()
        longest_word = max(words, key=len) if words else ""
        if longest_word:
            search_traditional(longest_word)
        else:
            print("❌ مش قادر أفهم السؤال.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_question = " ".join(sys.argv[1:])
    else:
        user_question = input("💬 اكتب سؤالك القانوني: ")
    
    ask_graph(user_question)
