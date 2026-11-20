# Changelog

## 0.2.1

### Fixed
- Notifications no longer stay in the desktop's notification list. Each one now
  removes itself after `AGENT_CALLBACK_NOTIFY_SECONDS` (default 60; `0` keeps the old
  stay-until-dismissed behaviour), is marked transient so KDE, GNOME and others don't
  keep it in their history, and comes back with each later burst of chimes.
- When an alert gave up (`AGENT_CALLBACK_MAX_SECONDS`), its notification was left open.

## 0.2.0

### Added
- **KDE Plasma support** for clicking a notification to jump back, on Wayland and
  X11, through a small KWin script. Works with VS Code and other editors running as
  native Wayland apps.
- **Konsole:** clicking switches to the exact tab and raises its window.
- **Kitty** (with remote control enabled) and **WezTerm:** clicking switches to the
  exact tab or pane.
- **Any other terminal** (Ptyxis, Alacritty, XFCE Terminal, MATE Terminal, Tilix, ...):
  clicking raises its window on KDE and on X11 desktops.
- **X11 desktops** (Linux Mint Cinnamon, XFCE, MATE): windows are raised with
  `wmctrl` or `xdotool`; idle time comes from `xprintidle` when installed.
- **macOS:** with `terminal-notifier` installed, clicking a notification activates
  the app the agent runs in (Terminal, iTerm2, VS Code, ...) and silences that session.
- Screen-lock detection on KDE, Cinnamon, MATE and XFCE (it was GNOME only).
- Notifications now pass on the desktop's activation token (notification spec 1.2).
- `AGENT_CALLBACK_LOG` also logs what a click tried to focus.
- Without `--session`, Konsole, Kitty, WezTerm, iTerm2 and macOS Terminal tabs (or the
  tty) are now used as the session id, not just GNOME Terminal tabs.

### Changed
- Code editors: with only one window of the editor open, clicking raises it even if its
  title doesn't show the session's folder.

### Fixed
- Clicking did nothing on KDE Plasma, and for VS Code running as a native Wayland app.
- Python deprecation warning from `GLib.unix_signal_add` in the notifier.

## 0.1.0

First release: notification and chime bursts for Claude Code on GNOME, click to jump
back to GNOME Terminal tabs and VS Code-based editors.
