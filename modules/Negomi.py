import datetime
import os
from typing import Optional, Dict, Any
import httpx
import ollama
from rich import print
from json import dumps, loads
import logging
from nexon import utils
logger = logging.getLogger(__name__)
from aiofiles import open as aio_open
from rich.progress import Progress, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn
from .DiscordConfig import ip
from pathlib import Path
from .system_template import system_template

CheckerClient = ollama.Client(ip, timeout = 1)
client = ollama.AsyncClient(ip)
offline = False
online = True

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
        
        async for status in (await client.pull(model_name, stream=True)):
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
        self.summary_threshold = 30  # Number of messages before summarizing
        self.keep_recent = 12  # Keep more recent messages
        self.model = model
        self.memory_decay_rate = 0.95  # Rate at which old memories fade

    async def load_histories(self):
        """Load conversation histories from JSON file."""
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            
            if self.history_file.exists():
                async with aio_open(self.history_file, 'r', encoding='utf-8') as f:
                    self.conversation_histories = loads(await f.read())
                logger.info("Successfully loaded conversation histories")
        except Exception as e:
            logger.error(f"Error loading conversation histories: {e}")
            self.conversation_histories = {}

    async def save_histories(self):
        """Save conversation histories to JSON file."""
        try:
            async with aio_open(self.history_file, 'w', encoding='utf-8') as f:
                await f.write(dumps(self.conversation_histories, indent=4, ensure_ascii=False))
        except Exception as e:
            logger.error(f"Error saving conversation histories: {e}")

    async def archive_conversation(self, user_id):
        """Archive a conversation to a dated log file."""
        if user_id in self.conversation_histories:
            current_datetime = utils.utcnow()
            date = current_datetime.strftime("%Y-%m-%d")
            timed = current_datetime.strftime("%H-%M-%S-%f")
            
            log_path = Path(f"logs/{date}")
            log_path.mkdir(parents=True, exist_ok=True)

            async with aio_open(log_path / f"output_for_{self.model}_{timed}.json", "w", encoding='utf-8') as f:
                await f.write(dumps(self.conversation_histories[user_id], indent=4, ensure_ascii=False))

    async def summarize_conversation(self, conversation_history):
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
        
        # Weight messages by importance and recency
        weighted_messages = []
        for idx, msg in enumerate(messages_to_summarize):
            age_weight = self.memory_decay_rate ** (len(messages_to_summarize) - idx)
            importance = 1.0
            
            # Increase importance for emotional content
            if any(word in msg['content'].lower() for word in ['love', 'hate', 'angry', 'happy', 'sad']):
                importance *= 1.5
                
            # Increase importance for questions
            if '?' in msg['content']:
                importance *= 1.3
                
            weighted_messages.append((msg, age_weight * importance))
        
        # Sort by weight and select top messages
        weighted_messages.sort(key=lambda x: x[1], reverse=True)
        key_messages = [msg[0] for msg in weighted_messages[:min(5, len(weighted_messages))]]
        
        # Generate focused summary
        summary_prompt = "Create a concise summary focusing on key emotional moments, important decisions, and critical context. Include:\n"
        summary_prompt += "1. Main emotional themes\n2. Important decisions or agreements\n3. Key facts discussed\n\n"
        
        for msg in key_messages:
            summary_prompt += f"{msg['role']}: {msg['content']}\n"

        try:
            # Get the summary and ensure it doesn't leak internal details
            summary = await generate(summary_prompt)
            
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

    async def get_response(self, channel_id: str, user: str, user_message: str, type: str = "public", 
                    guild_info: Optional[dict] = None, personality_state: Optional[dict] = None, 
                    mommy_mode: bool = False):
        """Process user message and get AI response with emotional intelligence."""
        
        try:
            # Format system message with personality state
            if personality_state:
                core_traits = personality_state.get('core_traits', {})
                relationship = personality_state.get('relationship_dynamics', {}).get(str(user), {})
                current_mood = personality_state.get('current_mood', 'relaxed')
                
                # Emotional memory integration - include recent significant memories
                emotional_memory = personality_state.get('emotional_memory', [])
                memory_context = ""
                if emotional_memory:
                    memory_context = "\nRecent emotional memories:\n"
                    # Add up to 3 most recent emotional memories
                    for memory in emotional_memory[-3:]:
                        memory_context += f"- {memory.get('description', 'Interaction')} " \
                                         f"(Feeling: {memory.get('mood', 'neutral')})\n"
                
                # Format custom traits with emotional context
                custom_traits = f"Current mood: {current_mood}\n" \
                               f"Channel: {guild_info['channel'] if guild_info else 'DM'}\n" \
                               f"{memory_context}"
                
                # Create system message with personality parameters
                system_vars = {
                    'AI': 'Negomi',
                    'openness': core_traits.get('openness', 0.85),
                    'conscientiousness': core_traits.get('conscientiousness', 0.9),
                    'extraversion': core_traits.get('extraversion', 0.75),
                    'name': user,
                    'trust_level': relationship.get('trust', 0.5),
                    'custom_traits': custom_traits
                }
                
                formatted_system = system_template.format(**system_vars)
            else:
                formatted_system = system_template.format(
                    AI='Negomi',
                    openness=0.85,
                    conscientiousness=0.9,
                    extraversion=0.75,
                    name=user,
                    trust_level=0.5,
                    custom_traits=''
                )

            # Initialize conversation if needed
            if channel_id not in self.conversation_histories:
                self.conversation_histories[channel_id] = [
                    {'role': 'system', 'content': formatted_system}
                ]

            # Update system message with current personality state
            conversation_history = self.conversation_histories[channel_id]
            for msg in conversation_history:
                if msg['role'] == 'system':
                    msg['content'] = formatted_system
                    break

            # Add user message to history
            conversation_history.append({'role': 'user', 'content': f"{user}: {user_message}"})
            non_system_messages = [msg for msg in conversation_history if msg['role'] != 'system']
            
            # Summarize if needed
            try:
                if len(non_system_messages) > self.summary_threshold:
                    conversation_history = await self.summarize_conversation(conversation_history)
                    self.conversation_histories[channel_id] = conversation_history
            except httpx.ConnectTimeout as e:
                logger.error(f"Error in ollama.chat: {e}")
                return offline

            # Generate response using Ollama with personality-appropriate parameters
            try:
                # Adjust temperature based on personality traits
                temperature = 0.85
                if personality_state:
                    openness = personality_state.get('core_traits', {}).get('openness', 0.85)
                    extraversion = personality_state.get('core_traits', {}).get('extraversion', 0.75)
                    # Higher openness = slightly higher temperature (more creative)
                    # Higher extraversion = slightly higher temperature (more expressive)
                    temperature = min(1.0, 0.7 + (openness * 0.1) + (extraversion * 0.1))
                
                response = await client.chat(
                    model=self.model,
                    messages=conversation_history,
                    options={
                        'temperature': temperature,
                        'top_p': 0.9,
                        'frequency_penalty': 0.7,
                        'presence_penalty': 0.7,
                        'max_tokens': 150
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
                await self.save_histories()

            return text
        except Exception as e:
            logger.error(f"Error in get_response: {e}")
            return "An error occurred while processing the response."

async def generate(prompt, model: str="Negomi") -> str:
    try:
        response = await client.generate(model, prompt)
        return response["response"]
    except Exception:
        return "Error: Unable to generate response - service offline"

# if __name__ == '__main__':
#     os.system("cls")
#     conversation_manager = ConversationManager()
#     while True:
#         text = input("--> ")
#         print("Mahiro: " + text)
#         if text.startswith("/bye"):
#             break
#         conversation_manager.get_response("test_user", "Mahiro", text)
#         print("\n")