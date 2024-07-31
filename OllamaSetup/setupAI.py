import ollama

# Prompt the user to choose between 'Delete' or 'Create'
q = input("Delete or Create?\n> ")

# If the user inputs 'Create' (or similar starting letter)
if q.lower().startswith("c"):
    # Define the maximum number of tokens (characters) to output
    max_tokens = 2000

    # Open and read the 'system' file, replacing newline characters with spaces
    with open("system") as f:
        system_content = f.read().replace("\n", " ")
        
    # Create the modelfile content for 'NegomiX'
    modelfile = f'''
    FROM llama3
    PARAMETER num_ctx {max_tokens}
    SYSTEM {system_content}
    '''
    # Create the model using Ollama
    ollama.create(model='NegomiX', modelfile=modelfile)
    
    # Open and read the 'systemNormalTalk' file, replacing newline characters with spaces
    with open("systemNormalTalk") as f:
        system_content = f.read().replace("\n", " ")
        
    # Create the modelfile content for 'Negomi'
    modelfile = f'''
    FROM llama3
    PARAMETER num_ctx {max_tokens}
    SYSTEM {system_content}
    '''
    # Create the model using Ollama
    ollama.create(model='Negomi', modelfile=modelfile)

# If the user inputs 'Delete' (or similar starting letter)
elif q.lower().startswith("d"):
    # Delete the models 'NegomiX' and 'Negomi' using Ollama
    ollama.delete("NegomiX")
    ollama.delete("Negomi")
