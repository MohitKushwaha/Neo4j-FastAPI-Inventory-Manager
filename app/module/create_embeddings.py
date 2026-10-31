def create_embeddings(driver, DATABASE, SentenceTransformer):
    model = SentenceTransformer('all-MiniLM-L6-v2')  # vector size 384

    batch_size = 100
    batch_n = 1
    customers_with_embeddings = []
    with driver.session(database=DATABASE) as session:
        # Fetch `Customer` nodes
        result = session.run('MATCH (c:Customer) RETURN c.name AS name')
        for record in result:
            name = record.get('name')

            # Create embedding for title and plot
            if name is not None:
                customers_with_embeddings.append({
                    'name': name,
                    'embedding': model.encode(f'''
                        Name: {name}
                    '''),
                })

            # Import when a batch of movies has embeddings ready; flush buffer
            if len(customers_with_embeddings) == batch_size:
                import_batch(driver, customers_with_embeddings, batch_n, DATABASE)
                customers_with_embeddings = []
                batch_n += 1

        # Flush last batch
        import_batch(driver, customers_with_embeddings, batch_n, DATABASE)

    # Import complete, show counters
    records, _, _ = driver.execute_query('''
    MATCH (c:Customer WHERE c.embedding IS NOT NULL)
    RETURN count(*) AS countCustomersWithEmbeddings, size(c.embedding) AS embeddingSize
    ''', database_=DATABASE)
    print(f"""
    Embeddings generated and attached to nodes.
    Customer nodes with embeddings: {records[0].get('countCustomersWithEmbeddings')}.
    Embedding size: {records[0].get('embeddingSize')}.
    """)

    return {'status': 'success', 'message': 'Embeddings generated and attached to nodes.'}

def import_batch(driver, nodes_with_embeddings, batch_n, DATABASE):
    # Add embeddings to Customer nodes
    driver.execute_query('''
    UNWIND $customers as customer
    MATCH (c:Customer {name: customer.name})
    CALL db.create.setNodeVectorProperty(c, 'embedding', customer.embedding)
    ''', customers=nodes_with_embeddings, database_=DATABASE)
    print(f'Processed batch {batch_n}.')


# Create Embeddings with OPENAI Model
def create_embeddings_OPENAI(driver, DATABASE, OPENAI_TOKEN):
    batch_size = 100
    batch_n = 1
    customers_batch = []
    with driver.session(database=DATABASE) as session:
        # Fetch `Customer` nodes
        result = session.run("""
            MATCH (c:Customer)-[:PLACED]->(:Order)
            RETURN c.name AS name
            """
        )
        for record in result:
            name = record.get('name')

            if name is not None:
                customers_batch.append({
                    'name': name,
                    'to_encode': f'Name: {name}'
                })

            # Import a batch; flush buffer
            if len(customers_batch) == batch_size:
                import_batch_OPENAI(driver, customers_batch, batch_n, DATABASE, OPENAI_TOKEN)
                customers_batch = []
                batch_n += 1

        # Flush last batch
        import_batch_OPENAI(driver, customers_batch, batch_n, DATABASE, OPENAI_TOKEN)

    # Import complete, show counters
    records, _, _ = driver.execute_query('''
    MATCH (c:Customer WHERE c.embedding IS NOT NULL)
    RETURN count(*) AS countCustomersWithEmbeddings, size(c.embedding) AS embeddingSize
    ''', database_=DATABASE)
    print(f"""
    Embeddings generated and attached to nodes.
    Customer nodes with embeddings: {records[0].get('countCustomersWithEmbeddings')}.
    Embedding size: {records[0].get('embeddingSize')}.
    """)

    return {'status': 'success', 'message': 'Embeddings generated and attached to nodes.'}

def import_batch_OPENAI(driver, nodes, batch_n, DATABASE, OPENAI_TOKEN):
    # Generate and store embeddings for Customer nodes
    driver.execute_query('''
    CALL ai.text.embedBatch($listToEncode, 'OpenAI', {
      token: $token, model: 'text-embedding-ada-002'
    }) YIELD index, vector
    MATCH (c:Customer {name: $customers[index].name})
    CALL db.create.setNodeVectorProperty(c, 'embedding', toFloatList(vector))
    ''', customers=nodes, listToEncode=[customer['to_encode'] for customer in nodes], token=OPENAI_TOKEN,
    database_=DATABASE)
    print(f'Processed batch {batch_n}')

