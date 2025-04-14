# TimeSeriesAgent

from functions.elasticsearch_utils.similarity_search_full_and_question import similarity_search_full_and_question
from autogen_core import MessageContext, RoutedAgent, message_handler
from .Message import Message
# Agent to collect information about the company
class TimeSeriesAgent(RoutedAgent):
    '''
    We could actually do only one agent for both papers, changing onlu the document_name in our search.
    The advantage of one agent per paper is that if we had more than one relevant paper, we could run several similarity search in pararel and make a new agent to sumarize and group the ideas from different papers.
    '''
    def __init__(
        self, 
        description, 
        dict_vectordb,
    ):
        super().__init__(description) 
        self.dict_vectordb = dict_vectordb

    @message_handler
    async def on_my_message(self, message: Message, ctx: MessageContext) -> Message:
        print("TESTING: Inside TimeSeriesAgent.")

        # Similarity search
        dict_similarity_search = similarity_search_full_and_question(
            dict_vectordb = self.dict_vectordb,
            user_question = message.content,
            document_name_to_find = 'A Survey of Time Series Foundation Models Generalizing Time Series.pdf',
        )
        
        print(f"TESTING: TimeSeriesAgent: {dict_similarity_search}.")
        
        
        print('-----------------------------------------------------------------------')
        print()
        return Message(content = dict_similarity_search)