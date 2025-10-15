from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

# Connection details
URI = "bolt://0.0.0.0:7687"  # Change if running remotely
USER = "neo4j"
PASSWORD = "test_pass"

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

def create_database(db_name):
    """Create a new database in Neo4j (requires admin privileges)"""
    try:
        with driver.session(database="system") as session:
            session.run(f"CREATE DATABASE {db_name}")
            print(f"Database '{db_name}' created successfully.")
    except ServiceUnavailable as e:
        print(f"Error creating database: {e}")

def add_sample_nodes(db_name):
    """Add sample Person nodes to the given database"""
    with driver.session(database=db_name) as session:
        session.run("""
            CREATE (p1:Person {name: 'Alice', age: 30}),
                   (p2:Person {name: 'Bob', age: 25}),
                   (p3:Person {name: 'Charlie', age: 35})
        """)
        print("Sample nodes added successfully.")

def verify_nodes(db_name):
    """Query the Person nodes and print them"""
    with driver.session(database=db_name) as session:
        result = session.run("MATCH (p:Person) RETURN p.name AS name, p.age AS age")
        for record in result:
            print(f"{record['name']} ({record['age']} years old)")

if __name__ == "__main__":
    DB_NAME = "dummydb"

    # 1. Create database
    create_database(DB_NAME)

    # 2. Add sample nodes
    add_sample_nodes(DB_NAME)

    # 3. Verify nodes
    print("\nVerifying data in 'dummy-db':")
    verify_nodes(DB_NAME)

    # Close driver
    driver.close()