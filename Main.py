from nextcord import AppInfo, TeamMember
from rich.console import Console
from rich.traceback import install
from Lib.richer import *
from Lib.Logger import *
install()
try:
    import nextcord
    from nextcord.ext import commands, ipc
    from requests import request
    from Lib.Side import *
    from rich import print
    import os
    from nextcord import Interaction as init
    from datetime import datetime
    import threading
    import time

    intents = nextcord.Intents.all()
    client = commands.Bot(command_prefix=prefix, intents=intents)
    BotInfo: AppInfo = None
    global Bot
    Bot = client

    clear()

    #On Bot Start
    @client.event
    async def on_ready():
        await client.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.watching, name=Presence))
        print(Rule(f'{client.user.display_name}  Is Online',style="bold green")) # type: ignore
        if send_to_owner_enabled:
            BotInfo: AppInfo = await client.application_info()
            if BotInfo.owner.name.startswith("team"):
                user =  client.get_user(BotInfo.team.owner.id)
                channel =await user.create_dm()
            else:
                channel =await BotInfo.owner.create_dm()
            await channel.send("Running ✅",embeds=[
                info_embed("Bot is Online")])
        await client.sync_all_application_commands()
    ipc = ipc.Server(bot= client, secret_key=IpcPassword)
    @client.event
    async def on_ipc_ready():
        print("Ipc is ready.")
    @client.event
    async def on_ipc_error(endpoint, error):
        """Called upon an error being raised within an IPC route"""
        print(endpoint, "raised", error)
    #End

    #Classes
    def get_classes(folder="./classes", replace=True) -> List[str]:
        folder_prefix = folder.strip("./").replace("\\", ".").replace("/", ".") + "." if replace else folder.strip("./").replace("\\", ".").replace("/", ".")
        initial_extension = []

        for root, _, files in os.walk(folder):
            for file in files:
                if file.endswith(".py"):
                    if "__pycache__" in root or "Working on Progress" in root:
                        continue
                    if "." in file[:-3]:
                        raise Exception("You can't have a dot in the class name")
                    if DisableAiClass and file[:-3] == "AI":
                        continue
                    relative_path = os.path.relpath(os.path.join(root, file), folder).replace("\\", ".").replace("/", ".")
                    initial_extension.append(folder_prefix + relative_path[:-3])

        return initial_extension
        
    initial_extension = get_classes()
    print(f"Classes: {initial_extension}")

    for extension in initial_extension:
        LOGGER.info(f"Loading Class: {extension}")
        if (extension == "classes.Welcome") and (Welcome_enabled == False):
            LOGGER.info(f"Failed to load Class: {extension}, Because Welcome Class isn't enabled")
            continue
        client.load_extension(extension)
        LOGGER.info(f"Loaded Class: {extension}")
    
    if __name__ == '__main__':
        try:
            # ipc.start()
            client.run(token)
        except nextcord.errors.LoginFailure:
            LOGGER.error("Failed to Login")
            print(Panel(f"""Here's the step to check if you Have put your Token right:
            1- Add your token in the config file in `.secrets/config.ini`
            2- see if it didn't change back to "Your Bot Token" and if is change it to your token
            3- Reset your token in https://discord.com/developers/applications""",
            title="Invalid Token",style="bold red",border_style="bold red"))
except Exception as e:
    LOGGER.error(e)
    console.print_exception()