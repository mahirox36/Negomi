from typing import Union
import emoji
import random
from string import hexdigits
from typing import Any, Dict, List, Union, Optional

def get_by_percent(percent: Union[int, float] ,text: str, min_words: int = 5, returns: str = "") -> str:
    """Get a specified percentage of words from a sentence.

    Args:
        percent (Union[int, float]): The percentage of words to return (between 0 and 100).
        text (str): The input sentence to extract words from.
        min_words (int, optional): Minimum number of words required to return any result. Defaults to 5.

    Returns:
        str: The extracted percentage of words from the input text, or an empty string if the text has fewer words than `min_words`.
    """
    if isinstance(percent, int):
        percent /= 100
    words = text.split()
    if len(words) < min_words:
        return returns

    take_count = max(1, int(len(words) * percent))
    return " ".join(words[:take_count])

def extract_emojis(text: str) -> list:
    """
    Extract all emojis from a string.
    """
    return [char for char in text if char in emoji.EMOJI_DATA]

def remove_numbers(text: str) -> str:
    """Remove numbers from a string."""
    return ''.join(char for char in text if not char.isdigit())

class IDManager:
    def __init__(self,file: str = "codes",max:int = 7):
        self.max = max
        self.file = DataManager("IDManager", default=[], file_name=file)
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

    def __getitem__(self, key: str) -> Optional[Union[Dict[str, Any], List[Any]]]:
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