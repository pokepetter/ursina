import os
import sys


class Monitor(object):
    x = 0
    y = 0
    width = 0
    height = 0

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __repr__(self):
        return 'monitor(%dx%d+%d+%d)' % (
            self.width, self.height, self.x, self.y)


def _enumerate_windows():
    import ctypes
    import ctypes.wintypes
    monitors = []

    def callback(_monitor, _dc, rect, _data):
        rct = rect.contents
        monitors.append(Monitor(
            rct.left,
            rct.top,
            rct.right - rct.left,
            rct.bottom - rct.top))
        return 1

    MonitorEnumProc = ctypes.WINFUNCTYPE(
        ctypes.c_int,
        ctypes.c_ulong,
        ctypes.c_ulong,
        ctypes.POINTER(ctypes.wintypes.RECT),
        ctypes.c_double)

    ctypes.windll.user32.EnumDisplayMonitors(
        0, 0, MonitorEnumProc(callback), 0)

    return monitors


def _enumerate_cygwin():
    import ctypes
    user32 = ctypes.cdll.LoadLibrary('user32.dll')

    LONG = ctypes.c_int32
    BOOL = ctypes.c_int
    HANDLE = ctypes.c_void_p
    HMONITOR = HANDLE
    HDC = HANDLE

    ptr_size = ctypes.sizeof(ctypes.c_void_p)
    if ptr_size == ctypes.sizeof(ctypes.c_long):
        WPARAM = ctypes.c_ulong
        LPARAM = ctypes.c_long
    elif ptr_size == ctypes.sizeof(ctypes.c_longlong):
        WPARAM = ctypes.c_ulonglong
        LPARAM = ctypes.c_longlong

    class RECT(ctypes.Structure):
        _fields_ = [
            ('left', LONG),
            ('top', LONG),
            ('right', LONG),
            ('bottom', LONG)
        ]

    MonitorEnumProc = ctypes.CFUNCTYPE(
        BOOL,
        HMONITOR,
        HDC,
        ctypes.POINTER(RECT),
        LPARAM)

    user32.EnumDisplayMonitors.argtypes = [
        HANDLE,
        ctypes.POINTER(RECT),
        MonitorEnumProc,
        LPARAM]
    user32.EnumDisplayMonitors.restype = ctypes.c_bool

    monitors = []

    def callback(_monitor, _dc, rect, _data):
        rct = rect.contents
        monitors.append(Monitor(
            rct.left,
            rct.top,
            rct.right - rct.left,
            rct.bottom - rct.top))
        return 1

    user32.EnumDisplayMonitors(None, None, MonitorEnumProc(callback), 0)
    return monitors


def _enumerate_x11():
    import ctypes
    import ctypes.util

    def load_library(name):
        path = ctypes.util.find_library(name)
        if not path:
            raise ImportError('Could not load ' + name)
        return ctypes.cdll.LoadLibrary(path)

    class XineramaScreenInfo(ctypes.Structure):
        _fields_ = [
            ('screen_number', ctypes.c_int),
            ('x', ctypes.c_short),
            ('y', ctypes.c_short),
            ('width', ctypes.c_short),
            ('height', ctypes.c_short),
        ]

    xlib = load_library('X11')
    xlib.XOpenDisplay.argtypes = [ctypes.c_char_p]
    xlib.XOpenDisplay.restype = ctypes.POINTER(ctypes.c_void_p)
    d = xlib.XOpenDisplay(b'')
    if not d:
        raise Exception('Could not open display')

    xinerama = load_library('Xinerama')
    if not xinerama.XineramaIsActive(d):
        raise Exception('Xinerama is not active')

    number = ctypes.c_int()
    xinerama.XineramaQueryScreens.restype = (
        ctypes.POINTER(XineramaScreenInfo))
    infos = xinerama.XineramaQueryScreens(d, ctypes.byref(number))
    infos = ctypes.cast(
        infos, ctypes.POINTER(XineramaScreenInfo * number.value)).contents

    return [Monitor(i.x, i.y, i.width, i.height) for i in infos]


def _enumerate_osx():
    from pyobjus import autoclass
    from pyobjus.dylib_manager import load_framework, INCLUDE
    load_framework(INCLUDE.AppKit)

    screens = autoclass('NSScreen').screens()
    monitors = []

    for i in range(screens.count()):
        f = screens.objectAtIndex_(i).frame
        if callable(f):
            f = f()

        monitors.append(
            Monitor(f.origin.x, f.origin.y, f.size.width, f.size.height))

    return monitors


_ENUMERATORS = {
    'windows': _enumerate_windows,
    'cygwin': _enumerate_cygwin,
    'x11': _enumerate_x11,
    'osx': _enumerate_osx,
}


def _get_enumerator():
    for enumerator in _ENUMERATORS.values():
        try:
            enumerator()
            return enumerator
        except:
            pass
    raise NotImplementedError('This environment is not supported.')


def get_monitors(name=None):
    enumerator = _ENUMERATORS[name] if name else _get_enumerator()
    return enumerator()


if __name__ == '__main__':
    for m in get_monitors():
        print(str(m))
