import datetime
import os
from typing import Dict, List, NewType
import httpx
import ollama
from rich import print
from json import dumps, loads
from .logger import logger
from rich.progress import Progress, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn
from .config import ip
from pathlib import Path

CheckerClient = ollama.Client(ip, timeout = 1)
client = ollama.Client(ip)
offline = NewType("offline", False)
online = NewType("online", True)

def isClientOnline():
    try:
        list = CheckerClient.list()
        return online
    except: return offline

async def download_model(model_name: str) -> None:
    """
    Download an Ollama model with a progress bar.
    
    Args:
        model_name (str): Name of the model to download
    """
    with Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=40),
        DownloadColumn(),
        TransferSpeedColumn(),
    ) as progress:
        current_digest, tasks = '', {}
        
        for status in client.pull(model_name, stream=True):
            digest = status.get('digest', '')
            
            if not digest:
                logger.info(status.get('status'))
                continue
                
            if digest != current_digest and current_digest in tasks:
                progress.update(tasks[current_digest], completed=progress.tasks[tasks[current_digest]].total)
                
            if digest not in tasks and (total := status.get('total')):
                task_id = progress.add_task(f"[cyan]Pulling {digest[7:19]}", total=total)
                tasks[digest] = task_id
                
            if completed := status.get('completed'):
                progress.update(tasks[digest], completed=completed)
                
            current_digest = digest

class ConversationManager:
    def __init__(self, model: str = "Negomi"):
        self.conversation_histories = {}
        self.history_file = Path("Data/Features/AI/history.json")
        self.summary_threshold = 20
        self.keep_recent = 8
        self.model = model
        self.load_histories()

    def load_histories(self):
        """Load conversation histories from JSON file."""
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.conversation_histories = loads(f.read())
                logger.info("Successfully loaded conversation histories")
        except Exception as e:
            logger.error(f"Error loading conversation histories: {e}")
            self.conversation_histories = {}

    def save_histories(self):
        """Save conversation histories to JSON file."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                f.write(dumps(self.conversation_histories, indent=4, ensure_ascii=False))
        except Exception as e:
            logger.error(f"Error saving conversation histories: {e}")

    def archive_conversation(self, user_id):
        """Archive a conversation to a dated log file."""
        if user_id in self.conversation_histories:
            current_datetime = datetime.datetime.now()
            date = current_datetime.strftime("%Y-%m-%d")
            timed = current_datetime.strftime("%H-%M-%S-%f")
            
            log_path = Path(f"logs/{date}")
            log_path.mkdir(parents=True, exist_ok=True)
            
            with open(log_path / f"output_for_{self.model}_{timed}.json", "w", encoding='utf-8') as f:
                f.write(dumps(self.conversation_histories[user_id], indent=4, ensure_ascii=False))

    def summarize_conversation(self, conversation_history):
        """
        Create a concise summary of the conversation while maintaining system messages
        and keeping recent context.
        """
        # Separate system messages from other messages
        system_messages = [msg for msg in conversation_history if msg['role'] == 'system']
        non_system_messages = [msg for msg in conversation_history if msg['role'] != 'system']
        
        # If we don't have enough messages to summarize, return original
        if len(non_system_messages) <= self.keep_recent:
            return conversation_history
        
        # Get messages to summarize (excluding recent ones)
        messages_to_summarize = non_system_messages[:-self.keep_recent]
        recent_messages = non_system_messages[-self.keep_recent:]
        
        prompt = """Summarize this conversation naturally, focusing on key information and context that would be important for future responses. Create a concise internal summary that captures the main points, decisions, and context of the conversation.

Do not include any meta-commentary about the summary itself or formatting instructions.

Previous conversation:
"""
        
        # Add messages to the prompt
        for msg in messages_to_summarize:
            if msg['role'] == 'user':
                content = msg['content'].replace('Mahiro: ', '')  # Remove prefix for cleaner summary
                prompt += f"User: {content}\n"
            else:
                prompt += f"{self.model}: {msg['content']}\n"

        try:
            # Get the summary and ensure it doesn't leak internal details
            summary = generate(prompt)
            
            # Create new summary message with clear internal marker
            summary_message = {
                'role': 'system',
                'content': f"Internal context: {summary}"
            }
            
            # Combine everything in the right order:
            # 1. Original system messages
            # 2. New summary as internal context
            # 3. Recent messages
            final_history = system_messages + [summary_message] + recent_messages
            
            # Verify no summary meta-commentary is present in messages
            for msg in final_history:
                if msg['role'] == 'assistant':
                    # Remove any accidental summary formatting or meta-commentary
                    content = msg['content']
                    content = content.replace("**Main Topics and Flow of Discussion:**", "")
                    content = content.replace("**Important Context and Personality Elements:**", "")
                    content = content.replace("Feel free to add or modify anything you'd like!", "")
                    msg['content'] = content
            
            return final_history
        except httpx.ConnectTimeout as e:
            raise e
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return conversation_history

    def get_response(self, channel_id: str, user: str, user_message: str, type: str = "public"):
        """Process user message and get AI response with improved context handling."""
        if user == "HackedMahiro Hachiro":
            user = "Mahiro"
        if channel_id not in self.conversation_histories:
            self.conversation_histories[channel_id] = []

        conversation_history = self.conversation_histories[channel_id]

        if user_message.startswith("/clear"):
            self.archive_conversation(channel_id)
            # Keep only the initial system message when clearing
            self.conversation_histories[channel_id] = [msg for msg in conversation_history if msg['role'] == 'system'][:1]
            self.save_histories()
            return False

        # Add user message to history
        conversation_history.append({'role': 'user', 'content': f"{user}: {user_message}"})
        non_system_messages = [msg for msg in conversation_history if msg['role'] != 'system']
        # Summarize if needed
        try:
            if len(non_system_messages) > self.summary_threshold:
                conversation_history = self.summarize_conversation(conversation_history)
                self.conversation_histories[channel_id] = conversation_history
        except httpx.ConnectTimeout as e:
            logger.error(f"Error in ollama.chat: {e}")
            return offline

        # Generate response using Ollama
        try:
            response = client.chat(
                model=self.model,
                messages=conversation_history,
                options={
                    'temperature': 0.9,  # High creativity but still somewhat controlled
                    'top_p': 0.85,       # Keeps responses coherent while allowing some diversity
                    'frequency_penalty': 0.4,  # Reduces word/phrase repetition
                    'presence_penalty': 0.6  # Encourages the bot to introduce new ideas
                }
            )
            text = response.get('message', {}).get('content', "Error: No response generated.")
        except httpx.ConnectTimeout as e:
            logger.error(f"Error in ollama.chat: {e}")
            return offline
        except Exception as e:
            logger.error(f"Error in ollama.chat: {e}")
            text = "Sorry, I encountered an issue generating a response."

        # Add cleaned response to history if valid
        if text and text != "Error: No response generated.":
            conversation_history.append({'role': 'assistant', 'content': text})
            self.save_histories()

        return text

def generate(prompt, model: str="Negomi") -> str:
    try:
        response = client.generate(model, prompt)
        return response["response"]
    except Exception:
        return offline

if __name__ == '__main__':
    os.system("cls")
    conversation_manager = ConversationManager()
    while True:
        text = input("--> ")
        print("Mahiro: " + text)
        if text.startswith("/bye"):
            break
        conversation_manager.get_response("test_user", "Mahiro", text)
        print("\n")