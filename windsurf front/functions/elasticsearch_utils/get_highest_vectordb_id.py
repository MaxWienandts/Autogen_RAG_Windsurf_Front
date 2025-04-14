# get_highest_vectordb_id

# get_highest_vectordb_id
# Get the highest id in vector db so we can add new entries.
def get_highest_vectordb_id(es_fc, index_name):
    # Check if the index exists
    if not es_fc.indices.exists(index=index_name):
        print(f"Index '{index_name}' does not exist.")
        return 0
        
    query = {
        "size": 0,  # We don't need to return any actual documents, just the aggregation
        "aggs": {
            "max_vector_db_id": {
                "max": {
                    "field": "metadata.vector_db_id"    
                }
            }
        }
    }
    
    # Perform the search with the aggregation
    response = es_fc.search(index = index_name, body = query)
    
    # Extract the maximum value from the aggregation response
    max_vector_db_id = response['aggregations']['max_vector_db_id']['value']
    if max_vector_db_id == None:
        return 0
    return max_vector_db_id