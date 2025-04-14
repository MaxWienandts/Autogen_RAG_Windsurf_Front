# search_document_by_document_name

def search_document_by_document_name(
    dict_vectordb_fc, 
    index_name, 
    document_name_to_find
):
    """
    Search Elasticsearch index for a document with a matching content query and return its metadata.
    
    :param index_name: Elasticsearch index name
    :param query: Query to search in the document content
    :param size: Number of documents to retrieve
    :return: Document id, including the metadata
    """
    search_result = dict_vectordb_fc['es'].search(
        index = index_name,
        body = {
            "query": {
                "term": {
                    "metadata.document_name.keyword": document_name_to_find  # Search in the 'text' field
                }
            },
            "size": 10000  # Move 'size' inside the 'body'
        }
    )
    
    if search_result["hits"]["total"]["value"] > 0:  # represents the total number of documents that match the query.
        document_ids = [hit['_id'] for hit in search_result['hits']['hits']]
        return document_ids
    else:
        return None