from flask import Flask, render_template, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from pymongo import MongoClient
import random

# Initialize the model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

# Connect to the MongoDB database
client = MongoClient("mongodb://localhost:27017")
db = client["ibm_chatbot"]
collection = db["convo"]

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('chat.html')


@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    response = get_Chat_response(msg)
    return jsonify({"response": str(response)})


def get_Chat_response(text):
    # Fetch the data from the database based on the user input
    document = collection.find_one({"patterns": {"$in": [text]}})
    if document:
        responses = document["responses"]
        response = random.choice(responses)
        return response
    else:
        fallback_responses = collection.find_one({"tag": "fallback"})["responses"]
        return random.choice(fallback_responses)


if __name__ == '__main__':
    app.run()



"""
from flask import Flask, request, jsonify, render_template
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from pymongo import MongoClient
import random
import telegram  # Import the Telegram module

# Initialize the model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

# Connect to the MongoDB database
client = MongoClient("mongodb://localhost:27017")
db = client["ibm_chatbot"]
collection = db["convo"]

# Initialize the Flask app
app = Flask(__name__)

# Replace this with your Telegram bot API token
TELEGRAM_API_TOKEN = "6389965231:AAFmkyPdhOAZT_1HM07dg1uigpRRKELC520"

# Create a Telegram Bot instance
bot = telegram.Bot(token=TELEGRAM_API_TOKEN)


@app.route("/")
def index():
    return render_template('chat.html')


@app.route("/get", methods=["POST"])
def chat():
    msg = request.form["msg"]
    response = get_Chat_response(msg)

    # Send the response back to the user on Telegram
    chat_id = request.form.get("chat_id")
    if chat_id:
        bot.send_message(chat_id=chat_id, text=response)

    return jsonify({"response": response})


# Route to handle incoming updates from Telegram
@app.route("/telegram_webhook", methods=["POST"])
def telegram_webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat_id
    text = update.message.text
    response = get_Chat_response(text)

    # Send the response back to the user on Telegram
    if response:
        bot.send_message(chat_id=chat_id, text=response)

    return jsonify({"status": "ok"}), 200


# Get the chat response
def get_Chat_response(text):
    # Fetch the data from the database based on the user input
    document = collection.find_one({"patterns": {"$in": [text]}})
    if document:
        responses = document["responses"]
        response = random.choice(responses)
        return response
    else:
        fallback_responses = collection.find_one({"tag": "fallback"})["responses"]
        return random.choice(fallback_responses)


# Set up the Telegram webhook
def set_telegram_webhook():
    webhook_url = "YOUR_PUBLIC_URL/telegram_webhook"  # Replace with your public URL
    bot.set_webhook(url=webhook_url)


if __name__ == '__main__':
    # Set up the Telegram webhook when the app runs
    set_telegram_webhook()
    app.run()


from flask import Flask, render_template, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from pymongo import MongoClient
import random

# Initialize the model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

# Connect to the MongoDB database
client = MongoClient("mongodb://localhost:27017")
db = client["ibm_chatbot"]
collection = db["convo"]

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('chat.html')


@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    response = get_Chat_response(msg)
    return jsonify({"response": str(response)})


def get_Chat_response(text):
    # Fetch the data from the database based on the user input
    document = collection.find_one({"patterns": {"$in": [text]}})
    if document:
        responses = document["responses"]
        response = random.choice(responses)
        return response
    else:
        fallback_responses = collection.find_one({"tag": "fallback"})["responses"]
        return random.choice(fallback_responses)


if __name__ == '__main__':
    app.run()

client.close()


from flask import Flask, render_template, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from pymongo import MongoClient
import random

# Initialize the model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

# Connect to the MongoDB database
client = MongoClient("mongodb://localhost:27017")
db = client["ibm_chatbot"]
collection = db["convo"]

# Initialize the conversation history for each user session
conversation_history = {}


app = Flask(__name__)


@app.route("/")
def index():
    return render_template('chat.html')


@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    response = get_Chat_response(msg)
    return jsonify({"response": str(response)})


def get_Chat_response(text):
    # Fetch the data from the database based on the user input
    document = collection.find_one({"patterns": {"$in": [text]}})
    if document:
        responses = document["responses"]
        response = random.choice(responses)
    else:
        fallback_responses = collection.find_one({"tag": "fallback"})["responses"]
        response = random.choice(fallback_responses)

    # Update conversation history with the user input
    user_input_ids = tokenizer.encode(text + tokenizer.eos_token, return_tensors='pt')
    if 'chat_history_ids' in conversation_history:
        conversation_history['chat_history_ids'] = torch.cat([conversation_history['chat_history_ids'], user_input_ids], dim=-1)
    else:
        conversation_history['chat_history_ids'] = user_input_ids

    # Generate a response using the model
    chat_history_ids = model.generate(conversation_history['chat_history_ids'], max_length=1000, pad_token_id=tokenizer.eos_token_id)
    response = tokenizer.decode(chat_history_ids[:, conversation_history['chat_history_ids'].shape[-1]:][0], skip_special_tokens=True)

    # Update conversation history with the model-generated response
    conversation_history['chat_history_ids'] = torch.cat([conversation_history['chat_history_ids'], chat_history_ids], dim=-1)

    return response


if __name__ == '__main__':
    app.run()

client.close()





from flask import Flask, render_template, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from pymongo import MongoClient

tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
client = MongoClient("mongodb://localhost:27017")
db = client["ibm_chatbot"]
collection = db["convo"]

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('chat.html')


@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    input = msg
    return get_Chat_response(input)


def get_Chat_response(text):
    for step in range(5):
        # encode the new user input, add the eos_token and return a tensor in Pytorch
        new_user_input_ids = tokenizer.encode(str(text) + tokenizer.eos_token, return_tensors='pt')

        # append the new user input tokens to the chat history
        bot_input_ids = torch.cat([chat_history_ids, new_user_input_ids], dim=-1) if step > 0 else new_user_input_ids

        # generated a response while limiting the total chat history to 1000 tokens,
        chat_history_ids = model.generate(bot_input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)

        # pretty print last ouput tokens from bot
        return tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)


if __name__ == '__main__':
    app.run()

client.close()
"""