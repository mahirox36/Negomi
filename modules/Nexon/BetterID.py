import random
import string
from typing import Any, Dict, List, Union
from .Data import Data



class BetterID:
    def __init__(self,subFolder: str = None,max:int = 7):
        self.max = max
        self.file = Data("BetterID",subFolder)
        
        try:
            self.data = self.file.load()
        except FileNotFoundError:
            self.data = []
            self.file.data = self.data
            self.file.save()
    def create_random_id(self) -> str:
        hexdigits = string.digits + 'abcdef'
        code = ''.join(random.choice(hexdigits) for _ in range(self.max))
        for i in self.data:
            if code == i:
                return self.create_random_id()
        else:
            self.data.append(code)
            self.file.data = self.data
            self.file.save()
            return code
    def generate(self) -> str:
        return self.create_random_id()
        
    def check_id(self,code) -> bool:
        for i in self.data:
            if code == i:
                return False
        else:
            return True

    def __getitem__(self, key: str) -> Union[Dict[str, Any], List[Any]]:
        if key in self.data:
            try:
                return self.data[key]
            except KeyError:
                return None
        else:
            raise KeyError(f"'{key}' not found in the data")
    
    def __setitem__(self, key: str, value: Any) -> None:
        self.data[key] = value

    def __delitem__(self, key: str) -> None:
        del self.data[key]