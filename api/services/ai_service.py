import re
from core.llm_engine import LLMEngine
from api.services.graph_service import get_related_documents, execute_cypher_query

llm = LLMEngine()

def extract_keywords(question: str):
    """دالة بسيطة لاستخراج الكلمات المفتاحية من السؤال"""
    # بنشيل علامات الترقيم والكلمات الشائعة اللي مش ليها لازمة
    stop_words = ["إيه", "هي", "القوانين", "اللي", "عدلت", "قانون", "ما", "هو", "عن", "في", "من", "إلى", "الـ"]
    words = re.findall(r'\w+', question)
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    return " ".join(keywords)

def analyze_question(question: str):
    # 1. محاولة استخدام AI لتوليد Cypher
    cypher = llm.generate_cypher(question)
    data = []
    source = "rule_based"
    
    if cypher:
        try:
            data = execute_cypher_query(cypher)
            source = "ai"
        except Exception as e:
            print(f"⚠️ فشل تنفيذ Cypher: {e}")

    # 2. لو مفيش بيانات أو الـ AI فشل، نستخدم البحث التقليدي
    if not data:
        print("⚠️ استخدام البحث التقليدي.")
        # استخراج الكلمات المفتاحية
        keywords = extract_keywords(question)
        print(f"🔍 البحث عن الكلمات المفتاحية: {keywords}")
        data = get_related_documents(keywords)
        source = "rule_based"

    if not data:
        return {"source": source, "data": [], "answer": "مفيش نتايج مطابقة.", "cypher": cypher}

    # 3. تنسيق الإجابة
    print("✍️ جاري تنسيق الإجابة...")
    formatted_answer = llm.format_response(question, data)

    return {
        "source": source, 
        "data": data, 
        "answer": formatted_answer, 
        "cypher": cypher
    }
