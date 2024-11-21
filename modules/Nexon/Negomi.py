import datetime
import os
import ollama
from rich import print
from json import dumps, loads
from .logger import logger

conversation_histories = {}

def get_response(user_id, user_message, originalText, previousContent=None, previousRole="assistant"):
    global conversation_histories

    # Initialize user-specific history if not present
    if user_id not in conversation_histories:
        conversation_histories[user_id] = []

    conversation_history = conversation_histories[user_id]

    # Handle the /clear command
    if originalText.startswith("/clear"):
        current_datetime = datetime.datetime.now()
        date = current_datetime.strftime("%Y-%m-%d")
        timed = current_datetime.strftime("%H-%M-%S-%f")
        os.makedirs(f"logs/{date}", exist_ok=True)
        with open(f'logs/{date}/output_for_Negomi_{timed}.json', "w") as f:
            f.write(dumps(conversation_history, indent=4))
        conversation_histories[user_id] = []  # Clear specific user's history
        return False

    # Add the new user message to the conversation history
    if previousContent:
        conversation_history.append({'role': previousRole, 'content': previousContent})
    conversation_history.append({'role': 'user', 'content': user_message})

    # Generate response using Ollama
    try:
        response = ollama.chat(model='Negomi', messages=conversation_history)
        text = response.get('message', {}).get('content', "Error: No response generated.")
    except Exception as e:
        logger.error(f"Error in ollama.chat: {e}")
        text = "Sorry, I encountered an issue generating a response."

    # Append the assistant's response to history if valid
    if text and text != "Error: No response generated.":
        conversation_history.append({'role': 'assistant', 'content': text})

    return text

def generate(prompt,model="NegomiX") ->str:
    response = ollama.generate(model,prompt)
    return response["response"]
    

if __name__ == '__main__':
    os.system("cls")
    while True:
        text = input("--> ")
        print("Mahiro: "+ text)
        if text.startswith("/bye"):
            break
        get_response("Mahiro: "+ text)
        print("\n")
