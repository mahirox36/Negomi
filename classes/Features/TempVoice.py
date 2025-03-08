from modules.Nexon import *

__UserSettingsVersion__ = 2

async def validate_voice_channel_ownership(ctx: init, data: Dict | List) -> bool:
    """
    Validates user's permissions and ownership for voice channel operations.

    This asynchronous function verifies if:
    1. The user is in a voice channel
    2. The voice channel exists in the provided data
    3. The user owns the voice channel they're in

    Parameters:
        ctx (init): The context object containing user and guild information
        data (Dict | List): Collection of voice channel data containing channel IDs and owner IDs

    Returns:
        bool: True if all checks pass, False otherwise

    Raises:
        Exception: If user is not found or not in a voice channel

    Examples:
        >>> await validate_voice_channel_ownership(ctx, [{user_id: channel_id}])
        True
    """
    if not ctx.user or not ctx.guild or isinstance(ctx.user, User) or not ctx.user.voice or not ctx.user.voice.channel:
        raise Exception("User not found")
    num = 0
    for i in data:
        i = dict(i)
        values_list = list(i.values())
        if ctx.user.voice.channel.id == values_list[0]:
            break
        num += 1
    else:
        await ctx.send(embed=Embed.Warning("You haven't Created a Channel"), ephemeral=True)
        return False

    if ctx.user.voice.channel.id != data[num].get(str(ctx.user.id)):
        await ctx.send(embed=Embed.Warning("You are not the Owner of this channel!"), ephemeral=True)
        return False
    return True

def UserSettings(member: User | Member):
    user = DataManager("TempVoice", file_name=f"{member.id}")
    Default = {
        "Name": member.display_name + "'s Chat",
        "Hide": True,
        "Lock": True,
        "Max": 0,
        "Version": __UserSettingsVersion__,
        "Banned_Users": [],  # New: Track banned users
        "Kicked_Users": []   # New: Track kicked users
    }
    if user.data == None or user.data.get("Version") != __UserSettingsVersion__:
        user.data = Default
    return user
def get_channel(data,ctx:init):
    if not ctx.user or not ctx.guild or isinstance(ctx.user, User) or not ctx.user.voice or not ctx.user.voice.channel:
        raise Exception("User not found")
    num = 0
    for i in data:
        i = dict(i)
        values_list = list(i.values())
        if ctx.user.voice.channel.id == values_list[0]:break
        num += 1
    else:
        raise Exception
    channel = ctx.guild.get_channel(data[num].get(str(ctx.user.id)))
    return channel
def get_before(data,ctx:VoiceState,user:Member):
    num = 0
    if not ctx.channel:
        raise Exception("Channel not found")
    for i in data:
        i = dict(i)
        values_list = list(i.values())
        try:
            if ctx.channel.id == values_list[0]:break
        except AttributeError:
            return None
        num += 1
    else:
        return None
    return ctx.channel.guild.get_channel(data[num].get(str(user.id)))

class EditMaxModal(Modal):
    def __init__(self, channel:VoiceChannel,ctx:init):
        super().__init__(title="Edit Max Number of users")
        if not ctx.user:
            raise Exception("User not found")
        self.user = UserSettings(ctx.user)
        self.channel = channel

        self.max = TextInput(label="Enter the Max number Of User",
                               placeholder="0 for Unlimited",
                               max_length=2, required=True)
        self.add_item(self.max)

    async def callback(self, ctx: Interaction):
        # This is called when the modal is submitted
        try:
            if not self.max.value:
                await ctx.send(embed=Embed.Error("Please enter a number"), ephemeral=True)
                return
            num = int(self.max.value)
        except ValueError:
            await ctx.send(embed=Embed.Error(f"Value \"{self.max.value}\" isn't a number"),ephemeral=True)
            return
        if num > 99:
            await ctx.send(embed=Embed.Error("The Value should be less than or equal to 99"),ephemeral=True)
            return
        elif num < 0:
            await ctx.send(embed=Embed.Error("The Value should be greater than or equal to 0"),ephemeral=True)
            return
        self.user["Max"] = num
        self.user.save()
        await self.channel.edit(user_limit=num)

