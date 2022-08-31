import ctypes
from ctypes import wintypes

GetKeyState = ctypes.windll.user32.GetKeyState
GetKeyState.argtypes = (ctypes.c_int,)
GetKeyState.restype = wintypes.USHORT  # !!! It's actually wt.SHORT, but chose unsigned for display purposes !!!
scancodes = [
'', '', '', '', '', '', '', '', # 8 unused
'backspace', # 8
'tab', # 9
'', '', '', # 10,11,12
'enter', # 13
'', '', # 14, 15
'shift', # 16
'control', #17
'alt', # 18
'pause/break', # pause/break	19
'capslock', # 20
'', '', '', '', '', '', # 21-26
'escape', #	27
'', '', '', '',
'space', #32
'page up', #	33
'page down', #	34
'end', #	35
'home', #	36
'arrow left', #	37
'arrow up', #	38
'arrow right', #	39
'arrow down', #	40
'','','',
'printscreen', #	44
'insert', #	45
'delete', #	46
'', # 47
'0','1','2','3','4','5','6','7','8','9', # 48-57
'','','','','','','', # 58-64
'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
'', # left window key	91
'', # right window key	92
'', # select key	93
'', '',
'numpad 0', # numpad 0	96
'numpad 1', # numpad 1	97
'numpad 2', # numpad 2	98
'numpad 3', # numpad 3	99
'numpad 4', # numpad 4	100
'numpad 5', # numpad 5	101
'numpad 6', # numpad 6	102
'numpad 7', # numpad 7	103
'numpad 8', # numpad 8	104
'numpad 9', # numpad 9	105
'*', # multiply	106
'+', # add	107
'',
'-', # subtract	109
'.', # decimal point	110
'/', # divide	111
# f1-f12, 112-123
'f1','f2','f3','f4','f5','f6','f7','f8','f9','f10','f11','f12',
'', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
'num lock', # num lock	144
'scroll lock', # scroll lock	145
*['' for i in range(146, 186)],
# My Computer (multimedia keyboard)	182
# My Calculator (multimedia keyboard)	183
';', # 186
'=', # equal sign	187
',', # comma	188
'-', # dash	189
'.', # period	190
'/', # forward slash	191
'(' # open bracket	219
'\\', # back slash	220
')', # close braket	221
'\'' # single quote	222
]
for i, e in enumerate(scancodes):
    print(i, e)

from collections import defaultdict
held_keys = defaultdict(lambda: 0)

while True:
    for i, key in enumerate(scancodes):
        # vkc = 65  # 65, 'A'
        # ks = GetKeyState(vkc)
        is_pressed = int(GetKeyState(i) > 1)
        if not held_keys[key] and is_pressed:
            print(key)
        elif held_keys[key] and not is_pressed:
            print(key + ' up')
        held_keys[key] = is_pressed
        # print(ks)
    # print(held_keys)
    # if any(held_keys.values()):
    #     for key, value in held_keys.items():
    #             if value:
    #                 print(key,value)
    # else:
    #     print(' ')
