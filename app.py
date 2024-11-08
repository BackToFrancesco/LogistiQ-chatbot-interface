from flask import Flask, render_template, request, jsonify
from chatbot import chat, get_initial_message_english, LANGUAGE, ORIGIN, DESTINATION, translate_message

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
    
    response, agreement_result = chat(user_input, LANGUAGE, current_offer, ORIGIN, DESTINATION, starting_price, max_price)
    conversation_history.append({"role": "human", "content": user_input})
    conversation_history.append({"role": "assistant", "content": response})

    new_offer = extract_offer_from_response(response)
    if new_offer is not None:
        current_offer = new_offer

    if agreement_result["agreement_reached"]:
        final_deal = {
            "final_price": agreement_result["final_price"] or current_offer,
            "origin": ORIGIN,
            "destination": DESTINATION,
            "explanation": agreement_result["explanation"]
        }
        return jsonify({"message": response, "end_chat": True, "agreement": True, "final_deal": final_deal})

    if current_offer > max_price:
        return jsonify({"message": response, "end_chat": True, "agreement": False})

    return jsonify({"message": response})

def extract_offer_from_response(response):
    import re
    match = re.search(r"Current offer: \$(\d+(?:\.\d{2})?)", response)
    if match:
        return float(match.group(1))
    return None

if __name__ == '__main__':
    app.run(debug=True)
