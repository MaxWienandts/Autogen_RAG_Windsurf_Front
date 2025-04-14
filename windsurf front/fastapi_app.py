import os
import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi import status
import traceback

# LangChain components
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

# Elasticsearch vector DB utils
from functions.elasticsearch_utils.return_vectordb_full_text_and_questions import return_vectordb_full_text_and_questions

# Autogen components
from autogen_core import AgentId, MessageContext, RoutedAgent, SingleThreadedAgentRuntime, message_handler
from functions.autogen_utils.RouterAgent import RouterAgent
from functions.autogen_utils.DeepSeekAgent import DeepSeekAgent
from functions.autogen_utils.TimeSeriesAgent import TimeSeriesAgent
from functions.autogen_utils.OuterAgent import OuterAgent
from functions.autogen_utils.Message import Message

# Templates for Router and Outer agents
from functions.set_system_template_RouterAgent import set_system_template_RouterAgent
from functions.set_system_template_OuterAgent import set_system_template_OuterAgent

###########################################################
# Global state
store = {}  # This dictionary will retain all chat history

###########################################################
# Create the FastAPI app
###########################################################
app = FastAPI()
# Add CORS (Cross-Origin Resource Sharing) middleware to the FastAPI app
app.add_middleware(
    CORSMiddleware,
    
    # Allow requests from any origin (for development or public APIs)
    # You can replace "*" with specific origins like ["http://localhost:3000"]
    allow_origins=["*"],
    
    # Allow sending cookies and authorization headers in cross-origin requests
    allow_credentials=True,
    
    # Allow all HTTP methods: GET, POST, PUT, DELETE, etc.
    allow_methods=["*"],
    
    # Allow all custom headers from the frontend (like Content-Type, Authorization)
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────
# Global Exception Handler (prints errors in the console)
# ─────────────────────────────────────────────────────────────
# Register a custom exception handler for all unhandled exceptions
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    
    # Print the full traceback to the console for debugging purposes
    print("Exception occurred:", traceback.format_exc())
    
    # Return a generic 500 Internal Server Error response to the client
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,  # HTTP status code 500
        content={"detail": str(exc)},  # temporarily include the actual error message
    )

# ─────────────────────────────────────────────────────────────
# Data Models
# ─────────────────────────────────────────────────────────────
class UserQuery(BaseModel):
    question: str
    settings: Optional[dict] = None

