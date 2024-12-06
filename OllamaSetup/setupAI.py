import ollama

# Prompt the user to choose between 'Delete' or 'Create'
q = input("Delete, Create or replace?\n> ")

# If the user inputs 'Create' (or similar starting letter)
def create():
    max_tokens = 2000

    # Open and read the 'system' file, replacing newline characters with spaces
    with open("OllamaSetup/system") as f:
        system_content = f.read().replace("\n", " ")
        
    # Create the modelfile content for 'NegomiX'
    modelfile = f'''
    FROM llama3.1
    PARAMETER num_ctx {max_tokens}
    SYSTEM {system_content}
    '''
    # Create the model using Ollama
    ollama.create(model='NegomiX', modelfile=modelfile)
    
    # Open and read the 'systemNormalTalk' file, replacing newline characters with spaces
    with open("OllamaSetup/systemNormalTalk") as f:
        system_content = f.read().replace("\n", " ")
        
    # Create the modelfile content for 'Negomi'
    modelfile = f'''
    FROM llama3.1
    PARAMETER num_ctx {max_tokens}
    SYSTEM {system_content}
    '''
    # Create the model using Ollama
    ollama.create(model='Negomi', modelfile=modelfile)

def delete():
    try:
        X1= ollama.delete("NegomiX")
        X2= ollama.delete("Negomi")
        return {1:X1,2:X2}   
    except:
        return False

if q.lower().startswith("c"):
    # Define the maximum number of tokens (characters) to output
    create()

# If the user inputs 'Delete' (or similar starting letter)
elif q.lower().startswith("d"):
    # Delete the models 'NegomiX' and 'Negomi' using Ollama
    delete()
    
elif q.lower().startswith("r"):
    delete()
    create()
