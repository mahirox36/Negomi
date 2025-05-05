from modules.Nexon import *
from nexon import Client, Member, ButtonStyle, Interaction
from nexon.ui import Button, View
from typing import Optional

class RoleAcceptView(View):
    def __init__(self, guild_id: int, client: Client, inviter: Member, role_key: str):
        super().__init__(timeout=600)  # 10 minute timeout
        self.guild_id = guild_id
        self.client = client
        self.inviter = inviter
        self.role_key = role_key
        self.timed_out = False
        
        # Add buttons
        self.accept_button = Button(
            label="✅ Accept",
            style=ButtonStyle.green,
            custom_id=f"role_accept_{role_key}"
        )
        self.decline_button = Button(
            label="❌ Decline",
            style=ButtonStyle.red,
            custom_id=f"role_decline_{role_key}"
        )
        
        self.accept_button.callback = self.accept_callback
        self.decline_button.callback = self.decline_callback
        
        self.add_item(self.accept_button)
        self.add_item(self.decline_button)

    async def accept_callback(self, interaction: Interaction):
        """Handle role accept"""
        if not (guild := self.client.get_guild(self.guild_id)):
            await interaction.response.send_message(
                embed=Embed.Error("Server not found"),
                ephemeral=True
            )
            return
        if not interaction.user:
            await interaction.response.send_message(
                embed=Embed.Error("User not found"),
                ephemeral=True
            )
            return
            

        feature = await Feature.get_guild_feature(self.guild_id, "custom_roles")
        data = feature.get_global("MembersRoles", {})
        
        # Verify role still exists
        if not (role_entry := data.get(self.role_key)):
            await interaction.response.send_message(
                embed=Embed.Error("This role no longer exists"),
                ephemeral=True
            )
            return

        # Check member limit
        max_members = role_entry["settings"].get("max_members", 10)
        if len(role_entry["members"]) >= max_members:
            await interaction.response.send_message(
                embed=Embed.Error("This role has reached its member limit"),
                ephemeral=True
            )
            # Notify the role owner
            if owner := guild.get_member(int(role_entry["owner_id"])):
                await owner.send(
                    embed=Embed.Error(
                        f"Could not add {interaction.user.mention} to role - member limit reached"
                    )
                )
            return

        # Add member to role
        role_entry["members"].append(str(interaction.user.id))
        data[self.role_key] = role_entry
        await feature.save()

        # Add Discord role
        if member := guild.get_member(interaction.user.id):
            if role := guild.get_role(role_entry["role_id"]):
                try:
                    await member.add_roles(role)
                    
                    # Notify both users
                    await interaction.response.send_message(
                        embed=Embed.Info(
                            title=f"Joined {self.inviter.display_name}'s Role",
                            description=f"You've been added to the role '{role.name}'"
                        ),
                        ephemeral=True
                    )
                    
                    if owner := guild.get_member(int(role_entry["owner_id"])):
                        await owner.send(
                            embed=Embed.Info(
                                f"{interaction.user.mention} accepted your role invitation"
                            )
                        )
                except:
                    await interaction.response.send_message(
                        embed=Embed.Error("Failed to add role. Please contact the server admin."),
                        ephemeral=True
                    )
                    return
        
        # Disable buttons after accepting
        self.accept_button.disabled = True
        self.decline_button.disabled = True
        if not interaction.message:
            await interaction.response.send_message(
                embed=Embed.Error("Message not found"),
                ephemeral=True
            )
            return
        await interaction.message.edit(view=self)

    async def decline_callback(self, interaction: Interaction):
        """Handle role decline"""
        # Notify the role owner
        if not interaction.user:
            await interaction.response.send_message(
                embed=Embed.Error("User not found"),
                ephemeral=True
            )
            return 
        if guild := self.client.get_guild(self.guild_id):
            feature = await Feature.get_guild_feature(self.guild_id, "custom_roles")
            data = feature.get_global("MembersRoles", {})
            
            if role_entry := data.get(self.role_key):
                if owner := guild.get_member(int(role_entry["owner_id"])):
                    await owner.send(
                        embed=Embed.Info(
                            f"{interaction.user.mention} declined your role invitation"
                        )
                    )

        await interaction.response.send_message(
            embed=Embed.Info("You declined the role invitation"),
            ephemeral=True
        )
        
        # Disable buttons after declining
        self.accept_button.disabled = True
        self.decline_button.disabled = True
        if not interaction.message:
            await interaction.response.send_message(
                embed=Embed.Error("Message not found"),
                ephemeral=True
            )
            return
        await interaction.message.edit(view=self)

    async def on_timeout(self):
        """Handle view timeout"""
        self.timed_out = True
        self.accept_button.disabled = True
        self.decline_button.disabled = True

        # Notify the role owner
        if guild := self.client.get_guild(self.guild_id):
            feature = await Feature.get_guild_feature(self.guild_id, "custom_roles")
            data = feature.get_global("MembersRoles", {})
            
            if role_entry := data.get(self.role_key):
                if owner := guild.get_member(int(role_entry["owner_id"])):
                    await owner.send(
                        embed=Embed.Info(
                            "A role invitation expired without response"
                        )
                    )