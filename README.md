# Neo4j FastAPI Inventory Manager

A high-performance, asynchronous **Inventory Management System** built with **FastAPI** and **Neo4j graph database**. This project simulates neo4j python package apis through integration with FastAPI. Leverage simple graph queries, create vector embeddings and vector indices, and perform vector search on customer - product - order relationships.

## 🚀 Key Features

* **Graph-Based Inventory Tracking:** Naturally models relationships between Customers, Products, Orders, and Categories.
* **Asynchronous Architecture:** Built on FastAPI and the official Neo4j Python Async Driver for optimal performance.
* **Vector Embeddings and Vector Indices:** Create multi-dimension embedding and vector indices.
* **Prompt based Search:** Perform search on vector index with prompts (ex: 'customers with names of WWE wrestlers').
* **API Documentation:** Interactive documentation out-of-the-box via Swagger UI and ReDoc.

---

## 🛠️ Tech Stack

* **Framework:** FastAPI (Python 3.10+)
* **Database:** Neo4j (Graph Database)
* **Query Language:** Cypher
* **ODM / Driver:** Neo4j Python Driver (Async)
* **AI Models:** OpenAI and Sentence-Transformers

---

## 🏗️ Graph Data Model

The application utilizes the following node labels and relationships matching the target schema:
```
(:Customer) ----------[:PLACED]-----------> (:Order)
|                                         |
|                                         |
[:REVIEWED]                               [:CONTAINS]
|                                         |
v                                         v
(:Product) ----------[:BELONGS_TO]---------> (:Category)
```

* **Nodes:** `Customer`, `Order`, `Product`, `Category`
* **Relationships:** 
  * `(Customer)-[:PLACED]->(Order)`
  * `(Customer)-[:REVIEWED]->(Product)`
  * `(Order)-[:CONTAINS]->(Product)`
  * `(Product)-[:BELONGS_TO]->(Category)`

---

## 🧠 Vector Index Configuration

Customers are vectorized using name properties. Text embeddings are stored directly on the (:Customer) nodes alongside a custom Neo4j Vector Index to handle similarity search via Cosine distance algorithms.

---

## ⚙️ Setup & Installation

### Prerequisites
* Python 3.10 or higher
* Neo4j Database (Local instance or Neo4j AuraDB)

### 1. Clone the Repository
```bash
git clone https://github.com/MohitKushwaha/Neo4j-FastAPI-Inventory-Manager.git
cd neo4j-fastapi-inventory-manager
```

### 2. Environment Configuration
Create a `.env` file in the root directory:
```env
NEO4J_URI=<neo4j-uri>
NEO4J_USERNAME=<neo4j-username>
NEO4J_PASSWORD=<neo4j-password>
NEO4J_DATABASE=<neo4j-database>
APP_PORT=8000
```

### 3. Local Development Manual Setup
Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Run the application:
```bash
uvicorn app.main:app --reload
```

---

## 🛣️ API Endpoints

Once running, navigate to `http://localhost:8000/docs` to view the interactive Swagger UI context.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/` | welcome |
| **GET** | `/customer/` | get_customer |
| **GET** | `/customer/all` | get_all_customers |
| **GET** | `/vector_search` | get_vector_search |
| **POST** | `/create_embeddings` | create_embeddings |
| **POST** | `/create_embeddings_openai` | create_embeddings_openai |
| **POST** | `/create_vector_index` | create_vector_index |
| **POST** | `/create_vector_index_openai` | create_vector_index_openai |
| **POST** | `/customer` | post_customer |
| **PUT** | `/customer` | update_customer |
| **DELETE** | `/customer` | delete_customer |

---

## 🧪 Running Tests

Execute the test suite using `pytest`:
```bash
pytest
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
