import os
import nextcord #type: ignore
from nextcord.ext.commands import MissingPermissions
from nextcord import Interaction
from .Side import owner_id
from nextcord import Interaction as init
import random
import json


def check_permission(interaction:Interaction,**perms:bool) -> bool:
    invalid = set(perms) - set(nextcord.Permissions.VALID_FLAGS)
    if invalid:
        raise TypeError(f"Invalid permission(s): {', '.join(invalid)}")
    async def predicate(ctx:Interaction) -> bool:
        ch = ctx.channel
        permissions = ch.permissions_for(ctx.user)
        missing = [perm for perm, value in perms.items() if getattr(permissions, perm) != value]
        if not missing:
            return True
        await ctx.send("You Don't have permission to do that command",ephemeral=True)
        raise MissingPermissions(missing)
    return predicate(interaction)

def check_owner_permission(interaction:Interaction) -> bool:
    async def predicate(ctx:Interaction) -> bool:
        if ctx.user.id == owner_id:
            return True
        await ctx.send("You'r Not The Owner Of this Bot",ephemeral=True)
        raise MissingPermissions(ctx.user.name)
    return predicate(interaction)

def check_owner_permission_message(message:nextcord.Message) -> bool:
    async def predicate(ctx:Interaction) -> bool:
        if ctx.author.id == owner_id:
            return True
        return False
    return predicate(message)

def create_random_id(data) -> int:
    code = random.randint(1,99999999999999)
    for i in data:
        if code == i:
            return create_random_id(data)
    else:
        return code
    
def check_id(data,code) -> bool:
    for i in data:
        if code == i:
            return False
    else:
        return True
    


class Data():
    def __init__(self):
        pass

    def save(self, id: int, name: str, data: any,
             custom_name:str = "data"):
        os.makedirs(f"data/{name}/{id}", exist_ok=True)
        with open(f"data/{name}/{id}/{custom_name}.json", "w", encoding='utf-8') as fp:
            json.dump(data, fp)

    def load(self, id: int, name: str,
             custom_name:str = "data"):
        try:
            with open(f"data/{name}/{id}/{custom_name}.json", "r", encoding='utf-8') as fp:
                return json.load(fp)
        except FileNotFoundError:
            return None
    
    def save_global(self, name: str, data: any,custom_name:str = "data"):
        os.makedirs(f"data/{name}", exist_ok=True)
        with open(f"data/{name}/{custom_name}.json", "w", encoding='utf-8') as fp:
            json.dump(data, fp)

    def load_global(self, name: str,custom_name:str = "data"):
        try:
            with open(f"data/{name}/{custom_name}.json", "r", encoding='utf-8') as fp:
                return json.load(fp)
        except FileNotFoundError:
            return None

    def check(self, id: int,
               name: str,custom_name:str = "data"):
        return os.path.isfile(f"data/{name}/{id}/{custom_name}.json")
    
    def check_global(self, name: str,custom_name:str = "data"):
        return os.path.isfile(f"data/{name}/{custom_name}.json")
async def high(ctx:init,user:nextcord.Member):
    if user.top_role.position >= ctx.user.top_role.position:
        await ctx.send(f"User {user} Is Higher Than you")
        return True
    return False