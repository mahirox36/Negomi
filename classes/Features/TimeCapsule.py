import re
from modules.Nexon import *

class timeCapsule(commands.Cog):
    def __init__(self, client:Bot):
        self.client = client
    #commands: add, delete, 
    @slash_command("time", integration_types=[
        IntegrationType.user_install,
        IntegrationType.guild_install
    ],
    contexts=[
        InteractionContextType.guild,
        InteractionContextType.bot_dm,
        InteractionContextType.private_channel
    ])
    async def timeCommand(self, ctx: init):
        pass
    @timeCommand.subcommand("capsule")
    async def capsule(self, ctx: init):
        pass
    
    @capsule.subcommand("create", "Create a new Time Capsule, when the time comes it will be sent in your DM", cooldown=120)
    @cooldown(120)
    async def create(self, ctx: init, message:str, year: int, month: int, day: int):
        await ctx.response.defer(ephemeral=True)
        if not ctx.user:
            return await ctx.send(embed=Embed.Error("You must be a user to use this command"))
        links = re.findall(r"https?://(?:www\.)?([a-zA-Z0-9.-]+)", message)
        if links:
            await ctx.send(embed=Embed.Error("You cannot send Links"))
        now = utils.utcnow().replace(tzinfo=None)
        try:
            target_date = datetime(year, month, day)
        except ValueError:
            return await ctx.send(embed=Embed.Error("Invalid date! Please enter a valid year, month, and day."))
        if target_date.replace(tzinfo=timezone.utc) <= now:
            return await ctx.send(embed=Embed.Error("The date must be in the future!"))
        feature = await Feature.get_global_feature("TimeCapsule", default=[])

        feature.get_setting(default=[]).append({
            "ID": ctx.user.id,
            "message": message,
            "time": target_date.isoformat()
        })
        await feature.save()
        await ctx.send(embed=Embed.Info(title="Saved",description="Your Time Capsule saved"))
    
    @capsule.subcommand("list", "List of your time Capsules", cooldown=5)
    @cooldown(5)
    async def listTime(self, ctx: init):
        await ctx.response.defer(ephemeral=True)
        if not ctx.user:
            return await ctx.send(embed=Embed.Error("You must be a user to use this command"))
        feature = await Feature.get_global_feature("TimeCapsule", default=[])
        data = []
        for time in feature.get_setting(default=[]):
            if time["ID"] == ctx.user.id:
                data.append(time)
        if data:
            await ctx.send(embed=Embed.Info(
                         title="List of time Capsules",
                         description=
                         "\n".join(f"{count}. <t:{int(datetime.fromisoformat(item["time"]).timestamp())}:R> {f"||{get_by_percent(20,item["message"],returns="*No Spoilers*")}...||" }" for count, item in enumerate(data, start=1))
                         )
                     )
        else:
            await ctx.send(embed=Embed.Info(
                         title="List of time Capsules",
                         description="You don't have any time Capsules")
                     )
            
    @commands.Cog.listener()
    async def on_ready(self):
        await self.check_time_capsules()
        self.check_capsules_loop.start()

    @tasks.loop(hours=24)
    async def check_capsules_loop(self):
        await self.check_time_capsules()

    async def check_time_capsules(self):
        feature = await Feature.get_global_feature("TimeCapsule", default=[])
        now = utils.utcnow().replace(tzinfo=None)
        updated_data = []

        for capsule in feature.get_setting(default=[]):
            try:
                target_date = datetime.fromisoformat(capsule["time"])
            except ValueError:
                # Skip invalid date formats
                continue

            if target_date <= now:
                try:
                    user = await self.client.fetch_user(capsule["ID"])
                    if user:
                        await user.send(
                            embed=Embed.Info(
                                title="Time Capsule",
                                description=f"📜 **Here's your message from the past:**\n\n{capsule['message']}"
                            )
                        )
                except Exception as e:
                    # Log the error for debugging purposes
                    print(f"Failed to send Time Capsule to user {capsule['ID']}: {e}")
            else:
                updated_data.append(capsule)

        # Update the feature settings with remaining capsules
        await feature.replace_settings(updated_data)
    
    async def cog_application_command_error(self, ctx: Interaction, error: ApplicationError):
        command_name = ctx.application_command.qualified_name if ctx.application_command else "Unknown Command"
        Logger = Logs.Logger(guild=None, user=ctx.user, cog=self, command=command_name)
        await Logger.error(
            f"Error occurred in TimeCapsule commands: {error}",
            context={
                "guild": ctx.guild.name if ctx.guild else "non-guild",
                "user": ctx.user.name if ctx.user else "bot",
                "channel": ctx.channel.name if ctx.channel and not isinstance(ctx.channel, PartialMessageable) else "DM",
            },
        )
    

def setup(client):
    client.add_cog(timeCapsule(client))