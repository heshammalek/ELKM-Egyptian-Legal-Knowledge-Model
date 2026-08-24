from neo4j import GraphDatabase

URI = "neo4j://127.0.0.1:7687"
AUTH = ("neo4j", "newpass@elkm")

try:
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.verify_connectivity()
        print("✅ Neo4j connected successfully.")
except Exception as e:
    print(f"❌ Connection failed: {e}")