from nextcord import Interaction
from nextcord.ext import commands
from typing import Callable, Any, List

def setup_hybrid(bot: commands.Bot):
    """
    Register commands on the bot instance.
    """
    def hybrid(name: str, description: str, aliases: List[str] = [], **kwargs: Any):
        def decorator(func: Callable[..., Any]):
            # Register text command
            bot.add_command(commands.Command(func, name=name, aliases=aliases, **kwargs))
            
            # Register slash command
            bot.slash_command(name=name, description=description)(func)
            
            return func
        return decorator
    
    return hybrid

def userCTX(ctx:Interaction):
    try:
        ctx.user = ctx.author
    except:
        pass
    return ctx
