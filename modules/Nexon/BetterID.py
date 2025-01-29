import random
from string import hexdigits
from typing import Any, Dict, List, Union
from .DataManager import DataManager



class BetterID:
    def __init__(self,file: str = "codes",max:int = 7):
        self.max = max
        self.file = DataManager("BetterID", default=[], file=file)
    def create_random_id(self) -> str:
        code = ''.join(random.choice(hexdigits) for _ in range(self.max))
        for i in self.file.data:
            if code == i:
                return self.create_random_id()
        else:
            self.file.data.append(code)
            self.file.save()
            return code
    def generate(self) -> str:
        return self.create_random_id()
        
    def check_id(self,code) -> bool:
        for i in self.file.data:
            if code == i:
                return False
        else:
            return True

    def __getitem__(self, key: str) -> Union[Dict[str, Any], List[Any]]:
        if key in self.file.data:
            try:
                return self.file.data[key]
            except KeyError:
                return None
        else:
            raise KeyError(f"'{key}' not found in the data")
    
    def __setitem__(self, key: str, value: Any) -> None:
        self.file.data[key] = value

    def __delitem__(self, key: str) -> None:
        del self.file.data[key]