class EditNameModal(Modal):
    def __init__(self, channel:VoiceChannel,ctx:init):
        super().__init__(title="Edit Name")
        if not ctx.user:
            raise Exception("User not found")
        self.user = UserSettings(ctx.user)
        self.channel = channel

        self.name = TextInput(label="New Name", placeholder=ctx.user.display_name + "'s Chat", required=True, max_length=100, min_length=1)
        self.add_item(self.name)

    async def callback(self, interaction: Interaction):
        # This is called when the modal is submitted
        name = self.name.value
        if not name:
            await interaction.send(embed=Embed.Error("Name cannot be empty"),ephemeral=True)
            return
        self.user["Name"] = name
        self.user.save()
        await self.channel.edit(name=name)

class ControlPanel(View):
    def __init__(self, data:Dict,user:Member):
        super().__init__(timeout=None)
        self.create_buttons()
        self.data = data
        self.user = UserSettings(user)       

    def create_buttons(self):
        self.button1 = Button(label=f"📝 Edit Name", style=ButtonStyle.primary)
        self.button1.callback = self.Edit_Name
        self.add_item(self.button1)

        self.button2 = Button(label=f"🫥 Hide/Show", style=ButtonStyle.primary)
        self.button2.callback = self.Hide
        self.add_item(self.button2)

        self.button3 = Button(label=f"🔓 Lock/Unlock", style=ButtonStyle.primary)
        self.button3.callback = self.Lock
        self.add_item(self.button3)

        self.button4 = Button(label=f"📝 Change Max Users", style=ButtonStyle.primary)
        self.button4.callback = self.Max
        self.add_item(self.button4)

        self.button5 = Button(label=f"🚫 Delete Channel Messages", style=ButtonStyle.primary)
        self.button5.callback = self.Delete_Messages
        self.add_item(self.button5)

        self.button6 = Button(label=f"⛔ Delete", style=ButtonStyle.primary)
        self.button6.callback = self.Delete
        self.add_item(self.button6)

    async def Edit_Name(self, interaction: Interaction):
        if await validate_voice_channel_ownership(interaction,self.data) == False:
            await self.disable(interaction)
            return
        try:
            channel = get_channel(self.data,interaction)
            if not channel:
                await interaction.send(embed=Embed.Warning("Channel not found"),ephemeral=True)
                return
            if not isinstance(channel, VoiceChannel):
                await interaction.send(embed=Embed.Warning("This command can only be used in voice channels"),ephemeral=True)
                return
            modal = EditNameModal(channel,interaction)
        except Exception:
            await interaction.send(embed=Embed.Warning("You haven't Created a Channel"),ephemeral=True)
            return
        await interaction.response.send_modal(modal)
        
    async def Hide(self, interaction: Interaction):
        if await validate_voice_channel_ownership(interaction,self.data) == False:
            await self.disable(interaction)
            return
        channeled = get_channel(self.data,interaction)
        if not channeled or not interaction.guild:
            await interaction.send(embed=Embed.Warning("Channel not found"),ephemeral=True)
            return
        if self.user.data["Hide"] == True:
            self.user.data["Hide"] = False
            await channeled.set_permissions(interaction.guild.default_role,view_channel=True,
                                            connect=True if self.user.data["Lock"] == False else False)
            await interaction.send(embed=Embed.Info("The channel is showing", title="Operation Success"),ephemeral=True)
        else:
            self.user.data["Hide"] = True
            await channeled.set_permissions(interaction.guild.default_role,view_channel=False,
                                            connect=True if self.user.data["Lock"] == False else False)
            await interaction.send(embed=Embed.Info("The channel is hiding", title="Operation Success"),ephemeral=True)
        self.user.save()
        return
    
    async def Lock(self, interaction: Interaction):
        if await validate_voice_channel_ownership(interaction,self.data) == False:
            await self.disable(interaction)
            return
        channeled = get_channel(self.data,interaction)
        if not channeled or not interaction.guild:
            await interaction.send(embed=Embed.Warning("Channel not found"),ephemeral=True)
            return
        if self.user.data["Lock"] == True:
            self.user.data["Lock"] = False
            await channeled.set_permissions(interaction.guild.default_role,connect=True,
                view_channel=True if self.user.data["Hide"] == False else False)
            await interaction.send(embed=Embed.Info("The channel is Unlocked", title="Operation Success"),ephemeral=True)
        else:
            self.user.data["Lock"] = True
            await channeled.set_permissions(interaction.guild.default_role,connect=False,
                view_channel=True if self.user.data["Hide"] == False else False)
            await interaction.send(embed=Embed.Info("The channel is Locked", title="Operation Success"),ephemeral=True)
        self.user.save()
        return
    
    async def Max(self, interaction: Interaction):
        if await validate_voice_channel_ownership(interaction,self.data) == False:
            await self.disable(interaction)
            return
        try:
            channel = get_channel(self.data,interaction)
            if not channel:
                await interaction.send(embed=Embed.Warning("Channel not found"),ephemeral=True)
                return
            if not isinstance(channel, VoiceChannel):
                await interaction.send(embed=Embed.Warning("This command can only be used in voice channels"),ephemeral=True)
                return
            modal = EditMaxModal(channel,interaction)
        except Exception:
            await interaction.send(embed=Embed.Warning("You haven't Created a Channel"),ephemeral=True)
            return
        await interaction.response.send_modal(modal)

    async def Delete_Messages(self, interaction: Interaction):
        if not interaction.guild:
            await interaction.send(embed=Embed.Warning("This command can only be used in a guild"),ephemeral=True)
            return
        if await validate_voice_channel_ownership(interaction,self.data) == False:
            await self.disable(interaction)
            return
        try:
            channeled = get_channel(self.data,interaction)
        except Exception:
            await interaction.send(embed=Embed.Warning("You haven't Created a Channel"),ephemeral=True)
            return
        if not channeled:
            await interaction.send(embed=Embed.Warning("Channel not found"),ephemeral=True)
            return
        if isinstance(channeled, (StageChannel, ForumChannel, CategoryChannel)):
            await interaction.send(embed=Embed.Warning("This command can only be used in voice channels"),ephemeral=True)
            return
        await channeled.purge(limit=10000)

    async def Delete(self, interaction: Interaction):
        if not interaction.guild:
            await interaction.send(embed=Embed.Warning("This command can only be used in a guild"),ephemeral=True)
            return
        if await validate_voice_channel_ownership(interaction,self.data) == False:
            await self.disable(interaction)
            return
        try:
            channeled = get_channel(self.data,interaction)
            if not channeled:
                await interaction.send(embed=Embed.Warning("Channel not found"),ephemeral=True)
                return
        except Exception:
            await interaction.send(embed=Embed.Warning("You haven't Created a Channel"),ephemeral=True)
            return
        
        file = DataManager("TempVoice", interaction.guild.id, file_name="TempVoices")
        num = 0
        for i in file.data:
            i = dict(i)
            values_list = list(i.values())
            if channeled.id == values_list[0]:break
            num += 1
        else:return
        
        try:
            await channeled.delete()
        except Exception:
            await interaction.send(embed=Embed.Error("Failed to delete the channel"),ephemeral=True)
            return
        file.data.remove(file.data[num])
        file.save()
        await self.disable(interaction)

    async def disable(self, ctx: Interaction):
        buttons = [
            self.button1,self.button2,self.button3,
            self.button4,self.button5,self.button6]
        for button in buttons:
            button.disabled = True
        self.stop()
        await ctx.response.edit_message(view=self)

