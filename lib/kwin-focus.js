// KWin script used by `agent-callback __focus` on KDE Plasma (Wayland and X11).
// agent-callback prepends `var ARGS = {...};` with:
//   pids  - process ids from the agent up to the root, nearest first
//   key   - lowercase window-class fragment to fall back on (editors), or ""
//   hints - caption fragments that identify the right window, best first
// The nearest process that owns windows decides. One window: raise it. Several:
// raise the first one whose caption matches a hint; none match: do nothing
// rather than guess.
(function () {
    var all = workspace.windowList ? workspace.windowList() : workspace.clientList();
    var wins = [], i, j, p, m;
    for (i = 0; i < all.length; i++) {
        if (all[i].normalWindow) wins.push(all[i]);
    }

    function pick(list) {
        if (list.length === 1) return list[0];
        for (var h = 0; h < ARGS.hints.length; h++) {
            for (var k = 0; k < list.length; k++) {
                if ((" - " + list[k].caption + " - ").indexOf(ARGS.hints[h]) >= 0) return list[k];
            }
        }
        return null;
    }

    var chosen = null, matched = false;
    for (p = 0; p < ARGS.pids.length && !matched; p++) {
        m = [];
        for (j = 0; j < wins.length; j++) if (wins[j].pid === ARGS.pids[p]) m.push(wins[j]);
        if (m.length) { matched = true; chosen = pick(m); }
    }
    if (!matched && ARGS.key) {
        m = [];
        for (j = 0; j < wins.length; j++) {
            if (String(wins[j].resourceClass).toLowerCase().indexOf(ARGS.key) >= 0) m.push(wins[j]);
        }
        if (m.length) chosen = pick(m);
    }
    if (!chosen) return;
    if (chosen.minimized) chosen.minimized = false;
    if ("activeWindow" in workspace) workspace.activeWindow = chosen;  // Plasma 6
    else workspace.activeClient = chosen;                               // Plasma 5
})();
