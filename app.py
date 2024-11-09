from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from chatbot import chat, get_initial_message_english, LANGUAGE, ORIGIN, DESTINATION, translate_message, ChatbotResponse
import urllib.parse
import time
import threading

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Add this line for session management

conversation_history = []
current_offer = 0
starting_price = 0
max_price = 0
final_price = 0  # Initialize final_price
origin = ORIGIN
destination = DESTINATION
chat_completed = False
chat_completed_lock = threading.Lock()

@app.route('/')
def index():
    # Pass any existing chat parameters to the template
    return render_template('index.html', 
                           starting_price=session.get('starting_price'),
                           max_price=session.get('max_price'),
                           origin=session.get('origin'),
                           destination=session.get('destination'))

@app.route('/start_chat', methods=['POST'])
def start_chat():
    global starting_price, max_price, current_offer, conversation_history, final_price
    starting_price = float(request.json['starting_price'])
    final_price = starting_price  # Set initial final_price
    max_price = float(request.json['max_price'])
    current_offer = starting_price
    conversation_history = []

    initial_message = translate_message(get_initial_message_english(starting_price, ORIGIN, DESTINATION), target_language=LANGUAGE)
    conversation_history.append({"role": "assistant", "content": initial_message})

    return jsonify({"message": initial_message})

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    global current_offer, conversation_history, final_price, chat_completed
    user_input = request.json['message']
    
    if user_input.lower().strip() == "accept":
        final_message = translate_message("Great! The negotiation has concluded successfully. We are now waiting for approval from the company to proceed with the payment. Thank you for your cooperation.", LANGUAGE)
        conversation_history.append({"role": "human", "content": user_input})
        conversation_history.append({"role": "assistant", "content": final_message})
        print(f"final message: {final_message}")
        
        return_value = jsonify({
            "message": final_message,
            "end_chat": True,
            "agreement_reached": True,
            "price": final_price,
        })
        
        print("Return value when user accepts:")
        print(return_value.get_data(as_text=True))
        with chat_completed_lock:
            chat_completed = True
        
        return return_value
    
    response: ChatbotResponse = chat(user_input, LANGUAGE, current_offer, ORIGIN, DESTINATION, starting_price, max_price)
    conversation_history.append({"role": "human", "content": user_input})
    conversation_history.append({"role": "assistant", "content": response.message})
    print(f"response: {response}")

    if response and response.price_offered is not None:
        final_price = response.price_offered
        current_offer = final_price

    return jsonify({"message": response.message})

# The extract_offer_from_response function has been removed as it's no longer needed

def analyze_conversation_for_final_price(conversation_history):
    # Get the latest AI assistant message
    latest_ai_message = next((msg for msg in reversed(conversation_history) if msg['role'] == 'assistant'), None)
    
    if not latest_ai_message:
        return None
    print(latest_ai_message)
    # The content should already be a ChatbotResponse object
    return latest_ai_message['content'].price_offered

import webbrowser
import threading

@app.route('/receive_params', methods=['POST'])
def receive_params():
    global chat_completed
    data = request.json
    print("Received params:", data)
    
    # Store parameters in global variables
    global starting_price, max_price, origin, destination
    starting_price = float(data.get('minimum_price', 0))
    max_price = float(data.get('maximum_price', 0))
    origin = data.get('load_city', ORIGIN)
    destination = data.get('unload_city', DESTINATION)
    
    # Reset chat_completed flag
    with chat_completed_lock:
        chat_completed = False

    # Start a web window locally to chat with the bot
    def open_browser(data):
        # Pass the parameters to the chat interface
        params = urllib.parse.urlencode({
            'starting_price': starting_price,
            'max_price': max_price,
            'origin': origin,
            'destination': destination,
            'chat_initiated': 'true'
        })
        webbrowser.open_new(f'http://localhost:8080/?{params}')

    threading.Timer(1.0, open_browser, args=(data,)).start()
    
    # Wait for the chat to complete
    while True:
        with chat_completed_lock:
            if chat_completed:
                break
        time.sleep(1)
    print("Chat completed")
    
    # Return the final result
    final_price = analyze_conversation_for_final_price(conversation_history)
    return jsonify({
        "final_price": final_price,
        "conversation_history": conversation_history
    })

@app.route('/get_chat_result', methods=['GET'])
def get_chat_result():
    if session.get('chat_completed'):
        final_price = analyze_conversation_for_final_price(conversation_history)
        return jsonify({
            "final_price": final_price,
            "conversation_history": conversation_history
        })
    else:
        return jsonify({"message": "Chat not completed yet."}), 202

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
