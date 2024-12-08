import os
import re
import sys
from typing import NewType


url = NewType("url", str)

def clear():
    os.system("cls" if os.name == "nt" else "clear")
    
def remove_prefix(s, prefix):
    if s.startswith(prefix):
        return s[len(prefix):]
    return s

# Dictionary to convert words to numbers
word_to_number = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
    "seventy": 70, "eighty": 80, "ninety": 90,"hundred":100
}

# Dictionary to convert time units to seconds
time_units = {
    "s"     : 1 ,       'sec'   : 1,     'second'   : 1,    'seconds'   : 1,
    "m"     : 60 ,      'min'   : 60,    'minute'   : 60,   'minutes'   : 60,
    'h'     : 3600,     'hour'  : 3600,  'hours'    : 3600,
    'd'     : 86400,    'day'   : 86400, 'days'     : 86400,
    'w'     : 604800,   'week'  : 604800,'weeks'    : 604800,
    'month' : 2592000,  'months': 2592000  # Assuming 1 month = 30 days
}

def text_to_number(text: str):
    text = text.lower().strip()
    if text.isdigit():  # Direct number
        return int(text)
    return word_to_number.get(text, None)

def convert_to_seconds(time_string: str):
    """Convert any time to seconds

    Args:
        time_string (str): Time

    Raises:
        ValueError: Invalid time Format 
        ValueError: _description_

    Returns:
        int: Seconds
    """
    time_string = time_string.lower()
    
    # Regex to find patterns like '5 days', 'five days', '5d', etc.
    pattern = r'(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred)\s*(s|sec|second|seconds|m|min|minute|minutes|h|hour|hours|d|day|days|w|week|weeks|month|months)?'
    match = re.match(pattern, time_string)
    
    if match:
        number_text, unit = match.groups()
        number = text_to_number(number_text) if not number_text.isdigit() else int(number_text)
        unit = unit if unit else 'sec'  # Default to seconds if no unit is provided

        if number is None or unit not in time_units:
            raise ValueError(f"Invalid time format: {time_string}")
        
        return number * time_units[unit]
    else:
        raise ValueError(f"Invalid time format: {time_string}")



def remove_numbers(text):
    return re.sub(r'\d+', '', text)

def get_resource_path(relative_path):
    """Get the absolute path to a resource."""
    # If running as a PyInstaller bundle, use the _MEIPASS directory.
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        # Otherwise, use the script's directory.
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)

def is_bundled():
    """Check if the script is running as a bundled executable or a normal script."""
    return hasattr(sys, '_MEIPASS')