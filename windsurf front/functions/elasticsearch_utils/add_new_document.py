# add_new_document

from uuid import uuid4
from langchain_core.documents import Document

def add_new_document(
    highest_id_collection_full_text,
    document_name,
    first_page,
    last_page,
    added_by,
    llm_chain,
    dict_vectordb,
):
    # Add documents in vector db
    vector_db_id = highest_id_collection_full_text + 1
    
    # Prepare bulk data
    bulk_full_text = []
    bulk_questions_text = []
    
    print('Adding documents to Elasticsearch:')
    

    # Add full text chunk
    bulk_full_text.append(Document
        (
            page_content = text_who_am_I,
            metadata = {
                "document_name": document_name,  
                "vector_db_id": vector_db_id, 
                'first_page': first_page, # This is a custom added text, so there isn't a first and last page.
                'last_page': last_page,
                'added_by': added_by,
            },
        )
    )
    # Make questions
    context = text_who_am_I
    result = llm_chain.invoke({"context": context, "question": question})
    # Add questions in the collection
    bulk_questions_text.append(Document
        (
            page_content = result.content,
            metadata = {
                "document_name": document_name,
                "vector_db_id": vector_db_id,
                'first_page': first_page,
                'last_page': last_page,
                'added_by': added_by,
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