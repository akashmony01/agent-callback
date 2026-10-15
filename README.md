# agent-callback

**Get called back to your AI coding agent when it's waiting on you.**

You start a long task in Claude Code, walk away, and it sits there for 20 minutes
waiting for a "yes" on a permission prompt. agent-callback fixes that:

- 🔔 **Desktop notification** that stays on screen until you deal with it, titled
  with the project folder so you know *which* session needs you.
- 🎵 **Gentle chime bursts**, not an endless alarm: 30 s right away, 60 s after
  5 minutes, 90 s after 10 more minutes, then silence.
- 🎹 **A different sound per session**, so with several sessions open you can
  tell them apart by ear.
- 🙈 **Quiet when you're away**: no sound while the screen is locked, and the later
  bursts are skipped if you haven't touched the keyboard or mouse for 15 minutes.
- ✋ **Stops by itself** the moment you reply, approve a permission prompt, or close
  the session. Clicking the notification takes you back to the right terminal
  tab or code editor window (VS Code, Cursor, ...).

> Unofficial community project, not affiliated with or endorsed by Anthropic.

## Install (Claude Code)

Inside Claude Code:

```
/plugin marketplace add akashmony01/agent-callback
/plugin install agent-callback@agent-callback
```

Or from a shell: `claude plugin marketplace add akashmony01/agent-callback && claude plugin install agent-callback@agent-callback`.

Start a new session (or run `/reload-plugins`) and you're done. Nothing is written
to your `settings.json`.

**Requirements:** `jq`, plus on Linux a sound player (`pw-play`, `paplay` or
`aplay`), for notifications `python3-gi` and `gdbus`, and for jumping back to
a code editor `xprop`. These are present on a
stock Ubuntu desktop. On macOS, `afplay` is built in; install `jq` with `brew install jq`.

### Optional: `hush` in your terminal

```bash
git clone https://github.com/akashmony01/agent-callback && cd agent-callback && ./install.sh
```

This adds `agent-callback` and `hush` to `~/.local/bin`. `./install.sh --uninstall` removes them.

## Stopping an alert

It stops on its own when you respond. To silence it by hand:

| Where | What to type | Silences |
|---|---|---|
| The notification | click it, or **Stop sound** | that session |
| Claude Code | `/agent-callback:hush` (or `/hush` if the name is free) | every session |
| Any terminal (after `./install.sh`) | `hush` | every session |

## Settings

Set these as environment variables before starting Claude Code, or put them in the
`"env"` block of `~/.claude/settings.json`:

| Variable | Default | Meaning |
|---|---|---|
| `AGENT_CALLBACK_DELAY` | `10` | Seconds to wait before alerting (reply within this and nothing happens) |
| `AGENT_CALLBACK_SCHEDULE` | `0:30 300:60 600:90` | Bursts as `wait:duration` in seconds |
| `AGENT_CALLBACK_AWAY_SECONDS` | `900` | Idle this long = away; bursts after the first are skipped |
| `AGENT_CALLBACK_SOUND` | *(rotates)* | Force one sound for all sessions: a name (`bell`, `Glass`) or a file path |
| `AGENT_CALLBACK_MAX_SECONDS` | `3600` | Hard limit for one alert |
| `AGENT_CALLBACK_STATE_DIR` | `~/.local/state/agent-callback` | Where per-session state lives |
| `AGENT_CALLBACK_EDITOR` | *(auto)* | Editor command to focus when the notification is clicked (`code`, `cursor`, `codium`, `windsurf`); auto-detected |
| `AGENT_CALLBACK_LOG` | *(off)* | File to log every hook call to, for troubleshooting |

Example, chimes every 2 minutes, 20 seconds each:

```json
{ "env": { "AGENT_CALLBACK_SCHEDULE": "0:20 120:20 120:20" } }
```

## Other AI tools

The core is a plain command, so any tool that can run a command when it's waiting
for you can use it:

```bash
agent-callback start --session <id> --app "My Agent" --cwd "$PWD" --message "Waiting for you"
agent-callback stop  --session <id>          # you responded
agent-callback stop  --session <id> --end    # session closed
agent-callback hush                          # silence everything
agent-callback status                        # what's running
```

Leave out `--session` to use the current terminal tab as the session. Only the
Claude Code adapter ships today. Adapters for other tools (Codex CLI, Gemini CLI,
Cursor, Aider, ...) are welcome: see `adapters/claude-code/hook.sh` for the pattern.

## Where it works

### Operating systems

| Platform | Sound | Notification | Click to jump back | Locked / away detection |
|---|---|---|---|---|
| Ubuntu 24.04, GNOME 46 (Wayland) | ✅ tested | ✅ tested | ✅ tested (see below) | ✅ tested |
| Other GNOME-based Linux | ✅ should work | ✅ should work | ✅ should work | ✅ should work |
| Other Linux desktops (KDE, XFCE, ...) | ✅ | ✅ needs a freedesktop notification server | ❌ | ❌ always treated as "present" |
| macOS | ⚠️ untested | ⚠️ untested, basic banner only | ❌ | ❌ |
| Windows / WSL | ❌ not supported | ❌ | ❌ | ❌ |

### Where you run your agent (clicking the notification)

Sound and the notification work wherever the agent runs. What differs is
where a click on the notification takes you:

