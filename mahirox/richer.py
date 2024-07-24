import rich as r
from rich.console import Console
from rich.progress import track
from rich.columns import Columns
from rich import print
from rich.traceback import install
from rich.tree import Tree
from rich.filesize import decimal
from rich.text import Text
from rich.table import Table
from rich.pretty import Pretty
from rich.markup import escape
from rich.panel import Panel
from rich.live import Live
from time import sleep as wait

console = Console()
#Welcome to Mahiro OS

def typing_effect_in_panel(text: str,title:str = "", delay: float = 0.05, style: str = "bold green",title_typing:bool = False):
    displayed_text = ""
    displayed_title = ""

    with Live(console=console, refresh_per_second=60) as live:
        if title_typing == True:
            for char in title:
                displayed_title += char
                panel = Panel(displayed_text, title=displayed_title, border_style=style)
                live.update(panel)
                wait(delay)
                if char == "!" or char == "." or char == "?"  or char == "," or char == ":":
                    wait(1)
        else:
            displayed_title = title
            panel = Panel(displayed_text, title=displayed_title, border_style=style)
            live.update(panel)
            wait(delay)
        for char in text:
            displayed_text += char
            panel = Panel(displayed_text, title=displayed_title, border_style=style)
            live.update(panel)
            wait(delay)
            if char == "!" or char == "." or char == "?"  or char == "," or char == ":":
                wait(1)

if __name__ == "__main__":
    typing_effect_in_panel("Hi There user! I am Your Personal AI In this OS by Mahiro (My master), anyway\nPlease Enter your name!","Welcome to Mahiro OS",delay=0.05)