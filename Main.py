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
        await channel.send("Running ✅")
#End

#Classes
initial_extension = []

for filename in os.listdir("./classes"):
    if filename.endswith(".py"):
        initial_extension.append("classes." + filename[:-3])

print(f"These All The Extension {initial_extension} ")
@client.slash_command("reload_classes")
async def reload_classes(ctx:init):
    await ctx.response.defer(ephemeral=True)
    """Reload all Classes
        ~~~~~~~"""
    await Data.check_owner_permission(ctx)
    temp = 0
    await ctx.response.send_message("Reloading...",ephemeral=True)
    a = await ctx.channel.send("```Reloading...```")
    for i in list(client.extensions):
        client.reload_extension(i)
        fv = a.content.replace(".```","")
        temp += 1
    fv = a.content.replace(".```","")
    await a.edit(fv + f"\n\nReloaded {temp} Classes!```")
    # clear()
    print('Your Bot Is Reloaded!\nWe have logged in as {0.user}'.format(client))
    print(line)


@client.slash_command("list_classes")
async def list_classes(ctx:init):
    await ctx.response.defer(ephemeral=True)
    await Data.check_owner_permission(ctx)
    temp = 0
    a = "```\n"
    for i in list(client.extensions):
        a += str(i + "\n")
        temp += 1
    a += f"\n{temp} Classes!```"
    await ctx.send(a)


# client.unload_extension("Lib.fun")

if __name__ == '__main__':
    for extension in initial_extension:
        client.load_extension(extension)

client.run(token)