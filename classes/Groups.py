import nextcord
import nextcord as discord
from nextcord import *
from nextcord.ext import commands
from nextcord import Interaction as init
from Lib.Side import *
from Lib.Logger import *
import emoji as emojis
import re
import os
import json


class DeleteSelect(ui.View):
    def __init__(self, data: list, update: int) -> None:
        super().__init__(timeout=None)
        self.update = update
        self.uses = 0
        self.options= [
                SelectOption(
                    label=item["name"],
                    value=str(idx + 1),
                    emoji=item["emoji"],
                    description=item["topic"]
                )
                for idx, item in enumerate(data)
            ]
        self.options.append(SelectOption(
                    label="Delete everything",
                    value="-1",
                    emoji="🗑️",
                    description="Delete Every Group You have"
                ))
        self.select = ui.Select(
            placeholder="Choose an option...",
            options=self.options
        )
        self.select.callback = self.callback
        self.add_item(self.select)

    async def callback(self, ctx: Interaction):
        selected_value = int(self.select.values[0])
        if selected_value == -1:
            file = Data(ctx.guild.id, "Groups")
            file_user = Data(ctx.guild.id, "Groups", f"{ctx.user.id}", subFolder="Members")
            
            # Safely iterate over a copy of file_user.data
            for i in list(file_user.data):
                try:
                    channel_id = i.get("channel")
                    if channel_id is None:
                        continue
                    
                    channel = ctx.guild.get_channel(channel_id)
                    if channel is not None:
                        # Remove data from file_user and file
                        file_user.data.remove(i)
                        file["groups"].pop(str(channel_id), None)  # Use pop with default to avoid KeyError
                        await channel.delete()
                    else:
                        # Optionally log or notify if the channel was not found
                        LOGGER.warn(f"Channel with ID {channel_id} not found.")
    
                except Exception as e:
                    # Log or handle exceptions that occur during deletion
                    print(f"An error occurred while processing channel ID {i.get('channel')}: {e}")
    
            # Save changes to the data files
            file_user.save()
            file.save()
            await ctx.response.edit_message(content=None, embed=info_embed("Every Group You had has been deleted!", "Deletion Success"), view=None)
            return
        selected_option = next((opt for opt in self.select.options if opt.value == str(selected_value)), None)
        if selected_option:
            self.select.options.remove(selected_option)
        
        file = Data(ctx.guild_id, "Groups")
        message = "The Group has been deleted!"

        if not self.select.options:
            self.select.options.append(SelectOption(label="Nothing", value="Yeah"))
            self.select.disabled = True
            message = "The Group has been deleted!\nThere are no more Groups left to delete."

        file_user = Data(ctx.guild_id, "Groups", f"{ctx.user.id}", subFolder="Members")

        if self.update != file_user.data[0]["update"]:
            self.select.disabled = True
            await ctx.response.edit_message(
                embed=error_embed("Sorry, this select is outdated.\nPlease type `/group-delete` again!", "Outdated"),
                view=self
            )
            return
        data = file_user.data[selected_value]
        channel = ctx.guild.get_channel(data["channel"])
        file_user.data.pop(selected_value)
        file["groups"].pop(str(channel.id))
        self.update += 1
        file_user.data[0]["update"] += 1
        file_user.data[0]["count"] -= 1

        await channel.delete()
        file.save()
        file_user.save()
        
        # Delete the original ephemeral message by editing it with no content
        await ctx.response.edit_message(content=None, embed=info_embed(message, "Deletion Success"), view=None)
        
        


class Groups(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
    
    @slash_command(name="group-create",description="Create a group (AKA Text Channels) For you and your friends")
    async def group_create(self,ctx:init,name: str, emoji: str, topic: str = SlashOption("topic","Topic is the small description in the top of the channel",max_length=100,required=False), nsfw: bool = False):
        await cooldown(60,ctx.user,__name__)
        is_standard_emoji = emoji.replace(" ","") in emojis.EMOJI_DATA
        # Check if the emoji is a custom emoji (e.g., <a:customemoji:123456789012345678>)
        custom_emoji_pattern = re.compile(r'<a?:\w{2,32}:\d{18,}>')
        is_custom_emoji = bool(custom_emoji_pattern.fullmatch(emoji))
        if (not is_custom_emoji) and (not is_standard_emoji):
            await ctx.send(embed=error_embed("That isn't emoji","Emoji Error"))
            return
        elif is_custom_emoji:
            await ctx.send(embed=error_embed("Sorry, but the custom emoji doesn't work"))
            return
        else:
            emoji_id = emoji
        file= Data(ctx.guild_id,"Groups")
        fileUser= Data(ctx.guild_id,"Groups",f"{ctx.user.id}",subFolder="Members")
        if not file.data:
            category = await ctx.guild.create_category("Groups")
            file.data= {
                "category"  : category.id,
                "limit"     : 20,
                "groups"    : {}
            }
        else:category= ctx.guild.get_channel(file["category"])
        if not fileUser.data:
            fileUser.data = [{"count":0}]
        if fileUser.data[0]["count"] >= file["limit"]:
            await ctx.send(embed= error_embed("Sorry but you hit the limit"))
            return
        overwrite = {
            ctx.user: PermissionOverwriteWith(manage_messages=True,send_messages=True,view_channel=True),
            everyone(ctx.guild): PermissionOverwriteWith(view_channel=False)
        }
        channel= await ctx.guild.create_text_channel(f"{emoji}・{name}",overwrites=overwrite,category=category,
                                      topic=topic, nsfw=nsfw,reason=f"User {ctx.user.name}/{ctx.user.id} Created a Group")
        fileUser.data.append({
            "channel"   : channel.id,
            "name"      : name,
            "emoji"     : emoji_id,
            "topic"     : topic,
            "nsfw"      : nsfw,
            "Members"   : []
        })
        fileUser.data[0]["count"] += 1
        fileUser.data[0]["update"] +=1 
        file["groups"].update({channel.id:ctx.user.id})
        fileUser.save()
        file.save()
        await ctx.send(embed=info_embed(f"<#{channel.id}>","Group Created!"),ephemeral=True)
    
    @slash_command(name="group-delete",description="Delete a group")
    async def group_delete(self,ctx:init):
        fileUser= Data(ctx.guild_id,"Groups",f"{ctx.user.id}",subFolder="Members")
        if not fileUser.data:
            await ctx.send(embed=error_embed("You don't have groups to delete"))
            return
        elif fileUser.data[0]["count"] == 0:
            await ctx.send(error_embed("You don't have groups to delete"))
            return
        update= fileUser.data[0]["update"]
        fileUser.data.pop(0)
        view = DeleteSelect(fileUser.data, update)
        await ctx.send(embed=info_embed("Please Select the the Group you want to delete!","Delete Group"),ephemeral=True,view=view)



def setup(client):
    client.add_cog(Groups(client))