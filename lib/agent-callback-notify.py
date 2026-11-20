#!/usr/bin/env python3
"""Persistent desktop notification for agent-callback (Linux).

Usage: agent-callback-notify.py <pidfile> <app> <title> <body> <seconds> [on-click command...]

Shows a critical notification with a "Stop sound" button and blocks until the
user closes it or clicks it (exit 0). Clicking the body also runs the on-click
command (agent-callback __focus, which brings the session's terminal tab or
editor window to the front). On SIGTERM it closes the notification itself
(exit 1) -- GNOME only lets the creating process close it. After <seconds>
(0 = never) it closes the notification itself too (exit 2), so it doesn't pile
up in the desktop's notification list. It is marked transient, so desktops
that keep a history (KDE, GNOME, ...) drop it instead of storing it.

Works with any freedesktop notification server (GNOME, KDE Plasma, Cinnamon,
XFCE's xfce4-notifyd, MATE, dunst, mako, ...).
"""
import os
import signal
import subprocess
import sys

import gi

gi.require_version("Gio", "2.0")
from gi.repository import Gio, GLib  # noqa: E402

try:  # GLib >= 2.80 moved unix_signal_add here
    gi.require_version("GLibUnix", "2.0")
    from gi.repository import GLibUnix  # noqa: E402
    unix_signal_add = GLibUnix.signal_add
except (ImportError, ValueError):
    unix_signal_add = GLib.unix_signal_add

BUS, PATH = "org.freedesktop.Notifications", "/org/freedesktop/Notifications"

pidfile, app, title, body = sys.argv[1:5]
timeout = int(sys.argv[5]) if len(sys.argv) > 5 and sys.argv[5].isdigit() else 0
on_click = sys.argv[6:]
with open(pidfile, "w") as f:
    f.write(str(os.getpid()))

conn = Gio.bus_get_sync(Gio.BusType.SESSION, None)
loop = GLib.MainLoop()
result = {"code": 0}
activation_token = {"value": ""}


def call(method, params, reply=None):
    return conn.call_sync(BUS, PATH, BUS, method, params, reply,
                          Gio.DBusCallFlags.NONE, -1, None)


hints = {"urgency": GLib.Variant("y", 2), "resident": GLib.Variant("b", True),
         "transient": GLib.Variant("b", True)}

nid = call(
    "Notify",
    GLib.Variant("(susssasa{sv}i)", (
        app, 0, "dialog-information", title, body,
        ["default", "", "stop", "Stop sound"],
        hints,
        timeout * 1000,  # backup: the server expires it if we're gone
    )),
    GLib.VariantType("(u)"),
).unpack()[0]


def run_on_click():
    if not on_click:
        return
    env = dict(os.environ)
    # Notification spec 1.2: the server hands us a token that lets the program
    # we start raise a window on Wayland (and a startup id on X11).
    if activation_token["value"]:
        env["XDG_ACTIVATION_TOKEN"] = activation_token["value"]
        env["DESKTOP_STARTUP_ID"] = activation_token["value"]
    subprocess.Popen(on_click, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL, start_new_session=True)


def on_signal(_c, _s, _p, _i, signal_name, params):
    args = params.unpack()
    if args[0] != nid:
        return
    if signal_name == "ActivationToken":
        activation_token["value"] = args[1]
        return  # always sent just before ActionInvoked
    if signal_name == "NotificationClosed" and args[1] == 1:
        result["code"] = 2  # expired by the server: not the user's doing
    if signal_name == "ActionInvoked":
        if args[1] == "default":
            run_on_click()
        try:
            call("CloseNotification", GLib.Variant("(u)", (nid,)))
        except GLib.Error:
            pass
    loop.quit()


for name in ("NotificationClosed", "ActionInvoked", "ActivationToken"):
    conn.signal_subscribe(BUS, BUS, name, PATH, None,
                          Gio.DBusSignalFlags.NONE, on_signal)


def close_self(code):
    result["code"] = code
    try:
        call("CloseNotification", GLib.Variant("(u)", (nid,)))
    except GLib.Error:
        pass
    loop.quit()
    return GLib.SOURCE_REMOVE


unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, lambda: close_self(1))
if timeout > 0:
    GLib.timeout_add_seconds(timeout, lambda: close_self(2))
loop.run()
sys.exit(result["code"])
