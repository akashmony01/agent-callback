#!/usr/bin/env python3
"""Persistent desktop notification for agent-callback (Linux).

Usage: agent-callback-notify.py <pidfile> <app> <title> <body> [terminal-tab-id] [on-click command...]

Shows a critical notification with a "Stop sound" button and blocks until the
user closes it or clicks it (exit 0). Clicking the body also brings the
GNOME Terminal tab that runs the session to the front, or runs the on-click
command (used to raise a code editor's window). On SIGTERM it closes the
notification itself (exit 1) -- GNOME only lets the creating process close it.
"""
import os
import signal
import subprocess
import sys

import gi

gi.require_version("Gio", "2.0")
from gi.repository import Gio, GLib  # noqa: E402

BUS, PATH = "org.freedesktop.Notifications", "/org/freedesktop/Notifications"

pidfile, app, title, body = sys.argv[1:5]
tab_id = sys.argv[5] if len(sys.argv) > 5 else ""
on_click = sys.argv[6:]
with open(pidfile, "w") as f:
    f.write(str(os.getpid()))

conn = Gio.bus_get_sync(Gio.BusType.SESSION, None)
loop = GLib.MainLoop()
result = {"code": 0}


def call(method, params, reply=None):
    return conn.call_sync(BUS, PATH, BUS, method, params, reply,
                          Gio.DBusCallFlags.NONE, -1, None)


hints = {"urgency": GLib.Variant("y", 2), "resident": GLib.Variant("b", True)}

nid = call(
    "Notify",
    GLib.Variant("(susssasa{sv}i)", (
        app, 0, "dialog-information", title, body,
        ["default", "", "stop", "Stop sound"],
        hints,
        0,
    )),
    GLib.VariantType("(u)"),
).unpack()[0]


def focus_terminal_tab():
    # Same call GNOME's Activities search uses to jump to a terminal tab.
    try:
        conn.call_sync("org.gnome.Terminal", "/org/gnome/Terminal/SearchProvider",
                       "org.gnome.Shell.SearchProvider2", "ActivateResult",
                       GLib.Variant("(sasu)", (tab_id, [], 0)), None,
                       Gio.DBusCallFlags.NONE, 2000, None)
    except GLib.Error:
        pass


def on_signal(_c, _s, _p, _i, signal_name, params):
    if params.unpack()[0] != nid:
        return
    if signal_name == "ActionInvoked":
        if params.unpack()[1] == "default":
            if on_click:
                subprocess.Popen(on_click, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL, start_new_session=True)
            elif tab_id:
                focus_terminal_tab()
        try:
            call("CloseNotification", GLib.Variant("(u)", (nid,)))
        except GLib.Error:
            pass
    loop.quit()


for name in ("NotificationClosed", "ActionInvoked"):
    conn.signal_subscribe(BUS, BUS, name, PATH, None,
                          Gio.DBusSignalFlags.NONE, on_signal)


def on_term():
    try:
        call("CloseNotification", GLib.Variant("(u)", (nid,)))
    except GLib.Error:
        pass
    result["code"] = 1
    loop.quit()
    return GLib.SOURCE_REMOVE


GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, on_term)
loop.run()
sys.exit(result["code"])
