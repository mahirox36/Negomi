from modules.Nexon import *
import random
import ast
import math
import operator
from better_profanity import profanity
import aiohttp

class Other(commands.Cog):
    def __init__(self, client:commands.Bot):
        self.client = client
        self.session = aiohttp.ClientSession()  # Create a single session for reuse
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
            "Nuh Uh","Yea Uh","Bling-bang-bang, bling-bang-bang-born",
            "UwU","OwO",":3"
        ]
        self.jokes_links = ["https://official-joke-api.appspot.com/random_joke", #setup and punchline
                            "https://v2.jokeapi.dev/joke/Any?blacklistFlags=nsfw,religious,political,racist,sexist,explicit", #sometimes it's joke and sometimes it's setup and delivery
                            "https://api.chucknorris.io/jokes/random", # value is joke
                            "https://geek-jokes.sameerkumar.website/api" # it gives u string (that's the joke)
                            ]
    
    def cog_unload(self):
        # Ensure the session is closed when the cog is unloaded
        self.client.loop.create_task(self.session.close())

    @slash_command("fun",description="Fun Commands")
    async def fun(self,ctx:init):
        pass
    @slash_command("utils",description="Utils Commands")
    async def utils(self,ctx:init):
        pass
    
    @fun.subcommand("uwu",description="What Does this thing do?")
    async def uwu2(self,ctx:init):
        await ctx.send("UwU")
    @fun.subcommand(name="joke",description="Get a Random Joke")
    async def joke(self,ctx:init):
        await ctx.response.defer()
        joke_url = random.choice(self.jokes_links)
        async with self.session.get(joke_url) as response:
            joke = await response.json()
        if joke_url == self.jokes_links[0]:
            setup = joke['setup']
            punchline = joke['punchline']
            embed = Embed(title="Joke", description=f"## {setup}\n\n||{punchline}||", colour=int(colors.Info.value))
        elif joke_url == self.jokes_links[1]:
            if joke['type'] == 'single':
                embed = Embed(title="Joke", description=joke['joke'], colour=int(colors.Info.value))
            else:
                setup = joke['setup']
                delivery = joke['delivery']
                embed = Embed(title="Joke", description=f"## {setup}\n\n||{delivery}||", colour=int(colors.Info.value))
        elif joke_url == self.jokes_links[2]:
            embed = Embed(title="Joke", description=joke['value'], colour=int(colors.Info.value))
        elif joke_url == self.jokes_links[3]:
            embed = Embed(title="Joke", description=joke, colour=int(colors.Info.value))
        else:
            embed = Embed(title="Joke", description="No joke found!", colour=int(colors.Error.value))
        await ctx.send(embed=embed)

    @fun.subcommand(name="meme",description="Get a random Meme")
    async def meme(self,ctx:init):
        async with self.session.get("https://meme-api.com/gimme") as response:
            meme_data = await response.json()

        title = meme_data['title']
        image_url = meme_data['url']

        embed = Embed(title=title, colour=int(colors.Info.value))
        embed.set_image(url=image_url)

        await ctx.send(embed=embed)
    
    @fun.subcommand(name="roll",description="Roll a Dice")
    async def roll(self,ctx:init, max_num:int=6,min_num:int=1):
        await ctx.send(str(random.randint(min_num,max_num)))
    
    @fun.subcommand(name="8ball", description="Ask the magic 8-ball a question")
    async def eight_ball(self,ctx: init, question: str):
        if await self.check_profane_message(ctx, question):
            return
        response = random.choice(self.eight_ball_responses)
        await ctx.send(embed=Embed.Info(title=f"🎱 **Question:** {question}",
                           description=f"**Answer:** {response}"))
        
    @fun.subcommand(name="coin-flip", description="Flip a coin")
    async def coinflip(self, ctx: init):
        result = random.choice(["Heads", "Tails"])
        await ctx.send(embed=Embed.Info(title="Coin Flip", description=f"🪙 The coin landed on **{result}**!"))

    @fun.subcommand(name="choose", description="Choose between multiple options split by commas")
    async def choose(self, ctx: init, options: str):
        if await self.check_profane_message(ctx, options):
            return
        choices = [x.strip() for x in options.split(",")]
        if len(choices) < 2:
            return await ctx.send("Please provide at least 2 options separated by commas!", ephemeral=True)
        choice = random.choice(choices)
        await ctx.send(embed=Embed.Info(title="Choice", description=f"I choose: **{choice}**"))

    @fun.subcommand(name="reverse", description="Reverse some text")
    async def reverse(self, ctx: init, text: str):
        if await self.check_profane_message(ctx, text):
            return
        await ctx.send(embed=Embed.Info(title="Reversed Text", description=text[::-1]))

    @fun.subcommand(name="say", description="Make the bot say something")
    async def say(self, ctx: init, message: str):
        if await self.check_profane_message(ctx, message):
            return
        await ctx.send(message)

    async def check_profane_message(self, ctx: Interaction, message: str):
        if profanity.contains_profanity(message):
            await ctx.send("Profanity is not allowed! i am going to report to my dad!", ephemeral=True)
            if self.client.owner_id is not None:
                user = self.client.get_user(self.client.owner_id)
                if user:
                    channel = await user.create_dm()
                    await channel.send(f"Profanity detected in {ctx.guild.id if ctx.guild else "DM"} in channel {ctx.channel.id if ctx.channel else "Unknown"} by {ctx.user.display_name if ctx.user else "Unknown"}: {message}")
            return True
        return False
        
    @utils.subcommand(name="server-info",description="Gives This server Information")
    async def server_info(self,interaction:init):
        if not interaction.guild:
            return await interaction.send("This command can only be used in a server.",ephemeral=True)
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
        embed.add_field(name= "💎 Boost Tier", value=str(interaction.guild.premium_tier))
        if interaction.guild.banner:
            embed.set_image(url=interaction.guild.banner.url)
        if interaction.guild.owner:
            embed.add_field(name= "👑 Owner", value=f"{interaction.guild.owner.mention}")
        embed.add_field(name= "👥 Members", value=memberCount)
        embed.add_field(name=f"💬 Channels ({len(interaction.guild.channels)})",value=f"**{len(interaction.guild.text_channels)}** Text|**{len(interaction.guild.voice_channels)}** Voice")
        embed.add_field(name= "🌍 Region", value=region)
        embed.add_field(name= "🔐 Roles",value=str(len(interaction.guild.roles)))
        await interaction.send(embed=embed,ephemeral=True)
        
    @utils.subcommand(name="ping",description="Ping the Bot")
    async def ping(self,ctx:init):
        latency = round(self.client.latency * 1000)
        await ctx.response.send_message(f"Pong! Latency is `{latency}ms`.",ephemeral=True)
    
    @utils.subcommand(name="avatar", description="Show user's avatar")
    async def avatar(self, ctx: init, target_user: Optional[User] = None):
        user: Union[User, Member, None] = target_user or ctx.user
        if not user:
            return await ctx.send("User not found!", ephemeral=True)
        if not user.avatar:
            return await ctx.send("User has no avatar!", ephemeral=True)
        embed = Embed.Info(title=f"{user.name}'s Avatar")
        embed.set_image(url=user.avatar.url)
        await ctx.send(embed=embed)

    @utils.subcommand(name="user-info", description="Get information about a user")
    async def userinfo(self, ctx: init, target_user: Optional[Member] = None):
        user: Union[User, Member, None] = target_user or ctx.user
        if not user or isinstance(user, User):
            return await ctx.send("User not found!", ephemeral=True)
        roles = [role.mention for role in user.roles[1:]]
        embed = Embed.Info(title="User Information")
        embed.add_field(name="Name", value=str(user))
        embed.add_field(name="ID", value=str(user.id))
        embed.add_field(name="Created at", value=user.created_at.strftime("%Y-%m-%d"))
        embed.add_field(name="Joined at", value=user.joined_at.strftime("%Y-%m-%d") if user.joined_at else "Not available")
        embed.add_field(name="Roles", value=" ".join(roles) if roles else "None")
        if user.avatar:
            embed.set_thumbnail(url=user.avatar.url)
        await ctx.send(embed=embed)

    @utils.subcommand(name="calculate", description="Calculate a math expression")
    async def calculate(self, ctx: Interaction, expression: str):
        try:
            operators = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.Pow: operator.pow,
                ast.BitXor: operator.xor,
                ast.USub: operator.neg
            }
            def eval_node(node):
                if isinstance(node, ast.Constant):
                    return node.n
                elif isinstance(node, ast.BinOp):
                    return operators[type(node.op)](eval_node(node.left), eval_node(node.right))
                elif isinstance(node, ast.UnaryOp):
                    return operators[type(node.op)](eval_node(node.operand))
                elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in dir(math):
                    # Allow only specific math functions
                    return getattr(math, node.func.id)(*[eval_node(arg) for arg in node.args])
                else:
                    raise TypeError(f"Unsupported operation: {type(node).__name__}")

            result = eval_node(ast.parse(expression, mode='eval').body)
            await ctx.send(embed=Embed.Info(title="Calculator", description=f"{expression} = {result}"))
        except Exception as e:
            await ctx.send(f"Invalid expression: {str(e)}", ephemeral=True)
    

def setup(client):
    client.add_cog(Other(client))