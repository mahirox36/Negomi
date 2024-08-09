import nextcord
import nextcord as discord
from nextcord import *
from nextcord.ext import commands
from nextcord import Interaction as init
import requests
from Lib.Side import *
from Lib.Logger import *
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import gc
from Lib.Hybrid import setup_hybrid, userCTX
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
    
    @commands.command(name = "j",)
    async def join(self, ctx:commands.Context):
        avatar_url = str(ctx.author.avatar.url)  # Get the avatar URL
        welcome_image = self.create_welcome_image(ctx.author.name, avatar_url)
        await ctx.send(file=nextcord.File(welcome_image, 'welcome_image.png'))
        del welcome_image
        gc.collect()
    
    

def setup(client):
    client.add_cog(Welcome(client))