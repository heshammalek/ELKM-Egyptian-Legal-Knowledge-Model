from core.llm_engine import LLMEngine
from api.services.graph_service import get_related_documents, execute_cypher_query

llm = LLMEngine()

def analyze_question(question: str):
    """
    بيحلل السؤال، ويحاول يستخدم AI عشان يجيب Cypher.
    لو فشل، بيرجع للبحث التقليدي.
    """
    # 1. محاولة استخدام AI
    cypher = llm.generate_cypher(question)
    
    if cypher:
        try:
            # تنفيذ الـ Cypher اللي الـ AI طلعه
            results = execute_cypher_query(cypher)
            if results:
                return {"source": "ai", "data": results, "cypher": cypher}
        except Exception as e:
            print(f"⚠️ فشل تنفيذ Cypher من الـ AI: {e}. جاري استخدام البحث التقليدي.")

    # 2. البحث التقليدي (Rule-based) كبديل
    print("⚠️ استخدام البحث التقليدي.")
    return {"source": "rule_based", "data": get_related_documents(question), "cypher": None}
