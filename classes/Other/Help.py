from modules.Nexon import *

class descriptionNone:
    def __init__(self) -> None:
        value = None
    def __str__(self):
        return "No description Provided"

home_embed = Embed.Info(
    "**⚠️WARNING⚠️**\n\
    This Command is Outdated please visit the website by using command`/website` for realtime commands,\n\n\
    Hello, I am Negomi Made By my master/papa Mahiro\n\
    What Can I do you ask? Well a lot of stuff.\n\n\
    To get started Check Select List Below!", 
    title="🏠 Home"
)
homeAdmin_embed = Embed.Info(
    "**⚠️WARNING⚠️**\n\
    This Command is Outdated please visit the website by using command`/website` for realtime commands,\n\n\
    Welcome Admin! Here's' stuff that only shows for admins.\n\n\
    To get started Check Select List Below!", 
    title="🏠 Admin Home"
)

def embed_builder_static(title: str, description: str, commands: dict):
    embed = Embed.Info(description=description, title=title)
    for name, description in commands.items():
        embed.add_field(name=f"`{name}`", value=f"{description}")
    return embed

class HelpSelectAdmin(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.options = [
            SelectOption(label="Setups", value="setup", emoji="🔮"),
            SelectOption(label="Plugins Manager", value="plugin", emoji="🛠️"),
            SelectOption(label="Moderator Manager", value="mod", emoji="💀"),
            SelectOption(label="Backup", value="backup", emoji="💾"),
            SelectOption(label="Other", value="other", emoji="🗿")
        ]
        self.select = ui.Select(placeholder="Choose an option...", options=self.options)
        self.select.callback = self.callback
        self.add_item(self.select)

    async def callback(self, ctx: Interaction):
        selected_value = self.select.values[0]
        embeds = {
            "setup": embed_builder_static(
                "🔮 Setups",
                "Here are the setup commands:",
                {"auto role setup": "Setup auto role for members and bots",
                "mod manager setup": "Setup the Moderator Manager",
                "welcome setup": "Setup the Welcoming Message, check /welcome how to know how to set it up",
                "voice-setup": "Setup temp voice",
                }
            ),
            "plugin": embed_builder_static(
                "🛠️ Plugins Manager",
                "Here are the plugin manager commands:",
                {"feature enable": "Enable a feature in your server",
                 "feature disable": "Disable a feature in your server"}
            ),
            "mod": embed_builder_static(
                "💀 Moderator Manager",
                "Here are the Moderator Manager commands:",
                {"mod manager add": "Add a Moderator",
                 "mod manager remove": "Remove a moderator",
                 "mod manager promote": "Promote a moderator to a higher role",
                 "mod manager demote": "Demote a moderator to a lower role",
                 "mod manager hacked": "Handle hacked moderator account",
                 "mod manager list": "List all moderators",
                 "mod manager info": "Get information about a moderator",
                 }
            ),
            "backup": embed_builder_static(
                "💾 Backup",
                "Here are the Backup commands:",
                {"backup export": "this will export Roles, Channels, and Bots Names",
                 "backup import": "This will import Roles, Channels, and Bots Names. You need to upload the file you made with export",
                 }
            ),
            "other": embed_builder_static(
                "🗿 Other",
                "Here are other commands:",
                {"debug": "Displays detailed debug information about the bot. (Not Really Admin Only Command)",
                "mode": "Change the mode of role creation"},
            )
        }
        embed = embeds.get(selected_value, home_embed)
        await ctx.response.edit_message(embed=embed, view=self)

class HelpSelect(ui.View):
    def __init__(self, admin: bool = False):
        super().__init__(timeout=None)
        self.options = [
            SelectOption(label="Role", value="role", emoji="👥"),
            SelectOption(label="Temp Voice", value="temp", emoji="🎤"),
            SelectOption(label="Other", value="other", emoji="⚙️")
        ]
        self.select = ui.Select(placeholder="Choose an option...", options=self.options)
        self.select.callback = self.callback
        self.add_item(self.select)
        if admin:
            self.adminButton = ui.Button(style=ButtonStyle.green, label="🧑‍💻 Admin")
            self.adminButton.callback = self.adminButtonCallback
            self.add_item(self.adminButton)

    async def callback(self, ctx: Interaction):
        selected_value = self.select.values[0]
        embeds = {
            "role": embed_builder_static(
                "👥 Role",
                "Here are the role commands:",
                {"role create": "Create a role for your self",
                 "role edit": "Edit your own role like the name or role or both!",
                 "role delete": "delete your own role",
                 "Role: Add User": "Add the role to a user, (Shows when right click on user)",
                 "Role: Remove User": "delete your own role, (Shows when right click on user)",
                 "role add": "Add the role to a user",
                 "role remove": "Remove the role from a user",
                 }
            ),
            "temp": embed_builder_static(
                "🎤 Temp Voice",
                "Here are the temp voice commands:",
                {"voice panel": "Bring the Control Panel for the TempVoice chat",
                 "voice invite": "Invite a member to Voice chat",
                 "voice ban": "Ban a user from your temporary voice channel",
                 "voice kick": "Kick a user from your temporary voice channel",
                 "Voice: Invite": "Invite a member to Voice chat, (Shows when right click on user)",
                 "Voice: Ban": "Ban a user from your temporary voice channel, (Shows when right click on user)",
                 "Voice: Kick": "Kick a user from your temporary voice channel, (Shows when right click on user)",
                 }
            ),
            "other": embed_builder_static(
                "⚙️ Other",
                "Here are other commands:",
                {"uwu": "What Does this thing do?",
                 "joke": "Get a Random Joke",
                 "meme": "Get a random Meme",
                 "roll": "Roll a Dice",
                 "8ball": "Ask the magic 8-ball a question",
                 "server-info": "Gives This server Information",
                 "ping": "Ping the Bot",
                 "debug": "Displays detailed debug information about the bot.",
                 }
            )
        }
        embed = embeds.get(selected_value, home_embed)
        await ctx.response.edit_message(embed=embed, view=self)

    async def adminButtonCallback(self, ctx: init):
        await ctx.response.edit_message(embed=homeAdmin_embed, view=HelpSelectAdmin())

class Help(commands.Cog):
    def __init__(self, client: Client):
        self.client = client

    @slash_command(name="help", description="Help command")
    async def help(self, ctx: init):
        global home_embed
        admin = ctx.user.guild_permissions.administrator
        view = HelpSelect(admin)
        await ctx.send(embed=home_embed, view=view, ephemeral=True)

def setup(client):
    client.add_cog(Help(client))