| Running in | Click takes you to | Status |
|---|---|---|
| **GNOME Terminal** | GNOME shows a "Terminal is ready" prompt; click it to land on the exact tab | ✅ tested |
| **VS Code** (snap or .deb) terminal | the VS Code window with your project | ✅ tested |
| **Cursor** terminal | the Cursor window with your project | ✅ tested |
| **VSCodium** terminal | the VSCodium window with your project | 🟡 built in, untested |
| **Windsurf** terminal | the Windsurf window with your project | 🟡 built in, untested |
| **VS Code Insiders** terminal | the Insiders window with your project | 🟡 built in, untested |
| PyCharm / IntelliJ / other JetBrains IDEs | nothing (the notification just closes) | ❌ not supported yet |
| Zed, Sublime Text, Atom, other editors | nothing | ❌ not supported (Atom is discontinued) |
| Other terminals (Kitty, Alacritty, Konsole, tmux, ...) | nothing | ❌ not supported |
| vim / Neovim / Emacs inside GNOME Terminal | the GNOME Terminal tab | ✅ same as GNOME Terminal |

**Requirements for the code editors:**

- The editor's command must be on your `PATH`: `code`, `cursor`, `codium`,
  `windsurf` or `code-insiders`. VS Code installs `code` for you. For Cursor
  run *"Shell Command: Install 'cursor' command"* from its command palette, or
  make a small `cursor` script that starts the AppImage.
- `xprop` (package `x11-utils`, installed on stock Ubuntu).
- The editor must run under X11/XWayland, which is the default for all of
  them. If you force one to native Wayland (`--ozone-platform=wayland`), its
  window titles can't be read and clicking does nothing.

**Known limits with the code editors:**

- It brings the right **window** forward, not a particular terminal tab or
  chat panel inside it.
- The session's folder must be the project folder or inside it. If no open
  window has it, clicking does nothing (on purpose, so it never opens a new
  window you didn't ask for).
- Projects are recognised by folder **name** in the window title. Two open
  projects with the same folder name (e.g. two `app` folders) can pick the
  wrong one or open a new window.
- Multi-folder workspaces (`.code-workspace`) usually aren't matched; the click
  then does nothing.
- If you changed VS Code's `window.title` setting so it no longer shows the
  folder name, matching fails.

## How it works

- **Claude Code hooks** (`hooks/hooks.json` → `adapters/claude-code/hook.sh`)
  call the core command `bin/agent-callback`. `Stop` and the permission
  `Notification` start an alert. `UserPromptSubmit`, `PostToolUse` and
  `PostToolUseFailure` stop that session's alert. `SessionEnd` stops it and
  frees its sound.
- `agent-callback start` waits `AGENT_CALLBACK_DELAY` seconds, then shows the
  notification (`lib/agent-callback-notify.py`, a small Python/GLib program
  that stays alive so it can close the notification later, since GNOME only lets
  the creator close it) and plays the chime bursts in a background loop.
  State and PIDs live in `~/.local/state/agent-callback/<session>/`.
- **Away / locked:** idle time comes from `org.gnome.Mutter.IdleMonitor`, the
  lock state from `org.gnome.ScreenSaver` (both over D-Bus with `gdbus`).
- **Click → GNOME Terminal:** the tab id comes from `GNOME_TERMINAL_SCREEN`
  and is opened through GNOME Terminal's search provider (`ActivateResult`).
  Wayland makes GNOME show its "is ready" prompt first; there is no way around
  that for a background program.
- **Click → code editor:** when the alert starts, it walks up the process tree
  from the agent to find the editor binary hosting the terminal (`code`,
  `cursor`, ...). On click it runs `agent-callback __focus <editor> <folder>`,
  which reads the editor's window titles with `xprop`, finds the deepest
  folder (from the session's folder upwards) named in a title, and runs
  `<editor> <that folder>`. The editor then focuses the window that already
  has it open.
- **Safety:** nothing goes over the network. Session ids are sanitised before
  being used as folder names. Recorded PIDs are checked against their command
  line before being killed, so a reused PID is never hit.

## Adding another editor

VS Code-based editors need one word added to the `EDITORS` list in
`bin/agent-callback`: the name of the editor's binary, which you can see with
`readlink /proc/<pid>/exe`, mapped to its command-line launcher. Check
that its `WM_CLASS` (from `xprop`) contains the launcher name, then test from the
editor's terminal. To force it without code changes, set
`AGENT_CALLBACK_EDITOR=<launcher>`.

Other editors need their own focus method. For JetBrains IDEs the likely
route is the IDE's launcher (`pycharm <folder>`, which focuses an open
project) with the binary name detected the same way. It's untested, so it isn't
included. Contributions with a tested setup are welcome.

## Troubleshooting

- **No sound?** Run `AGENT_CALLBACK_DELAY=0 agent-callback start --message test`
  in a terminal (after `./install.sh`), then `hush`.
- **Not triggering in Claude Code?** Check `/hooks` lists the agent-callback hooks,
  and set `AGENT_CALLBACK_LOG=/tmp/agent-callback.log` to see every hook call.
- **Clicking does nothing in VS Code / Cursor?** Check that the editor's
  command works in a terminal (`code --version`, `cursor --version`), that
  `xprop -root _NET_CLIENT_LIST` lists windows, and that the window title
  shows your project folder name. You can test the jump directly:
  `agent-callback __focus code ~/path/to/project`.
- **Cursor quits right after starting (AppImage)?** Some systems need it
  started with `--no-sandbox`. That's a Cursor issue, unrelated to agent-callback.
- **Sounds keep going after you replied?** If you answer "No" to a permission
  prompt, Claude Code doesn't always fire a hook. The alert still ends after its
  last burst, or run `hush`.

## Uninstall

```
/plugin uninstall agent-callback@agent-callback
/plugin marketplace remove agent-callback
```

and `./install.sh --uninstall` if you installed the terminal commands.

## Development

```bash
claude --plugin-dir ~/path/to/agent-callback     # load your working copy for one session
claude plugin validate ~/path/to/agent-callback  # check the manifests
```

Inside a session, `/reload-plugins` picks up edits.

## License

MIT
