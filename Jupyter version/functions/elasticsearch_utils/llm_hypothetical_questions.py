# llm_hypothetical_questions

from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings
from langchain.prompts import PromptTemplate

def llm_hypothetical_questions(
    deployment_name_llm,
    model_name_llm,
    api_version,
    azure_endpoint_llm,
    azure_openai_api_key,
    model_name_embedding,
    embedding_key,
    deployment_name_embedding,
    azure_endpoint_embedding,
):    
    # Model used
    llm = AzureChatOpenAI(
        deployment_name = deployment_name_llm,
        model_name = model_name_llm,
        api_version = api_version,
        azure_endpoint = azure_endpoint_llm,
        api_key = azure_openai_api_key,
    )
    # Embedding for LangChain
    # Embedding for LangChain
    embedding_function_to_langchain = AzureOpenAIEmbeddings(
        model = model_name_embedding,
        api_key = embedding_key,
        deployment = deployment_name_embedding,
        azure_endpoint = azure_endpoint_embedding
    ) 
    # Define template for answers
    # Build prompt
    template = """Use the following pieces of context to complete the task at the end.
    {context}
    If you can't make a answer with context, just say that you don't know, don't try to make up an answer.
    Do not hallucinate.
    Task: {question}"""
    
    prompt = PromptTemplate.from_template(template)
    llm_chain = prompt | llm
    
    question = """Make as many relevant technical specific and/or generic questions that the above text can answer.
    If you can't make a technical question with the context, just don't write anything, don't try to make up an questions just to fill the quota."""

    dict_return = {}
    dict_return['llm_chain'] = llm_chain
    dict_return['question'] = question 

    return dict_return