import os
import json
import sys
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

# إضافة مسار الجذر
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from scripts.utils.db import get_driver

# تحميل المتغيرات من .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ مفتاح GEMINI_API_KEY مش موجود في ملف .env")
    sys.exit(1)

# تهيئة العميل بالمكتبة الجديدة
client = genai.Client(api_key=GEMINI_API_KEY)

def build_dynamic_prompt():
    metadata_dir = os.path.join(BASE_DIR, "corpus", "metadata")
    
    relation_types = []
    try:
        with open(os.path.join(metadata_dir, "relation_types.json"), 'r', encoding='utf-8') as f:
            rel_data = json.load(f)
            relation_types = [f'"{t["name"]}" ({t["name_ar"]})' for t in rel_data["relation_schema"]["types"]]
    except Exception as e:
        print(f"⚠️ تحذير: لم يتم قراءة relation_types.json: {e}")

    entities = []
    try:
        with open(os.path.join(metadata_dir, "entities.json"), 'r', encoding='utf-8') as f:
            ent_data = json.load(f)
            entities = [f'"{e["entity_id"]}" ({e.get("name_ar", "")})' for e in ent_data["entities"]]
    except Exception as e:
        print(f"⚠️ تحذير: لم يتم قراءة entities.json: {e}")

    positions = []
    try:
        with open(os.path.join(metadata_dir, "positions.json"), 'r', encoding='utf-8') as f:
            pos_data = json.load(f)
            positions = [f'"{p["position_id"]}" ({p.get("name_ar", "")})' for p in pos_data["positions"]]
    except Exception as e:
        print(f"⚠️ تحذير: لم يتم قراءة positions.json: {e}")

    rel_types_str = ", ".join(relation_types)
    entities_str = ", ".join(entities)
    positions_str = ", ".join(positions)

    prompt = f"""
أنت خبير في قاعدة بيانات Neo4j Cypher ولغة الاستعلامات.
عندك جراف معرفي للقانون المصري بالهيكلة التالية:
- العقد (Nodes):
  - (:Document {{doc_id, title_ar, doc_type, year}})
  - (:Article {{doc_id, article_number, text_normalized}})
  - (:Entity {{entity_id, name_ar}})
  - (:Position {{position_id, name_ar}})

- العلاقات (Relationships):
  - (:Document)-[:HAS_ARTICLE]->(:Article)
  - (:Article)-[r:RELATION]->(:Article) 
  - (:Article)-[r:RELATION]->(:Entity) 
  - (:Article)-[r:RELATION]->(:Position) 

- أنواع العلاقات (type_name) المتاحة حالياً:
  {rel_types_str}

- الكيانات (Entities) المتاحة حالياً:
  {entities_str}

- المناصب (Positions) المتاحة حالياً:
  {positions_str}

المهمة:
حول السؤال التالي إلى استعلام Cypher صالح. أرجع فقط الكود، بدون أي شرح أو علامات مارك داون (مثل ```cypher).
لو السؤال مش متعلق بالقانون المصري، أرجع: MATCH (n) RETURN n LIMIT 0;

السؤال: {{question}}
"""
    return prompt

def ask_graph(question):
    print(f"🤔 جاري تحليل السؤال: {question}")
    
    base_prompt = build_dynamic_prompt()
    prompt = base_prompt.replace("{question}", question)
    
    cypher_query = None
    
    # محاولة الاتصال بـ Gemini (بحد أقصى 3 محاولات)
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=prompt
            )
            cypher_query = response.text.strip()
            break # لو نجح، نخرج من اللوب
            
        except Exception as e:
            error_msg = str(e)
            if "503" in error_msg or "UNAVAILABLE" in error_msg or "429" in error_msg:
                print(f"⏳ السيرفر مشغول (محاولة {attempt+1}/3). جاري إعادة المحاولة بعد 5 ثواني...")
                time.sleep(5)
            else:
                print(f"❌ فشل في الاتصال بـ Gemini: {e}")
                return

    if not cypher_query:
        print("❌ فشلت كل المحاولات بسبب ضغط السيرفر. جرب تاني بعد شوية.")
        return

    # تنظيف الرد من أي علامات مارك داون
    if cypher_query.startswith("```"):
        cypher_query = cypher_query.split("\n", 1)[1]
    if cypher_query.endswith("```"):
        cypher_query = cypher_query.rsplit("\n", 1)[0]
    cypher_query = cypher_query.strip()

    print(f"\n📝 الاستعلام المترجم:\n{cypher_query}\n")
    
    print("🔍 جاري البحث في الجراف...")
    driver = get_driver()
    try:
        with driver.session() as session:
            result = session.run(cypher_query)
            records = list(result)
            
            if not records:
                print("📭 مفيش نتايج مطابقة للسؤال ده.")
                return
            
            print(f"\n✅ تم العثور على {len(records)} نتيجة:\n")
            for i, record in enumerate(records, 1):
                print(f"--- النتيجة {i} ---")
                for key, value in record.data().items():
                    print(f"{key}: {value}")
                print()
                
    except Exception as e:
        print(f"❌ خطأ في تنفيذ الاستعلام في Neo4j: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_question = " ".join(sys.argv[1:])
    else:
        user_question = input("💬 اكتب سؤالك القانوني: ")
    
    ask_graph(user_question)
