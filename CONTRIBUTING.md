# Contributing to agent-callback

Thanks for helping! agent-callback is small on purpose: a bash script, a short
Python notifier and a few hooks. Contributions that keep it that way are the
easiest to merge.

## Most wanted

- **Test reports** from setups marked 🟡 *untested* in the README tables (Linux
  Mint, XFCE, MATE, Plasma 5, Kitty, WezTerm, Ptyxis, macOS, ...). Open an issue
  with the *Works on my setup* or *Bug report* form, even if everything works.
- **Adapters for other AI tools** (Codex CLI, Gemini CLI, Aider, ...). See
  `adapters/claude-code/hook.sh` for the pattern: call `agent-callback start`
  when the tool waits for you and `agent-callback stop` when you respond.
- **More editors and terminals** for click-to-focus. See *Adding another editor
  or terminal* in the README.

## Developing

```bash
git clone https://github.com/akashmony01/agent-callback && cd agent-callback
claude --plugin-dir .                  # run Claude Code with your working copy
claude plugin validate .               # check the manifests
```

Inside that session, `/reload-plugins` picks up your edits. To try an alert
without Claude Code:

```bash
AGENT_CALLBACK_DELAY=0 AGENT_CALLBACK_LOG=/tmp/agent-callback.log \
  bin/agent-callback start --session test --message "hello" --cwd "$PWD"
bin/agent-callback hush
```

Before opening a pull request:

```bash
bash -n bin/agent-callback adapters/claude-code/hook.sh install.sh
shellcheck -S warning bin/agent-callback adapters/claude-code/hook.sh install.sh
python3 -m py_compile lib/agent-callback-notify.py
```

CI runs the same checks on every pull request.

## Guidelines

- **Portability:** `bin/agent-callback` must run on macOS's bash 3.2, so no
  associative arrays, `;;&`, `mapfile` or `${var,,}`.
- **No new hard dependencies.** Optional tools (`wmctrl`, `xprintidle`,
  `terminal-notifier`, ...) are fine if things degrade quietly without them.
- **Nothing over the network**, and never kill a PID without checking it's ours
  (`is_ours`).
- Say in the pull request which desktops and terminals you tested on, and update
  the README tables.
- Add a line to `CHANGELOG.md` under an `## Unreleased` heading.

## Releasing (maintainers)

Bump `version` in `.claude-plugin/plugin.json`, rename `## Unreleased` in
`CHANGELOG.md` to the version, commit, then `git tag vX.Y.Z && git push origin
main vX.Y.Z`. The Release workflow publishes the GitHub release.
