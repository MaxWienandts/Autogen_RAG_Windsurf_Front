import os
from dotenv import load_dotenv
import json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory


from functions.elasticsearch_utils.return_vectordb_full_text_and_questions import return_vectordb_full_text_and_questions


from autogen_core import AgentId, MessageContext, RoutedAgent, SingleThreadedAgentRuntime, message_handler
from functions.autogen_utils.RouterAgent import RouterAgent
from functions.autogen_utils.DeepSeekAgent import DeepSeekAgent
from functions.autogen_utils.TimeSeriesAgent import TimeSeriesAgent
from functions.autogen_utils.OuterAgent import OuterAgent
from functions.autogen_utils.Message import Message

from set_system_template_RouterAgent import set_system_template_RouterAgent
from set_system_template_OuterAgent import set_system_template_OuterAgent

###########################################################
# 2) Create the FastAPI app
###########################################################
app = FastAPI()


@app.on_event("startup")
async def startup_event():
    """
    This will run one time when the server starts.
    We initialize the SingleThreadedAgentRuntime, register your agents,
    and store it in app.state so it is accessible in endpoints.
    """

    ###########################################################
    # 1) Load environment variables and define your settings
    ###########################################################
    load_dotenv()

    # Check if variables are correctly loaded from .env
    AZURE_OPENAI_API_KEY_2 = os.getenv('AZURE_OPENAI_API_KEY')
    if not AZURE_OPENAI_API_KEY_2:
        raise ValueError("AZURE_OPENAI_API_KEY not found in environment variables")
    
    DEPLOYMENT_NAME_LLM = os.getenv('DEPLOYMENT_NAME_LLM')
    if not DEPLOYMENT_NAME_LLM:
        raise ValueError("DEPLOYMENT_NAME_LLM not found in environment variables")
    
    API_VERSION = os.getenv('API_VERSION')
    if not API_VERSION:
        raise ValueError("API_VERSION not found in environment variables")
        
    AZURE_ENDPOINT_LLM = os.getenv('AZURE_ENDPOINT_LLM')
    if not AZURE_ENDPOINT_LLM:
        raise ValueError("AZURE_ENDPOINT_LLM not found in environment variables")
    
    EMBEDDING_KEY = os.getenv('EMBEDDING_KEY')
    if not EMBEDDING_KEY:
        raise ValueError("EMBEDDING_KEY not found in environment variables")
    
    DEPLOYMENT_NAME_EMBEDDING = os.getenv('DEPLOYMENT_NAME_EMBEDDING')
    if not DEPLOYMENT_NAME_EMBEDDING:
        raise ValueError("DEPLOYMENT_NAME_EMBEDDING not found in environment variables")
        
    AZURE_ENDPOINT_EMBEDDING = os.getenv('AZURE_ENDPOINT_EMBEDDING')
    if not AZURE_ENDPOINT_EMBEDDING:
        raise ValueError("AZURE_ENDPOINT_EMBEDDING not found in environment variables")
    
    API_BASE_EMBEDDING = os.getenv('API_BASE_EMBEDDING')
    if not API_BASE_EMBEDDING:
        raise ValueError("API_BASE_EMBEDDING not found in environment variables")
    
    ELASTICSEARCH_USER = os.getenv('ELASTICSEARCH_USER')
    if not ELASTICSEARCH_USER:
        raise ValueError("ELASTICSEARCH_USER not found in environment variables")
    
    ELASTICSEARCH_PASSWORD = os.getenv('ELASTICSEARCH_PASSWORD')
    if not ELASTICSEARCH_PASSWORD:
        raise ValueError("ELASTICSEARCH_PASSWORD not found in environment variables")
    
    ELASTICSEARCH_API_KEY = os.getenv('ELASTICSEARCH_API_KEY')
    if not ELASTICSEARCH_API_KEY:
        raise ValueError("ELASTICSEARCH_API_KEY not found in environment variables")
    
    ELASTICSEARCH_ENDPOINT = os.getenv('ELASTICSEARCH_ENDPOINT')
    if not ELASTICSEARCH_ENDPOINT:
        raise ValueError("ELASTICSEARCH_ENDPOINT not found in environment variables")
        
    # Connect with elastic seach and langchain
    dict_vectordb = return_vectordb_full_text_and_questions(
        embedding_key = EMBEDDING_KEY,
        deployment_name_embedding = DEPLOYMENT_NAME_EMBEDDING,
        azure_endpoint_embedding = AZURE_ENDPOINT_EMBEDDING,
        elasticsearch_endpoint = ELASTICSEARCH_ENDPOINT,
        elasticsearch_user = ELASTICSEARCH_USER,
        elasticsearch_password = ELASTICSEARCH_PASSWORD,
    )


    # Define LLM model
    llm = AzureChatOpenAI(
        temperature = 0,
        model_name = "gpt-4o-mini",
        deployment_name = DEPLOYMENT_NAME_LLM,  
        api_version = API_VERSION,
        azure_endpoint = AZURE_ENDPOINT_LLM
    )
    
    ### Statefully manage chat history ###
    store = {} # This dictionary will retain all chat history

    # Define system prompts
    system_template_RouterAgent = set_system_template_RouterAgent()
    system_template_OuterAgent = set_system_template_OuterAgent()

    # Get information about how the LLM should answer the questions
    target_audience = 'PhD student'
    answer_tone = 'Professional and Clear'
    answer_length = '4 paragraphs'

    # Get necessary information about the collection in the vector db
    index_name_collection_full_text = 'collection_full_text'
    index_name_collection_questions_text = 'collection_questions_text'

    # initializes a runtime environment for multiple agents, registers them, and starts the runtime.
    runtime = SingleThreadedAgentRuntime()
    await RouterAgent.register(runtime, "router_agent", lambda: RouterAgent(
        description = "RouterAgent",
        system_template = system_template_RouterAgent,
        llm = llm,
    ))
    await TimeSeriesAgent.register(runtime, "TimeSeries_agent", lambda: TimeSeriesAgent(
        description = "TimeSeriesAgent",
        dict_vectordb = dict_vectordb,
    ))
    await DeepSeekAgent.register(runtime, "DeepSeek_agent", lambda: DeepSeekAgent(
        description = "DeepSeekAgent",
        dict_vectordb = dict_vectordb,
    ))
    await OuterAgent.register(
        runtime,
        "outer_agent",
        lambda: OuterAgent(
            description = "OuterAgent",
            llm = llm,
            session_id = 'Teste_01',
            store = store,
            system_template = system_template_OuterAgent,
            router_agent_id = "router_agent",
            TimeSeries_agent_id = "TimeSeries_agent",
            DeepSeek_agent_id = "DeepSeek_agent",
            target_audience = target_audience,
            answer_tone = answer_tone,
            answer_length = answer_length,
        ),
    )
    
    # The runtime.start() command launches the runtime, enabling the agents to function and interact as intended.
    runtime.start()

    # Store the runtime in the app so we can use it in endpoints
    app.state.runtime = runtime



class UserQuery(BaseModel):
    question: str

@app.get("/")
def root():
    

    return {"message": "AI Multi-Agent FastAPI is running"}

@app.post("/ask")
async def ask_question(query: UserQuery):
    # Get the runtime from app.state
    runtime = app.state.runtime

    # Send and receive a message
    # Give an id for the agent that will communicate with the user
    outer_agent_id = AgentId("outer_agent", "default")
    
    # Send message to chat
    # Prepare the user message from the query text
    user_message = Message(content=query.question)
    response = await runtime.send_message(user_message, outer_agent_id)

    return {"response": response.content}
