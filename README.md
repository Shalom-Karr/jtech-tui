# jtech-tui

A terminal client for [jtech forums](https://forums.jtechforums.org) — and any
other Discourse-powered site (But heavilly customized for jtech) — built with [Textual](https://textual.textualize.io/).
Browse feeds, read threads, reply, react, search, check notifications, send private
messages and follow the gamification leaderboard and much more!! All without leaving your shell.

> **Note on provenance.** A large portion of this project was written by an AI
> coding assistant working against the public Discourse API. Expect rough edges
> and bugs. Please file issues with reproduction steps and I'll fix what I can.

## Highlights

- **Full feed coverage** — Latest, New, Top, Unseen, Categories, Messages,
  Notifications and Search, each as its own tab.
- **Proper thread view** — markdown rendering with syntax-highlighted code
  blocks, `[quote=…]` blocks converted to real blockquotes, per-post reaction
  summaries, `#post_number` pill and a `↱ replying to @user #N` breadcrumb.
- **Resume-at-last-read** — a topic you've opened before lands you where you
  stopped (first unread if there is one, otherwise the last post you saw),
  matching the web UI. Threads you've never opened start at the top.
- **Auto-collapse for long posts** — posts over 40 lines fold into a short
  preview; `x` toggles.
- **Compose in `$EDITOR` as `.md`** — new topics, replies, quote-replies and
  PMs all drop you into your editor with proper markdown syntax highlighting.
- **Reactions** — if the `discourse-reactions` plugin is installed, the picker
  shows only the reactions the server actually accepts, falling back to the
  core "like" action otherwise. Counts update in place with no reload.
- **Leaderboard** — the gamification-plugin boards at `/leaderboard/<id>`.
  Period switches with `[` / `]` (daily, weekly, monthly, quarterly, yearly,
  all); cycle between boards with `<` / `>`.
- **Copy menu** — `Y` on a post picks between the post permalink and any code
  blocks in the post; no code blocks → link copied directly.
- **Live refresh** — auto-poll a thread every 30 s with `a`; the feeds refresh
  automatically when you back out of a thread.
- **Upload attachments** — `U` uploads a file via `/uploads.json` and copies
  the resulting markdown to your clipboard.
- **Vim-style navigation** — `j` / `k` / `g` / `G` everywhere. `↑` at the top
  of a list hands focus to the tab bar without teleporting.

## Requirements

- Python 3.10+
- A Discourse forum with a username + password login (the client stores the
  `_t` session cookie)
- A clipboard helper on `PATH` for yank / copy-link / copy-code:
  `termux-clipboard-set`, `pbcopy`, `wl-copy`, `xclip`, or `xsel`
- `$EDITOR` (or `$VISUAL`) set for compose — falls back to `nano`

## Install

```sh
git clone https://github.com/flipphoneguy/jtech-tui
cd jtech-tui
pip install -e .
```

## Run

```sh
jtech                 # opens your default feed
jtech --feed latest   # override the starting tab
```

Valid `--feed` values: `latest`, `new`, `top`, `unseen`, `categories`,
`messages`, `notifications`.

On first launch you'll be prompted for your forum URL, username and password.
The session cookie is written to `~/.config/jtech-tui/config.json` with mode
`0600`. Subsequent launches skip the login screen.

## Configuration

`~/.config/jtech-tui/config.json`:

| Field            | Default                              | Purpose                                      |
|------------------|--------------------------------------|----------------------------------------------|
| `forum_url`      | `https://forums.jtechforums.org`     | Base URL of the Discourse site.              |
| `default_feed`   | `latest`                             | Tab to open when `--feed` is not passed.     |
| `session_cookie` | *(empty)*                            | Discourse `_t` cookie. Cleared on reauth.    |
| `username`       | *(empty)*                            | Cached for ownership checks on edit/delete.  |

Point the client at a different Discourse host by editing `forum_url` and
clearing `session_cookie` so you get a fresh login prompt.

## Keys

### Main screen

| Key              | Action                                    |
|------------------|-------------------------------------------|
| `tab` / `shift+tab`, `←` / `→` | Switch tabs          |
| `↓` on a tab     | Focus the current list                   |
| `↑` at the top of a list | Back to the tab bar              |
| `j` / `k`        | Move cursor down / up                    |
| `g` / `G`        | Jump to top / bottom of the list         |
| `enter`          | Open the selected row                    |
| `/`              | Open the search modal                    |
| `N`              | New topic                                |
| `M`              | New private message                      |
| `U`              | Upload a file                            |
| `L`              | Open the leaderboard                     |
| `R`              | Reload the current tab                   |
| `ctrl+q`         | Quit                                     |
| `?`              | Show the full key list for this screen   |

Reaching the bottom of a feed triggers a page fetch, so you get infinite-scroll
without a separate action.

### Thread view

| Key              | Action                                                       |
|------------------|--------------------------------------------------------------|
| `j` / `k`        | Next / previous post (scrolls within the post first if long) |
| `g` / `G`        | Jump to the first / last post                                |
| `enter`          | Open the reaction picker on the highlighted post             |
| `r`              | Reply (threaded under the highlighted post if any)           |
| `Q`              | Quote-reply — opens `$EDITOR` with a `[quote=…]` prefilled   |
| `y`              | Copy the highlighted post's raw markdown                     |
| `Y`              | Copy menu — pick between post link and any code blocks       |
| `p`              | Jump to the post this one is replying to                     |
| `l`              | Show who reacted to the highlighted post (per reaction)      |
| `x`              | Toggle collapse on the highlighted post                      |
| `u`              | Open the author's profile                                    |
| `+` / `ctrl+r`   | React to the highlighted post                                |
| `E`              | Edit your own post (opens `$EDITOR`)                         |
| `D`              | Delete your own post (with confirmation)                     |
| `a`              | Toggle auto-refresh (poll every 30 s)                        |
| `e`              | Open the full thread in `$EDITOR` as read-only `.md`         |
| `U`              | Upload a file and get its markdown on the clipboard          |
| `R`              | Hard-reload the thread                                       |
| `esc` / `q`      | Back to the previous screen                                  |

### Leaderboard

| Key       | Action                                     |
|-----------|--------------------------------------------|
| `[` / `]` | Previous / next period                     |
| `<` / `>` | Previous / next leaderboard (when > 1)    |
| `enter`   | Open the selected user's profile           |
| `R`       | Reload                                     |
| `esc` / `q` | Back                                     |

## Architecture

```
jtech_tui/
├── api.py            # Thin Discourse client (requests.Session, CSRF, JSON)
├── app.py            # Textual App + argparse entrypoint
├── config.py         # ~/.config/jtech-tui/config.json (dataclass)
├── editor.py         # $EDITOR round-trip with a temporary .md file
├── styles.tcss       # Textual CSS
└── screens/
    ├── login.py         # Login modal
    ├── main.py          # Tabbed top-level (feeds, categories, PMs, …)
    ├── thread.py        # Thread view, reactions, reply composer
    ├── composer.py      # Shared modal dialogs
    ├── leaderboard.py   # Gamification plugin viewer
    ├── user_profile.py  # User bio + recent activity
    └── smart_footer.py  # Footer that truncates to "? all keys"
```

All network calls run in `textual.work` threads so the UI never blocks; results
are marshalled back with `call_from_thread`.

## Known limitations

- **Gamification plugin required** for the leaderboard feature. Without it the
  screen shows "Load failed".
- **Reactions** need the `discourse-reactions` plugin to list anything other
  than core like / unlike.
- **Images** render as placeholder markdown, not actual pixels — terminals
  generally can't display images without extra setup, so this is a deliberate
  omission.
- **Drafts** are not persisted: quitting `$EDITOR` without writing discards
  the buffer.
- **Infinite scroll** is per-tab and resets on resume (so read state stays
  accurate after you come back from a thread).

## Contributing

Issues and pull requests welcome. If you're filing a bug, please include:

- The forum URL (if it's a public site)
- Output of `python --version` and `pip show textual`
- The traceback, if any, and the steps to reproduce

The Python source lives under `python/`. Run the app from source with
`pip install -e .` then `jtech`. There are no tests yet; adding some is a
welcome contribution.

## License

GPL-3 See `LICENSE`
