from modules.Nexon import *
from requests import get
import random

class Other(commands.Cog):
    def __init__(self, client:commands.Bot):
        self.client = client
        self.eight_ball_responses = [
            "It is certain.","It is decidedly so.","Without a doubt.",
            "Yes – definitely.","You may rely on it.","As I see it, yes.",
            "Most likely.","Outlook good.","Yes.","Signs point to yes.",
            "Reply hazy, try again.","Ask again later.","Better not tell you now.",
            "Cannot predict now.","Concentrate and ask again.","Don't count on it.",
            "My reply is no.","My sources say no.","Outlook not so good.",
            "Very doubtful.","You are Gay","This question is Gay",
            #JOKE!!!!!!!!
            "No","Hell Nah", "I don't care about your question, I am The Best",
            "Nuh Uh","Yea Uh","Bling-bang-bang, bling-bang-bang-born","Ni-",
            "UwU","OwO",":3"
        ]
    @slash_command("uwu",description="What Does this thing do?")
    async def uwu2(self,ctx:init):
        await ctx.send("UwU")
    @slash_command(name="joke",description="Get a Random Joke")
    async def joke(self,ctx:init):
        joke= get("https://official-joke-api.appspot.com/random_joke").json()
        phrase      = joke["setup"]
        punchline   = joke["punchline"]
        ID          = joke["id"]
        await ctx.send(embed=Embed.Info(title=phrase,description=f"||{punchline}||",footer=f"id: {ID}"))

    @slash_command(name="meme",description="Get a random Meme")
    async def meme(self,ctx:init):
        response = get("https://meme-api.com/gimme")
        meme_data = response.json()

        title = meme_data['title']
        image_url = meme_data['url']

        embed = Embed(title=title, colour=colors.Info.value)
        embed.set_image(url=image_url)

        await ctx.send(embed=embed)
    
    @slash_command(name="roll",description="Roll a Dice")
    async def roll(self,ctx:init, max_num:int=6,min_num:int=1):
        await ctx.send(random.randint(min_num,max_num))
    
    @slash_command(name="8ball", description="Ask the magic 8-ball a question")
    async def eight_ball(self,ctx: init, question: str):
        response = random.choice(self.eight_ball_responses)
        await ctx.send(embed=Embed.Info(title=f"🎱 **Question:** {question}",
                           description=f"**Answer:** {response}"))
        
        
    @slash_command(name="server-info",description="Gives This server Information")
    async def server_info(self,interaction:init):
        name = interaction.guild.name
        description = interaction.guild.description
        idd = str(interaction.guild.id)
        region = str(interaction.guild.region)
        memberCount = str(interaction.guild.member_count)
        icon = str(interaction.guild.icon)
    
        embed = Embed.Info(
            title=name + " Info",
            description=description,
        )
        embed.set_thumbnail(url=icon)
        embed.add_field(name= "🆔 ID", value=idd)
        embed.add_field(name= "👑 Owner", value=f"{interaction.guild.owner.mention}")
        embed.add_field(name= "👥 Members", value=memberCount)
        embed.add_field(name=f"💬 Channels ({len(interaction.guild.channels)})",value=f"**{len(interaction.guild.text_channels)}** Text|**{len(interaction.guild.voice_channels)}** Voice")
        embed.add_field(name= "🌍 Region", value=region)
        embed.add_field(name= "🔐 Roles",value=len(interaction.guild.roles))
        await interaction.send(embed=embed,ephemeral=True)
        
    @slash_command(name="ping",description="Ping the Bot")
    async def ping(self,ctx:init):
        latency = round(self.client.latency * 1000)
        await ctx.response.send_message(f"Pong! Latency is `{latency}ms`.",ephemeral=True)
    @slash_command(name="website", description="The Bot's Website.")
    async def website(self, ctx: init):
        link = f"http://{get("https://api64.ipify.org?format=text").text}:25400" if dashboard_domain == "" else dashboard_domain
        button = Button(label="Go to Website", url=link, style=ButtonStyle.primary)

        # Create a view and add the button
        view = View()
        view.add_item(button)

        # Send the button in response to the command
        await ctx.response.send_message(embed=Embed.Info("Click the button below to visit the website:","Negomi Website"), view=view,ephemeral=True)
    
    

def setup(client):
    client.add_cog(Other(client))