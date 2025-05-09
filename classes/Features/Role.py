from modules.Nexon import *
from modules.config import Color
from typing import Optional, Union
from nexon import Client, Member, User, ButtonStyle, Interaction, Role, Guild
from nexon.ui import Button, View
from better_profanity import profanity
from nexon.ext import commands
import uuid


class Request(View):
    def __init__(
        self,
        guild_id: int,
        client: commands.Bot,
        fromUser: Member,
        role_key: Optional[str] = None,
    ):
        super().__init__(timeout=None)
        self.accept_button = Button(label="✅ Accept", style=ButtonStyle.green)
        self.accept_button.callback = self.accept_callback
        self.add_item(self.accept_button)
        self.guild_id = guild_id
        self.client = client
        self.fromUser = fromUser
        self.role_key = role_key

    async def accept_callback(self, interaction: Interaction):
        if not (guild := self.client.get_guild(self.guild_id)):
            return

        feature = await Feature.get_guild_feature(self.guild_id, "custom_roles")
        data: dict = feature.get_global("MembersRoles", {})
        if not (role_entry := data.get(self.role_key)):
            return

        if not interaction.user:
            return

        role_entry["members"].append(f"{interaction.user.id}")
        data[self.role_key] = role_entry
        await feature.save()

        if not (member := guild.get_member(interaction.user.id)):
            return

        if not (role := guild.get_role(role_entry["role_id"])):
            return

        await member.add_roles(role)

        await interaction.response.send_message(
            embed=Embed.Info(
                title=f"You Joined {self.fromUser.display_name}'s Role",
                description=f"In {guild.name} and Role {role.name}",
            ),
            ephemeral=True,
        )


# Settings:
#  - creation_mode: "everyone" | "boosters" | "specific_roles"
#  - not_allowed: Custom Not Allowed Words List
#  - allowed_roles: List of role IDs that can create roles (when creation_mode is "specific_roles")
#  - max_roles_per_user: Maximum number of roles a user can create (default: 1)
#  - can_hoist: Whether users can make their roles appear separately in the member list (default: true)
#  - can_mention: Whether users can make their roles mentionable (default: false)
#  - color_restriction: "all" | "preset" | "none" - Controls color options (default: "all")
#  - max_members_per_role: Maximum number of members that can be added to a custom role (default: 10)
#  - require_confirmation: Whether role additions require confirmation from the target user (default: true)
#  - parent_role_id: Role ID under which new roles will be created


