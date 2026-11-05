from neo4j_graphrag.embeddings.sentence_transformers import SentenceTransformerEmbeddings
from neo4j_graphrag.retrievers import VectorRetriever
from langchain_ollama import ChatOllama
from neo4j_graphrag.generation import GraphRAG
from main import driver, NEO4J_DATABASE
# from neo4j_graphrag.embeddings.openai import OpenAIEmbeddings
# from neo4j_graphrag.llm import OpenAILLM

# Create Embedder
embedder = SentenceTransformerEmbeddings(model='all-MiniLM-L6-v2')
# embedder = OpenAIEmbeddings(model='text-embedding-ada-002')

# Create retriever
retriever = VectorRetriever(
    driver,
    neo4j_database=NEO4J_DATABASE,
    index_name="customerNames",
    embedder=embedder,
    return_properties=["name"],
)

# Create LLM
llm = ChatOllama(model="llama3.2:3b")
# llm = OpenAILLM(
#     model_name="gpt-5-mini",
#     model_params={
#         "resoning_effort": "low"
#     }
# )

# Create Rag
rag = GraphRAG(retriever=retriever, llm=llm)


def rag_query(query:str):
    global rag
    response = rag.search(query_text=query, retriever_config={"top_k": 5})

    return response.answer