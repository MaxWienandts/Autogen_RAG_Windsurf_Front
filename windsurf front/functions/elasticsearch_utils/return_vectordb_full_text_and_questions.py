# return_vectordb_full_text_and_questions
from langchain_openai import AzureOpenAIEmbeddings
from langchain_elasticsearch import ElasticsearchStore
from elasticsearch import Elasticsearch

def return_vectordb_full_text_and_questions(
    embedding_key,
    deployment_name_embedding,
    azure_endpoint_embedding,
    elasticsearch_endpoint,
    elasticsearch_user,
    elasticsearch_password,
):
    '''
    collection_full_text: Connection to the full-text index.
    collection_questions_text: Connection to the question-based index.
    es: Direct Elasticsearch client instance.
    '''
    

    # Embedding for LangChain
    embedding_function_to_langchain = AzureOpenAIEmbeddings(
        model = 'text-embedding-3-small',
        api_key = embedding_key,
        deployment = deployment_name_embedding,
        azure_endpoint = azure_endpoint_embedding
    ) 

    dict_return = {}
    # Conect to elastic search
    dict_return['collection_full_text'] = ElasticsearchStore(
        es_url = elasticsearch_endpoint,
        index_name = "collection_full_text",
        embedding = embedding_function_to_langchain,
        es_user = elasticsearch_user,
        es_password = elasticsearch_password,
    )
    
    dict_return['collection_questions_text'] = ElasticsearchStore(
        es_url = elasticsearch_endpoint,
        index_name = "collection_questions_text",
        embedding = embedding_function_to_langchain,
        es_user = elasticsearch_user,
        es_password = elasticsearch_password,
    )

    dict_return['es'] = Elasticsearch(
        elasticsearch_endpoint,
        basic_auth=(elasticsearch_user, elasticsearch_password)
    )
    
    return dict_return