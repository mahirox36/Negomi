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
    
    @capsule.subcommand("create", "Create a new Time Capsule, when the time comes it will be sent in your DM")
    async def create(self, ctx: init, message:str, year: int, month: int, day: int):
        await ctx.response.defer(ephemeral=True)
        if not ctx.user:
            return await ctx.send(embed=Embed.Error("You must be a user to use this command"))
        links = re.findall(r"https?://(?:www\.)?([a-zA-Z0-9.-]+)", message)
        if links:
            await ctx.send(embed=Embed.Error("You cannot send Links"))
        now = datetime.now()
        try:
            target_date = datetime(year, month, day)
        except ValueError:
            return await ctx.send(embed=Embed.Error("Invalid date! Please enter a valid year, month, and day."))
        if target_date <= now:
            return await ctx.send(embed=Embed.Error("The date must be in the future!"))
        feature = await Feature.get_global_feature("TimeCapsule", default=[])
        feature.settings.append({
            "ID":ctx.user.id,
            "message":message,
            "time": target_date.isoformat()
        })
        await feature.save()
        await ctx.send(embed=Embed.Info(title="Saved",description="Your Time Capsule saved"))
    
    @capsule.subcommand("list", "List of your time Capsules")
    async def listTime(self, ctx: init):
        await ctx.response.defer(ephemeral=True)
        if not ctx.user:
            return await ctx.send(embed=Embed.Error("You must be a user to use this command"))
        feature = await Feature.get_global_feature("TimeCapsule", default=[])
        data = []
        for time in feature.settings:
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
        now = datetime.now()
        updated_data = []

        for capsule in feature.settings:
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
        feature.settings = updated_data
        await feature.save()
    
    

def setup(client):
    client.add_cog(timeCapsule(client))