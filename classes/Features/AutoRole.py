from modules.Nexon import *

class AutoRole(commands.Cog):
    def __init__(self, client:Bot):
        self.client = client

    @slash_command(name="auto",default_member_permissions=Permissions(administrator=True))
    async def auto(self,ctx:init):
        pass
    @auto.subcommand(name="role")
    async def role(self,ctx:init):
        pass

    @role.subcommand(name="setup",
                   description="Setup auto role for members and bots")
    @feature()
    async def setup_auto_role(self,ctx:init,member_role:Role,bot_role:Role = None):
        file= DataManager("Auto role", ctx.guild_id)
        file.data = {
            "member_role":member_role.id,
            "bot_role"   :bot_role.id if bot_role else None
        }
        file.save()
        
        await ctx.send(embed=Embed.Info("Auto role setup successfully"))
        
            
    @commands.Cog.listener()
    async def on_member_join(self, member:Member):
        try:await check_feature_inside(member.guild.id, self)
        except: return
        guild = member.guild
        try:
            if DataManager("Auto role", member.guild_id).exists():
                data = DataManager("Auto role", member.guild_id).load()
                if data == None:
                    return
                if (member.bot) and (data["bot_role"] != None):
                    await member.add_roles(guild.get_role(data["bot_role"]))
                if member.bot == False:
                    await member.add_roles(guild.get_role(data["member_role"]))
        except:
            return


def setup(client):
    client.add_cog(AutoRole(client))