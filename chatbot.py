import boto3
from langchain_aws import ChatBedrock
from langchain.schema import HumanMessage, AIMessage
from langchain_core.runnables import RunnablePassthrough

# Set up Amazon Bedrock client
bedrock_client = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-west-2'
)

# Initialize the Bedrock LLM
llm = ChatBedrock(
    client=bedrock_client,
    model_id="anthropic.claude-v2",
    model_kwargs={"temperature": 0.7}
)

# Initialize conversation history
conversation_history = []

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
Transport Cost: {input_dict['transport_cost']}
Supplier's response: {input_dict['input']}

Respond professionally as the AI assistant, addressing the supplier's input and continuing the negotiation.
"""

chain = create_prompt | llm

def chat(input_text, language, transport_cost):
    conversation_history.append(HumanMessage(content=input_text))
    response = chain.invoke({"input": input_text, "language": language, "transport_cost": transport_cost})
    
    # Extract the content from the response
    if isinstance(response, dict) and 'content' in response:
        content = response['content']
    elif isinstance(response, str):
        content = response
    else:
        content = str(response)  # Fallback to string representation
    
    conversation_history.append(AIMessage(content=content))
    return content

# Main loop for interaction
language = input("Enter the conversation language: ")
transport_cost = input("Enter the transport cost: ")

initial_message = (
    "Greetings! I'm ChatBot, the AI assistant for LogisticsPro Inc. I'm reaching out to discuss "
    "contracting transportation services for our upcoming needs. Specifically, we're looking to "
    "arrange a truck for a shipment from New York to Los Angeles. Our initial budget estimate "
    "for this route is around $3,000, but we're open to negotiation based on the services you can offer. "
)

print(f"Chatbot: {initial_message}")

# Add the initial message to the conversation history
conversation_history.append(AIMessage(content=initial_message))

while True:
    user_input = input("Supplier: ")
    if user_input.lower() in ['quit', 'exit', 'bye']:
        print("Chatbot: Goodbye!")
        break
    
    response = chat(user_input, language, transport_cost)
    print(f"Chatbot: {response}")
