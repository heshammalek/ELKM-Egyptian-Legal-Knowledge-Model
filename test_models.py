# test_models.py - ضعه في جذر المشروع وشغّله
#لمعرفة موديلات جيمناي المتاحة

from google import genai

def load_env():
    env = {}
    with open(".env", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                env[key.strip()] = value.strip().strip('"').strip("'")
    return env

ENV = load_env()
client = genai.Client(api_key=ENV["GEMINI_API_KEY"])

print("الموديلات المتاحة:")
for m in client.models.list():
    if "generateContent" in (m.supported_actions or []):
        print(f"  {m.name}")