from datetime import timedelta
from modules.Nexon import *
#TODO: Highly Customable
class moderatormanager(commands.Cog):
    def __init__(self, client:Client):
        self.client = client
        self.logger = logger
        self.token_refresh_task = self.client.loop.create_task(self.refresh_tokens_task())
    
    
    async def refresh_tokens_task(self):
        """Background task to refresh tokens every 60 days"""
        while not self.client.is_closed():
            try:
                # Get all guild data
                for guild in self.client.guilds:
                    file = Data(guild.id, "Moderator Manager", "users", default={})
                    data = file.load()
                    
                    if not data:
                        continue
                        
                    updated = False
                    for user_id, mod_data in data.items():
                        token_date = datetime.fromisoformat(mod_data.get("token_created", datetime.now().isoformat()))
                        if datetime.now() - token_date >= timedelta(days=60):
                            # Generate new token
                            new_token = self.generate_token()
                            mod_data["token"] = new_token
                            mod_data["token_created"] = datetime.now().isoformat()
                            updated = True
                            
                            # Try to notify the user
                            try:
                                member = guild.get_member(int(user_id))
                                if member:
                                    await member.send(f"Your moderator token has been automatically refreshed. Your new token is: `{new_token}`")
                            except:
                                self.logger.warning(f"Could not send token refresh notification to user {user_id}")
                    
                    if updated:
                        file.save()
                        
            except Exception as e:
                self.logger.error(f"Error in token refresh task: {e}")
            
            # Wait for 24 hours before next check
            await asyncio.sleep(86400)  # 24 hours in seconds

    def generate_token(self):
        """Generate a new unique token"""
        better_id = BetterID("Moderator Manager", 42)
        return better_id.generate()

    def get_mod_data(self, guild_id: int):
        """Get moderator data file"""
        return Data(guild_id, "Moderator Manager", "users", default={})

    async def create_backup_data(self, guild_id: int, user_id: str):
        """Create backup of moderator data"""
        file = self.get_mod_data(guild_id)
        data = file.load()
        if user_id in data:
            backup_file = Data(guild_id, "Moderator Manager", "backups", default={})
            backup_data = backup_file.load()
            backup_data[user_id] = data[user_id].copy()
            backup_file.save()
    
    @slash_command(name="mod",default_member_permissions=Permissions(administrator=True))
    async def moded(self, ctx:init):
        pass
    @moded.subcommand(name="manager")
    async def manager(self, ctx:init):
        pass
    
    @manager.subcommand("setup", "Setup the Moderator Manager")
    @feature()
    async def setup(self, ctx:init,
                    staffRole:Role  = SlashOption("staff"   , "Role for staff members"   ,required=False),
                    trailRole:Role  = SlashOption("trail"   , "Role for trail mod"   ,required=False),
                    modRole:Role    = SlashOption("mod"     , "Role for Mod"   ,required=False),
                    highModRole:Role= SlashOption("high_mod", "Role for High mod"   ,required=False),
                    adminRole:Role  = SlashOption("admin"   , "Role for Admin"   ,required=False)):
        await ctx.response.defer(ephemeral=True)
        guild = ctx.guild
        if adminRole == None:
            adminRole= await guild.create_role(name="Admin",
                                               permissions=Permissions(administrator=True),
                                               color=0x0EE08B, hoist=True)
        if highModRole == None:
            highModRole= await guild.create_role(name="High Moderator",
                                                 permissions=Permissions(moderate_members=True, kick_members=True,
                                                                         ban_members=True, manage_messages=True, manage_nicknames=True,
                                                                         view_audit_log=True, manage_threads=True,
                                                                         mute_members=True, move_members=True, deafen_members=True),
                                                 color=0x824040, hoist=True)
        if modRole == None:
            modRole= await guild.create_role(name="Moderator",
                                             permissions=Permissions(moderate_members=True, kick_members=True,
                                                                     manage_messages=True, manage_nicknames=True,
                                                                     manage_threads=True, mute_members=True),
                                             color=0xFF7D7D, hoist=True)
        if trailRole == None:
            trailRole= await guild.create_role(name="Trail Moderator",
                                               permissions=Permissions(moderate_members=True, manage_messages=True),
                                               color=0x5C5CFF, hoist=True)
            PermissionOverwriteWith()
        if staffRole == None:
            staffRole= await guild.create_role(name="Staff")
        file = Data(ctx.guild_id, "Moderator Manager")
        file.data = {
            "staff": staffRole.id if staffRole else None,
            "trail": trailRole.id if trailRole else None,
            "mod": modRole.id if modRole else None,
            "high": highModRole.id if highModRole else None,
            "admin": adminRole.id if adminRole else None
        }
        file.save()
        await ctx.send(embed=info_embed("Moderator Manager setup successfully", "Moderator Manager"))
    @manager.subcommand("add", "Add a Moderator")
    @feature()
    async def add(self, ctx: init, member: Member, role: Role):
        await ctx.response.defer()
        file = self.get_mod_data(ctx.guild_id)
        mods = file.load()
        data = Data(ctx.guild_id, "Moderator Manager").data
        
        if data is None:
            await ctx.send(embed=error_embed("Moderator Manager is not setup yet", "Moderator Manager"))
            return
        
        if role.id not in data.values():
            await ctx.send(embed=error_embed("This role is not a Moderator role", "Moderator Manager"))
            return

        if str(member.id) in data:
            await ctx.send(embed=error_embed("This member is already a Moderator", "Moderator Manager"))
            return
        try:
            staffRole = ctx.guild.get_role(data["staff"])
            await member.add_roles(role)
            await member.add_roles(staffRole)
        except:
            await ctx.send(embed=error_embed(f"Error while adding Role. please check that the bot role is on top of the {role.mention} role", "Moderator Manager"),ephemeral=True)

        token = self.generate_token()
        
        mod_data = {
            "currentRole": role.id,
            "token": token,
            "token_created": datetime.now().isoformat(),
            "since": str(ctx.created_at),
            "by": ctx.user.id,
            "pastRoles": []
        }
        
        mods[str(member.id)] = mod_data
        file.save()
        
        # DM the token to the new moderator
        try:
            await member.send(f"Your moderator token is: `{token}`\nThis token will be automatically refreshed every 60 days.")
            await ctx.send(embed=info_embed(f"{member.mention} is now a {role.mention}\nToken has been sent via DM", "Moderator Manager"))
        except:
            await ctx.send(embed=warn_embed(f"{member.mention} is now a {role.mention}, but I couldn't DM them the token", "Moderator Manager"))
    @manager.subcommand("promote", "Promote a moderator to a higher role")
    @feature()
    async def promote(self, ctx: init, member: Member):
        await ctx.response.defer()
        file = Data(ctx.guild_id, "Moderator Manager", "users", default={})
        data = file.load()
        roles_data = Data(ctx.guild_id, "Moderator Manager").load()
        
        if str(member.id) not in data:
            await ctx.send(embed=error_embed("This member is not a moderator", "Moderator Manager"))
            return
            
        current_role_id = data[str(member.id)]["currentRole"]
        role_hierarchy = [roles_data["staff"], roles_data["trail"], roles_data["mod"], roles_data["high"], roles_data["admin"]]
        
        try:
            current_index = role_hierarchy.index(current_role_id)
            if current_index >= len(role_hierarchy) - 1:
                await ctx.send(embed=error_embed("This moderator is already at the highest role", "Moderator Manager"))
                return
                
            new_role_id = role_hierarchy[current_index + 1]
            new_role = ctx.guild.get_role(new_role_id)
            
            # Update the moderator's data
            data[str(member.id)]["pastRoles"].append(current_role_id)
            data[str(member.id)]["currentRole"] = new_role_id
            file.save()
            
            # Update roles
            await member.add_roles(new_role)
            await member.remove_roles(ctx.guild.get_role(current_role_id))
            
            await ctx.send(embed=info_embed(f"{member.mention} has been promoted to {new_role.mention}", "Moderator Manager"))
        except ValueError:
            await ctx.send(embed=error_embed("Error in role hierarchy", "Moderator Manager"))

    @manager.subcommand("demote", "Demote a moderator to a lower role")
    @feature()
    async def demote(self, ctx: init, member: Member):
        await ctx.response.defer()
        file = Data(ctx.guild_id, "Moderator Manager", "users", default={})
        data = file.load()
        roles_data = Data(ctx.guild_id, "Moderator Manager").load()
        
        if str(member.id) not in data:
            await ctx.send(embed=error_embed("This member is not a moderator", "Moderator Manager"))
            return
            
        current_role_id = data[str(member.id)]["currentRole"]
        role_hierarchy = [roles_data["staff"], roles_data["trail"], roles_data["mod"], roles_data["high"], roles_data["admin"]]
        
        try:
            current_index = role_hierarchy.index(current_role_id)
            if current_index <= 1:
                await ctx.send(embed=error_embed("This moderator is already at the lowest role", "Moderator Manager"))
                return
                
            new_role_id = role_hierarchy[current_index - 1]
            new_role = ctx.guild.get_role(new_role_id)
            
            # Update the moderator's data
            data[str(member.id)]["pastRoles"].append(current_role_id)
            data[str(member.id)]["currentRole"] = new_role_id
            file.save()
            
            # Update roles
            await member.add_roles(new_role)
            await member.remove_roles(ctx.guild.get_role(current_role_id))
            
            await ctx.send(embed=info_embed(f"{member.mention} has been demoted to {new_role.mention}", "Moderator Manager"))
        except ValueError:
            await ctx.send(embed=error_embed("Error in role hierarchy", "Moderator Manager"))

    @manager.subcommand("remove", "Remove a moderator")
    @feature()
    async def remove(self, ctx: init, member: Member):
        await ctx.response.defer()
        file = Data(ctx.guild_id, "Moderator Manager", "users", default={})
        data = file.load()
        
        if str(member.id) not in data:
            await ctx.send(embed=error_embed("This member is not a moderator", "Moderator Manager"))
            return
            
        # Remove all mod roles
        current_role_id = data[str(member.id)]["currentRole"]
        await member.remove_roles(ctx.guild.get_role(current_role_id))
        
        # Remove from database
        del data[str(member.id)]
        file.save()
        
        await ctx.send(embed=info_embed(f"{member.mention} has been removed from the moderator team", "Moderator Manager"))

    @manager.subcommand("hacked", "Handle hacked moderator account")
    @feature()
    async def hacked(self, ctx: init, compromised_member: Member, backup_token: str, new_member: Member = None):
        """
        Handle a hacked moderator account
        compromised_member: The account that was hacked
        backup_token: The original token of the mod before being hacked
        new_member: Optional - New account of the moderator if they created one
        """
        await ctx.response.defer(ephemeral=True)
        
        file = self.get_mod_data(ctx.guild_id)
        data = file.load()
        
        if str(compromised_member.id) not in data:
            await ctx.send(embed=error_embed("The specified account is not a moderator", "Moderator Manager"))
            return
            
        mod_data = data[str(compromised_member.id)]
        
        # Verify backup token
        if mod_data["token"] != backup_token:
            await ctx.send(embed=error_embed("Invalid backup token provided", "Moderator Manager"))
            return
            
        # Create backup of mod data before any changes
        await self.create_backup_data(ctx.guild_id, str(compromised_member.id))
        
        try:
            # 1. Ban the hacked account
            reason = "Account compromised - Moderator security measure"
            await compromised_member.ban(reason=reason)
            
            # 2. Restore moderator access
            if new_member:
                # If mod has a new account, transfer roles to it
                mod_role = ctx.guild.get_role(mod_data["currentRole"])
                
                # Generate new token for the new account
                new_token = self.generate_token()
                
                # Create new mod data entry
                new_mod_data = {
                    "currentRole": mod_data["currentRole"],
                    "token": new_token,
                    "token_created": datetime.now().isoformat(),
                    "since": mod_data["since"],  # Keep original appointment date
                    "by": ctx.user.id,  # Record who handled the hack recovery
                    "pastRoles": mod_data["pastRoles"],
                    "previous_account": compromised_member.id  # Track account history
                }
                
                # Update database
                del data[str(compromised_member.id)]  # Remove old account entry
                data[str(new_member.id)] = new_mod_data  # Add new account entry
                file.save()
                
                # Apply roles
                await new_member.add_roles(mod_role)
                
                # Send new token via DM
                try:
                    await new_member.send(f"Your moderator access has been restored. Your new token is: `{new_token}`\n"
                                        f"This token will be automatically refreshed every 60 days.")
                    success_msg = f"Account recovered:\n- Banned compromised account\n- Restored access to {new_member.mention}\n- New token sent via DM"
                except:
                    success_msg = f"Account recovered:\n- Banned compromised account\n- Restored access to {new_member.mention}\n- ⚠️ Could not send token via DM"
                
            else:
                # If no new account provided, just ban the compromised account and save backup
                success_msg = f"Compromised account {compromised_member.mention} has been banned. No new account was provided for restoration."
            
            # Send success message
            await ctx.send(embed=info_embed(success_msg, "Moderator Manager"))
            
            # Log the action
            self.logger.info(f"Handled hacked moderator account: {compromised_member.id} banned" + 
                           (f", restored to {new_member.id}" if new_member else ""))
            
        except Exception as e:
            self.logger.error(f"Error handling hacked account: {e}")
            await ctx.send(embed=error_embed(f"An error occurred while handling the hacked account: {str(e)}", "Moderator Manager"))

    @manager.subcommand("list", "List all moderators")
    @feature()
    async def list(self, ctx: init):
        await ctx.response.defer()
        file = Data(ctx.guild_id, "Moderator Manager", "users", default={})
        data = file.load()
        
        if not data:
            await ctx.send(embed=warn_embed("No moderators found", "Moderator Manager"))
            return
        embed = info_embed(title="Moderator List")
        
        for user_id, mod_data in data.items():
            member = ctx.guild.get_member(int(user_id))
            if member:
                role = ctx.guild.get_role(mod_data["currentRole"])
                since = mod_data["since"]
                embed.add_field(
                    name=f"{get_name(member)}",
                    value=f"Role: {role.mention}\nSince: {since}",
                    inline=False
                )
        
        await ctx.send(embed=embed)

    @manager.subcommand("info", "Get information about a moderator")
    @feature()
    async def info(self, ctx: init, member: Member):
        await ctx.response.defer()
        file = Data(ctx.guild_id, "Moderator Manager", "users", default={})
        data = file.load()
        
        if str(member.id) not in data:
            await ctx.send(embed=error_embed("This member is not a moderator", "Moderator Manager"))
            return
            
        mod_data = data[str(member.id)]
        embed = info_embed(title=f"Moderator Information - {get_name(member)}")
        
        current_role = ctx.guild.get_role(mod_data["currentRole"])
        added_by = ctx.guild.get_member(mod_data["by"])
        
        embed.add_field(name="Current Role", value=current_role.mention, inline=False)
        embed.add_field(name="Since", value=mod_data["since"], inline=False)
        embed.add_field(name="Added By", value=added_by.mention if added_by else "Unknown", inline=False)
        
        if mod_data["pastRoles"]:
            past_roles = [ctx.guild.get_role(role_id).mention for role_id in mod_data["pastRoles"] if ctx.guild.get_role(role_id)]
            embed.add_field(name="Past Roles", value=" → ".join(past_roles), inline=False)
        
        await ctx.send(embed=embed)
    def cog_unload(self):
        """Cleanup when cog is unloaded"""
        if self.token_refresh_task:
            self.token_refresh_task.cancel()
    

def setup(client):
    client.add_cog(moderatormanager(client))