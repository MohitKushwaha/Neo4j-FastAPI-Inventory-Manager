from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import random
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
from module import create_embeddings, vector_search
from module import rag

app = FastAPI(
    title="Neo4j FastAPI Integration",
    description="Backend service providing Neo4j APIs using FastAPI",
    version="1.0.0",
)

# Enable CORS for cross-origin requests (e.g. from a frontend dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Credentials (store in .env file or environment variables for security)
NEO4J_URI = '<neo4j_uri>'
NEO4J_USERNAME = '<neo4j_username>'
NEO4J_PASSWORD = '<neo4j_password>'
NEO4J_DATABASE="<neo4j_database>"
OPENAI_TOKEN = '<openai_token>'

# Connect to Neo4j database
driver = GraphDatabase.driver(
    NEO4J_URI, 
    auth=(
        NEO4J_USERNAME, 
        NEO4J_PASSWORD
    )
)

# APIs

# Root API
@app.get("/")
def welcome():
    return {"message": "Welcome to Neo4j implementation in FastAPI!"}

# Get All Customers
@app.get("/customer/all")
def get_all_customers():
    try:
        records, summary, keys = driver.execute_query("""
            MATCH (c:Customer)-[:PLACED]->(:Order)
            RETURN c.name AS name
            """,
            database_=NEO4J_DATABASE,
        )

        # Summary information
        print("The query `{query}` returned {records_count} records in {time} ms.".format(
            query=summary.query, records_count=len(records),
            time=summary.result_available_after
        ))
        return records
    except:
        return {'error': 'Something went wrong'}

# Get Customer
@app.get("/customer/")
def get_customer(name: str = 'George'):
    try:
        records, summary, keys = driver.execute_query("""
            MATCH (c:Customer {name: $name})-[:PLACED]->(:Order)
            RETURN c
            """, name=name,
            database_=NEO4J_DATABASE,
        )

        # Summary information
        print("The query `{query}` returned {records_count} records in {time} ms.".format(
            query=summary.query, records_count=len(records),
            time=summary.result_available_after
        ))
        return records
    except:
        return {'error': 'Something went wrong'}

# Update Customer
@app.put("/customer")
def update_customer(name: str = 'George', email: str = 'George_Anderson62@yahoo.com'):
    try:
        records, summary, keys = driver.execute_query("""
            MATCH (c:Customer {name: $name})
            SET c.email = $email
            """, name=name, email=email,
            database_=NEO4J_DATABASE,
        )
        print(f"Query counters: {summary.counters}.")
        return {'status': 'success'}
    except:
        return {'error': 'Something went wrong'}

# Create Customer
@app.post("/customer")
def post_customer(name: str, email: str):
    try:
        joined_date = datetime.now()
        customer_id = f"customer{random.randrange(100,1000)}"
        records, summary, keys = driver.execute_query("""
            CREATE (c:Customer {name: $name, email: $email, joinedDate: $joined_date, customerId: $customer_id})
            """, name=name, email=email, joined_date=joined_date,customer_id=customer_id,
            database_=NEO4J_DATABASE,
        )

        print("Created {nodes_created} nodes in {time} ms.".format(
            nodes_created=summary.counters.nodes_created,
            time=summary.result_available_after
        ))

        return {'nodes': summary.counters.nodes_created}
    except:
        return {'error': 'Something went wrong'}

# Delete Customer
@app.delete("/customer")
def delete_customer(name: str):
    try:
        records, summary, keys = driver.execute_query("""
        MATCH (c:Customer {name: $name})
        DETACH DELETE c
        """, name=name,
        database_=NEO4J_DATABASE)

        print("Deleted {nodes_deleted} nodes in {time} ms.".format(
            nodes_deleted=summary.counters.nodes_deleted,
            time=summary.result_available_after
        ))

        return {'nodes': summary.counters.nodes_created}
    except:
        return {'error': 'Something went wrong'}


# Create Embeddings API
@app.post("/create_embeddings")
def create_embedding():
    try:
        return create_embeddings.create_embeddings(driver, NEO4J_DATABASE, SentenceTransformer)
    except:
        return {'error': 'Something went wrong'}

@app.post("/create_embeddings_openai")
def create_embedding_OPENAI():
    try:
        return create_embeddings.create_embeddings_OPENAI(driver, NEO4J_DATABASE, OPENAI_TOKEN)
    except:
        return {'error': 'Something went wrong'}


# Create Vector Index API
@app.post("/create_vector_index")
def create_vector_index():
    try:
        records, summary, keys = driver.execute_query('''
        CREATE VECTOR INDEX customerNames
        FOR (c:Customer)
        ON c.embedding
        OPTIONS {indexConfig: {
            `vector.dimensions`: 384,
            `vector.similarity_function`: 'cosine'
        }}
        ''', database_=NEO4J_DATABASE)
        print(f"Query counters: {summary.counters}.")
        return {'status': 'success', 'message': 'Vector index created.'}
    except:
        return {'error': 'Something went wrong'}

@app.post("/create_vector_index_openai")
def create_vector_index_openai():
    try:
        records, summary, keys = driver.execute_query('''
        CREATE VECTOR INDEX customerNames
        FOR (c:Customer)
        ON c.embedding
        OPTIONS {indexConfig: {
            `vector.dimensions`: 1536,
            `vector.similarity_function`: 'cosine'
        }}
        ''', database_=NEO4J_DATABASE)
        print(f"Query counters: {summary.counters}.")
        return {'status': 'success', 'message': 'Vector index created.'}
    except:
        return {'error': 'Something went wrong'}


# Vector Search API
@app.get("/vector_search")
def get_vector_search(query: str = 'customers with names similar to WWE wrestlers'):
    try:
        return vector_search.vector_search(query, driver, NEO4J_DATABASE, SentenceTransformer)
    except:
        return {'error': 'Something went wrong'}


# RAG Query API
@app.get("/rag_query")
def rag_query(query:str = "Find customers with names similar to WWE wrestlers"):
    try:
        return rag.rag_query(query=query)
    except:
        return {'error': 'Something went wrong'}


# Graceful Shutdown Event
@app.on_event("shutdown")
async def shutdown_event():
    driver.close()
    print('Neo4j Driver Closed')

# Verify Neo4j Connection
def verify_neo4j_connection():
    global driver
    try:
        driver.verify_connectivity()
        return "Neo4j verify connection successful."
    except:
        driver.close()
        return "Neo4j verify connection failed. Check the NEO4J_URI, NEO4J_USERNAME, and NEO4J_PASSWORD values in .env file."

# Main function
if __name__ == "__main__":
    # Verify Neo4j Connection
    conn_status = verify_neo4j_connection()
    print("Status: ", conn_status)

    # Run local server
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
