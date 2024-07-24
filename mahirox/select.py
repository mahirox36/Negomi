from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.align import Align
import keyboard

running = False

class Menu:
    def __init__(self, items, title="Menu", border_style="bold cyan", padding=(1, 2), screen_center=True,
                 color="green"):
        self.console = Console()
        self.items = items
        self.title = title
        self.border_style = border_style
        self.padding = padding
        self.screen_center = screen_center
        self.color = color
        self.selected_index = 0
        self.running = True
        global running
        running = True

        keyboard.on_press_key("up", self.handle_arrow_up)
        keyboard.on_press_key("down", self.handle_arrow_down)
        keyboard.on_press_key("enter", self.handle_enter)
        keyboard.on_press_key("esc", self.handle_escape)

    def render_menu(self):
        panel = Panel(
            "\n".join(
                f"[reverse][{self.color}][green]> {item}[/green][/{self.color}][/reverse]" if i == self.selected_index else f"  {item}"
                for i, item in enumerate(self.items)
            ),
            title=self.title,
            border_style=self.border_style,
            padding=self.padding
        )
        if self.screen_center:
            return Align.center(panel)
        else:
            return panel

    def handle_arrow_up(self, event):
        self.selected_index = (self.selected_index - 1) % len(self.items)

    def handle_arrow_down(self, event):
        self.selected_index = (self.selected_index + 1) % len(self.items)

    def handle_enter(self, event):
        selected_item = self.items[self.selected_index]
        self.console.print(f"\nYou selected: [bold]{selected_item}[/bold]", style="bold yellow")
        self.running = False
        global running
        running = False

    def handle_escape(self, event):
        self.running = False
        global running
        running = False

    def start(self):
        with Live(self.render_menu(), refresh_per_second=60, screen=True) as live:
            while self.running:
                live.update(self.render_menu())
        keyboard.unhook_all()
        return (self.selected_index, self.items[self.selected_index])

if __name__ == "__main__":
    menu_items = ["Play", "Options", "Exit"]
    menu = Menu(menu_items, title="Main Menu", border_style="bold magenta", padding=(1, 2), screen_center=True)
    menu.start()
