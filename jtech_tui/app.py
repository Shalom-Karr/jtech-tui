from __future__ import annotations

import argparse
import sys

from textual import work
from textual.app import App
from textual.binding import Binding

from .api import Client
from .config import Config
from .screens import LoginScreen, MainScreen


class JtechApp(App):
    CSS_PATH = "styles.tcss"
    TITLE = "jtech forums"
    SUB_TITLE = "discourse · python · textual"

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", priority=True),
        Binding("?", "show_bindings_help", "Help", show=False),
    ]

    def action_show_bindings_help(self) -> None:
        from .screens.smart_footer import BindingsHelpModal, collect_screen_bindings
        self.push_screen(BindingsHelpModal(collect_screen_bindings(self.screen, self)))

    def __init__(self, starting_feed: str | None = None) -> None:
        super().__init__()
        self.cfg: Config = Config.load()
        if starting_feed:
            self.cfg.default_feed = starting_feed
        self.client: Client = Client(self.cfg.forum_url, self.cfg.session_cookie)

    def on_mount(self) -> None:
        if self.cfg.session_cookie:
            self.push_screen(MainScreen())
        else:
            self.push_screen(LoginScreen())

    def reauth(self) -> None:
        self.cfg.session_cookie = ""
        if self.cfg.password and self.cfg.username:
            self.notify("Session expired — reconnecting…", severity="warning")
            self._silent_reauth()
            return
        self.cfg.save()
        self.client = Client(self.cfg.forum_url, "")
        while len(self.screen_stack) > 1:
            self.pop_screen()
        self.switch_screen(LoginScreen())
        self.notify("Session expired — please sign in again.", severity="warning")

    @work(thread=True, exclusive=True, group="reauth")
    def _silent_reauth(self) -> None:
        try:
            cookie = self.client.login(self.cfg.username, self.cfg.password)
        except Exception:  # noqa: BLE001
            self.cfg.save()
            self.client = Client(self.cfg.forum_url, "")
            self.call_from_thread(self._show_login_after_failed_reauth)
            return
        self.cfg.session_cookie = cookie
        self.cfg.save()
        self.client = Client(self.cfg.forum_url, cookie)
        self.call_from_thread(self.notify, "Reconnected.", severity="information")

    def _show_login_after_failed_reauth(self) -> None:
        while len(self.screen_stack) > 1:
            self.pop_screen()
        self.switch_screen(LoginScreen())
        self.notify("Reconnect failed — please sign in again.", severity="warning")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(prog="jtech", description="jtech forums TUI")
    ap.add_argument(
        "--feed",
        choices=["latest", "new", "top", "unseen", "categories", "messages", "notifications"],
        help="starting tab",
    )
    return ap.parse_args(argv)


def run() -> None:
    args = _parse_args(sys.argv[1:])
    JtechApp(starting_feed=args.feed).run()


if __name__ == "__main__":
    run()