class Settings(BaseModel):
    # Response Settings
    target_audience: str = 'PhD student'
    answer_tone: str = 'Professional and Clear'
    answer_length: str = '4 paragraphs'
    
    # Azure OpenAI Settings
    AZURE_ENDPOINT_LLM: Optional[str] = None
    DEPLOYMENT_NAME_LLM: Optional[str] = None
    API_VERSION: Optional[str] = None
    AZURE_OPENAI_API_KEY: Optional[str] = None
    
    # Azure OpenAI Embeddings Settings
    EMBEDDING_KEY: Optional[str] = None
    AZURE_ENDPOINT_EMBEDDING: Optional[str] = None
    DEPLOYMENT_NAME_EMBEDDING: Optional[str] = None
    
    # Elasticsearch Settings
    ELASTICSEARCH_ENDPOINT: Optional[str] = None
    ELASTICSEARCH_USER: Optional[str] = None
    ELASTICSEARCH_PASSWORD: Optional[str] = None
    
    # System Templates
    system_template_RouterAgent: str = '''You are a helpful virtual assistant router that will decide which virtal assistant can help anserwing the user question.
    You will answer only the number of the description that is most related to the user question.
    You should answer just a number.
    
    Descriptions:
    1. A Survey of Time Series Foundation Models: Generalizing Time Series Representation with Large Language Model
    Time series data are ubiquitous across various domains, making time series analysis critically important. Traditional time series models
    are task-specific, featuring singular functionality and limited generalization capacity. Recently, large language foundation models have
    unveiled their remarkable capabilities for cross-task transferability, zero-shot/few-shot learning, and decision-making explainability.
    This success has sparked interest in the exploration of foundation models to solve multiple time series challenges simultaneously. There
    are two main research lines, namely pre-training foundation models from scratch for time series and adapting large language
    foundation models for time series. They both contribute to the development of a unified model that is highly generalizable, versatile,
    and comprehensible for time series analysis. This survey offers a 3E analytical framework for comprehensive examination of related
    research. Specifically, we examine existing works from three dimensions, namely Effectiveness, Efficiency and Explainability. In
    each dimension, we focus on discussing how related works devise tailored solution by considering unique challenges in the realm of
    time series.Furthermore, we provide a domain taxonomy to help followers keep up with the domain-specific advancements. In addition,
    we introduce extensive resources to facilitate the field's development, including datasets, open-source, time series libraries. A GitHub
    repository is also maintained for resource updates (https://github.com/start2020/Awesome-TimeSeries-LLM-FM).
    
    
    2. DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning
    We introduce our first-generation reasoning models, DeepSeek-R1-Zero and DeepSeek-R1.
    DeepSeek-R1-Zero, a model trained via large-scale reinforcement learning (RL) without supervised
    fine-tuning (SFT) as a preliminary step, demonstrates remarkable reasoning capabilities.
    Through RL, DeepSeek-R1-Zero naturally emerges with numerous powerful and intriguing
    reasoning behaviors. However, it encounters challenges such as poor readability, and language
    mixing. To address these issues and further enhance reasoning performance, we introduce
    DeepSeek-R1, which incorporates multi-stage training and cold-start data before RL. DeepSeek-
    R1 achieves performance comparable to OpenAI-o1-1217 on reasoning tasks. To support the
    research community, we open-source DeepSeek-R1-Zero, DeepSeek-R1, and six dense models
    (1.5B, 7B, 8B, 14B, 32B, 70B) distilled from DeepSeek-R1 based on Qwen and Llama.
    
    
    user question:
    {user_question}
    '''
    
    system_template_OuterAgent: str = """ 
    You are a helpful virtual assistant specialized in answering academic questions.
    Your answers must be based on the context that you will receive.
    You will answer considering the parameters:
    - Target audience: {target_audience}
    - Tone: {answer_tone}
    - Length: {answer_length}
    
    context:
    {text_context}
    
    
    User question:
    {user_question}
    """

# ─────────────────────────────────────────────────────────────
# Settings Management
# ─────────────────────────────────────────────────────────────
# Store settings globally
app_settings = Settings()

@app.post("/update_settings")
async def update_settings(settings: Settings):
    global app_settings
    app_settings = settings
    return {"message": "Settings updated successfully"}

@app.get("/settings")
async def get_settings():
    return app_settings

