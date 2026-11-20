# Security policy

## What agent-callback does on your machine

- Runs as your user from Claude Code hooks. It never needs `sudo`.
- Makes **no network connections**.
- Writes only to `~/.local/state/agent-callback/` (or `AGENT_CALLBACK_STATE_DIR`),
  plus the optional log file you set with `AGENT_CALLBACK_LOG`.
- Talks to your desktop over the session D-Bus: notifications, screen-lock and
  idle state, and on KDE a short KWin script that raises the window you clicked
  back to, unloaded right after.
- Session ids from hooks are sanitised before being used as folder names, and
  recorded PIDs are checked against their command line before being signalled.

## Supported versions

Only the latest release gets fixes.

## Reporting a vulnerability

Please **don't open a public issue**. Report it privately through
[GitHub's private vulnerability reporting](https://github.com/akashmony01/agent-callback/security/advisories/new).
Include the version, your OS and desktop, and steps to reproduce. You should get
a reply within a week.
