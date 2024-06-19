import nextcord
from nextcord.ext import commands
from Lib.Side import *
import os
import Lib.Data as Data
from nextcord import Interaction as init
import logging
from Lib.richer import *
from datetime import datetime
import threading
import time

clear()
if Logger_Enabled:
    current_datetime = datetime.now()
    date = str(current_datetime.strftime("%Y-%m-%d"))
    timed = str(current_datetime.strftime("%H-%M-%S-%f"))
    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    os.makedirs(f"logs/{date}" ,exist_ok=True)
    # Create a file handler
    handler = logging.FileHandler(f'logs/{date}/output_{timed}.txt')
    handler.setLevel(logging.INFO)
    # formatter
    formatter = logging.Formatter(Format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)


intents = nextcord.Intents.all()
client = commands.Bot(command_prefix=prefix, intents=intents)
# logging.basicConfig(filename=f'loggin/{datetime.datetime()}', level=logging.INFO)



#On Bot Start
@client.event
async def on_ready():
    await client.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.watching, name=f"Over {len(client.guilds)} Servers"))
    # clear()
    print(Rule(f'{client.user.display_name}  Is Online',style="bold green"))
    if send_to_owner_enabled:
        user = client.get_user(owner_id)
        channel = await user.create_dm()
        await channel.send("Running ✅",embeds=[
            debug_embed("Bot is Online"),
            info_embed("Bot is Online"),
            warn_embed("Bot is Online"),
            error_embed("Bot is Online")])
#End

#Classes
initial_extension = []
core_extension = []

for filename in os.listdir("./classes"):
    if filename.endswith(".py"):
        if "." in filename[:-3]: raise Exception("You can't have a dot in the class name")
        initial_extension.append("classes." + filename[:-3])
for filename in os.listdir("./classes/core"):
    if filename.endswith(".py"):
        if "." in filename[:-3]: raise Exception("You can't have a dot in the core name")
        core_extension.append("classes.core." + filename[:-3])

print(f"These are All the Core {core_extension}\nand These All The Extension {initial_extension} ")


# client.unload_extension("Lib.fun")

if __name__ == '__main__':
    for extension in core_extension:
        client.load_extension(extension)
    for extension in initial_extension:
        client.load_extension(extension)
try:
    client.run(token)
except nextcord.errors.LoginFailure:
    print(Panel(f"""Here's the step to check if you Have put your Token right:
    1- Add your token in the config file in {config_path}
    2- see if it didn't change back to "Your Bot Token" and if is change it to your token
    3- Reset your token in https://discord.com/developers/applications""",
    title="Invalid Token",style="bold red",border_style="bold red"))