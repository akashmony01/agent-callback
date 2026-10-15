#!/usr/bin/env bash
# Install the agent-callback command-line tool into ~/.local (no sudo).
#
# Claude Code users don't need this: install the plugin instead (see README).
# Run it if you also want `agent-callback` and `hush` in your own terminal,
# or to hook agent-callback up to another AI tool.
#
#   ./install.sh               install or update
#   ./install.sh --uninstall   remove it again
#   PREFIX=/some/dir ./install.sh   install somewhere other than ~/.local
set -e

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PREFIX="${PREFIX:-$HOME/.local}"
DEST="$PREFIX/share/agent-callback"
BIN="$PREFIX/bin"
MARK="# installed by agent-callback"

ours() { [[ -f "$1" ]] && grep -q "$MARK" "$1"; }

if [[ "$1" == "--uninstall" ]]; then
  "$BIN/agent-callback" hush >/dev/null 2>&1 || true
  for f in "$BIN/agent-callback" "$BIN/hush"; do ours "$f" && rm -f "$f"; done
  rm -rf "$DEST"
  echo "agent-callback removed from $PREFIX."
  exit 0
fi

mkdir -p "$DEST" "$BIN"
rm -rf "$DEST/bin" "$DEST/lib"
cp -R "$SRC/bin" "$SRC/lib" "$DEST/"
chmod +x "$DEST/bin/agent-callback" "$DEST/lib/agent-callback-notify.py"

write_wrapper() { # name, args
  local path="$BIN/$1"; shift
  if [[ -e "$path" ]] && ! ours "$path"; then
    echo "  skipped $path (a different '$(basename "$path")' already exists)"
    return
  fi
  printf '#!/usr/bin/env bash\n%s\nexec "%s" %s "$@"\n' "$MARK" "$DEST/bin/agent-callback" "$*" > "$path"
  chmod +x "$path"
  echo "  $path"
}

echo "Installed agent-callback to $DEST"
write_wrapper agent-callback
write_wrapper hush hush

# Friendly checks for what it needs at runtime.
missing=()
command -v jq >/dev/null || missing+=("jq (needed by the Claude Code adapter)")
if [[ "$(uname)" == "Darwin" ]]; then
  command -v afplay >/dev/null || missing+=("afplay")
else
  command -v pw-play >/dev/null || command -v paplay >/dev/null || command -v aplay >/dev/null \
    || missing+=("a sound player: pw-play, paplay or aplay")
  python3 -c 'import gi' 2>/dev/null || missing+=("python3-gi (for desktop notifications)")
  command -v gdbus >/dev/null || missing+=("gdbus (idle/lock detection, from libglib2.0-bin)")
  command -v xprop >/dev/null || missing+=("xprop (click-to-focus for code editors, from x11-utils)")
fi
(( ${#missing[@]} )) && printf 'Missing (optional but recommended):\n%s\n' "$(printf '  - %s\n' "${missing[@]}")"

case ":$PATH:" in
  *":$BIN:"*) ;;
  *) echo "Note: $BIN is not on your PATH. Add this to your shell config:"
     echo "  export PATH=\"$BIN:\$PATH\"" ;;
esac
echo "Done. Try: agent-callback --help"
