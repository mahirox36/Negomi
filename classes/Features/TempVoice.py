from modules.Nexon import *
__UserSettingsVersion__ = 2

async def check(ctx: init, data: Dict | List) -> bool:
    try:
        ctx.user.voice.channel
    except:
        await ctx.send(embed=warn_embed("You are not in a channel"), ephemeral=True)
        return False
    
    num = 0
    for i in data:
        i = dict(i)
        values_list = list(i.values())
        if ctx.user.voice.channel.id == values_list[0]:
            break
        num += 1
    else:
        await ctx.send(embed=warn_embed("You haven't Created a Channel"), ephemeral=True)
        return False

    if ctx.user.voice.channel.id != data[num].get(str(ctx.user.id)):
        await ctx.send(embed=warn_embed("You are not the Owner of this channel!"), ephemeral=True)
        return False
    return True

def UserSettings(member):
    user = DataManager("TempVoice", file=f"{member.id}")
    Default = {
        "Name": get_name(member) + "'s Chat",
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
    num = 0
    for i in data:
        i = dict(i)
        values_list = list(i.values())
        if ctx.user.voice.channel.id == values_list[0]:break
        num += 1
    else:
        raise Exception
    return ctx.guild.get_channel(data[num].get(str(ctx.user.id)))
def get_before(data,ctx:VoiceState,user:Member):
    num = 0
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
        self.user = UserSettings(ctx.user)
        self.channel = channel

        self.max = TextInput(label="Enter the Max number Of User",
                               placeholder="0 for Unlimited",
                               max_length=2, required=True)
        self.add_item(self.max)

    async def callback(self, ctx: Interaction):
        # This is called when the modal is submitted
        try:
            num = int(self.max.value)
        except ValueError:
            await ctx.send(embed=error_embed(f"Value \"{self.max.value}\" isn't a number"),ephemeral=True)
            return
        if num > 99:
            await ctx.send(embed=error_embed("The Value should be less than or equal to 99"),ephemeral=True)
            return
        elif num < 0:
            await ctx.send(embed=error_embed("The Value should be greater than or equal to 0"),ephemeral=True)
            return
        self.user["Max"] = num
        self.user.save()
        await self.channel.edit(user_limit=num)

class EditNameModal(Modal):
    def __init__(self, channel:VoiceChannel,ctx:init):
        super().__init__(title="Edit Name")
        self.user = UserSettings(ctx.user)
        self.channel = channel

        self.name = TextInput(label="New Name", placeholder=ctx.user.global_name + "'s Chat" if ctx.user.global_name != None
            else get_name(ctx.user) + "'s Chat", required=True, max_length=100, min_length=1)
        self.add_item(self.name)

    async def callback(self, interaction: Interaction):
        # This is called when the modal is submitted
        name = self.name.value
        self.user["Name"] = name
        self.user.save()
        await self.channel.edit(name=name)

class ControlPanel(View):
    def __init__(self, data:Dict,user:User):
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

    async def Edit_Name(self, ctx: Interaction):
        if await check(ctx,self.data) == False:
            await self.disable(ctx)
            return
        try:
            modal = EditNameModal(get_channel(self.data,ctx),ctx)
        except Exception:
            await ctx.send(embed=warn_embed("You haven't Created a Channel"),ephemeral=True)
            return
        await ctx.response.send_modal(modal)
        
    async def Hide(self, ctx: Interaction):
        if await check(ctx,self.data) == False:
            await self.disable(ctx)
            return
        channeled = get_channel(self.data,ctx)
        if self.user.data["Hide"] == True:
            self.user.data["Hide"] = False
            await channeled.set_permissions(everyone(ctx.guild),view_channel=True,
                                            connect=True if self.user.data["Lock"] == False else False)
            await ctx.send(embed=info_embed("The channel is showing", title="Operation Success"),ephemeral=True)
        else:
            self.user.data["Hide"] = True
            await channeled.set_permissions(everyone(ctx.guild),view_channel=False,
                                            connect=True if self.user.data["Lock"] == False else False)
            await ctx.send(embed=info_embed("The channel is hiding", title="Operation Success"),ephemeral=True)
        self.user.save()
        return
    
    async def Lock(self, ctx: Interaction):
        if await check(ctx,self.data) == False:
            await self.disable(ctx)
            return
        channeled = get_channel(self.data,ctx)
        if self.user.data["Lock"] == True:
            self.user.data["Lock"] = False
            await channeled.set_permissions(everyone(ctx.guild),connect=True,
                view_channel=True if self.user.data["Hide"] == False else False)
            await ctx.send(embed=info_embed("The channel is Unlocked", title="Operation Success"),ephemeral=True)
        else:
            self.user.data["Lock"] = True
            await channeled.set_permissions(everyone(ctx.guild),connect=False,
                view_channel=True if self.user.data["Hide"] == False else False)
            await ctx.send(embed=info_embed("The channel is Locked", title="Operation Success"),ephemeral=True)
        self.user.save()
        return
    
    async def Max(self, ctx: Interaction):
        if await check(ctx,self.data) == False:
            await self.disable(ctx)
            return
        try:
            modal = EditMaxModal(get_channel(self.data,ctx),ctx)
        except Exception:
            await ctx.send(embed=warn_embed("You haven't Created a Channel"),ephemeral=True)
            return
        await ctx.response.send_modal(modal)

    async def Delete_Messages(self, ctx: Interaction):
        if await check(ctx,self.data) == False:
            await self.disable(ctx)
            return
        try:
            channeled = get_channel(self.data,ctx)
        except Exception:
            await ctx.send(embed=warn_embed("You haven't Created a Channel"),ephemeral=True)
            return
        await channeled.purge(limit=10000)

    async def Delete(self, ctx: Interaction):
        if await check(ctx,self.data) == False:
            await self.disable(ctx)
            return
        try:
            channeled = get_channel(self.data,ctx)
        except Exception:
            await ctx.send(embed=warn_embed("You haven't Created a Channel"),ephemeral=True)
            return
        file = DataManager("TempVoice", ctx.guild.id, file="TempVoices")
        num = 0
        for i in file.data:
            i = dict(i)
            values_list = list(i.values())
            if channeled.id == values_list[0]:break
            num += 1
        else:return
        await channeled.delete()
        file.data.remove(file.data[num])
        file.save()
        await self.disable(ctx)

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
    async def invite_function(ctx:init,user:Member,client):
        await ctx.response.defer(ephemeral=True)
        if ctx.user.id == user.id:
            await ctx.send(embed=error_embed("You can't Invite yourself"))
            return
        elif user.id == client.user.id:
            await ctx.send(embed=error_embed("Are You trying to Invite me?",footer="No, You can't"))
            return
        elif user.bot:
            await ctx.send(embed=error_embed("You can't Invite Bot"))
            return
        file = DataManager("TempVoice", ctx.guild.id, file="TempVoices")
        await check(ctx,file.data)
        channel = get_channel(file.data,ctx)
        name = get_name(ctx.user)
        await channel.set_permissions(user, view_channel=True, connect=True)
        try:
            await user.send(embed=info_embed(
                f"You have Been Invited by {ctx.user.mention} to Channel {channel.mention}.\n[View The Channel]({channel.jump_url})",
                "Invitation",
                f"Click the Channel to Join it",[name,ctx.user.avatar.url]
                ))
        except HTTPException:
            ctx.channel.send(f"{user.mention}",embed=info_embed(
                f"{user.mention}, You have Been Invited by {ctx.user.mention} to Channel {channel.mention}.\n[View The Channel]({channel.jump_url})",
                "Invitation",
                f"Click the Channel to Join it",[name,ctx.user.avatar.url]
                ))
        await ctx.send("Sended!",ephemeral=True)
        return

    async def _check_voice_permissions(
        self, 
        ctx: init, 
        target: Member, 
        action: str
    ) -> tuple[bool, Optional[VoiceChannel], Optional[dict]]:
        """Check if the command user has proper permissions"""
        member = ctx.user

        # Check if user is in a voice channel
        if not member.voice or not member.voice.channel:
            await ctx.send(
                embed=error_embed("You must be in a voice channel to use this command"),
                ephemeral=True
            )
            return False, None, None

        # Get the voice channel
        channel = member.voice.channel

        # Check if target is in the same voice channel
        if not target.voice or target.voice.channel != channel:
            await ctx.send(
                embed=error_embed(f"Target user must be in your voice channel to be {action}"),
                ephemeral=True
            )
            return False, None, None

        # Check if user is the channel owner
        file = DataManager("TempVoice", ctx.guild.id, file="TempVoices")
        channel_data = None
        for data in file.data:
            if list(data.values())[0] == channel.id:
                if str(member.id) != list(data.keys())[0]:
                    await ctx.send(
                        embed=error_embed("You must be the channel owner to use this command"),
                        ephemeral=True
                    )
                    return False, None, None
                channel_data = data
                break
        else:
            await ctx.send(
                embed=error_embed("This command can only be used in temporary voice channels"),
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
        member = ctx.user
        user_settings = UserSettings(member)

        if target.id == member.id:
            await ctx.send(
                embed=error_embed("You cannot ban yourself"),
                ephemeral=True
            )
            return False

        if target.guild_permissions.administrator:
            await ctx.send(
                embed=error_embed("You cannot ban administrators"),
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
            await target.move_to(None, reason=f"Banned by {get_name(member)}: {reason}")
            await channel.set_permissions(target, connect=False, view_channel=False)

            # Try to DM the user
            try:
                await target.send(
                    embed=warn_embed(
                        f"You have been banned from {channel.name} by {get_name(member)}\n"
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
                embed=info_embed(
                    f"Banned {get_name(target)}\nReason: {reason}",
                    title="Member Banned"
                ),
                ephemeral=True
            )
            return True

        except Exception as e:
            await ctx.send(
                embed=error_embed(f"Failed to ban user: {str(e)}"),
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
        member = ctx.user
        user_settings = UserSettings(member)

        if target.id == member.id:
            await ctx.send(
                embed=error_embed("You cannot kick yourself"),
                ephemeral=True
            )
            return False

        if target.guild_permissions.administrator:
            await ctx.send(
                embed=error_embed("You cannot kick administrators"),
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
                    embed=warn_embed(
                        f"You have been kicked from {channel.name} by {get_name(member)}\n"
                        f"Reason: {reason}"
                    )
                )
            except:
                pass  # DM failed, continue anyway

            # Kick the user
            await target.move_to(None, reason=f"Kicked by {get_name(member)}: {reason}")

            # Re-enable channel cleanup
            if cleanup_disabled:
                if guild_id in self.voice_states and channel_id in self.voice_states[guild_id]:
                    self.voice_states[guild_id][channel_id].pop('mod_action', None)

            await ctx.send(
                embed=info_embed(
                    f"Kicked {get_name(target)}\nReason: {reason}",
                    title="Member Kicked"
                ),
                ephemeral=True
            )
            return True

        except Exception as e:
            await ctx.send(
                embed=error_embed(f"Failed to kick user: {str(e)}"),
                ephemeral=True
            )
            return False
    
    @slash_command(name="voice")
    async def voice(self,ctx:init):
        pass
    @voice.subcommand(name="panel",
        description="Bring the Control Panel for the TempVoice chat")
    @feature()
    async def control_panel(self,ctx:init):
        file = DataManager("TempVoice", ctx.guild.id, file="TempVoices")
        checks = check(ctx,file.data)
        if await checks == False: return
        
        await ctx.response.send_message(embed=info_embed(title="Control Panel",
                description="Please Chose"),view=ControlPanel(file.data,ctx.user),
                ephemeral=True)

    @voice.subcommand(name="ban",description="Ban a user from your temporary voice channel")
    @feature()
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
        if not valid:
            return
        await self._ban_member(ctx, target, channel, channel_data, reason)

    @voice.subcommand(name="kick",description="Kick a user from your temporary voice channel")
    @feature()
    async def kick_slash(self, ctx: init, target: Member = SlashOption(
            description="The user to kick", required=True), reason: str = SlashOption(description="Reason for the kick",
            required=False, default="No reason provided")
    ):
        """Kick a user from your temporary voice channel"""
        await ctx.response.defer(ephemeral=True)
        valid, channel, channel_data = await self._check_voice_permissions(ctx, target, "kicked")
        if not valid:
            return
        await self._kick_member(ctx, target, channel, channel_data, reason)

    # @user_command(name="Voice: Ban", contexts=[InteractionContextType.guild])
    # @feature()
    # async def ban_user(self, ctx: init, target: Member):
    #     """Ban a user from your temporary voice channel (User Command)"""
    #     await ctx.response.defer(ephemeral=True)
    #     valid, channel, channel_data = await self._check_voice_permissions(ctx, target, "banned")
    #     if not valid:
    #         return
    #     await self._ban_member(ctx, target, channel, channel_data)

    # @user_command(name="Voice: Kick", contexts=[InteractionContextType.guild])
    # @feature()
    # async def kick_user(self, ctx: init, target: Member):
    #     """Kick a user from your temporary voice channel (User Command)"""
    #     await ctx.response.defer(ephemeral=True)
    #     valid, channel, channel_data = await self._check_voice_permissions(ctx, target, "kicked")
    #     if not valid:
    #         return
    #     await self._kick_member(ctx, target, channel, channel_data)
     
    @voice.subcommand("invite",description="Invite a member to Voice chat")
    @feature()
    async def invite_slash(self,ctx:init,user:Member):
        return await self.invite_function(ctx,user,self.client)
    
    # @user_command("Voice: Invite", contexts=[InteractionContextType.guild])
    # @feature()
    # async def invite(self,ctx:init, user:Member):
    #     return await self.invite_function(ctx,user,self.client)
        
    @slash_command("voice-setup", "Setup temp voice",default_member_permissions=Permissions(administrator=True))
    @feature()
    async def setup(self, ctx:init, category:CategoryChannel):
        file = DataManager("TempVoice", ctx.guild.id)
        overwrites = {ctx.guild.default_role: PermissionOverwrite(speak=False)}
        createChannel = await ctx.guild.create_voice_channel("➕・Create",
            reason=f"Used setup Temp Voice by {ctx.user}", category=category,overwrites=overwrites)
        data = {
            "CreateChannel"     : createChannel.id,
            "categoryChannel"   : category.id
        }
        file.data = data
        file.save()
        await ctx.send(embed=info_embed("Setup Done!"),ephemeral=True)
    
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
            # Check if this is a valid state change
            if not await self._update_voice_state(member, before, after):
                return
                
            file = DataManager("TempVoice", guild.id)
            file2 = DataManager("TempVoice", guild.id, file="TempVoices")
            
            if not file.exists():
                return

            if get_before(file2.data, before, member) is not None or get_before(file2.data, after, member) is not None:
                return
            
            # Get channel settings
            user = DataManager("TempVoice", file=f"{member.id}")
            channel_settings = self._get_channel_settings(member, user)
            
            if file.data is None:
                file.data = []
                
            create_channel = guild.get_channel(file["CreateChannel"])
            if not create_channel or create_channel.id != after.channel.id:
                return

            # Create new temp channel
            new_channel = await self._create_temp_channel(
                member, guild, channel_settings, file["categoryChannel"]
            )
            
            # Initialize state tracking for new channel
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
            
            # Move member with state preservation
            await self._safe_move_member(member, new_channel, after)
            
            # Update database
            file2.data.append({str(member.id): new_channel.id})
            file2.save()
            
            await self._send_channel_info(new_channel, member)

    async def handle_channel_cleanup(self, member: Member, guild: Guild,
                           before: VoiceState, after: VoiceState):
        """Handle cleanup of empty temporary voice channels with state tracking"""
        async with self.lock:
            if not before.channel:
                return
            if not await self._update_voice_state(member, before, after):
                return
            file = DataManager("TempVoice", guild.id, file="TempVoices")
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
            "name": get_name(member) + "'s Chat",
            "connect": False,
            "view": False,
            "max": 0
        }

    async def _create_temp_channel(self, member: Member, guild: Guild, 
                                 settings: dict, category_id: int) -> VoiceChannel:
        """Create temporary voice channel with proper settings"""
        overwrites = {
            everyone(guild): PermissionOverwriteWith(
                connect=settings["connect"],
                view_channel=settings["view"]
            ),
            member: PermissionOverwriteWith(
                connect=True,
                view_channel=True,
                priority_speaker=True,
                move_members=True,
                stream=True  # Add stream permission to fix screen share issues
            )
        }

        return await guild.create_voice_channel(
            settings["name"],
            category=guild.get_channel(category_id),
            reason=f"User {member} Created a TempVoice",
            overwrites=overwrites,
            user_limit=settings["max"],
            bitrate=guild.bitrate_limit  # Set optimal bitrate for stability
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
        try:
            await channel.send(
                embed=warn_embed(
                    "Only the Owner can change the settings of this channel, "
                    "even if they leave. Screen sharing and video are enabled.",
                    title="Channel Information",
                    author=[member.name, member.avatar.url]
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

            try:
                await check_feature_inside(guild.id, self)
            except AttributeError:
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