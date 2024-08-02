import os
import nextcord #type: ignore
from nextcord.ext.commands import MissingPermissions
from nextcord import Interaction
import Lib.Side as Side
from nextcord import Interaction as init
import random
import json
from typing import Any, Dict, List, Union

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
        if ctx.user.id == Side.owner_id:
            return True
        await ctx.send("You'r Not The Owner Of this Bot",ephemeral=True)
        raise MissingPermissions(ctx.user.name)
    return predicate(interaction)

def check_owner_permission_message(message:nextcord.Message) -> bool:
    async def predicate(ctx:Interaction) -> bool:
        if ctx.author.id == Side.owner_id:
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
    



class Data:
    def __init__(self,server_id:int, name:str,file:str="data"):
        self.path = f"Data/{name}/{server_id}/"
        self.file = f"{self.path}{file}.json"
        os.makedirs(self.path,exist_ok=True)
        
        try:
            self.load()
        except FileNotFoundError:
            self.data = None | dict | list
    
    def save(self) -> None:
        with open(self.file, "w") as f:
            json.dump(self.data,f,indent=4)
    
    def load(self) -> Any:
        with open(self.file, "r") as f:
            self.data = json.load(f)
        return self.data
    
    def check(self) -> bool:
        if os.path.exists(self.file):
            return True
        return False
    
    def delete(self,code) -> None:
        del self.data[code]
        self.save()
        os.remove(self.file)
    
    def __getitem__(self, key: str) -> Union[Dict[str, Any], List[Any]]:
        if key in self.data:
            try:
                return self.data[key]
            except KeyError:
                return None
        else:
            raise KeyError(f"'{key}' not found in the data")

    def __setitem__(self, key: str, value: Union[Dict[str, Any], List[Any]]) -> None:
        if key in self.data:
            self.data[key] = value
        else:
            raise KeyError(f"'{key}' not found in the data")

class DataGlobal:
    def __init__(self, name:str,file:str="data"):
        if name == ""   : self.path = f"Data/"
        else            : self.path = f"Data/{name}/"
        self.file = f"{self.path}{file}.json"
        os.makedirs(self.path,exist_ok=True)
        self.data = {}
        try:
            self.load()
        except FileNotFoundError:
            pass
    
    def save(self):
        with open(self.file, "w") as f:
            json.dump(self.data,f)
        return self
    
    def load(self) -> Any:
        with open(self.file, "r") as f:
            self.data = json.load(f)
        return self.data
    
    def check(self) -> bool:
        if os.path.exists(self.file):
            return True
        return False
    
    def delete(self,code) -> None:
        del self.data[code]
        self.save()
        os.remove(self.file)
    def __getitem__(self, key: str) -> Union[Dict[str, Any], List[Any]]:
        if key in self.data:
            try:
                return self.data[key]
            except KeyError:
                return None
        else:
            raise KeyError(f"'{key}' not found in the data")

    def __setitem__(self, key: str, value: Union[Dict[str, Any], List[Any]]) -> None:
        if key in self.data:
            self.data[key] = value
        else:
            raise KeyError(f"'{key}' not found in the data")

async def high(ctx:init,user:nextcord.Member):
    if user.top_role.position >= ctx.user.top_role.position:
        await ctx.send(f"User {user} Is Higher Than you")
        return True
    return False