class Roles(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.colors = {
            "Red": Color("#FF0000"),
            "Green": Color("#008000"),
            "Blue": Color("#0000FF"),
            "Yellow": Color("#FFFF00"),
            "Cyan": Color("#00FFFF"),
            "Magenta": Color("#FF00FF"),
            "Orange": Color("#FFA500"),
            "Purple": Color("#800080"),
            "Pink": Color("#FFC0CB"),
            "Brown": Color("#A52A2A"),
            "Gray": Color("#808080"),
            "Black": Color("#000001"),
            "White": Color("#FFFFFF"),
            "Lime": Color("#00FF00"),
            "Olive": Color("#808000"),
            "Navy": Color("#000080"),
            "Teal": Color("#008080"),
            "Maroon": Color("#800000"),
            "Silver": Color("#C0C0C0"),
            "Gold": Color("#FFD700"),
            "Coral": Color("#FF7F50"),
            "Salmon": Color("#FA8072"),
            "Turquoise": Color("#40E0D0"),
            "Indigo": Color("#4B0082"),
            "Violet": Color("#EE82EE"),
        }

    @slash_command(name="role")
    async def role(self, ctx: init):
        pass

    async def check_user_roles(
        self, ctx: Interaction, feature: Feature
    ) -> tuple[dict, list, int]:
        """Helper function to check user's custom roles"""
        data = feature.get_global("MembersRoles", {})
        settings = feature.get_setting()
        max_roles = settings.get("max_roles_per_user", 1)
        if not ctx.user:
            return data, [], max_roles

        user_roles = [r for r in data.values() if r.get("owner_id") == str(ctx.user.id)]
        return data, user_roles, max_roles

    @role.subcommand(name="create", description="Create a custom role")
    async def create_role(
        self,
        ctx: Interaction,
        name: str,
        color: str = SlashOption(
            "color",
            "Type Hex code or one of these colors",
            required=True,
            autocomplete=True,
        ),
        hoist: bool = SlashOption(
            "hoist",
            "Display members separately in the member list",
            required=False,
            default=None,
        ),
        mentionable: bool = SlashOption(
            "mentionable",
            "Allow anyone to @mention this role",
            required=False,
            default=None,
        ),
    ):
        if not ctx.guild or not ctx.user or isinstance(ctx.user, User):
            return await ctx.send(embed=Embed.Error("You are not in a server"))
        

        # Get feature settings and data
        feature = await Feature.get_guild_feature(ctx.guild.id, "custom_roles")
        data, user_roles, max_roles = await self.check_user_roles(ctx, feature)
        settings = feature.get_setting()
        if not feature.enabled:
            return await ctx.send(
                embed=Embed.Error("This feature is disabled"), ephemeral=True
            )

        # Check if user has reached their role limit
        if len(user_roles) >= max_roles:
            return await ctx.response.send_message(
                embed=Embed.Error(f"You can only create up to {max_roles} role(s)"),
                ephemeral=True,
            )

        # Check creation mode permissions
        mode = settings.get("creation_mode", "everyone")
        if mode == "boosters" and not getattr(ctx.user, "premium_since", None):
            return await ctx.response.send_message(
                embed=Embed.Error("Only server boosters can create roles"),
                ephemeral=True,
            )
        elif mode == "specific_roles":
            allowed_roles = settings.get("allowed_roles", [])
            user_role_ids = [role.id for role in ctx.user.roles]
            if not any(str(role_id) in allowed_roles for role_id in user_role_ids):
                return await ctx.response.send_message(
                    embed=Embed.Error("You don't have the required roles"),
                    ephemeral=True,
                )

        # Check name against prohibited words
        if name.lower() in settings.get(
            "not_allowed", []
        ) or profanity.contains_profanity(name.lower()):
            return await ctx.send(
                embed=Embed.Error("This word/name isn't allowed"), ephemeral=True
            )

        # Handle color restrictions
        color_restriction = settings.get("color_restriction", "all")
        if color_restriction == "none":
            color_obj = Color("#99AAB5")
        elif color_restriction == "preset" and color.capitalize() not in self.colors:
            return await ctx.response.send_message(
                embed=Embed.Error("You can only use preset colors"), ephemeral=True
            )
        else:
            try:
                if color.capitalize() in self.colors:
                    color_obj = self.colors[color.capitalize()]
                else:
                    try:
                        color_value = color if color.startswith("#") else f"#{color}"
                        color_obj = Color(color_value)
                    except Exception:
                        return await ctx.send(
                            embed=Embed.Error("Invalid color format"), ephemeral=True
                        )
            except (KeyError, ValueError):
                return await ctx.response.send_message(
                    embed=Embed.Error("Invalid color format"), ephemeral=True
                )

        # Check role properties permissions
        can_hoist = settings.get("can_hoist", True)
        can_mention = settings.get("can_mention", False)

        if hoist is None:
            hoist = can_hoist
        elif hoist and not can_hoist:
            return await ctx.response.send_message(
                embed=Embed.Error("You cannot hoist roles"), ephemeral=True
            )

        if mentionable is None:
            mentionable = can_mention
        elif mentionable and not can_mention:
            return await ctx.response.send_message(
                embed=Embed.Error("You cannot make roles mentionable"), ephemeral=True
            )

        # Create the role under the specified parent role if set
        parent_role_id = settings.get("parent_role_id")
        
        role = await ctx.guild.create_role(
            reason=f"{ctx.user.name} created a custom role",
            name=name,
            color=color_obj.value,
            hoist=hoist,
            mentionable=mentionable,
            
        )

        if parent_role_id:
            try:
                parent_role = ctx.guild.get_role(int(parent_role_id))
                if parent_role:
                    # Place the new role just below the parent role
                    positions = {
                        role: parent_role.position - 1
                    }
                    await ctx.guild.edit_role_positions(positions=positions) # type: ignore
            except Exception as e:
                print(f"Failed to set role position: {e}")

        await ctx.user.add_roles(role)

        # Generate unique ID for the role entry
        role_id = str(uuid.uuid4())

        # Add role to database
        data[role_id] = {
            "owner": True,
            "owner_id": str(ctx.user.id),
            "role_id": role.id,
            "members": [],
            "settings": {
                "max_members": settings.get("max_members_per_role", 10),
                "require_confirmation": settings.get("require_confirmation", True),
            },
            "created_at": str(utils.utcnow()),
        }

        await feature.set_global("MembersRoles", data)

        await ctx.send(embed=Embed.Info(f"Created role: {name}"), ephemeral=True)

    @role.subcommand(name="edit", description="Edit one of your custom roles")
    async def role_edit(
        self,
        ctx: Interaction,
        role_name: str = SlashOption(
            "role", "Select which role to edit", autocomplete=True
        ),
        new_name: str = SlashOption("name", "New role name", required=False),
        color: str = SlashOption(
            "color", "New role color", required=False, autocomplete=True
        ),
        hoist: bool = SlashOption(
            "hoist", "Display members separately", required=False
        ),
        mentionable: bool = SlashOption(
            "mentionable", "Allow @mentions", required=False
        ),
    ):
        if not ctx.guild:
            return await ctx.send(embed=Embed.Error("Command must be used in a server"))
        if not ctx.user or isinstance(ctx.user, User):
            return await ctx.send(embed=Embed.Error("You are not in a server"))
        

        feature = await Feature.get_guild_feature(ctx.guild.id, "custom_roles")
        data = feature.get_global("MembersRoles", {})
        settings = feature.get_setting()

        if not feature.enabled:
            return await ctx.send(
                embed=Embed.Error("This feature is disabled"), ephemeral=True
            )
        # Find the role entry
        role_entry = None
        role_key = None
        for key, entry in data.items():
            role = ctx.guild.get_role(entry["role_id"])
            if not role:
                role = await ctx.guild.fetch_role(entry["role_id"])
            if entry.get("owner_id") == str(ctx.user.id) and role.name == role_name:
                role_entry = entry
                role_key = key
                break

        if not role_entry:
            return await ctx.send(
                embed=Embed.Error("You don't own this role"), ephemeral=True
            )

        role = ctx.guild.get_role(role_entry["role_id"])
        if not role:
            return await ctx.send(embed=Embed.Error("Role not found"), ephemeral=True)

        updates = {}

        # Handle name change
        if new_name:
            if new_name.lower() in settings.get(
                "not_allowed", []
            ) or profanity.contains_profanity(new_name.lower()):
                return await ctx.send(
                    embed=Embed.Error("This name isn't allowed"), ephemeral=True
                )
            updates["name"] = new_name

        # Handle color change
        if color:
            color_restriction = settings.get("color_restriction", "all")
            if color_restriction == "none":
                return await ctx.send(
                    embed=Embed.Error("Color customization is disabled"), ephemeral=True
                )
            elif color_restriction == "preset" and color.capitalize() not in self.colors:
                return await ctx.send(
                    embed=Embed.Error("You can only use preset colors"), ephemeral=True
                )
            else:
                try:
                    if color.capitalize() in self.colors:
                        color_obj = self.colors[color.capitalize()]
                    else:
                        try:
                            color_value = color if color.startswith("#") else f"#{color}"
                            color_obj = Color(color_value)
                        except Exception:
                            return await ctx.send(
                                embed=Embed.Error("Invalid color format"), ephemeral=True
                            )
                except (KeyError, ValueError):
                    return await ctx.response.send_message(
                        embed=Embed.Error("Invalid color format"), ephemeral=True
                    )

        # Handle permission-based properties
        if hoist is not None:
            if not settings.get("can_hoist", True) and hoist:
                return await ctx.send(
                    embed=Embed.Error("You cannot hoist roles"), ephemeral=True
                )
            updates["hoist"] = hoist

        if mentionable is not None:
            if not settings.get("can_mention", False) and mentionable:
                return await ctx.send(
                    embed=Embed.Error("You cannot make roles mentionable"),
                    ephemeral=True,
                )
            updates["mentionable"] = mentionable

        if not updates:
            return await ctx.send(
                embed=Embed.Error("No changes specified"), ephemeral=True
            )

        # Apply updates
        await role.edit(**updates)
        await ctx.send(embed=Embed.Info("Role updated successfully"), ephemeral=True)

    @role.subcommand(name="add", description="Add someone to your custom role")
    async def role_add(
        self,
        ctx: Interaction,
        member: Member,
        role_name: str = SlashOption(
            "role", "Select which role to add them to", autocomplete=True
        ),
    ):
        if not ctx.guild:
            return await ctx.send(embed=Embed.Error("Command must be used in a server"))

        if member.bot:
            return await ctx.send(
                embed=Embed.Error("You cannot add bots to custom roles"), ephemeral=True
            )
        if not ctx.user or isinstance(ctx.user, User):
            return await ctx.send(embed=Embed.Error("You are not in a server"))

        feature = await Feature.get_guild_feature(ctx.guild.id, "custom_roles")
        data = feature.get_global("MembersRoles", {})

        if not feature.enabled:
            return await ctx.send(
                embed=Embed.Error("This feature is disabled"), ephemeral=True
            )
        
        # Find the role entry
        role_entry = None
        role_key = None
        for key, entry in data.items():
            role = ctx.guild.get_role(entry["role_id"])
            if not role:
                role = await ctx.guild.fetch_role(entry["role_id"])
            if entry.get("owner_id") == str(ctx.user.id) and role.name == role_name:
                role_entry = entry
                role_key = key
                break

        if not role_entry:
            return await ctx.send(
                embed=Embed.Error("You don't own this role"), ephemeral=True
            )

        role = ctx.guild.get_role(role_entry["role_id"])
        if not role:
            return await ctx.send(embed=Embed.Error("Role not found"), ephemeral=True)

        # Check member limit
        max_members = role_entry["settings"].get("max_members", 10)
        if len(role_entry["members"]) >= max_members:
            return await ctx.send(
                embed=Embed.Error(
                    f"This role has reached its member limit ({max_members})"
                ),
                ephemeral=True,
            )

        # Handle confirmation requirement
        if role_entry["settings"].get("require_confirmation", True):
            view = Request(ctx.guild.id, self.client, ctx.user, role_key)
            try:
                await member.send(
                    embed=Embed.Info(
                        title=f"Role Invitation from {ctx.user.display_name}",
                        description=f"Would you like to join the role '{role.name}'?",
                    ),
                    view=view,
                )
                await ctx.send(
                    embed=Embed.Info(f"Invitation sent to {member.mention}"),
                    ephemeral=True,
                )
            except:
                await ctx.send(
                    embed=Embed.Error(
                        "Could not DM the user. They may have DMs disabled."
                    ),
                    ephemeral=True,
                )
        else:
            # Direct addition
            role_entry["members"].append(str(member.id))
            await member.add_roles(role)
            data[role_key] = role_entry
            await feature.set_global("MembersRoles", data)

            await ctx.send(
                embed=Embed.Info(f"Added {member.mention} to {role.name}"),
                ephemeral=True,
            )

    @role.subcommand(name="remove", description="Remove someone from your custom role")
    async def role_remove(
        self,
        ctx: Interaction,
        member: Member,
        role_name: str = SlashOption(
            "role", "Select which role to remove them from", autocomplete=True
        ),
    ):
        if not ctx.guild:
            return await ctx.send(embed=Embed.Error("Command must be used in a server"))
        if not ctx.user or isinstance(ctx.user, User):
            return await ctx.send(embed=Embed.Error("You are not in a server"))

        feature = await Feature.get_guild_feature(ctx.guild.id, "custom_roles")
        data = feature.get_global("MembersRoles", {})
        
        if not feature.enabled:
            return await ctx.send(
                embed=Embed.Error("This feature is disabled"), ephemeral=True
            )
        # Find the role entry
        role_entry = None
        role_key = None
        for key, entry in data.items():
            role = ctx.guild.get_role(entry["role_id"])
            if not role:
                role = await ctx.guild.fetch_role(entry["role_id"])
            if entry.get("owner_id") == str(ctx.user.id) and role.name == role_name:
                role_entry = entry
                role_key = key
                break

        if not role_entry:
            return await ctx.send(
                embed=Embed.Error("You don't own this role"), ephemeral=True
            )

        role = ctx.guild.get_role(role_entry["role_id"])
        if not role:
            return await ctx.send(embed=Embed.Error("Role not found"), ephemeral=True)

        if str(member.id) not in role_entry["members"]:
            return await ctx.send(
                embed=Embed.Error(f"{member.mention} is not in this role"),
                ephemeral=True,
            )

        # Remove member
        role_entry["members"].remove(str(member.id))
        await member.remove_roles(role)
        data[role_key] = role_entry
        await feature.set_global("MembersRoles", data)

        await ctx.send(
            embed=Embed.Info(f"Removed {member.mention} from {role.name}"),
            ephemeral=True,
        )

    @role.subcommand(name="delete", description="Delete one of your custom roles")
    async def role_delete(
        self,
        ctx: Interaction,
        role_name: str = SlashOption(
            "role", "Select which role to delete", autocomplete=True
        ),
    ):
        if not ctx.guild:
            return await ctx.send(embed=Embed.Error("Command must be used in a server"))
        if not ctx.user or isinstance(ctx.user, User):
            return await ctx.send(embed=Embed.Error("You are not in a server"))

        feature = await Feature.get_guild_feature(ctx.guild.id, "custom_roles")
        data = feature.get_global("MembersRoles", {})

        if not feature.enabled:
            return await ctx.send(
                embed=Embed.Error("This feature is disabled"), ephemeral=True
            )
        
        # Find the role entry
        role_entry = None
        role_key = None
        for key, entry in data.items():
            role = ctx.guild.get_role(entry["role_id"])
            if not role:
                role = await ctx.guild.fetch_role(entry["role_id"])
            if entry.get("owner_id") == str(ctx.user.id) and role.name == role_name:
                role_entry = entry
                role_key = key
                break

        if not role_entry:
            return await ctx.send(
                embed=Embed.Error("You don't own this role"), ephemeral=True
            )

        role = ctx.guild.get_role(role_entry["role_id"])
        if role:
            await role.delete(reason=f"Deleted by owner {ctx.user.name}")

        # Remove from database
        del data[role_key]
        await feature.set_global("MembersRoles", data)

        await ctx.send(
            embed=Embed.Info(f"Deleted role: {role_name}"), ephemeral=True
        )

    @create_role.on_autocomplete("color")
    @role_edit.on_autocomplete("color")
    async def color_autocomplete(self, interaction: Interaction, current: str):
        colors = list(self.colors.keys())
        return [name for name in colors if current.lower() in name.lower()] or (
            [current] if current.startswith("#") else []
        )

    @role_edit.on_autocomplete("role_name")
    @role_add.on_autocomplete("role_name")
    @role_remove.on_autocomplete("role_name")
    @role_delete.on_autocomplete("role_name")
    async def role_autocomplete(self, interaction: Interaction, current: str):
        if not interaction.guild or not interaction.user or isinstance(interaction.user, User):
            return []

        feature = await Feature.get_guild_feature(interaction.guild.id, "custom_roles")
        data = feature.get_global("MembersRoles", {})

        user_roles = []
        for entry in data.values():
            if entry.get("owner_id") == str(interaction.user.id):
                if role := interaction.guild.get_role(entry["role_id"]):
                    user_roles.append(role.name)

        return [name for name in user_roles if current.lower() in name.lower()]


def setup(client: commands.Bot):
    client.add_cog(Roles(client))
