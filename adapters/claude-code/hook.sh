#!/usr/bin/env bash
# Claude Code adapter for agent-callback.
# Wired up by hooks/hooks.json; reads the hook's JSON on stdin.
#   hook.sh start   Claude finished its turn (Stop) or needs permission (Notification)
#   hook.sh stop    you responded (UserPromptSubmit, PostToolUse, PostToolUseFailure)
#   hook.sh end     the session closed (SessionEnd)

CLI="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/bin/agent-callback"

command -v jq >/dev/null || exit 0
input=$(cat)
session=$(jq -r '.session_id // empty' <<<"$input" 2>/dev/null)
[[ -n "$session" ]] || exit 0
# Troubleshooting: AGENT_CALLBACK_LOG=/path/to/file records every hook call.
[[ -n "$AGENT_CALLBACK_LOG" ]] &&
  echo "$(date '+%F %T') $1 session=$session event=$(jq -r '.hook_event_name // ""' <<<"$input")" >> "$AGENT_CALLBACK_LOG"

case "$1" in
  start)
    exec "$CLI" start --session "$session" --app "Claude Code" \
      --cwd "$(jq -r '.cwd // empty' <<<"$input")" \
      --message "$(jq -r '.message // "Claude is waiting for your input"' <<<"$input")" ;;
  stop) exec "$CLI" stop --session "$session" ;;
  end)  exec "$CLI" stop --session "$session" --end ;;
esac
exit 0