# ─────────────────────────────────────────────────────────────
# On Startup Event: Load settings from Settings class
# ─────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    """
    This will run one time when the server starts.
    We initialize the SingleThreadedAgentRuntime, register your agents,
    and store it in app.state so it is accessible in endpoints.
    """
    # Initialize default settings
    global app_settings
    app_settings = Settings(
        AZURE_ENDPOINT_LLM=os.getenv('AZURE_ENDPOINT_LLM', ''),
        DEPLOYMENT_NAME_LLM=os.getenv('DEPLOYMENT_NAME_LLM', ''),
        API_VERSION=os.getenv('API_VERSION', ''),
        AZURE_OPENAI_API_KEY=os.getenv('AZURE_OPENAI_API_KEY', ''),
        EMBEDDING_KEY=os.getenv('EMBEDDING_KEY', ''),
        AZURE_ENDPOINT_EMBEDDING=os.getenv('AZURE_ENDPOINT_EMBEDDING', ''),
        DEPLOYMENT_NAME_EMBEDDING=os.getenv('DEPLOYMENT_NAME_EMBEDDING', ''),
        ELASTICSEARCH_ENDPOINT=os.getenv('ELASTICSEARCH_ENDPOINT', ''),
        ELASTICSEARCH_USER=os.getenv('ELASTICSEARCH_USER', ''),
        ELASTICSEARCH_PASSWORD=os.getenv('ELASTICSEARCH_PASSWORD', '')
    )

def get_current_settings():
    """Helper function to get current settings"""
    global app_settings
    current_settings = app_settings.dict()
    
    return current_settings

# ─────────────────────────────────────────────────────────────
# Initialize Multi-Agent Runtime
# ─────────────────────────────────────────────────────────────
async def initialize_runtime(llm, dict_vectordb, store, settings):
    """Initialize the runtime environment and register all agents"""
    runtime = SingleThreadedAgentRuntime()
    
    # Register all agents with current settings
    await RouterAgent.register(runtime, "router_agent", lambda: RouterAgent(
        description="RouterAgent",
        system_template=settings['system_template_RouterAgent'],
        llm=llm,
    ))
    
    await TimeSeriesAgent.register(runtime, "TimeSeries_agent", lambda: TimeSeriesAgent(
        description="TimeSeriesAgent",
        dict_vectordb=dict_vectordb,
    ))
    
    await DeepSeekAgent.register(runtime, "DeepSeek_agent", lambda: DeepSeekAgent(
        description="DeepSeekAgent",
        dict_vectordb=dict_vectordb,
    ))
    
    await OuterAgent.register(
        runtime,
        "outer_agent",
        lambda: OuterAgent(
            description="OuterAgent",
            llm=llm,
            session_id='Teste_01',
            store=store,
            system_template=settings['system_template_OuterAgent'],
            router_agent_id="router_agent",
            TimeSeries_agent_id="TimeSeries_agent",
            DeepSeek_agent_id="DeepSeek_agent",
            target_audience=settings['target_audience'],
            answer_tone=settings['answer_tone'],
            answer_length=settings['answer_length'],
        ),
    )
    
    runtime.start()
    return runtime

# ─────────────────────────────────────────────────────────────
# Endpoint: POST /ask → Main agent interaction
# ─────────────────────────────────────────────────────────────
@app.post("/ask")
async def ask_question(query: UserQuery):
    try:

        ##################### DEBUG ######################
        print("📥 Received question:", query.question)
        ##################### DEBUG ######################


        # Get current settings
        current_settings = get_current_settings()
        
        ##################### DEBUG ######################
        print("⚙️ Settings loaded")
        ##################### DEBUG ######################

        # Validate required settings
        if not current_settings['AZURE_ENDPOINT_LLM']:
            raise ValueError("AZURE_ENDPOINT_LLM not configured")
        if not current_settings['DEPLOYMENT_NAME_LLM']:
            raise ValueError("DEPLOYMENT_NAME_LLM not configured")
        if not current_settings['API_VERSION']:
            raise ValueError("API_VERSION not configured")
        
        # Initialize runtime with current settings
        llm = AzureChatOpenAI(
            temperature=0,
            model_name="gpt-4o-mini",
            deployment_name=current_settings['DEPLOYMENT_NAME_LLM'],  
            api_version=current_settings['API_VERSION'],
            azure_endpoint=current_settings['AZURE_ENDPOINT_LLM'],
            api_key=current_settings['AZURE_OPENAI_API_KEY']
        )
        
        # Get necessary information about the collection in the vector db
        dict_vectordb = return_vectordb_full_text_and_questions(
            embedding_key=current_settings['EMBEDDING_KEY'],
            deployment_name_embedding=current_settings['DEPLOYMENT_NAME_EMBEDDING'],
            azure_endpoint_embedding=current_settings['AZURE_ENDPOINT_EMBEDDING'],
            elasticsearch_endpoint=current_settings['ELASTICSEARCH_ENDPOINT'],
            elasticsearch_user=current_settings['ELASTICSEARCH_USER'],
            elasticsearch_password=current_settings['ELASTICSEARCH_PASSWORD'],
        )
        
        ##################### DEBUG ######################
        print("📦 Initializing runtime")
        ##################### DEBUG ######################

        
        
        # Initialize runtime with current settings
        runtime = await initialize_runtime(llm, dict_vectordb, store, current_settings)
        

        try:
            ##################### DEBUG ######################
            print("💬 Sending user message to OuterAgent")
            ##################### DEBUG ######################
            # Give an id for the agent that will communicate with the user
            outer_agent_id = AgentId("outer_agent", "default")
            # Process the message
            user_message = Message(content=query.question)
            response = await runtime.send_message(user_message, outer_agent_id)
            

            ##################### DEBUG ######################
            print("✅ Got response:", response.content)
            ##################### DEBUG ######################
            return {"response": response.content}

        except Exception as agent_error:
            print("🔥 Error while sending message to OuterAgent:", traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"OuterAgent error: {str(agent_error)}")
        
    except Exception as e:
        print("🔥 Unhandled error in /ask:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────
# Health check endpoint
# ─────────────────────────────────────────────────────────────
@app.get("/")
def root():
    

    return {"message": "AI Multi-Agent FastAPI is running"}
