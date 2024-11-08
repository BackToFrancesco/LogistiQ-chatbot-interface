from flask import Flask, render_template, request, jsonify
from chatbot import chat, get_initial_message_english, LANGUAGE, ORIGIN, DESTINATION, translate_message, llm

app = Flask(__name__)

conversation_history = []
current_offer = 0
starting_price = 0
max_price = 0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_chat', methods=['POST'])
def start_chat():
    global starting_price, max_price, current_offer, conversation_history
    starting_price = float(request.json['starting_price'])
    max_price = float(request.json['max_price'])
    current_offer = starting_price
    conversation_history = []

    initial_message = translate_message(get_initial_message_english(starting_price, ORIGIN, DESTINATION), target_language=LANGUAGE)
    conversation_history.append({"role": "assistant", "content": initial_message})

    return jsonify({"message": initial_message})

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    global current_offer, conversation_history
    user_input = request.json['message']
    
    if user_input.lower().strip() == "accept":
        final_message = translate_message("Great! The negotiation has concluded successfully. We are now waiting for approval from the company to proceed with the payment. Thank you for your cooperation.", LANGUAGE)
        conversation_history.append({"role": "human", "content": user_input})
        conversation_history.append({"role": "assistant", "content": final_message})
        
        # Analyze the conversation to get the final agreed price
        final_price = analyze_conversation_for_final_price(conversation_history)
        
        return jsonify({
            "message": final_message,
            "end_chat": True,
            "agreement_reached": True,
            "final_deal": {
                "price": final_price,
                "origin": ORIGIN,
                "destination": DESTINATION
            }
        })
    
    response = chat(user_input, LANGUAGE, current_offer, ORIGIN, DESTINATION, starting_price, max_price)
    conversation_history.append({"role": "human", "content": user_input})
    conversation_history.append({"role": "assistant", "content": response})

    new_offer = extract_offer_from_response(response)
    if new_offer is not None:
        current_offer = new_offer

    if current_offer > max_price:
        return jsonify({"message": response, "end_chat": True})

    return jsonify({"message": response})

def extract_offer_from_response(response):
    import re
    match = re.search(r"Current offer: \$(\d+(?:\.\d{2})?)", response)
    if match:
        return float(match.group(1))
    return None

def analyze_conversation_for_final_price(conversation_history):
    # Get the latest AI assistant message
    latest_ai_message = next((msg['content'] for msg in reversed(conversation_history) if msg['role'] == 'assistant'), None)
    
    if not latest_ai_message:
        return None
    
    prompt = f"""
    Analyze the following message and extract the final agreed price for the transportation service.
    Only return the numeric value of the final price, without any currency symbols or additional text.

    Message:
    {latest_ai_message}

    Final agreed price:
    """

    response = llm.invoke(prompt)
    
    # Extract the numeric value from the response
    import re
    price_match = re.search(r'\d+(\.\d{2})?', response.content)
    if price_match:
        return float(price_match.group())
    else:
        return None

if __name__ == '__main__':
    app.run(debug=True)
