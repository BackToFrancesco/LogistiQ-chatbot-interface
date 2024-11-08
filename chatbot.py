import boto3
from langchain_aws import ChatBedrock
from langchain.memory import ChatMessageHistory
from langchain.schema import HumanMessage, AIMessage
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory

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

# Set up the conversation chain
def create_prompt(input_dict):
    return f"""
You are an AI assistant for LogisticsPro Inc., negotiating transportation services.
Context: You initiated the conversation with the following message:
{initial_message}

Continue the conversation based on this context.
Language: {input_dict['language']}
Transport Cost: {input_dict['transport_cost']}
Supplier's response: {input_dict['input']}

Respond professionally as the AI assistant, addressing the supplier's input and continuing the negotiation.
"""

chain = create_prompt | llm

conversation = RunnableWithMessageHistory(
    chain,
    lambda session_id: ChatMessageHistory(),
    input_messages_key="input",
    history_messages_key="history",
)

def chat(input_text, language, transport_cost):
    response = conversation.invoke(
        {"input": input_text, "language": language, "transport_cost": transport_cost},
        config={"configurable": {"session_id": "chat_session"}}
    )
    return response.content

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

# Add the initial message to the conversation memory
conversation.get_session_history("chat_session").add_ai_message(initial_message)

while True:
    user_input = input("Supplier: ")
    if user_input.lower() in ['quit', 'exit', 'bye']:
        print("Chatbot: Goodbye!")
        break
    
    response = chat(user_input, language, transport_cost)
    print(f"Chatbot: {response}")
