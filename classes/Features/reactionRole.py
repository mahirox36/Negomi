from modules.Nexon import *
from nexon.errors import NotFound

logger = logging.getLogger(__name__)


# Settings:
# Reaction/Buttons
# remove reaction when role is added: boolean: True
# able to unselect role: boolean: True


class ReactionRole(commands.Cog):
    def __init__(self, client: Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: Reaction, user: Union[Member, User]):
        reaction_id = (
            reaction.emoji if isinstance(reaction.emoji, str) else reaction.emoji.id
        )
        if user.bot:
            return
        guild = reaction.message.guild
        if guild is None:
            return
        if isinstance(user, User):
            return
        Logger = Logs.Logger(guild=guild, user=user, cog=self)

        feature = await Feature.get_guild_feature_or_none(
            feature_name="reaction_role",
            guild_id=guild.id,
        )
        if not feature:
            return
        if not feature.settings.get("enabled", False):
            return
        if reaction_id is None:
            await Logger.warning(
                "ReactionRole: Reaction ID is None. This may be due to a custom emoji. Please check the settings.",
                context={
                    "reaction": reaction_id,
                },
            )
            return
        # Example settings structure for customization:
        # {
        #     str(message.id): {
        #         "reactions": {
        #             str(reaction_id): {
        #                 "role_id": role.id,
        #                 "remove_reaction": True,  # Whether to remove the reaction after adding the role
        #                 "allow_unselect": True   # Whether the user can unselect the role by removing the reaction
        #             }
        #         },
        #         "default_role": None  # Optional: Default role to assign if no reaction matches
        #     }
        # }

        # Get Matched Reaction
        if reaction.message.id not in feature.get_setting("messages", {}):
            return
        message_settings = feature.get_setting("messages", {}).get(
            str(reaction.message.id), {}
        )
        reactions = message_settings.get("reactions", {})
        reaction_settings = reactions.get(str(reaction_id), None)
        if reaction_settings is None:
            return
        role_id = reaction_settings.get("role_id")
        remove_reaction = reaction_settings.get("remove_reaction", True)
        allow_unselect = reaction_settings.get("allow_unselect", True)
        role = guild.get_role(role_id)
        if not role:
            try:
                role = await guild.fetch_role(role_id)
            except NotFound:
                await Logger.warning(
                    "ReactionRole: Role not found. Please check the role ID. Message ID getting removed.",
                    context={
                        "role_id": role_id,
                        "message_id": reaction.message.id,
                    },
                )
                feature.get_setting("messages", {}).pop(str(reaction.message.id), None)
                await feature.save()
                return
        if role in user.roles:
            if allow_unselect:
                await user.remove_roles(role, reason="ReactionRole: Unselected role")
                if remove_reaction:
                    await reaction.remove(user)
                await Logger.info(
                    "ReactionRole: Removed role from user.",
                    context={
                        "role_id": role_id,
                        "user_id": user.id,
                    },
                )
            else:
                try:
                    await user.send(
                        embed=Embed().Warning(
                            title="ReactionRole",
                            description="You already have this role. Please remove it manually.",
                        )
                    )
                except Exception as e:
                    await Logger.error(
                        "ReactionRole: Failed to send DM to user.",
                        context={
                            "user_id": user.id,
                            "error": str(e),
                        },
                    )
        else:
            await user.add_roles(role, reason="ReactionRole: Added role")
            if remove_reaction:
                await reaction.remove(user)
            await Logger.info(
                "ReactionRole: Added role to user.",
                context={
                    "role_id": role_id,
                    "user_id": user.id,
                },
            )

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction: Reaction, user: Union[Member, User]):
        reaction_id = (
            reaction.emoji if isinstance(reaction.emoji, str) else reaction.emoji.id
        )
        if user.bot:
            return
        guild = reaction.message.guild
        if guild is None:
            return
        if isinstance(user, User):
            return
        Logger = Logs.Logger(guild=guild, user=user, cog=self)

        feature = await Feature.get_guild_feature_or_none(
            feature_name="reaction_role",
            guild_id=guild.id,
        )
        if not feature:
            return
        if not feature.settings.get("enabled", False):
            return
        if reaction_id is None:
            await Logger.warning(
                "ReactionRole: Reaction ID is None. This may be due to a custom emoji. Please check the settings.",
                context={
                    "reaction": reaction_id,
                },
            )
            return

        # Get Matched Reaction
        if reaction.message.id not in feature.get_setting("messages", {}):
            return
        message_settings = feature.get_setting("messages", {}).get(
            str(reaction.message.id), {}
        )
        reactions = message_settings.get("reactions", {})
        reaction_settings = reactions.get(str(reaction_id), None)
        allow_unselect = reaction_settings.get("allow_unselect", True)
        if reaction_settings is None:
            return
        role_id = reaction_settings.get("role_id")
        role = guild.get_role(role_id)
        if not role:
            try:
                role = await guild.fetch_role(role_id)
            except NotFound:
                await Logger.warning(
                    "ReactionRole: Role not found. Please check the role ID. Message ID getting removed.",
                    context={
                        "role_id": role_id,
                        "message_id": reaction.message.id,
                    },
                )
                feature.get_setting("messages", {}).pop(str(reaction.message.id), None)
                await feature.save()
                return
        if role in user.roles:
            if not allow_unselect:
                try:
                    await user.send(
                        embed=Embed().Warning(
                            title="ReactionRole",
                            description="You already have this role. Please remove it manually.",
                        )
                    )
                except Exception as e:
                    await Logger.error(
                        "ReactionRole: Failed to send DM to user.",
                        context={
                            "user_id": user.id,
                            "error": str(e),
                        },
                    )
            await user.remove_roles(role, reason="ReactionRole: Unselected role")
            await Logger.info(
                "ReactionRole: Removed role from user.",
                context={
                    "role_id": role_id,
                    "user_id": user.id,
                },
            )
        else:
            try:
                await user.send(
                    embed=Embed().Warning(
                        title="ReactionRole",
                        description="You don't have this role. Please select it again.",
                    )
                )
            except Exception as e:
                await Logger.error(
                    "ReactionRole: Failed to send DM to user.",
                    context={
                        "user_id": user.id,
                        "error": str(e),
                    },
                )


def setup(client):
    client.add_cog(ReactionRole(client))
