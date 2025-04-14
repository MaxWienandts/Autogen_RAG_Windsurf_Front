# Outer Agent

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory  # For get_session_history
from langchain_community.chat_message_histories import ChatMessageHistory # For get_session_history

from autogen_core import AgentId, MessageContext, RoutedAgent, message_handler
from .Message import Message
    
class OuterAgent(RoutedAgent):
    def __init__(
        self,
        description,
        llm,
        session_id,
        store,
        system_template,
        router_agent_id,
        TimeSeries_agent_id,
        DeepSeek_agent_id,
        target_audience,
        answer_tone,
        answer_length,
    ):
        super().__init__(description)
        self.llm = llm
        self.session_id = session_id
        self.store = store
        self.system_template = system_template
        self.router_agent_id = AgentId(router_agent_id, self.id.key)
        self.TimeSeries_agent_id = AgentId(TimeSeries_agent_id, self.id.key)
        self.DeepSeek_agent_id = AgentId(DeepSeek_agent_id, self.id.key)
        self.target_audience = target_audience
        self.answer_tone = answer_tone
        self.answer_length = answer_length

    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self.store:
            self.store[session_id] = ChatMessageHistory()
        return self.store[session_id]
        
    @message_handler
    async def on_my_message(self, message: Message, ctx: MessageContext) -> Message:

        print("TESTING: Inside OuterAgent.")

        # Get information from other agents
        RouterAgent_response = await self.send_message(message, self.router_agent_id)
        RouterAgent_content = RouterAgent_response.content
        if RouterAgent_content == '1':    
            text_context_response = await self.send_message(message, self.TimeSeries_agent_id)
            text_context_response_content = text_context_response.content
        elif RouterAgent_content == '2': 
            text_context_response = await self.send_message(message, self.DeepSeek_agent_id)
            text_context_response_content = text_context_response.content
        else:
            text_context_response_content = [""]
            

        # Get context
        text_context = []
        if len(text_context_response_content) > 1:  # In case we didn't find any relevant paper in our knowledge database.
            for key in text_context_response_content['scores_collection_full_text']:
                text_context.append(text_context_response_content['scores_collection_full_text'][key]['page_content'])
        text_context = "\n\n".join(text_context)
        
        
        # Set LLM 
        # Use this to add chat history
        system_prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_template),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{user_question}"),
        ])
        chain_OuterAgent = system_prompt | self.llm
        ### Statefully manage chat history ###
        conversational_chain_OuterAgent = RunnableWithMessageHistory(
            chain_OuterAgent,
            get_session_history=self.get_session_history,
            input_messages_key="user_question",
            history_messages_key="chat_history",
        )

        answer_chain_OuterAgent = conversational_chain_OuterAgent.invoke(
            {
                # Variables used in prompt
                'target_audience': self.target_audience,
                'answer_tone': self.answer_tone,
                'answer_length': self.answer_length,
                "text_context": text_context,
                'user_question': message.content, 
            },
            config={
                "configurable": {"session_id": self.session_id}
            },  # constructs a key "session_id" in `store`.
        ) 

        print(f"TESTING: answer_chain_OuterAgent: {answer_chain_OuterAgent.content}")
        print('-----------------------------------------------------------------------')
        print()
        return Message(content=answer_chain_OuterAgent.content)