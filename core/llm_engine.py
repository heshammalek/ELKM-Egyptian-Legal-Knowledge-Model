import os
import json
from dotenv import load_dotenv
from google import genai
from openai import OpenAI

load_dotenv()

class LLMEngine:
    def __init__(self):
        # إعداد Gemini
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_client = None
        if self.gemini_api_key:
            self.gemini_client = genai.Client(api_key=self.gemini_api_key)

        # إعداد DeepSeek
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.deepseek_client = None
        if self.deepseek_api_key:
            self.deepseek_client = OpenAI(
                api_key=self.deepseek_api_key,
                base_url="https://api.deepseek.com"
            )

    def generate_cypher(self, question: str, model_preference="gemini"):
        """
        بيحول السؤال لـ Cypher Query باستخدام الموديل المفضل.
        """
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
        
        # 1. محاولة Gemini
        if model_preference == "gemini" and self.gemini_client:
            try:
                response = self.gemini_client.models.generate_content(
                    model='gemini-3.8-flash', 
                    contents=prompt
                )
                return self._clean_cypher(response.text)
            except Exception as e:
                print(f"⚠️ فشل Gemini: {e}. جاري تجربة DeepSeek...")

        # 2. محاولة DeepSeek (كبديل)
        if self.deepseek_client:
            try:
                response = self.deepseek_client.chat.completions.create(
                    model="deepseek-flash",
                    messages=[{"role": "user", "content": prompt}],
                    stream=False
                )
                return self._clean_cypher(response.choices[0].message.content)
            except Exception as e:
                print(f"❌ فشل DeepSeek: {e}")

        return None

    def _clean_cypher(self, text: str):
        """تنظيف الـ Cypher من أي علامات مارك داون"""
        if not text:
            return None
        cypher = text.strip()
        if cypher.startswith("```"):
            cypher = cypher.split("\n", 1)[1]
        if cypher.endswith("```"):
            cypher = cypher.rsplit("\n", 1)[0]
        return cypher.strip()