class TempVoice(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
        # Structure: {guild_id: {channel_id: {user_id: last_state}}}
        self.voice_states = {}  # Cache voice states to track transitions
        self.lock = asyncio.Lock()
    async def invite_function(self, ctx:Interaction, user:Member):
        await ctx.response.defer(ephemeral=True)
        if not self.client.user or not ctx.user or not ctx.guild or isinstance(ctx.user, User) or not ctx.user.voice or not ctx.user.voice.channel:
            return await ctx.send(
                embed=Embed.Error("This command can only be used in temporary voice channels"),
                ephemeral=True
            )
        if ctx.user.id == user.id:
            return await ctx.send(embed=Embed.Error("You can't Invite yourself"))
        elif user.id == self.client.user.id:
            return await ctx.send(embed=Embed.Error("Are You trying to Invite me?",footer="No, You can't"))
        elif user.bot:
            return await ctx.send(embed=Embed.Error("You can't Invite Bot"))
        file = DataManager("TempVoice", ctx.guild.id, file_name="TempVoices")
        await validate_voice_channel_ownership(ctx,file.data)
        channel = get_channel(file.data,ctx)
        name = ctx.user.display_name
        if not channel:
            return await ctx.send(embed=Embed.Warning("You haven't Created a Channel"),ephemeral=True)
        await channel.set_permissions(user, view_channel=True, connect=True)
        try:
            if ctx.user.avatar:
                await user.send(embed=Embed.Info(
                    f"You have Been Invited by {ctx.user.mention} to Channel {channel.mention}.\n[View The Channel]({channel.jump_url})",
                    "Invitation",
                    f"Click the Channel to Join it",[name,ctx.user.avatar.url]
                    ))
            else:
                await user.send(embed=Embed.Info(
                    f"You have Been Invited by {ctx.user.mention} to Channel {channel.mention}.\n[View The Channel]({channel.jump_url})",
                    "Invitation",
                    f"Click the Channel to Join it"
                    ))
        except HTTPException:
            if not ctx.channel or isinstance(ctx.channel, (CategoryChannel, ForumChannel)):
                return await ctx.send(embed=Embed.Error("I can't DM the user, Please check the Privacy Settings"),ephemeral=True)
            if ctx.user.avatar:
                await ctx.channel.send(f"{user.mention}",embed=Embed.Info(
                    f"{user.mention}, You have Been Invited by {ctx.user.mention} to Channel {channel.mention}.\n[View The Channel]({channel.jump_url})",
                    "Invitation",
                    f"Click the Channel to Join it",[name,ctx.user.avatar.url]
                    ))
            else:
                await ctx.channel.send(f"{user.mention}",embed=Embed.Info(
                    f"{user.mention}, You have Been Invited by {ctx.user.mention} to Channel {channel.mention}.\n[View The Channel]({channel.jump_url})",
                    "Invitation",
                    f"Click the Channel to Join it"
                    ))
        return await ctx.send("Sended!",ephemeral=True)

    async def _check_voice_permissions(
        self, 
        ctx: init, 
        target: Member, 
        action: str
    ) -> tuple[bool, Optional[VoiceChannel], Optional[dict]]:
        """Check if the command user has proper permissions"""
        # Check if user is in a voice channel
        if not ctx.user or not ctx.guild or isinstance(ctx.user, User) or not ctx.user.voice or not ctx.user.voice.channel:
            await ctx.send(
                embed=Embed.Error("This command can only be used in temporary voice channels"),
                ephemeral=True
            )
            return False, None, None
        if not ctx.user.voice or not ctx.user.voice.channel:
            await ctx.send(
                embed=Embed.Error("You must be in a voice channel to use this command"),
                ephemeral=True
            )
            return False, None, None

        # Get the voice channel
        channel = ctx.user.voice.channel

        # Check if target is in the same voice channel
        if not target.voice or target.voice.channel != channel:
            await ctx.send(
                embed=Embed.Error(f"Target user must be in your voice channel to be {action}"),
                ephemeral=True
            )
            return False, None, None

        # Check if user is the channel owner
        file = DataManager("TempVoice", ctx.guild.id, file_name="TempVoices")
        channel_data = None
        for data in file.data:
            if list(data.values())[0] == channel.id:
                if str(ctx.user.id) != list(data.keys())[0]:
                    await ctx.send(
                        embed=Embed.Error("You must be the channel owner to use this command"),
                        ephemeral=True
                    )
                    return False, None, None
                channel_data = data
                break
        else:
            await ctx.send(
                embed=Embed.Error("This command can only be used in temporary voice channels"),
                ephemeral=True
            )
            return False, None, None

        if not isinstance(channel, VoiceChannel):
            await ctx.send(
                embed=Embed.Error("This command can only be used in voice channels, not stage channels"),
                ephemeral=True
            )
            return False, None, None
        return True, channel, channel_data

    async def _ban_member(
        self, 
        ctx: init, 
        target: Member, 
        channel: VoiceChannel, 
        channel_data: dict,
        reason: str = "No reason provided"
    ) -> bool:
        """Ban a member from the voice channel"""
        if not ctx.user or not ctx.guild or isinstance(ctx.user, User) or not ctx.user.voice or not ctx.user.voice.channel:
            await ctx.send(
                embed=Embed.Error("This command can only be used in temporary voice channels"),
                ephemeral=True
            )
            return False
        user_settings = UserSettings(ctx.user)

        if target.id == ctx.user.id:
            await ctx.send(
                embed=Embed.Error("You cannot ban yourself"),
                ephemeral=True
            )
            return False

        if target.guild_permissions.administrator:
            await ctx.send(
                embed=Embed.Error("You cannot ban administrators"),
                ephemeral=True
            )
            return False

        try:
            # Temporarily disable channel cleanup for this operation
            guild_id = ctx.guild.id
            channel_id = channel.id
            cleanup_disabled = False

            if guild_id in self.voice_states and channel_id in self.voice_states[guild_id]:
                cleanup_disabled = True
                # Mark channel as having an ongoing moderation action
                self.voice_states[guild_id][channel_id]['mod_action'] = True

            # Add to banned users list
            if target.id not in user_settings.data["Banned_Users"]:
                user_settings.data["Banned_Users"].append(target.id)
                user_settings.save()

            # Remove user and set permissions
            await target.move_to(None, reason=f"Banned by {ctx.user.display_name}: {reason}")
            await channel.set_permissions(target, connect=False, view_channel=False)

            # Try to DM the user
            try:
                await target.send(
                    embed=Embed.Warning(
                        f"You have been banned from {channel.name} by {ctx.user.display_name}\n"
                        f"Reason: {reason}"
                    )
                )
            except:
                pass  # DM failed, continue anyway

            # Re-enable channel cleanup
            if cleanup_disabled:
                if guild_id in self.voice_states and channel_id in self.voice_states[guild_id]:
                    self.voice_states[guild_id][channel_id].pop('mod_action', None)

            await ctx.send(
                embed=Embed.Info(
                    f"Banned {target.display_name}\nReason: {reason}",
                    title="Member Banned"
                ),
                ephemeral=True
            )
            return True

        except Exception as e:
            await ctx.send(
                embed=Embed.Error(f"Failed to ban user: {str(e)}"),
                ephemeral=True
            )
            return False

    async def _kick_member(
        self, 
        ctx: init, 
        target: Member, 
        channel: VoiceChannel,
        channel_data: dict,
        reason: str = "No reason provided"
    ) -> bool:
        """Kick a member from the voice channel"""
        if not ctx.user or not ctx.guild or isinstance(ctx.user, User) or not ctx.user.voice or not ctx.user.voice.channel:
            await ctx.send(
                embed=Embed.Error("This command can only be used in temporary voice channels"),
                ephemeral=True
            )
            return False
        
        user_settings = UserSettings(ctx.user)

        if target.id == ctx.user.id:
            await ctx.send(
                embed=Embed.Error("You cannot kick yourself"),
                ephemeral=True
            )
            return False

        if target.guild_permissions.administrator:
            await ctx.send(
                embed=Embed.Error("You cannot kick administrators"),
                ephemeral=True
            )
            return False

        try:
            # Temporarily disable channel cleanup for this operation
            guild_id = ctx.guild.id
            channel_id = channel.id
            cleanup_disabled = False

            if guild_id in self.voice_states and channel_id in self.voice_states[guild_id]:
                cleanup_disabled = True
                # Mark channel as having an ongoing moderation action
                self.voice_states[guild_id][channel_id]['mod_action'] = True

            # Add to kicked users list
            if target.id not in user_settings.data["Kicked_Users"]:
                user_settings.data["Kicked_Users"].append(target.id)
                user_settings.save()

            # Try to DM the user
            try:
                await target.send(
                    embed=Embed.Warning(
                        f"You have been kicked from {channel.name} by {ctx.user.display_name}\n"
                        f"Reason: {reason}"
                    )
                )
            except:
                pass  # DM failed, continue anyway

            # Kick the user
            await target.move_to(None, reason=f"Kicked by {ctx.user.display_name}: {reason}")

            # Re-enable channel cleanup
            if cleanup_disabled:
                if guild_id in self.voice_states and channel_id in self.voice_states[guild_id]:
                    self.voice_states[guild_id][channel_id].pop('mod_action', None)

            await ctx.send(
                embed=Embed.Info(
                    f"Kicked {target.display_name}\nReason: {reason}",
                    title="Member Kicked"
                ),
                ephemeral=True
            )
            return True

        except Exception as e:
            await ctx.send(
                embed=Embed.Error(f"Failed to kick user: {str(e)}"),
                ephemeral=True
            )
            return False
    
    @slash_command(name="voice")
    async def voice(self,ctx:init):
        pass
    @voice.subcommand(name="panel",
        description="Bring the Control Panel for the TempVoice chat")
    async def control_panel(self,ctx:init):
        if not ctx.guild or not ctx.user or isinstance(ctx.user, User) or not ctx.user.voice or not ctx.user.voice.channel:
            return await ctx.response.send_message(embed=Embed.Error("You must be in a voice channel to use this command"),ephemeral=True)
        file = DataManager("TempVoice", ctx.guild.id, file_name="TempVoices")
        if not file.data or not file.data:
            return await ctx.response.send_message(embed=Embed.Error("You haven't Created a Channel"),ephemeral=True)
        checks = validate_voice_channel_ownership(ctx,file.data)
        if await checks == False: return
        
        await ctx.response.send_message(embed=Embed.Info(title="Control Panel",
                description="Please Chose"),view=ControlPanel(file.data,ctx.user),
                ephemeral=True)

    @voice.subcommand(name="ban",description="Ban a user from your temporary voice channel")
    async def ban_slash(
        self,
        ctx: init,
        target: Member = SlashOption(
            description="The user to ban",
            required=True
        ),
        reason: str = SlashOption(
            description="Reason for the ban",
            required=False,
            default="No reason provided"
        )
    ):
        """Ban a user from your temporary voice channel"""
        await ctx.response.defer(ephemeral=True)
        valid, channel, channel_data = await self._check_voice_permissions(ctx, target, "banned")
        if not valid or not channel or not channel_data:
            return
        await self._ban_member(ctx, target, channel, channel_data, reason)

    @voice.subcommand(name="kick",description="Kick a user from your temporary voice channel")
    async def kick_slash(self, ctx: init, target: Member = SlashOption(
            description="The user to kick", required=True), reason: str = SlashOption(description="Reason for the kick",
            required=False, default="No reason provided")
    ):
        """Kick a user from your temporary voice channel"""
        await ctx.response.defer(ephemeral=True)
        valid, channel, channel_data = await self._check_voice_permissions(ctx, target, "kicked")
        if not valid or not channel or not channel_data:
            return
        await self._kick_member(ctx, target, channel, channel_data, reason)

    # @user_command(name="Voice: Ban", contexts=[InteractionContextType.guild])
    # async def ban_user(self, ctx: init, target: Member):
    #     """Ban a user from your temporary voice channel (User Command)"""
    #     await ctx.response.defer(ephemeral=True)
    #     valid, channel, channel_data = await self._check_voice_permissions(ctx, target, "banned")
    #     if not valid:
    #         return
    #     await self._ban_member(ctx, target, channel, channel_data)

    # @user_command(name="Voice: Kick", contexts=[InteractionContextType.guild])
    # async def kick_user(self, ctx: init, target: Member):
    #     """Kick a user from your temporary voice channel (User Command)"""
    #     await ctx.response.defer(ephemeral=True)
    #     valid, channel, channel_data = await self._check_voice_permissions(ctx, target, "kicked")
    #     if not valid:
    #         return
    #     await self._kick_member(ctx, target, channel, channel_data)
     
    @voice.subcommand("invite",description="Invite a member to Voice chat")
    async def invite_slash(self,ctx:init,user:Member):
        return await self.invite_function(ctx,user)
    
    @user_command("Voice: Invite", contexts=[InteractionContextType.guild])
    async def invite(self, ctx:init, user:Member):
        return await self.invite_function(ctx,user)
    
    async def _update_voice_state(self, member: Member, before: VoiceState, after: VoiceState) -> bool:
        """
        Update voice state cache and return if state change is valid
        Returns: True if state change should be processed, False if it should be ignored
        """
        guild_id = member.guild.id
        
        # Initialize guild state if needed
        if guild_id not in self.voice_states:
            self.voice_states[guild_id] = {}

        # Get current channel IDs
        before_channel_id = before.channel.id if before.channel else None
        after_channel_id = after.channel.id if after.channel else None
        
        # Update state for old channel
        if before_channel_id:
            if before_channel_id not in self.voice_states[guild_id]:
                self.voice_states[guild_id][before_channel_id] = {}
            
            # Remove user from old channel state
            if before_channel_id != after_channel_id:
                self.voice_states[guild_id][before_channel_id].pop(member.id, None)
                
                # Cleanup empty channel state
                if not self.voice_states[guild_id][before_channel_id]:
                    self.voice_states[guild_id].pop(before_channel_id, None)

        # Update state for new channel
        if after_channel_id:
            if after_channel_id not in self.voice_states[guild_id]:
                self.voice_states[guild_id][after_channel_id] = {}
            
            # Get previous state in this channel
            prev_state = self.voice_states[guild_id][after_channel_id].get(member.id)
            
            # Update current state
            current_state = {
                'self_mute': after.self_mute,
                'self_deaf': after.self_deaf,
                'self_stream': after.self_stream,
                'self_video': after.self_video,
                'timestamp': datetime.now().timestamp()
            }
            
            self.voice_states[guild_id][after_channel_id][member.id] = current_state
            
            # Check if this is just a self-state update (mute/stream/video)
            if prev_state and before_channel_id == after_channel_id:
                changes = [k for k, v in current_state.items() 
                          if k != 'timestamp' and prev_state.get(k) != v]
                
                # If only self-state changed, don't process as a channel change
                if changes and all(c.startswith('self_') for c in changes):
                    return False

        return True

    async def handle_channel_creation(self, member: Member, guild: Guild, 
                                    before: VoiceState, after: VoiceState):
        """Handle creation of temporary voice channels with state tracking"""
        async with self.lock:
            try:
                # Validate basic conditions
                if not after or not after.channel:
                    return
                    
                # Check if this is a valid state change
                if not await self._update_voice_state(member, before, after):
                    return
                    
                file = DataManager("TempVoice", guild.id)
                if not file.exists() or not file.data:
                    return
                    
                create_channel_id = file.data.get("CreateChannel")
                category_id = file.data.get("categoryChannel")
                if not create_channel_id or not category_id:
                    return
                    
                # Skip if not joining the create channel
                create_channel = guild.get_channel(create_channel_id)
                if not create_channel or after.channel.id != create_channel_id:
                    return
                    
                # Initialize or get existing temp voices data
                file2 = DataManager("TempVoice", guild.id, file_name="TempVoices")
                if file2.data is None:
                    file2.data = []
                    
                # Check if user already has a temp channel
                for channel_data in file2.data:
                    if str(member.id) in channel_data:
                        existing_channel = guild.get_channel(channel_data[str(member.id)])
                        if isinstance(existing_channel, VoiceChannel):
                            # Move to existing channel instead of creating new one
                            await member.move_to(existing_channel)
                            return
                        else:
                            # Remove stale channel data
                            file2.data.remove(channel_data)
                            file2.save()
                            break
                            
                # Get user settings
                user = DataManager("TempVoice", file_name=f"{member.id}")
                channel_settings = self._get_channel_settings(member, user)
                
                # Create new temp channel
                new_channel = await self._create_temp_channel(
                    member, guild, channel_settings, category_id
                )
                
                if not new_channel:
                    return
                    
                # Initialize state tracking
                guild_id = guild.id
                if guild_id not in self.voice_states:
                    self.voice_states[guild_id] = {}
                    
                self.voice_states[guild_id][new_channel.id] = {
                    member.id: {
                        'self_mute': after.self_mute,
                        'self_deaf': after.self_deaf,
                        'self_stream': after.self_stream,
                        'self_video': after.self_video,
                        'timestamp': datetime.now().timestamp()
                    }
                }
                
                # Move member and update database
                await self._safe_move_member(member, new_channel, after)
                file2.data.append({str(member.id): new_channel.id})
                file2.save()
                
                # Send channel info
                await self._send_channel_info(new_channel, member)
                
            except Exception as e:
                logger.error(f"Error in channel creation: {str(e)}")
                if 'new_channel' in locals() and new_channel is not None:
                    try:
                        await new_channel.delete()
                    except:
                        pass

    async def handle_channel_cleanup(self, member: Member, guild: Guild,
                           before: VoiceState, after: VoiceState):
        """Handle cleanup of empty temporary voice channels with state tracking"""
        async with self.lock:
            if not before.channel:
                return
            if not await self._update_voice_state(member, before, after):
                return
            file = DataManager("TempVoice", guild.id, file_name="TempVoices")
            if not file.data:
                file.data = []
                file.save()
                return
            channel_index = self._find_channel_index(before.channel.id, file.data)
            if channel_index is None:
                return
            channel = before.channel
            if not channel:
                file.data.pop(channel_index)
                file.save()
                return
            
            # Check if the channel is a voice channel
            if not isinstance(channel, VoiceChannel):
                return
                
            member_count = len(channel.members)
            guild_id = guild.id
            channel_id = channel.id
            channel_states = self.voice_states.get(guild_id, {}).get(channel_id, {})
            if channel_states.get('mod_action'):
                return
            if member_count == 0:
                await self._cleanup_channel(channel, file, channel_index)
                if guild_id in self.voice_states and channel_id in self.voice_states[guild_id]:
                    del self.voice_states[guild_id][channel_id]

    def _get_channel_settings(self, member: Member, user: DataManager) -> dict:
        """Get channel settings with proper defaults"""
        if user.data and user.data.get("Version") == __UserSettingsVersion__:
            settings = user.data
            return {
                "name": settings["Name"],
                "connect": True if not settings["Lock"] else False,
                "view": True if not settings["Hide"] else False,
                "max": settings["Max"]
            }
        
        return {
            "name": member.display_name + "'s Chat",
            "connect": False,
            "view": False,
            "max": 0
        }

    async def _create_temp_channel(self, member: Member, guild: Guild, 
                                 settings: dict, category_id: int) -> Optional[VoiceChannel]:
        """Create temporary voice channel with proper settings"""
        channel = guild.get_channel(category_id)
        if not channel or not isinstance(channel, CategoryChannel):
            return None
        overwrites = {
            guild.default_role: PermissionOverwrite(
                connect=settings["connect"],
                view_channel=settings["view"]
            ),
            member: PermissionOverwrite(
                connect=True,
                view_channel=True,
                priority_speaker=True,
                move_members=True,
                stream=True
            )
        }

        return await guild.create_voice_channel(
            settings["name"],
            category=channel,
            reason=f"User {member} Created a TempVoice",
            overwrites=overwrites,
            user_limit=settings["max"],
            bitrate=int(guild.bitrate_limit)  # Set optimal bitrate for stability
        )

    async def _safe_move_member(self, member: Member, channel: VoiceChannel, state: VoiceState):
        """Safely move member while preserving their state"""
        max_retries = 3
        for i in range(max_retries):
            try:
                await member.move_to(
                    channel,
                    reason=f"User {member} Created a TempVoice"
                )
                
                # Preserve streaming/video state if it was active
                if state.self_stream or state.self_video:
                    await asyncio.sleep(0.5)  # Small delay to ensure move completed
                    
                    # Update state cache
                    guild_id = member.guild.id
                    if guild_id in self.voice_states and channel.id in self.voice_states[guild_id]:
                        self.voice_states[guild_id][channel.id][member.id].update({
                            'self_stream': state.self_stream,
                            'self_video': state.self_video,
                            'timestamp': datetime.now().timestamp()
                        })
                
                break
            except Exception as e:
                if i == max_retries - 1:
                    logger.error(f"Failed to move member after {max_retries} attempts: {str(e)}")
                await asyncio.sleep(1)

    async def _send_channel_info(self, channel: VoiceChannel, member: Member):
        """Send channel information message"""
        author = [member.name, member.avatar.url] if member.avatar else None
        try:
            if author:
                await channel.send(
                    embed=Embed.Warning(
                        "Only the Owner can change the settings of this channel, "
                        "even if they leave. Screen sharing and video are enabled.",
                        title="Channel Information",
                        author=author
                    )
                )
            else:
                await channel.send(
                    embed=Embed.Warning(
                        "Only the Owner can change the settings of this channel, "
                        "even if they leave. Screen sharing and video are enabled.",
                        title="Channel Information"
                    )
                )
        except Exception as e:
            logger.error(f"Failed to send channel info: {str(e)}")

    def _find_channel_index(self, channel_id: int, data: List[Dict]) -> Optional[int]:
        """Find channel index in data safely"""
        for i, item in enumerate(data):
            if list(item.values())[0] == channel_id:
                return i
        return None

    async def _cleanup_channel(self, channel: VoiceChannel, 
                             file: DataManager, channel_index: int):
        """Clean up channel and update database"""
        try:
            await channel.delete()
            file.data.pop(channel_index)
            file.save()
        except Exception as e:
            logger.error(f"Error cleaning up channel: {str(e)}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: Member,
                                  before: VoiceState, after: VoiceState):
        """Main voice state update handler with state tracking"""
        if member.bot:
            return
            
        try:
            guild = (after and after.channel and after.channel.guild) or \
                   (before and before.channel and before.channel.guild)
            
            if not guild:
                return

            # Handle channel creation
            if after and after.channel:
                await self.handle_channel_creation(member, guild, before, after)
                
            # Handle channel cleanup
            if before and before.channel:
                await self.handle_channel_cleanup(member, guild, before, after)

        except Exception as e:
            logger.error(f"Error in voice state update: {str(e)}")
            
            # Cleanup any invalid states on error
            try:
                if guild:
                    guild_id = guild.id
                    if guild_id in self.voice_states:
                        # Remove any empty channel states
                        empty_channels = [
                            channel_id for channel_id, states in self.voice_states[guild_id].items()
                            if not states
                        ]
                        for channel_id in empty_channels:
                            del self.voice_states[guild_id][channel_id]
                        
                        # Remove guild if no channels
                        if not self.voice_states[guild_id]:
                            del self.voice_states[guild_id]
            except Exception as cleanup_error:
                logger.error(f"Error cleaning up voice states: {str(cleanup_error)}")

def setup(client):
    client.add_cog(TempVoice (client))