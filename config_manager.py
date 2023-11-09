from dataclasses import dataclass
import os
import pathlib
import tomllib
import sys
import dacite
import pickle
from collections import defaultdict


@dataclass
class BlacklistConfigManager:
    def __post_init__(self) -> None:
        self.CONFIG_FOLDER = (
            pathlib.Path(
                os.environ.get("APPDATA")
                or os.environ.get("XDG_CONFIG_HOME")
                or os.path.join(os.environ["HOME"], ".config")
            )
            / "filter-usb"
        )
        self.CONFIG_FILE = self.CONFIG_FOLDER / "config.toml"
        self.BLACKLISTED_USB_PICKLE_FILE = (
            self.CONFIG_FOLDER / "blacklisted_usbs.pickle"
        )

        self.CONFIG_FOLDER.mkdir(parents=True, exist_ok=True)
        self.CONFIG_FILE.touch(exist_ok=True)
        self.BLACKLISTED_USB_PICKLE_FILE.touch(exist_ok=True)

        # mapping of VID :: list[PIDs]
        self.blacklisted_usbs: dict[str, set[str]] = defaultdict(set)
        self.load_blacklisted_usbs()

    def save_blacklisted_usbs(self) -> None:
        with open(self.BLACKLISTED_USB_PICKLE_FILE, "wb") as f:
            pickle.dump(self.blacklisted_usbs, f, protocol=pickle.HIGHEST_PROTOCOL)

    def load_blacklisted_usbs(self) -> None:
        with open(self.BLACKLISTED_USB_PICKLE_FILE, "rb") as f:
            try:
                self.blacklisted_usbs = pickle.load(f)
            except EOFError:
                print("Blacklisted USB data is corrupted!")

    def add_blacklisted_usb(self, vid: str, pid: str) -> None:
        self.blacklisted_usbs[vid].add(pid)

    def remove_blacklisted_usb(self, vid: str, pid: str) -> None:
        if self.is_blacklisted(vid, pid):
            self.blacklisted_usbs[vid].remove(pid)

    def is_blacklisted(self, vid: str, pid: str) -> None:
        pids = self.blacklisted_usbs.get(vid, None)
        if pids is not None and pid in pids:
            return True

        return False

    def clear_blacklisted_usb_list(self) -> None:
        self.blacklisted_usbs: dict[str, set[str]] = defaultdict(set)
        self.save_blacklisted_usbs()
