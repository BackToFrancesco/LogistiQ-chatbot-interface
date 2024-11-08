import boto3
from langchain_aws import ChatBedrock
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage

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
conversation = ConversationChain(
    llm=llm,
    memory=ConversationBufferMemory(return_messages=True)
)

def chat(input_text, language, transport_cost):
    # Prepare the input with parameters
    full_input = f"Language: {language}\nTransport Cost: {transport_cost}\nUser: {input_text}"
    
    # Get the response from the conversation chain
    response = conversation.predict(input=full_input)
    
    return response

# Main loop for interaction
language = input("Enter the conversation language: ")
transport_cost = input("Enter the transport cost: ")

initial_message = (
    "Greetings! I'm ChatBot, the AI assistant for LogisticsPro Inc. I'm reaching out to discuss "
    "contracting transportation services for our upcoming needs. Specifically, we're looking to "
    "arrange a truck for a shipment from New York to Los Angeles. Our initial budget estimate "
    "for this route is around $3,000, but we're open to negotiation based on the services you can offer. "
    "Could you please provide information on your available trucks, estimated delivery time, and pricing "
    "for this route? We're particularly interested in reliability, tracking capabilities, and any "
    "special handling services you might offer for sensitive cargo. Thank you for your time, and I look "
    "forward to discussing how we can work together to meet our transportation needs."
)

print(f"Chatbot: {initial_message}")

# Add the initial message to the conversation memory
conversation.memory.chat_memory.add_ai_message(initial_message)

while True:
    user_input = input("Supplier: ")
    if user_input.lower() in ['quit', 'exit', 'bye']:
        print("Chatbot: Goodbye!")
        break
    
    response = chat(user_input, language, transport_cost)
    print(f"Chatbot: {response}")
