from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Checkbox, Input, Label, Static

from ..api import Client


class LoginScreen(Screen):
    BINDINGS = [
        Binding("ctrl+q", "app.quit", "Quit", priority=True),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._busy = False
        self._pending_password = ""

    def compose(self) -> ComposeResult:
        with Vertical(id="login-box"):
            yield Static("jtech forums · sign in", id="login-title")
            yield Input(placeholder="Username", id="username")
            yield Input(placeholder="Password", id="password", password=True)
            yield Checkbox("Remember me", id="remember-me")
            yield Button("Log in", variant="primary", id="submit")
            yield Label("", id="login-error")

    def on_mount(self) -> None:
        cfg = self.app.cfg
        if cfg.username:
            self.query_one("#username", Input).value = cfg.username
        if cfg.password:
            self.query_one("#password", Input).value = cfg.password
            self.query_one("#remember-me", Checkbox).value = True
        self.query_one("#username", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "username":
            self.query_one("#password", Input).focus()
        elif event.input.id == "password":
            self._try_login()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            self._try_login()

    def _try_login(self) -> None:
        if self._busy:
            return
        username = self.query_one("#username", Input).value.strip()
        password = self.query_one("#password", Input).value
        if not username or not password:
            self._set_error("enter username and password")
            return
        self._busy = True
        self._pending_password = password
        self._set_error("signing in…")
        self._do_login(username, password)

    def _set_error(self, msg: str) -> None:
        self.query_one("#login-error", Label).update(msg)

    @work(thread=True, exclusive=True)
    def _do_login(self, username: str, password: str) -> None:
        app = self.app  # JtechApp
        try:
            cookie = app.client.login(username, password)
        except Exception as e:  # noqa: BLE001
            self.app.call_from_thread(self._on_login_failed, str(e))
            return
        self.app.call_from_thread(self._on_login_ok, username, cookie)

    def _on_login_failed(self, err: str) -> None:
        self._busy = False
        self._set_error(err)
        pwd = self.query_one("#password", Input)
        pwd.value = ""
        pwd.focus()

    def _on_login_ok(self, username: str, cookie: str) -> None:
        from .main import MainScreen  # avoid circular import

        remember = self.query_one("#remember-me", Checkbox).value
        app = self.app
        app.cfg.session_cookie = cookie
        app.cfg.username = username
        app.cfg.password = self._pending_password if remember else ""
        app.cfg.save()
        app.switch_screen(MainScreen())
