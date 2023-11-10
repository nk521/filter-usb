from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable
import rumps

from config_manager import BlacklistConfigManager
from utils.mac_utils import NSKey


@dataclass(frozen=True)
class Texts:
    TITLE_NORMAL_MODE = "✄"
    TITLE_LOCKDOWN_MODE = "🎚"
    BLACKLISTED_USB = "Blacklisted USBs"
    CLEAR_BLACKLIST = "Clear Blacklist"
    EDIT_BLACKLIST = "Edit Blacklist"
    EDIT_BLACKLIST_POPUP_MESSAGE = "Enter in particular format `vid:pid`.\nDelimeter is new line."
    LOCKDOWN_MODE = "🔴 Lockdown Mode"
    NORMAL_MODE = "🟢 Normal Mode"
    ABOUT = "About"
    QUIT = "Quit"
    SAVE = "Save"
    CLOSE = "Close"

class USBWatchGuardState(Enum):
    NORMAL = 1
    LOCKDOWN = 2

def normal(func: Callable[..., Any]):
    def wrapper(self: USBWatchGuard, *args, **kwargs):
        if self.lockdown_status == USBWatchGuardState.NORMAL:
            func(self, *args, **kwargs)
        else:
            print(f"Currently in Lockdown mode! Won't run {func.__name__}!")
    return wrapper

class USBWatchGuard(rumps.App):
    def __init__(self):
        super(USBWatchGuard, self).__init__(
            name=self.__class__.__name__,
            title=Texts.TITLE_NORMAL_MODE,
            quit_button=None,
        )

        self.blacklist = BlacklistConfigManager()
        self.lockdown_status = USBWatchGuardState.NORMAL

        self.menu = [
            rumps.MenuItem(
                title=Texts.NORMAL_MODE,
                callback=self.toggle_lockdown,
                key=chr(NSKey.NSF4FunctionKey),
            ),
            [rumps.MenuItem(title=Texts.BLACKLISTED_USB, callback=None), [None]],
            None,
            rumps.MenuItem(Texts.QUIT, callback=self.clean_up_before_quit),
        ]

        self.__refresh()

    @normal
    def clear_blacklist(self, _):
        self.blacklist.clear_blacklisted_usb_list()
        self.__refresh()

    def fetch_blacklist(self, _):
        return self.blacklist.blacklisted_usbs

    def toggle_lockdown(self, sender: rumps.rumps.MenuItem):
        self.lockdown_status = USBWatchGuardState.NORMAL if self.lockdown_status == USBWatchGuardState.LOCKDOWN else USBWatchGuardState.LOCKDOWN
        if self.lockdown_status == USBWatchGuardState.NORMAL:
            sender.title = Texts.NORMAL_MODE
            self.title = Texts.TITLE_NORMAL_MODE
        else:
            sender.title = Texts.LOCKDOWN_MODE
            self.title = Texts.TITLE_LOCKDOWN_MODE

    @normal
    def edit_blacklist(self, sender: rumps.rumps.MenuItem):
        flatten_list = self.blacklist.flatten_list()
        flattened_string = "\n".join(flatten_list)

        saved: rumps.rumps.Response = rumps.Window(
            title=Texts.EDIT_BLACKLIST,
            message=Texts.EDIT_BLACKLIST_POPUP_MESSAGE,
            ok=Texts.SAVE,
            cancel=Texts.CLOSE,
            default_text=flattened_string,
        ).run()

        if saved.clicked:
            self.blacklist.unflatten_list(str(saved.text).splitlines())
            self.__refresh()

    def clean_up_before_quit(self, _):
        self.blacklist.save_blacklisted_usbs()
        rumps.quit_application()

    def __refresh(self):
        blacklist_submenu: rumps.rumps.MenuItem = self.menu.get(Texts.BLACKLISTED_USB)
        blacklist_submenu.clear()

        for x in [
            *self.blacklist.flatten_list(),
            None,
            rumps.MenuItem(title=Texts.CLEAR_BLACKLIST, callback=self.clear_blacklist),
            rumps.MenuItem(title=Texts.EDIT_BLACKLIST, callback=self.edit_blacklist),
        ]:
            blacklist_submenu.add(x)

        return None
    
    def blacklist_routine(self):
        ...


if __name__ == "__main__":
    USBWatchGuard().run()
