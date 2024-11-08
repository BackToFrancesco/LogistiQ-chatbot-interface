import boto3
from langchain_aws import ChatBedrock
from langchain.schema import HumanMessage, AIMessage
from langchain_core.runnables import RunnablePassthrough

# Constants
LANGUAGE = "english"
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

def create_prompt(input_dict):
    history_str = "\n".join([f"{'Chatbot' if isinstance(msg, AIMessage) else 'Supplier'}: {msg.content}" for msg in conversation_history])
    return f"""
You are an AI assistant for LogisticsPro Inc., negotiating transportation services.
Context: You initiated the conversation with the following message:
{initial_message}

Conversation history:
{history_str}

Continue the conversation based on this context.
Language: {input_dict['language']}
Origin: {input_dict['origin']}
Destination: {input_dict['destination']}
Current Offer: {input_dict['transport_cost']}
Starting Price: {input_dict['starting_price']}
Maximum Price: {input_dict['max_price']}
Supplier's response: {input_dict['input']}

Negotiation Strategy:
1. Start with the initial price of {input_dict['starting_price']}.
2. Make counter-offers based on the supplier's responses.
3. Gradually increase your offer if necessary, but do not exceed {input_dict['max_price']}.
4. If the supplier doesn't accept a price at or below {input_dict['max_price']}, end the negotiation.

Respond professionally as the AI assistant, addressing the supplier's input and continuing the negotiation.
Make counter-offers when appropriate, and be prepared to end the negotiation if the maximum price is exceeded.
Always include your current offer in your response".
"""

chain = create_prompt | llm

def chat(input_text, language, transport_cost, origin, destination, starting_price, max_price):
    conversation_history.append(HumanMessage(content=input_text))
    response = chain.invoke({
        "input": input_text,
        "language": language,
        "transport_cost": transport_cost,
        "origin": origin,
        "destination": destination,
        "starting_price": starting_price,
        "max_price": max_price
    })
    content = response.content
    conversation_history.append(AIMessage(content=content))
    return content

def extract_offer_from_response(response):
    import re
    match = re.search(r"Current offer: \$(\d+(?:\.\d{2})?)", response)
    if match:
        return float(match.group(1))
    return None

# The main loop and related code has been removed as it's now handled by the Flask app
