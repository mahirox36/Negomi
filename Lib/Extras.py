import time
from nextcord import Interaction, Member
from nextcord.ext import commands
from typing import Callable, Any, List

class SlashCommandOnCooldown(Exception):
    def __init__(self, retry_after: float) -> None:
        super().__init__()
        self.retry_after = retry_after

def setup_hybrid(bot: commands.Bot):
    """
    Register commands on the bot instance.
    """
    def hybrid(name: str, description: str, aliases: List[str] = [], **kwargs: Any):
        def decorator(func: Callable[..., Any]):
            # Register text command
            bot.add_command(commands.Command(func, name="_"+name, **kwargs))
            
            # Register slash command
            bot.slash_command(name=name, description=description)(func)
            
            return func
        return decorator
    
    return hybrid


cooldowns= {}
async def cooldown(cooldown_time: int,user:Member,name):
    global cooldowns
    user_id = user.id
    
    if name not in cooldowns:
        cooldowns[name] = {}
    # Check if the user is on cooldown
    if user_id in cooldowns[name]:
        time_left = cooldowns[name][user_id] - time.time()
        if time_left > 0:
            raise SlashCommandOnCooldown(time_left)
    # Set a new cooldown for the user
    cooldowns[name][user_id] = time.time() + cooldown_time
    return
    
def userCTX(ctx:Interaction):
    try:
        ctx.user = ctx.author
    except:
        pass
    return ctx
