
import json
import os
import shutil
from typing import Any, Dict, List, Union


class Data:
    def __init__(self,
                 server_id:int,
                 name:str,
                 file:str="data",
                 subFolder: str = None,
                 default: Union[Dict, List, None] = None):
        self.path = f"Data/{name}/{server_id}" 
        self.file = f"{self.path}/{file}.json" if subFolder == None else f"{self.path}/{subFolder}/{file}.json"
        os.makedirs(self.path,exist_ok=True)
        if subFolder != None: os.makedirs(os.path.join(self.path, subFolder), exist_ok=True)
        
        try:
            self.load()
        except FileNotFoundError:
            self.data= default
    
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
    
    def delete(self) -> None:
        os.remove(self.file)
    def delete_guild(self):
        shutil.rmtree(self.path)
    def get(self,data):
        if type(self.data) == dict:
            return self.data.get(data)
        elif type(self.data) == list:
            for i in self.data:
                if i == data:
                    return i
            return None
        elif type(self.data) == tuple:
            for i in self.data:
                if i == data:
                    return i
            return None
    
    def __getitem__(self, key: str) -> Union[Dict[str, Any], List[Any]]:
        if key in self.data:
            try:
                return self.data[key]
            except KeyError:
                return None
        else:
            raise KeyError(f"'{key}' not found in the data")

    def __setitem__(self, key: str, value: Union[Dict[str, Any], List[Any]]) -> None:
        self.data[key] = value
class DataGlobal:
    def __init__(self,
                 name:str,
                 file:str="data",
                 default: Union[Dict, List, None] = None):
        if name == ""   : self.path = f"Data/"
        else            : self.path = f"Data/{name}/"
        self.file = f"{self.path}{file}.json"
        os.makedirs(self.path,exist_ok=True)
        try:
            self.load()
        except FileNotFoundError:
            self.data= default
    
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
    def get(self,data):
        if type(self.data) == dict:
            return self.data.get(data)
        elif type(self.data) == list:
            for i in self.data:
                if i == data:
                    return i
            return None
        elif type(self.data) == tuple:
            for i in self.data:
                if i == data:
                    return i
            return None
    def __getitem__(self, key: str) -> Union[Dict[str, Any], List[Any]]:
        if key in self.data:
            try:
                return self.data[key]
            except KeyError:
                return None
        else:
            raise KeyError(f"'{key}' not found in the data")

    def __setitem__(self, key: str, value: Union[Dict[str, Any], List[Any]]) -> None:
        self.data[key] = value