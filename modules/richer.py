import rich as r
from rich.console import Console
from rich.progress import track
from rich.columns import Columns
from rich.table import Table
from rich.rule import Rule
from rich.traceback import install
from rich.tree import Tree
from rich.filesize import decimal
from rich.text import Text
from rich.pretty import Pretty
from rich.markup import escape
from rich.panel import Panel
from rich.live import Live
from time import sleep as wait

console = Console()