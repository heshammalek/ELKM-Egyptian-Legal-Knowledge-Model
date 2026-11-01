import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# تحميل المتغيرات من .env
load_dotenv()

URI = os.getenv("NEO4J_URI", "neo4j://127.0.0.1:7687")
AUTH = (os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "newpass@elkm"))
DB = os.getenv("NEO4J_DATABASE", "egylaw")

def get_driver():
    """يرجع كائن الاتصال بالداتابيز"""
    return GraphDatabase.driver(URI, auth=AUTH)

def verify_connection():
    """يتأكد إن الداتابيز شغالة والاتصال سليم"""
    try:
        with get_driver() as driver:
            driver.verify_connectivity()
            print("✅ Neo4j connected successfully.")
            return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    # ده بيتشغل بس لو انت شغلت الملف ده مباشرة (للتجربة)
    verify_connection()
