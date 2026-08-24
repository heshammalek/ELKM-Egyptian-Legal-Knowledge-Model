from neo4j import GraphDatabase

URI = "neo4j://127.0.0.1:7687"
AUTH = ("neo4j", "newpass@elkm")
DB = "egylaw"

def init_graph():
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        with driver.session(database=DB) as session:
            # Constraints - تضمن uniqueness
            constraints = [
                "CREATE CONSTRAINT legislation_id IF NOT EXISTS FOR (n:Legislation) REQUIRE n.id IS UNIQUE",
                "CREATE CONSTRAINT article_id IF NOT EXISTS FOR (n:Article) REQUIRE n.id IS UNIQUE",
                "CREATE CONSTRAINT definition_id IF NOT EXISTS FOR (n:Definition) REQUIRE n.id IS UNIQUE",
                "CREATE CONSTRAINT constitutional_ruling_id IF NOT EXISTS FOR (n:Constitutional_Ruling) REQUIRE n.id IS UNIQUE",
                "CREATE CONSTRAINT cassation_principle_id IF NOT EXISTS FOR (n:Cassation_Principle) REQUIRE n.id IS UNIQUE",
                "CREATE CONSTRAINT admin_ruling_id IF NOT EXISTS FOR (n:Admin_Ruling) REQUIRE n.id IS UNIQUE",
                "CREATE CONSTRAINT fatwa_id IF NOT EXISTS FOR (n:Fatwa) REQUIRE n.id IS UNIQUE",
                "CREATE CONSTRAINT ascertained_meaning_id IF NOT EXISTS FOR (n:Ascertained_Meaning) REQUIRE n.id IS UNIQUE",
            ]
            
            for c in constraints:
                try:
                    session.run(c)
                    print(f"✅ {c.split('FOR')[0].strip().split(' ')[-1]} constraint created.")
                except Exception as e:
                    print(f"⚠️  Constraint skipped: {e}")
            
            print("✅ Graph initialized.")

if __name__ == "__main__":
    init_graph()