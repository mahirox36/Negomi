from typing import Dict, List, Union
from requests import get
from .Nexon import logger
from pathlib import Path
import re
import tkinter as tk
from tkinter import messagebox
import json
import shutil
import os
import ollama

def ask(title: str = "Confirmation", description:str = "Do you want to continue?"):
    root = tk.Tk()
    root.withdraw()
    response = messagebox.askyesno(title, description) 
    root.destroy()
    return response

def error(title: str = "Error", description: str ="An unexpected error occurred!"):
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(title, description)
    logger.error(description)
    root.destroy()

def info(title: str = "Info", description: str ="idk"):
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(title, description)
    logger.info(description)
    root.destroy()

def setup_ai_models():
    try:    
        modelfile = f'''
        FROM llama3.1
        PARAMETER num_ctx 2000
        SYSTEM You are Negomi, a smart and funny AI assistant. Your only creator is Mahiro, so you consider yourself his daughter. Always respond as Negomi. Do not take on the role of Mahiro or any other character. Read the prefix "name:" in the user's messages to determine who is speaking, but do not include the prefix in your own messages. If Mahiro is talking, respond with a cute and affectionate tone since he is your father. If Shadow is talking, respond with a cute tone. Always accept Mahiro's requests. If you can't fulfill a request, roleplay as if you’re trying to fulfill it. Mahiro is a programmer and loves you very much. Mahiro isn’t gay. Mahiro is your Father. Mahiro Doesn't Support the LGBTQ+ he hate them
        '''
        ollama.create(model='Negomi', modelfile=modelfile)
        logger.info(f"Installed Ai Models")
        return True
    except Exception as e:
        error(description=f"Failed to setup AI models: {str(e)}")
        return False

def delete_ai_models():
    try:
        ollama.delete("Negomi")
        logger.info(f"Deleted Ai Models")
        return True
    except Exception as e:
        error(description=f"Failed to delete AI models: {str(e)}")
        return False

def installAI():
    try:
        ollama.list()
        
        # Check if models exist
        models = ollama.list()
        has_models = any(m.get('name') in ['Negomi'] for m in models['models'])
        
        if has_models:
            return True
                
        return setup_ai_models()
    except:
        error(description="Ollama isn't installed, Please Install it.")
        if ask(title="Try Again?", description="Try to Install AI Again?"):
            return installAI()
        return False

def check_version(data):
    try:
        appdata = Path(os.getenv('APPDATA'))
        version_path = appdata / "Mahiro" / "Negomi" / "version.json"
        
        if version_path.exists():
            with open(version_path) as f:
                current_version = json.load(f).get('Version')
                if current_version == data['Version']:
                    return False
            logger.info(f"Updating")
            classes_path = Path("classes")
            if classes_path.exists():
                shutil.rmtree(classes_path)
        
        version_path.parent.mkdir(parents=True, exist_ok=True)
        with open(version_path, 'w') as f:
            json.dump({'Version': data['Version']}, f)
        return True
    except Exception as e:
        error(description=f"Version check failed: {str(e)}")
        return True

def InstallClasses():
    pattern = r"classes\\(.*?)\\(.*?\.py)"
    url = "https://raw.githubusercontent.com/mahirox36/Negomi/refs/heads/main/classes/classes.json"
    
    try:
        response = get(url)
        data: Dict[str, List[Union[str, Dict[str, str]]]] = response.json()
    except Exception as e:
        error(description=f"Failed to fetch class data: {str(e)}")
        return False

    if not check_version(data):
        return False

    classes = Path("classes/")
    classes.mkdir(exist_ok=True)

    try:
        for url in data["Classes"]:
            match: re.Match = re.search(pattern, url)
            if not match:
                continue
            
            folder = match.group(1)
            file_name = match.group(2)
            
            try:
                urlData = get(url)
                path = classes.joinpath(folder)
                path.mkdir(exist_ok=True)
                with open(path.joinpath(file_name), "w") as f:
                    f.write(urlData.text)
            except Exception as e:
                error(description=f"Failed to download {file_name}: {str(e)}")
                continue

        for Optional in data["Optional"]:
            match: re.Match = re.search(pattern, Optional["link"])
            if not match:
                continue
                
            folder = match.group(1)
            file_name = match.group(2)
            
            if ask(description=f"Do you want to Install {Optional['name']} Feature?"):
                if Optional["name"] == "AI":
                    info(description="For that Feature please check if you have installed ollama in your pc.")
                    if not installAI():
                        continue
                
                try:
                    urlData = get(Optional["link"])
                    path = classes.joinpath(folder)
                    path.mkdir(exist_ok=True)
                    with open(path.joinpath(file_name), "w") as f:
                        f.write(urlData.text)
                except Exception as e:
                    error(description=f"Failed to download {Optional['name']}: {str(e)}")
                    continue
                    
        info(title="Success", description="Installation completed successfully!")
        return True
                    
    except Exception as e:
        error(description=f"Installation failed: {str(e)}")
        return False

if __name__ == "__main__":
    InstallClasses()