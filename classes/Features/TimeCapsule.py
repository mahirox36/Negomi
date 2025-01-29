import re
from modules.Nexon import *

class timeCapsule(commands.Cog):
    def __init__(self, client:Bot):
        self.client = client
    #commands: add, delete, 
    @slash_command("time")
    async def timeCommand(self, ctx: init):
        pass
    @timeCommand.subcommand("capsule")
    async def capsule(self, ctx: init):
        pass
    
    @capsule.subcommand("create", "Create a new Time Capsule, when the time comes it will be sent in your DM")
    async def create(self, ctx: init, message:str, year: int, month: int, day: int):
        await ctx.response.defer(ephemeral=True)
        links = re.findall(r"https?://(?:www\.)?([a-zA-Z0-9.-]+)", message)
        if links:
            await ctx.send(embed=error_embed("You cannot send Links"))
        now = datetime.now()
        try:
            target_date = datetime(year, month, day)
        except ValueError:
            return await ctx.send(embed=error_embed("Invalid date! Please enter a valid year, month, and day."))
        if target_date <= now:
            return await ctx.send(embed=error_embed("The date must be in the future!"))
        file = DataManager("TimeCapsule", default=[])
        file.append({
            "ID":ctx.user.id,
            "message":message,
            "time": target_date.isoformat()
        })
        file.save()
        await ctx.send(embed=info_embed(title="Saved",description="Your Time Capsule saved"))
    
    @capsule.subcommand("list", "List of your time Capsules")
    async def listTime(self, ctx: init):
        await ctx.response.defer(ephemeral=True)
        file = DataManager("TimeCapsule", default=[])
        data = []
        for time in file.data:
            if time["ID"] == ctx.user.id:
                data.append(time)
        if data:
            await ctx.send(embed=info_embed(
                         title="List of time Capsules",
                         description=
                         "\n".join(f"{count}. <t:{int(datetime.fromisoformat(item["time"]).timestamp())}:R> {f"||{get_by_percent(20,item["message"],returns="*No Spoilers*")}...||" }" for count, item in enumerate(data, start=1))
                         )
                     )
        else:
            await ctx.send(embed=info_embed(
                         title="List of time Capsules",
                         description="You don't have any time Capsules")
                     )
    
    

def setup(client):
    client.add_cog(timeCapsule(client))