def vector_search(query_prompt, driver, DATABASE, SentenceTransformer):
    model = SentenceTransformer('all-MiniLM-L6-v2')

    query_embedding = model.encode(query_prompt)
    
    records, _, _ = driver.execute_query('''
        MATCH (customer:Customer)
            SEARCH customer IN (
                VECTOR INDEX customerNames
                FOR $queryEmbedding
                LIMIT 5
            ) SCORE AS similarityScore
        RETURN customer.name AS name, similarityScore
        ''', queryEmbedding=query_embedding,
        database_=DATABASE)
    print(f'Customers whose name relates to `{query_prompt}`:')
    for record in records:
        print(record)

    return {'status': 'success', 'message': 'Vector search completed.', 'related_customers': [record.data() for record in records]}