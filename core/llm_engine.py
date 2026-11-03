import os
import time
from dotenv import load_dotenv
from google import genai
from openai import OpenAI

load_dotenv()

class LLMEngine:
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_client = genai.Client(api_key=self.gemini_api_key) if self.gemini_api_key else None
        
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.deepseek_client = OpenAI(
            api_key=self.deepseek_api_key,
            base_url="https://api.deepseek.com"
        ) if self.deepseek_api_key else None

    def generate_cypher(self, question: str):
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
        
        # 1. محاولة Gemini (مع Retry)
        if self.gemini_client:
            for attempt in range(3):
                try:
                    response = self.gemini_client.models.generate_content(
                        model='gemini-3.8-flash', 
                        contents=prompt
                    )
                    return self._clean_cypher(response.text)
                except Exception as e:
                    if "503" in str(e) or "UNAVAILABLE" in str(e):
                        print(f"⏳ Gemini مشغول (محاولة {attempt+1}/3). استنى 5 ثواني...")
                        time.sleep(5)
                    else:
                        print(f"⚠️ Gemini فشل: {e}")
                        break # لو مش 503، متضيعش وقت
        
        # 2. محاولة DeepSeek (لو موجود)
        if self.deepseek_client:
            try:
                print("🔄 جاري تجربة DeepSeek...")
                response = self.deepseek_client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": prompt}],
                    stream=False
                )
                return self._clean_cypher(response.choices[0].message.content)
            except Exception as e:
                print(f"❌ DeepSeek فشل: {e}")

        return None

    def _clean_cypher(self, text: str):
        if not text:
            return None
        cypher = text.strip()
        if cypher.startswith("```"):
            cypher = cypher.split("\n", 1)[1]
        if cypher.endswith("```"):
            cypher = cypher.rsplit("\n", 1)[0]
        return cypher.strip()
