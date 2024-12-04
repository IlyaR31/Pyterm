import time
import blessed
import string
import threading
import sys
if sys.platform == "darwin":
    from AppKit import NSWorkspace
    from Quartz import (
        CGWindowListCopyWindowInfo,
        kCGWindowListOptionOnScreenOnly,
        kCGNullWindowID
    )
elif sys.platform == "win32":
    import win32gui
from pynput import keyboard

CLOSED = False

symb = {
    "\t": "tab",
    "\n": "return",
    "\r": "backspace",
    " ": "space",
    "`": "backtick",
    "~": "tilde",
    "!": "exclamation",
    "@": "at sign",
    "#": "hashtag",
    "$": "dollar sign",
    "%": "percent sign",
    "^": "exponent",
    "&": "and",
    "*": "asterisk",
    "(": "open round bracket",
    ")": "close round bracket",
    "-": "minus",
    "_": "underscore",
    "=": "equals",
    "+": "plus",
    "[": "open square bracket",
    "]": "close square bracket",
    "{": "open brace",
    "}": "close brace",
    "\\": "backslash",
    "/": "slash",
    "|": "vertical pipe",
    ";": "semicolon",
    ":": "colon",
    "'": "single quote",
    '"': "double quotes",
    ",": "comma",
    ".": "dot",
    "<": "left angle bracket",
    ">": "right angle bracket",
    "?": "question mark"
}


def get_key_name(key):
    try:
        n = key.name.upper()
    except AttributeError:
        try:
            n = key.char
        except AttributeError:
            n = key
    if n in list(symb.keys()):
        n = symb[n].replace(" ", "_").upper()
    name = "KEY_" + n
    return name


def get_win():
    if sys.platform == "darwin":
        curr_app = NSWorkspace.sharedWorkspace().frontmostApplication()
        curr_pid = NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationProcessIdentifier']
        curr_app_name = curr_app.localizedName()
        options = kCGWindowListOptionOnScreenOnly
        windowList = CGWindowListCopyWindowInfo(options, kCGNullWindowID)
        for window in windowList:
            pid = window['kCGWindowOwnerPID']
            windowNumber = window['kCGWindowNumber']
            ownerName = window['kCGWindowOwnerName']
            geometry = window['kCGWindowBounds']
            windowTitle = window.get('kCGWindowName', u'Unknown')
            if curr_pid == pid:
                # print("%s - %s (PID: %d, WID: %d): %s" % (
                # ownerName, windowTitle.encode('ascii', 'ignore'), pid, windowNumber, geometry))
                return "|".join((str(ownerName), str(pid), str(windowNumber)))  # , str(windowTitle.encode('ascii', 'ignore'))
    elif sys.platform == 'win32':
        thetitle = win32gui.GetWindowText(hwnd)

pressed = {
    get_key_name(i): False
    for i in [
        *list(keyboard.Key.__dict__["_member_map_"].values()),
        *list(string.printable.lower().replace("\x0b", "").replace("\x0c", ""))
    ]
}

events = []

start_term = get_win()


def on_press(key):
    if start_term != get_win():
        for k in pressed.keys():
            pressed[k] = False
        return
    try:
        name = "KEY_" + key.name.upper()
    except AttributeError:
        name = "KEY_" + key.char
    if name not in pressed:
        pressed[name] = False
    if (name, "KEYDOWN") not in events:
        events.append((name, "KEYDOWN"))

    if not pressed[name]:
        pressed[name] = True


def on_release(key):
    if start_term != get_win():
        for k in pressed.keys():
            pressed[k] = False
        return
    try:
        name = "KEY_" + key.name.upper()
    except AttributeError:
        name = "KEY_" + key.char
    if name not in pressed:
        pressed[name] = False

    if (name, "KEYUP") in events:
        events.remove((name, "KEYUP"))

    if pressed[name]:
        pressed[name] = False


def start():
    with keyboard.Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        term = blessed.Terminal()
        with term.cbreak(), term.hidden_cursor():
            # listener.join()
            while not CLOSED:
                time.sleep(0.01)
            listener.stop()


def get_pressed():
    return pressed


class Event:
    def __init__(self, key, event_type):
        self.__key = key
        self.__type = event_type

    @property
    def key(self):
        return self.__key

    @property
    def type(self):
        return self.__type

    def __str__(self):
        return f"Event(key={self.key}, type={self.type})"

    def __repr__(self):
        return f"Event(key={self.key}, type={self.type})"

    def __eq__(self, other):
        if not isinstance(other, Event):
            return False
        return self.key == other.key and self.__type == other.type


def get():
    ev = [Event(*event) for event in events.copy()]
    events.clear()
    return ev


th = threading.Thread(target=start)
th.start()
