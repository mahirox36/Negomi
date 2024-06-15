import nextcord
from nextcord.ext import commands
from Lib.Side import *
import os
import Lib.Data as Data
from nextcord import Interaction as init
import logging
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
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


intents = nextcord.Intents.all()
client = commands.Bot(command_prefix=prefix, intents=intents)
# logging.basicConfig(filename=f'loggin/{datetime.datetime()}', level=logging.INFO)


Data.owner_id = 829806976702873621

#On Bot Start
@client.event
async def on_ready():
    await client.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.watching, name=f"Over {len(client.guilds)} Servers"))
    # clear()
    print('Your Bot Is Ready!\nWe have logged in as {0.user}'.format(client))
    print(line)

    user = client.get_user(owner_id)
    channel = await user.create_dm()
    await channel.send("Running ✅")
#End

#Cogs
initial_extension = []

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        initial_extension.append("cogs." + filename[:-3])

print(f"These All The Extension {initial_extension} ")
@client.slash_command("reload_cogs")
async def reload_cogs(ctx:init):
    await ctx.response.defer(ephemeral=True)
    """Reload all cogs
        ~~~~~~~"""
    await Data.check_owner_persmsion(ctx)
    temp = 0
    await ctx.response.send_message("Reloading...",ephemeral=True)
    a = await ctx.channel.send("```Reloading...```")
    for i in list(client.extensions):
        client.reload_extension(i)
        fv = a.content.replace(".```","")
        temp += 1
    fv = a.content.replace(".```","")
    await a.edit(fv + f"\n\nReloaded {temp} Cogs!```")
    # clear()
    print('Your Bot Is Reloaded!\nWe have logged in as {0.user}'.format(client))
    print(line)


@client.slash_command("list_cogs")
async def list_cogs(ctx:init):
    await ctx.response.defer(ephemeral=True)
    await Data.check_owner_persmsion(ctx)
    temp = 0
    a = "```\n"
    for i in list(client.extensions):
        a += str(i + "\n")
        temp += 1
    a += f"\n{temp} Cogs!```"
    await ctx.send(a)


def run_test():
    # Replace with the path to your test.py file
    thread = threading.current_thread()
    print(f"Thread started by {thread.name}")
    # Replace with the path to your test.py file
    print(f"Thread finished by {thread.name}")
thread = threading.Thread(target=run_test, name="Test Thread")
# thread.start()
client.unload_extension("Lib.fun")

if __name__ == '__main__':
    for extension in initial_extension:
        client.load_extension(extension)
# else:
    # # clear()
    # print("you need to run checkversion.py")
    # print("But that's Alright")
    # time.sleep(1)
    # for extension in initial_extension:
    #     client.load_extension(extension)


client.run(token)