import asyncio
from nextcord import *
from nextcord.ext import commands
from nextcord import Interaction as init
from modules.Nexon import *
import emoji as emojis
import re


class GroupEditModal(ui.Modal):
    def __init__(self, group, file: Data, client: commands.Bot):
        super().__init__("Edit Group")
        self.group = group
        self.file = file
        self.client = client

        self.name = ui.TextInput(label="Group Name", placeholder="Enter the new group name", default_value=group["name"])
        self.emoji = ui.TextInput(label="Emoji", placeholder="Enter the new emoji", default_value=group["emoji"])

        self.add_item(self.name)
        self.add_item(self.emoji)

    async def callback(self, ctx: init):
        try:
            name = self.name.value.strip()
            emoji = self.emoji.value.strip()

            # Validate emoji
            is_standard_emoji = emoji.replace(" ", "") in emojis.EMOJI_DATA

            if not is_standard_emoji:
                await ctx.send(embed=error_embed("That isn't a valid emoji", "Emoji Error"), ephemeral=True)
                return

            # Update group data
            self.group["name"] = name
            self.group["emoji"] = emoji

            # Update channel properties
            channel = ctx.guild.get_channel(self.group["channel"])
            if channel:
                await channel.edit(name=f"{emoji}・{name}")
            else:
                await ctx.send(embed=error_embed("Channel not found", "Error"), ephemeral=True)
                return

            # Save changes
            self.file.save()

            await ctx.send(embed=info_embed(f"Group updated to {name} with {emoji}", "Group Edited"), ephemeral=True)

        except HTTPException as e:
            if e.status == 429:
                retry_after = e.retry_after or 5  # If no retry_after, wait for a few seconds
                logger.warning(f"Rate limited. Retrying in {retry_after} seconds.")
                await asyncio.sleep(retry_after)
                await self.callback(ctx)  # Retry after delay
            else:
                logger.error(f"HTTP Exception: {e}")
                await ctx.send(embed=error_embed("Error occurred, please try again later.", "Error"), ephemeral=True)
        
        except Forbidden:
            logger.error("Bot lacks permission to edit the channel.")
            await ctx.send(embed=error_embed("I lack permissions to edit this channel.", "Permission Error"), ephemeral=True)
        
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            await ctx.send(embed=error_embed("An unexpected error occurred.", "Error"), ephemeral=True)

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
            file_user.data[0]["count"] = 0
            file_user.data[0]["update"] += 1
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
                        logger.warn(f"Channel with ID {channel_id} not found.")
    
                except Exception as e:
                    # Log or handle exceptions that occur during deletion
                    logger.error(f"An error occurred while processing channel ID {i.get('channel')}: {e}")
    
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
        try: await ctx.response.edit_message(content=None, embed=info_embed(message, "Deletion Success"), view=None)
        except:pass
        
        


