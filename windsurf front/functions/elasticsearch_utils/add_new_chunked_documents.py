# add_new_chunked_documents

from uuid import uuid4
from langchain_core.documents import Document

from tqdm import tqdm

def add_new_chunked_documents(
    pdf_chunked_data,
    dict_documents,
    highest_id_collection_full_text,
    llm_chain,
    dict_vectordb,
):
    # Add documents in vector db
    vector_db_id = highest_id_collection_full_text + 1
    
    # Prepare bulk data
    bulk_full_text = []
    bulk_questions_text = []
    
    print('Adding documents to Elasticsearch:')
    
    # Add chunked document
    for key in pdf_chunked_data:
        document_name = dict_documents[key]
        for e in tqdm(pdf_chunked_data[key]):
            context = e['chunk']
            
            # Add full text chunk
            bulk_full_text.append(Document
                (
                    page_content = context,
                    metadata = {
                        "document_name": document_name,
                        "vector_db_id": vector_db_id,
                        'first_page': e['start_page'],
                        'last_page': e['end_page'],
                        'added_by': 'default',
                    },
                )
            )
            
            # Make question using LLM chain
            result = llm_chain.invoke({"context": context, "question": question})
            
            # Add question response chunk
            bulk_questions_text.append(Document
                (
                    page_content = result.content,
                    metadata = {
                        "document_name": document_name,
                        "vector_db_id": vector_db_id,
                        'first_page': e['start_page'],
                        'last_page': e['end_page'],
                        'added_by': 'default',
                    },
                )
            )
            
            vector_db_id += 1
    
    # Bulk index the data into Elasticsearch
    uuids_bulk_full_text = [str(uuid4()) for _ in range(len(bulk_full_text))]
    dict_vectordb['collection_full_text'].add_documents(documents = bulk_full_text, 
                                                             ids = uuids_bulk_full_text)
    
    uuids_bulk_questions_text = [str(uuid4()) for _ in range(len(bulk_questions_text))]
    dict_vectordb['collection_questions_text'].add_documents(documents = bulk_questions_text, 
                                                                  ids = uuids_bulk_questions_text)
    
    print("Documents added to Elasticsearch successfully.")

    return