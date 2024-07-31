import datetime
import os
import ollama
from rich import print
from json import dumps, loads
from Lib.Side import logForAI

if __name__ == '__main__':
    with open("system") as f:
        sys= f.read().replace("\n"," ")
    System = sys
    num_max = 2000
    modelfile=f'''
    FROM llama3
    PARAMETER num_ctx {num_max}
    SYSTEM {System}
    '''
    ollama.create(model='NegomiX', modelfile=modelfile)

conversation_history = []
def get_response(user_message,s:str) -> str:
    global conversation_history
    if (s.startswith("/clear")) and (logForAI):
        current_datetime = datetime.datetime.now()
        date = str(current_datetime.strftime("%Y-%m-%d"))
        timed = str(current_datetime.strftime("%H-%M-%S-%f"))
        with open(f'logs/{date}/output_for_Negomi_{timed}.txt') as f:
            f.write(dumps(conversation_history))
        conversation_history = []
        return False
    # Add the new user message to the conversation history
    conversation_history.append({'role': 'user', 'content': user_message})
    # print(conversation_history)
    
    response = ollama.chat(model='Negomi', messages=conversation_history)
    
    text = response['message']['content']
    conversation_history.append({'role': 'assistant', 'content': text})
    return text

def generate(prompt) ->str:
    response = ollama.generate("NegomiX",prompt)
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
    print(conversation_history)
