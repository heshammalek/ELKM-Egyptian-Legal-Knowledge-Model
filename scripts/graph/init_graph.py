from neo4j import GraphDatabase

URI = "neo4j://127.0.0.1:7687"
AUTH = ("neo4j", "newpass@elkm")
DB = "egylaw"

def init_graph():
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        with driver.session(database=DB) as session:
            constraints = [
                # Document (أو Legislation) - معرف فريد
                "CREATE CONSTRAINT doc_id IF NOT EXISTS FOR (n:Document) REQUIRE n.doc_id IS UNIQUE",
                # Article - معرف فريد مركب (مستند + رقم المادة)
                "CREATE CONSTRAINT article_id IF NOT EXISTS FOR (n:Article) REQUIRE (n.doc_id, n.article_number) IS UNIQUE",
                # Entity - معرف فريد
                "CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (n:Entity) REQUIRE n.entity_id IS UNIQUE",
                # Position - معرف فريد
                "CREATE CONSTRAINT position_id IF NOT EXISTS FOR (n:Position) REQUIRE n.position_id IS UNIQUE",
                # Relation - لضمان عدم تكرار العلاقات
                "CREATE CONSTRAINT rel_instance_id IF NOT EXISTS FOR ()-[r:RELATION]-() REQUIRE r.instance_id IS UNIQUE"
            ]
            
            for c in constraints:
                try:
                    session.run(c)
                    print(f"✅ Constraint created/verified.")
                except Exception as e:
                    print(f"⚠️  Constraint skipped: {e}")
            
            print("✅ Graph initialized successfully for ELKM Schema.")

if __name__ == "__main__":
    init_graph()