class Groups(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
    
    @slash_command(name="group",description="show group options")
    async def group(self,ctx:init):
        pass
    @group.subcommand(name="create",description="Create a group (AKA Text Channels) For you and your friends")
    @cooldown(60)
    @feature()
    async def group_create(self,ctx:init,name: str, emoji: str, topic: str = SlashOption("topic","Topic is the small description in the top of the channel",max_length=100,required=False), nsfw: bool = False):
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
            fileUser.data = [{"count":0,"update":0}]
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
    
    @group.subcommand(name="edit", description="Edit this group's details")
    @cooldown(180)
    @feature()
    async def group_edit(self, ctx: init):
        file = Data(ctx.guild_id, "Groups", f"{ctx.user.id}", subFolder="Members")
        group = self.get_group_by_channel(ctx, file)

        if not group:
            await ctx.send(embed=error_embed("This channel is not linked to a group you own", "Group Error"))
            return

        await ctx.response.send_modal(GroupEditModal(group, file, self.client))
    
    @group.subcommand(name="delete",description="Delete a group")
    @feature()
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
    
    def get_group_by_channel(self, ctx: init, file: Data) -> dict:
        """Helper method to get the group associated with the current channel."""
        for group in file.data:
            if group.get("channel") == ctx.channel.id:
                return group
        return None
    
    @group.subcommand(name="add", description="Add a member to this group")
    @feature()
    async def group_add(self, ctx: init, member: Member):
        file = Data(ctx.guild_id, "Groups", f"{ctx.user.id}", subFolder="Members")
        group = self.get_group_by_channel(ctx, file)
        
        if member.bot:
            await ctx.send(embed=error_embed("You can't Add Bots", "Member Error"), ephemeral=True)
            return

        if not group:
            await ctx.send(embed=error_embed("This channel is not linked to a group you own", "Group Error"), ephemeral=True)
            return

        if member.id in group["Members"]:
            await ctx.send(embed=error_embed(f"{member.mention} is already in this group", "Member Exists"), ephemeral=True)
            return

        channel = ctx.guild.get_channel(group["channel"])
        overwrite = channel.overwrites_for(member)
        overwrite.view_channel = True
        overwrite.send_messages = True
        await channel.set_permissions(member, overwrite=overwrite)

        group["Members"].append(member.id)
        file.save()
        await ctx.send(embed=info_embed(f"{member.mention} has been added to this group", "Member Added"))

    @group.subcommand(name="kick", description="Remove a member from this group")
    @feature()
    async def group_kick(self, ctx: init, member: Member):
        file = Data(ctx.guild_id, "Groups", f"{ctx.user.id}", subFolder="Members")
        group = self.get_group_by_channel(ctx, file)
        
        if member.bot:
            await ctx.send(embed=error_embed("You can't Kick Bots", "Member Error"), ephemeral=True)
            return

        if not group:
            await ctx.send(embed=error_embed("This channel is not linked to a group you own", "Group Error"), ephemeral=True)
            return

        if member.id not in group["Members"]:
            await ctx.send(embed=error_embed(f"{member.mention} is not in this group", "Member Not Found"), ephemeral=True)
            return

        channel = ctx.guild.get_channel(group["channel"])
        await channel.set_permissions(member, overwrite=None)

        group["Members"].remove(member.id)
        file.save()
        await ctx.send(embed=info_embed(f"{member.mention} has been removed from this group", "Member Removed"))

    @group.subcommand(name="transfer", description="Transfer group ownership to another member in this group")
    @feature()
    async def group_transfer(self, ctx: init, member: Member):
        file = Data(ctx.guild_id, "Groups")
        user_file = Data(ctx.guild_id, "Groups", f"{ctx.user.id}", subFolder="Members")
        group = self.get_group_by_channel(ctx, user_file)
        
        if member.bot:
            await ctx.send(embed=error_embed("You can't Transfer to Bots", "Member Error"), ephemeral=True)
            return

        if not group:
            await ctx.send(embed=error_embed("This channel is not linked to a group you own", "Group Error"), ephemeral=True)
            return

        if member.id == ctx.user.id:
            await ctx.send(embed=error_embed("You are already the owner of this group", "Transfer Error"), ephemeral=True)
            return

        group_owner = file["groups"].get(str(group["channel"]))

        if str(ctx.user.id) != str(group_owner):
            await ctx.send(embed=error_embed("You are not the owner of this group", "Transfer Error"), ephemeral=True)
            return
        elif member.id not in group["Members"]:
            await ctx.send(embed=error_embed("the Member that you have selected isn't in the Group", "Transfer Error"), ephemeral=True)
            return
        
        file["groups"][str(group["channel"])] = member.id
        await ctx.send(embed=info_embed(f"{member.mention} is now the owner of this group", "Ownership Transferred"))

        user_file.data.remove(group)
        user_file.data[0]["count"] -= 1
        user_file.save()

        new_owner_file = Data(ctx.guild_id, "Groups", f"{member.id}", subFolder="Members")
        if not new_owner_file.data:
            new_owner_file.data = [
                {
                    "count":0,
                    "update":0
                }
            ]
        new_owner_file.data[0]["count"] += 1
        new_owner_file.data[0]["update"] +=1 
        for user in group["Members"]:
            if user == ctx.user.id:
                group["Members"].remove(user)
                break
        group["Members"].append(ctx.user.id)
        new_owner_file.data.append(group)
        new_owner_file.save()
        file.save()



def setup(client):
    client.add_cog(Groups(client))