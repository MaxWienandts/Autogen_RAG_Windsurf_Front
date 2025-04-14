# similarity_search_full_and_question

def merge_scores(scores_collection_full_text, scores_collection_questions_text):
    """
    Merges two dictionaries containing similarity search results and retains the top 10 highest-scoring entries.

    This function takes two dictionaries, each containing search results from different collections:
    - `scores_collection_full_text`: Dictionary with similarity scores from a full-text document search.
    - `scores_collection_questions_text`: Dictionary with similarity scores from a question-based search.

    Each dictionary has numerical keys (e.g., 1, 2, 3, ...) mapping to a dictionary with:
    - "score": A numerical similarity score.
    - "page_content": The associated text content.
    - "metadata": The associated metadata.

    The function combines these two dictionaries, sorts all entries in descending order based on the "score", 
    and keeps only the top 10 highest-scoring entries. Additionally, it adds an "original_dictionary_name" 
    field to each entry, indicating whether it came from "collection_full_text" or "collection_questions_text".
    If an entry in `scores_collection_full_text` has the same metadata as an entry in `scores_collection_questions_text`,
    only the entry with the highest score is retained.

    Args:
        scores_collection_full_text (dict): A dictionary containing similarity scores and content from a full-text search.
        scores_collection_questions_text (dict): A dictionary containing similarity scores and content from a question-based search.

    Returns:
        dict: A new dictionary containing the top 10 highest-scoring results, with keys ranging from 1 to 10.
              Each entry includes "score", "page_content", and "original_dictionary_name".
    """
    
    merged_dict = {}

    # Function to process and insert entries while ensuring unique metadata
    def process_entries(source_dict, original_dict_name):
        for entry in source_dict.values():
            metadata_key = frozenset(entry["metadata"].items())  # Convert metadata dict to an immutable set for comparison
            if metadata_key in merged_dict:
                # Keep the entry with the highest score
                if entry["score"] > merged_dict[metadata_key]["score"]:
                    merged_dict[metadata_key] = {
                        "score": entry["score"],
                        "page_content": entry["page_content"],
                        "metadata": entry["metadata"],
                        "original_dictionary_name": original_dict_name
                    }
            else:
                merged_dict[metadata_key] = {
                    "score": entry["score"],
                    "page_content": entry["page_content"],
                    "metadata": entry["metadata"],
                    "original_dictionary_name": original_dict_name
                }

    # Process both dictionaries
    process_entries(scores_collection_full_text, "collection_full_text")
    process_entries(scores_collection_questions_text, "collection_questions_text")

    # Convert merged_dict to a sorted list based on score (descending)
    sorted_entries = sorted(merged_dict.values(), key=lambda x: x["score"], reverse=True)

    # Keep only the top 10 results
    top_10 = sorted_entries[:10]

    # Create final dictionary with keys from 1 to len(top_10)
    final_dict = {i: top_10[i - 1] for i in range(1, len(top_10) + 1)}
    
    return final_dict
    
def similarity_search_full_and_question(
    dict_vectordb,
    user_question,
    document_name_to_find,
):
    filter_query = {
        "term": {"metadata.document_name.keyword": document_name_to_find}
    }

    # collection_full_text
    # Perform similarity search with filter
    similarity_search_with_score_collection_full_text = dict_vectordb['collection_full_text'].similarity_search_with_score(user_question, k=10, filter=filter_query)

    # Get scores
    scores_collection_full_text = {}
    for i, (doc, score) in enumerate(similarity_search_with_score_collection_full_text):
        scores_collection_full_text[i + 1] = {}
        scores_collection_full_text[i + 1]['score'] = score
        scores_collection_full_text[i + 1]['page_content'] = doc.page_content
        scores_collection_full_text[i + 1]['metadata'] = doc.metadata

    # collection_questions_text
    # Perform similarity search with filter
    similarity_search_with_score_collection_questions_text = dict_vectordb['collection_questions_text'].similarity_search_with_score(user_question, k=10, filter=filter_query)

    # Get scores
    scores_collection_questions_text = {}
    for i, (doc, score) in enumerate(similarity_search_with_score_collection_questions_text):
        scores_collection_questions_text[i + 1] = {}
        scores_collection_questions_text[i + 1]['score'] = score
        scores_collection_questions_text[i + 1]['page_content'] = doc.page_content
        scores_collection_questions_text[i + 1]['metadata'] = doc.metadata

    # Merges dictionaries containing similarity search results and retains the top 10 highest-scoring entries. 
    dict_scores = merge_scores(scores_collection_full_text, scores_collection_questions_text)

    dict_return = {}
    dict_return['scores_collection_full_text'] = scores_collection_full_text
    dict_return['scores_collection_questions_text'] = scores_collection_questions_text
    dict_return['dict_scores'] = dict_scores
    
    return dict_return


   
