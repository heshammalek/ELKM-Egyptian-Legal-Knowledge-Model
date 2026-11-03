from core.llm_engine import LLMEngine
from api.services.graph_service import get_related_documents, execute_cypher_query

llm = LLMEngine()

def analyze_question(question: str):
    """
    بيحلل السؤال، ويحاول يستخدم AI عشان يجيب Cypher.
    لو فشل، بيرجع للبحث التقليدي.
    وبيحاول ينسق الإجابة لو الـ AI شغال.
    """
    # 1. محاولة استخدام AI لتوليد Cypher
    cypher = llm.generate_cypher(question)
    data = []
    source = "rule_based"
    
    if cypher:
        try:
            # تنفيذ الـ Cypher اللي الـ AI طلعه
            data = execute_cypher_query(cypher)
            source = "ai"
        except Exception as e:
            print(f"⚠️ فشل تنفيذ Cypher من الـ AI: {e}. جاري استخدام البحث التقليدي.")

    # 2. لو مفيش بيانات أو الـ AI فشل، نستخدم البحث التقليدي
    if not data:
        print("⚠️ استخدام البحث التقليدي.")
        data = get_related_documents(question)
        source = "rule_based"

    if not data:
        return {"source": source, "data": [], "answer": "مفيش نتايج مطابقة.", "cypher": cypher}

    # 3. محاولة تنسيق الإجابة باستخدام الـ AI
    print("✍️ جاري تنسيق الإجابة...")
    formatted_answer = llm.format_response(question, data)

    return {
        "source": source, 
        "data": data, 
        "answer": formatted_answer, 
        "cypher": cypher
    }
