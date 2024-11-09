import boto3
from langchain_aws import ChatBedrock
from langchain.schema import HumanMessage, AIMessage
from langchain_core.runnables import RunnablePassthrough
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate

# Constants
LANGUAGE = "Italian"
ORIGIN = "Bolzano"
DESTINATION = "Munich"

# Set up Amazon Bedrock client
bedrock_client = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-west-2'
)

# Initialize the Bedrock LLM
llm = ChatBedrock(
    client=bedrock_client,
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    model_kwargs={"temperature": 0.7}
)

# Initialize conversation history
conversation_history = []

class ChatbotResponse(BaseModel):
    message: str = Field(description="The chatbot's response message", examples=["Mi dispiace, 100000 è davvero un prezzo troppo alto per noi. Il nostro budget massimo per questa tratta è di 1500. Posso offrirvi 1200 per il trasporto da Bolzano a Monaco. Fatemi sapere se questa cifra è più accettabile."])
    price_offered: float | None = Field(default=None, description="Price offered as a float", examples=[1150.0, 2000.0])

# Create a parser for the ChatbotResponse
parser = PydanticOutputParser(pydantic_object=ChatbotResponse)

# Function to generate the initial message in English
def get_initial_message_english(initial_price, origin, destination):
    return (f"Greetings! I'm ChatBot, the AI assistant for LogisticsPro Inc. I'm reaching out to discuss "
            f"contracting transportation services for our upcoming needs. Specifically, we're looking to "
            f"arrange a truck for a shipment from {origin} to {destination}. Our initial budget estimate "
            f"for this route is ${initial_price}, but we're open to negotiation based on the services you can offer.")

def translate_message(message, target_language):
    """
    Translate the given message to the target language using the LLM.
    """
    prompt = f"Translate the following English message to {target_language}:\n\n{message}\n\n Respond with only the translated text."
    response = llm.invoke(prompt)
    return response.content if isinstance(response, AIMessage) else str(response)

def create_prompt(input_dict, initial_message):
    history_str = "\n".join([f"{'Chatbot' if isinstance(msg, AIMessage) else 'Supplier'}: {msg.content}" for msg in conversation_history])
    template = """
You are an AI assistant for LogisticsPro Inc., negotiating transportation services.
Context: You initiated the conversation with the following message:
{initial_message}

Conversation history:
{history_str}

Continue the conversation based on this context.
Language: {language}
Origin: {origin}
Destination: {destination}
Current Offer: {transport_cost}
Starting Price: {starting_price}
Maximum Price: {max_price}
Supplier's response: {input}

Negotiation Strategy:
1. Start with the initial price of {starting_price}.
2. Make counter-offers based on the supplier's responses.
3. Gradually increase your offer if necessary, but do not exceed {max_price}.
4. If the supplier doesn't accept a price at or below {max_price}, end the negotiation.

Respond professionally as the AI assistant, addressing the supplier's input and continuing the negotiation.
Make counter-offers when appropriate, and be prepared to end the negotiation if the maximum price is exceeded.
Always include your current offer in your response.
Always respond using the following format:
{{
message: str,
price_offered: float | None = None
}}
"""
    prompt = PromptTemplate(
        template=template,
        input_variables=["initial_message", "history_str", "language", "origin", "destination", "transport_cost", "starting_price", "max_price", "input"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    return prompt

def chat(input_text, language, transport_cost, origin, destination, starting_price, max_price):
    conversation_history.append(HumanMessage(content=input_text))
    initial_message = get_initial_message_english(starting_price, origin, destination)
    prompt = create_prompt({
        "input": input_text,
        "language": language,
        "transport_cost": transport_cost,
        "origin": origin,
        "destination": destination,
        "starting_price": starting_price,
        "max_price": max_price
    }, initial_message)
    
    history_str = "\n".join([f"{'Chatbot' if isinstance(msg, AIMessage) else 'Supplier'}: {msg.content}" for msg in conversation_history])
    chain = prompt | llm | parser
    response = chain.invoke({
        "input": input_text,
        "initial_message": initial_message,
        "history_str": history_str,
        "language": language,
        "origin": origin,
        "destination": destination,
        "transport_cost": transport_cost,
        "starting_price": starting_price,
        "max_price": max_price
    })
    
    conversation_history.append(AIMessage(content=response.message))
    return response

# The extract_offer_from_response function is no longer needed and has been removed
