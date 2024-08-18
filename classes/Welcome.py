import nextcord
import nextcord as discord
from nextcord import *
from nextcord.ext import commands
from nextcord import Interaction as init
import requests
from Lib.Side import *
from Lib.Logger import *
from PIL import Image, ImageDraw, ImageFont
import io
import gc
import os
import json

class Welcome(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
    
    def fetch_avatar(self,url):
        response = requests.get(url)
        return Image.open(io.BytesIO(response.content))

    def create_circular_avatar(self,image):
        size = min(image.size)
        mask = Image.new('L', image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)
        mask = mask.crop((0, 0, size, size))
        image = image.crop((0, 0, size, size))
        image.putalpha(mask)
        return image

    def create_welcome_image(self,member_name, avatar_url):
        base_image_path = baseImagePath
        img = Image.open(base_image_path)

        try:
            font = ImageFont.truetype(Font, SizeFont)
        except IOError:
            try:
                font = ImageFont.truetype(BackupFont, SizeFont)
            except IOError:
                font = ImageFont.load_default()

        avatar = self.fetch_avatar(avatar_url).resize(Resize)
        avatar = self.create_circular_avatar(avatar)  # Make the avatar circular
        # avatar = ImageOps.expand(avatar, border=3, fill='white') 
        img.paste(avatar, avatarPosition, avatar)

        draw = ImageDraw.Draw(img)
        text = f"{member_name}!"
        text_position = textPosition  # Adjust text position as needed
        draw.text(text_position, text, fill=textColor, font=font)

        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        # Clean up
        del img
        del avatar

        return buffer
    
    @commands.command(name = "setup-welcome-message",
                    aliases=["setup-welcome"],
                    description = """
Setup a welcome message in a specific Channel, in the message option you can uses these for info (Variables):
{server}  : For the name of the server
{count}   : For the count of members in the server
{mention} : Mention the user
{name}    : Just the name of the user
""")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def setupWelcome(self, ctx:commands.Context,message: str, channel:TextChannel):
        file = Data(ctx.guild.id,"Welcome")
        file.data= {
            "message":message,
            "channel":channel.id
        }
        file.save()
        await ctx.reply(embed=info_embed(f"The message was: ``` {message}```",title="Done!"))
        file= Data(ctx.guild.id,"Welcome","Members")
        file.data = [member.id for member in ctx.guild.members]
        file.save()
        file= DataGlobal("Welcome","Guilds")
        if file.data == None:
            file.data = []
        file.data.append(ctx.guild.id)
        file.save()
        
    
    
    @commands.Cog.listener()
    async def on_member_join(self, member:Member):
        guild = member.guild
        file = Data(guild.id,"Welcome")
        if not file.data:return
        channel = guild.get_channel(file["channel"])
        if channel == None:
            file.delete_guild()
            return
        name = get_name(member)
        message = str(file["message"]).replace("{server}",guild.name).replace("{count}",str(guild.member_count))\
            .replace("{mention}",member.mention).replace("{name}",name)
        avatar_url = member.avatar.url  # Get the avatar URL
        welcome_image = self.create_welcome_image(name, avatar_url)
        await channel.send(file=nextcord.File(welcome_image, f"welcome_{name}.png"))
        await channel.send(message)
        del welcome_image
        gc.collect()
        file= Data(member.guild.id,"Welcome","Members")
        file.data.append(member.id)
        file.save()
        
    @commands.Cog.listener()
    async def on_ready(self):
        GlobalFile= DataGlobal("Welcome","Guilds")
        guilds = GlobalFile.data
        for guild in guilds:
            file= Data(guild,"Welcome")
            guild= self.client.get_guild(guild)
            channel= guild.get_channel(file["channel"])
            
            if channel == None:
                file.delete_guild()
                continue
            members = Data(guild.id, "Welcome", "Members")
            oldMembers = members.data
            newMembers = [member.id for member in guild.members]
            joined_members = [member for member in newMembers if member not in oldMembers]
            
            members.data = newMembers
            members.save()
            message = str(file["message"]).replace("{server}",guild.name).replace("{count}",str(guild.member_count))\
                .replace("{mention}",member.mention).replace("{name}",name)
            
            for member in joined_members:
                member= guild.get_member(member)
                name = get_name(member)
                avatar_url = member.avatar.url  # Get the avatar URL
                welcome_image = self.create_welcome_image(name, avatar_url)
                await channel.send(file=nextcord.File(welcome_image, f"welcome_{name}.png"))
                await channel.send(message)
                del welcome_image
                gc.collect()
        print("Finished All Missed Welcome Messages")
            
            
        
    
        
    
    

def setup(client):
    client.add_cog(Welcome(client))