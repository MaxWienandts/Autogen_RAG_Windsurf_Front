# RouterAgent

from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_message_histories import ChatMessageHistory

from autogen_core import MessageContext, RoutedAgent, message_handler
from .Message import Message

# Agent to collect information about the company
class RouterAgent(RoutedAgent):
    '''
    This agent could be just a similarity search between the user question and the abstracts of the academic papers.
    '''
    def __init__(
        self, 
        description, 
        system_template, 
        llm, 
    ):
        super().__init__(description) 
        self.system_template = system_template
        self.llm = llm

    @message_handler
    async def on_my_message(self, message: Message, ctx: MessageContext) -> Message:
        print("TESTING: Inside RouterAgent.")

        # Set LLM
        system_prompt = ChatPromptTemplate.from_template(self.system_template) 
        chain_llm = system_prompt | self.llm
        answer_chain_llm = chain_llm.invoke(
            {
                'user_question': message.content,
            }
        )
        
        print(f"TESTING: Router: {answer_chain_llm.content}.")
        
        rout_to_agent = answer_chain_llm.content

        print(f"TESTING: rout_to_agent: {rout_to_agent}.")
        
        print('-----------------------------------------------------------------------')
        print()
        return Message(content = rout_to_agent)