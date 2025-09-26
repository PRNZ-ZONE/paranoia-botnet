import importlib
import pkgutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Type

from rich.align import Align
from rich.box import ROUNDED
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from src.base import BaseFunction
from src.storages.session_storage import SessionStorage


class AddonStorage(BaseFunction):
    def __init__(self, addons_package: str = "addons"):
        super().__init__()
        self.addons_package = addons_package
        self._addons: Dict[str, Type[BaseFunction]] = {}
        self.start_time = datetime.now()

        self.strings = {
            "loaded_addon": "Loaded addon: {name}",
            "no_addons": "[red]No addons loaded[/]",
            "menu_title": "Addon Manager",
            "menu_exit": "Exit",
            "menu_prompt": "[bold cyan]Select addon by number[/]: ",
            "menu_invalid_input": "[red]Please enter a number![/]",
            "menu_invalid_choice": "[red]Invalid number[/]",
            "not_implemented": "[yellow]execute_clients not implemented in {c}[/]",
            "addon_failed": "[red]Addon {c} failed: {e}[/]",
            "no_description": "No description provided",
            "badge_pyrogram": "[PYROGRAM]",
            "badge_telethon": "[TELETHON]",
            "badge_shared": "[SHARED]",
        }

    def load_addons(self) -> None:
        package = importlib.import_module(self.addons_package)
        package_path = Path(package.__file__).parent

        for _, name, is_pkg in pkgutil.iter_modules([str(package_path)]):
            if is_pkg:
                continue

            module_name = f"{self.addons_package}.{name}"
            module = importlib.import_module(module_name)

            if hasattr(module, "Addon"):
                addon_cls: Type[BaseFunction] = getattr(module, "Addon")
                self._addons[name] = addon_cls
                self.console.log(self.strings["loaded_addon"].format(name=name))

    @property
    def addons(self) -> Dict[str, Type[BaseFunction]]:
        return self._addons

    def get_addon(self, name: str) -> Type[BaseFunction]:
        return self._addons[name]

    def _get_function_type(self, addon_cls: Type[BaseFunction]) -> str:
        for base in addon_cls.mro():
            name = base.__name__.lower()
            if "pyrogramfunction" == name:
                return self.strings["badge_pyrogram"]
            if "telethonfunction" == name:
                return self.strings["badge_telethon"]
        return "[dim]UNKNOWN[/]"

    async def run_menu(self, session_storage: SessionStorage) -> None:
        if not self._addons:
            self.console.log(self.strings["no_addons"])
            return

        addon_names = list(self._addons.keys())
        console = Console()

        while True:
            console.clear()

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            uptime_delta = datetime.now() - self.start_time
            uptime_str = str(uptime_delta).split(".")[0]

            menu_content = Text()
            menu_content.append(
                "0. " + self.strings["menu_exit"] + "\n\n", style="bold red"
            )

            for idx, name in enumerate(addon_names, start=1):
                addon_cls = self.get_addon(name)
                description = getattr(
                    addon_cls, "description", self.strings["no_description"]
                )
                function_type = self._get_function_type(addon_cls)
                is_shared = getattr(addon_cls, "shared_addon", False)

                menu_content.append(f"{idx}. {name}\n", style="bold cyan")
                menu_content.append(function_type + "\n", style="green")
                menu_content.append(description, style="dim")
                if is_shared:
                    menu_content.append(
                        " " + self.strings["badge_shared"], style="yellow"
                    )
                menu_content.append("\n\n")

            menu_panel = Panel(
                Align.left(menu_content),
                title=f"[bold magenta]{self.strings['menu_title']}[/]",
                border_style="blue",
                box=ROUNDED,
                expand=True,
            )

            console.print(menu_panel)

            footer_text = Text()
            footer_text.append(
                f"Sessions: {len(session_storage.sessions)}", style="green"
            )
            footer_text.append(" | ")
            footer_text.append(f"Time: {now}", style="cyan")
            footer_text.append(" | ")
            footer_text.append(f"Botnet uptime: {uptime_str}", style="magenta")
            footer_text.append(" | ")
            footer_text.append(f"Addons: {len(self._addons)}", style="yellow")
            footer_text.append(" | ")
            footer_text.append("Exit: 0", style="green")

            footer = Panel(
                Align.center(footer_text),
                border_style="bright_black",
                box=ROUNDED,
            )
            console.print(footer)

            choice = console.input(self.strings["menu_prompt"])
            if not choice.isdigit():
                console.print(self.strings["menu_invalid_input"])
                continue

            choice_num = int(choice)
            if choice_num == 0:
                break

            if not (1 <= choice_num <= len(addon_names)):
                console.print(self.strings["menu_invalid_choice"])
                continue

            addon_name = addon_names[choice_num - 1]
            addon_cls = self.get_addon(addon_name)
            addon = addon_cls(session_storage)

            try:
                await addon.execute_clients()
            except NotImplementedError:
                console.print(self.strings["not_implemented"].format(c=addon_name))
            except Exception as e:
                console.print(self.strings["addon_failed"].format(c=addon_name, e=e))

            console.input("\n[dim]Press Enter to return to menu...[/]")
