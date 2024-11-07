import datetime
import os
import ollama
from rich import print
from json import dumps, loads
from modules.Side import logForAI

if __name__ == '__main__':
    with open("OllamaSetup/system") as f:
        sys= f.read().replace("\n"," ")
    System = sys
    num_max = 2000
    modelfile=f'''
    FROM llama3.1
    PARAMETER num_ctx {num_max}
    SYSTEM {System}
    '''
    ollama.create(model='NegomiX', modelfile=modelfile)

conversation_history = []
def get_response(user_message,originalText:str,previousContent:str=None,previousRole:str = "assistant") -> str:
    global conversation_history
    if (originalText.startswith("/clear")) and (logForAI):
        current_datetime = datetime.datetime.now()
        date = str(current_datetime.strftime("%Y-%m-%d"))
        timed = str(current_datetime.strftime("%H-%M-%S-%f"))
        os.makedirs(f"logs/{date}",exist_ok=True)
        with open(f'logs/{date}/output_for_Negomi_{timed}.json', "w") as f:
            f.write(dumps(conversation_history,indent=4))
        conversation_history = []
        return False
    # Add the new user message to the conversation history
    if previousContent:
        conversation_history.append({'role': f'{previousRole}', 'content': previousContent})
    conversation_history.append({'role': 'user', 'content': user_message})
    # print(conversation_history)
    
    response = ollama.chat(model='Negomi', messages=conversation_history)
    
    text = response['message']['content']
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
