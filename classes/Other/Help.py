from modules.Nexon import *

class descriptionNone:
    def __init__(self) -> None:
        value = None
    def __str__(self):
        return "No description Provided"

home_embed = info_embed(
    "Hello, I am Negomi Made By my master/papa Mahiro\n\
    What Can I do you ask? Well a lot of stuff.\n\n\
    To get started Check Select List Below!", 
    title="🏠 Home"
)
homeAdmin_embed = info_embed(
    "Welcome Admin! Here's' stuff that only shows for admins.\n\n\
    To get started Check Select List Below!", 
    title="🏠 Admin Home"
)

def embed_builder_static(title: str, description: str, commands: dict):
    embed = info_embed(description=description, title=title)
    for name, description in commands.items():
        embed.add_field(name=f"`{name}`", value=f"{description}")
    return embed

class HelpSelectAdmin(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.options = [
            SelectOption(label="Home", value="home", emoji="🏠", default=True),
            SelectOption(label="Setups", value="setup", emoji="🔮"),
            SelectOption(label="Plugins Manager", value="plugin", emoji="🛠️"),
            SelectOption(label="Other", value="other", emoji="🗿")
        ]
        self.select = ui.Select(placeholder="Choose an option...", options=self.options)
        self.select.callback = self.callback
        self.add_item(self.select)

    async def callback(self, ctx: Interaction):
        selected_value = self.select.values[0]
        embeds = {
            "home": home_embed,
            "setup": embed_builder_static(
                "🔮 Setups",
                "Here are the setup commands:",
                {"auto role setup": "Setup auto role for members and bots",
                "mod manager setup": "Setup the Moderator Manager",
                "welcome setup": "Setup the Welcoming Message, check '/welcome how' to know how to set it up",
                "voice-setup": "Setup temp voice",
                }
            ),
            "plugin": embed_builder_static(
                "🛠️ Plugins Manager",
                "Here are the plugin manager commands:",
                {"feature enable": "Enable a feature in your server",
                 "feature disable": "Disable a feature in your server"}
            ),
            "other": embed_builder_static(
                "🗿 Other",
                "Here are other commands:",
                {"debug": "Displays detailed debug information about the bot. (Not Really Admin Only Command)"}
            )
        }
        embed = embeds.get(selected_value, home_embed)
        await ctx.response.edit_message(embed=embed, view=self)

class HelpSelect(ui.View):
    def __init__(self, admin: bool = False):
        super().__init__(timeout=None)
        self.options = [
            SelectOption(label="Home", value="home", emoji="🏠", default=True),
            SelectOption(label="Role", value="role", emoji="👥"),
            SelectOption(label="Temp Voice", value="temp", emoji="🎤"),
            SelectOption(label="Groups", value="groups", emoji="💀"),
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
            "home": home_embed,
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
                 "voice invite": "Invite a member to Voice chat,",
                 "Invite Voice": "Invite a member to Voice chat, (Shows when right click on user)"
                 }
            ),
            "groups": embed_builder_static(
                "💀 Groups",
                "Here are the group commands:",
                {"group create": "Create a group (AKA Text Channels) For you and your friends",
                 "group edit": "Edit this group's details",
                 "group delete": "Delete a group",
                 "group add": "Add a member to this group",
                 "group kick": "Remove a member from this group",
                 "group transfer": "Transfer group ownership to another member in this group",
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
