# Lepes Virtual Keys Map

from operator import *
import  wx
#----------------------------------------------------------------------

keyMap = {
    wx.WXK_BACK : "WXK_BACK",
    wx.WXK_TAB : "WXK_TAB",
    wx.WXK_RETURN : "WXK_RETURN",
    wx.WXK_ESCAPE : "WXK_ESCAPE",
    wx.WXK_SPACE : "WXK_SPACE",
    wx.WXK_DELETE : "WXK_DELETE",
    wx.WXK_START : "WXK_START",
    wx.WXK_LBUTTON : "WXK_LBUTTON",
    wx.WXK_RBUTTON : "WXK_RBUTTON",
    wx.WXK_CANCEL : "WXK_CANCEL",
    wx.WXK_MBUTTON : "WXK_MBUTTON",
    wx.WXK_CLEAR : "WXK_CLEAR",
    wx.WXK_SHIFT : "WXK_SHIFT",
    wx.WXK_ALT : "WXK_ALT",
    wx.WXK_CONTROL : "WXK_CONTROL",
    wx.WXK_MENU : "WXK_MENU",
    wx.WXK_PAUSE : "WXK_PAUSE",
    wx.WXK_CAPITAL : "WXK_CAPITAL",
    #wx.WXK_PRIOR : "WXK_PRIOR",
    #wx.WXK_NEXT : "WXK_NEXT",
    wx.WXK_END : "WXK_END",
    wx.WXK_HOME : "WXK_HOME",
    wx.WXK_LEFT : "WXK_LEFT",
    wx.WXK_UP : "WXK_UP",
    wx.WXK_RIGHT : "WXK_RIGHT",
    wx.WXK_DOWN : "WXK_DOWN",
    wx.WXK_SELECT : "WXK_SELECT",
    wx.WXK_PRINT : "WXK_PRINT",
    wx.WXK_EXECUTE : "WXK_EXECUTE",
    wx.WXK_SNAPSHOT : "WXK_SNAPSHOT",
    wx.WXK_INSERT : "WXK_INSERT",
    wx.WXK_HELP : "WXK_HELP",
    wx.WXK_NUMPAD0 : "WXK_NUMPAD0",
    wx.WXK_NUMPAD1 : "WXK_NUMPAD1",
    wx.WXK_NUMPAD2 : "WXK_NUMPAD2",
    wx.WXK_NUMPAD3 : "WXK_NUMPAD3",
    wx.WXK_NUMPAD4 : "WXK_NUMPAD4",
    wx.WXK_NUMPAD5 : "WXK_NUMPAD5",
    wx.WXK_NUMPAD6 : "WXK_NUMPAD6",
    wx.WXK_NUMPAD7 : "WXK_NUMPAD7",
    wx.WXK_NUMPAD8 : "WXK_NUMPAD8",
    wx.WXK_NUMPAD9 : "WXK_NUMPAD9",
    wx.WXK_MULTIPLY : "WXK_MULTIPLY",
    wx.WXK_ADD : "WXK_ADD",
    wx.WXK_SEPARATOR : "WXK_SEPARATOR",
    wx.WXK_SUBTRACT : "WXK_SUBTRACT",
    wx.WXK_DECIMAL : "WXK_DECIMAL",
    wx.WXK_DIVIDE : "WXK_DIVIDE",
    wx.WXK_F1 : "WXK_F1",
    wx.WXK_F2 : "WXK_F2",
    wx.WXK_F3 : "WXK_F3",
    wx.WXK_F4 : "WXK_F4",
    wx.WXK_F5 : "WXK_F5",
    wx.WXK_F6 : "WXK_F6",
    wx.WXK_F7 : "WXK_F7",
    wx.WXK_F8 : "WXK_F8",
    wx.WXK_F9 : "WXK_F9",
    wx.WXK_F10 : "WXK_F10",
    wx.WXK_F11 : "WXK_F11",
    wx.WXK_F12 : "WXK_F12",
    wx.WXK_F13 : "WXK_F13",
    wx.WXK_F14 : "WXK_F14",
    wx.WXK_F15 : "WXK_F15",
    wx.WXK_F16 : "WXK_F16",
    wx.WXK_F17 : "WXK_F17",
    wx.WXK_F18 : "WXK_F18",
    wx.WXK_F19 : "WXK_F19",
    wx.WXK_F20 : "WXK_F20",
    wx.WXK_F21 : "WXK_F21",
    wx.WXK_F22 : "WXK_F22",
    wx.WXK_F23 : "WXK_F23",
    wx.WXK_F24 : "WXK_F24",
    wx.WXK_NUMLOCK : "WXK_NUMLOCK",
    wx.WXK_SCROLL : "WXK_SCROLL",
    wx.WXK_PAGEUP : "WXK_PAGEUP",
    wx.WXK_PAGEDOWN : "WXK_PAGEDOWN",
    wx.WXK_NUMPAD_SPACE : "WXK_NUMPAD_SPACE",
    wx.WXK_NUMPAD_TAB : "WXK_NUMPAD_TAB",
    wx.WXK_NUMPAD_ENTER : "WXK_NUMPAD_ENTER",
    wx.WXK_NUMPAD_F1 : "WXK_NUMPAD_F1",
    wx.WXK_NUMPAD_F2 : "WXK_NUMPAD_F2",
    wx.WXK_NUMPAD_F3 : "WXK_NUMPAD_F3",
    wx.WXK_NUMPAD_F4 : "WXK_NUMPAD_F4",
    wx.WXK_NUMPAD_HOME : "WXK_NUMPAD_HOME",
    wx.WXK_NUMPAD_LEFT : "WXK_NUMPAD_LEFT",
    wx.WXK_NUMPAD_UP : "WXK_NUMPAD_UP",
    wx.WXK_NUMPAD_RIGHT : "WXK_NUMPAD_RIGHT",
    wx.WXK_NUMPAD_DOWN : "WXK_NUMPAD_DOWN",
    #wx.WXK_NUMPAD_PRIOR : "WXK_NUMPAD_PRIOR",
    wx.WXK_NUMPAD_PAGEUP : "WXK_NUMPAD_PAGEUP",
    #wx.WXK_NUMPAD_NEXT : "WXK_NUMPAD_NEXT",
    wx.WXK_NUMPAD_PAGEDOWN : "WXK_NUMPAD_PAGEDOWN",
    wx.WXK_NUMPAD_END : "WXK_NUMPAD_END",
    wx.WXK_NUMPAD_BEGIN : "WXK_NUMPAD_BEGIN",
    wx.WXK_NUMPAD_INSERT : "WXK_NUMPAD_INSERT",
    wx.WXK_NUMPAD_DELETE : "WXK_NUMPAD_DELETE",
    wx.WXK_NUMPAD_EQUAL : "WXK_NUMPAD_EQUAL",
    wx.WXK_NUMPAD_MULTIPLY : "WXK_NUMPAD_MULTIPLY",
    wx.WXK_NUMPAD_ADD : "WXK_NUMPAD_ADD",
    wx.WXK_NUMPAD_SEPARATOR : "WXK_NUMPAD_SEPARATOR",
    wx.WXK_NUMPAD_SUBTRACT : "WXK_NUMPAD_SUBTRACT",
    wx.WXK_NUMPAD_DECIMAL : "WXK_NUMPAD_DECIMAL",
    wx.WXK_NUMPAD_DIVIDE : "WXK_NUMPAD_DIVIDE",

    wx.WXK_WINDOWS_LEFT : "WXK_WINDOWS_LEFT",
    wx.WXK_WINDOWS_RIGHT : "WXK_WINDOWS_RIGHT",
    wx.WXK_WINDOWS_MENU : "WXK_WINDOWS_MENU",

    wx.WXK_COMMAND : "WXK_COMMAND",

    wx.WXK_SPECIAL1 : "WXK_SPECIAL1",
    wx.WXK_SPECIAL2 : "WXK_SPECIAL2",
    wx.WXK_SPECIAL3 : "WXK_SPECIAL3",
    wx.WXK_SPECIAL4 : "WXK_SPECIAL4",
    wx.WXK_SPECIAL5 : "WXK_SPECIAL5",
    wx.WXK_SPECIAL6 : "WXK_SPECIAL6",
    wx.WXK_SPECIAL7 : "WXK_SPECIAL7",
    wx.WXK_SPECIAL8 : "WXK_SPECIAL8",
    wx.WXK_SPECIAL9 : "WXK_SPECIAL9",
    wx.WXK_SPECIAL10 : "WXK_SPECIAL10",
    wx.WXK_SPECIAL11 : "WXK_SPECIAL11",
    wx.WXK_SPECIAL12 : "WXK_SPECIAL12",
    wx.WXK_SPECIAL13 : "WXK_SPECIAL13",
    wx.WXK_SPECIAL14 : "WXK_SPECIAL14",
    wx.WXK_SPECIAL15 : "WXK_SPECIAL15",
    wx.WXK_SPECIAL16 : "WXK_SPECIAL16",
    wx.WXK_SPECIAL17 : "WXK_SPECIAL17",
    wx.WXK_SPECIAL18 : "WXK_SPECIAL18",
    wx.WXK_SPECIAL19 : "WXK_SPECIAL19",
    wx.WXK_SPECIAL2 : "WXK_SPECIAL2",
}
def LogKeyEvent(self, evType, evt):
    keycode = evt.GetKeyCode()
    keyname = keyMap.get(keycode, None)

    if keyname is None:
        if keycode < 256:
            if keycode == 0:
                keyname = "NUL"
            elif keycode < 27:
                keyname = "Ctrl-%s" % chr(ord('A') + keycode-1)
            else:
                keyname = "\"%s\"" % chr(keycode)
        else:
            keyname = "(%s)" % keycode

    UniChr = ''
    if "unicode" in wx.PlatformInfo:
        UniChr = "\"" + unichr(evt.GetUnicodeKey()) + "\""

    modifiers = ""
    for mod, ch in [(evt.ControlDown(), 'C'),
                    (evt.AltDown(),     'A'),
                    (evt.ShiftDown(),   'S'),
                    (evt.MetaDown(),    'M')]:
        if mod:
            modifiers += ch
        else:
            modifiers += '-'

    id = self.InsertStringItem(self.GetItemCount(), evType)
    self.SetStringItem(id, 1, keyname)
    self.SetStringItem(id, 2, str(keycode))
    self.SetStringItem(id, 3, modifiers)
    self.SetStringItem(id, 4, str(evt.GetUnicodeKey()))
    self.SetStringItem(id, 5, UniChr)
    self.SetStringItem(id, 6, str(evt.GetRawKeyCode()))
    self.SetStringItem(id, 7, str(evt.GetRawKeyFlags()))

    #print ( id, evType, keyname, str(keycode), modifiers, str(evt.GetRawKeyCode()), str(evt.GetRawKeyFlags()))


WXK_A	=	65
WXK_B	=	66
WXK_C	=	67
WXK_D	=	68
WXK_E	=	69
WXK_F	=	70
WXK_G	=	71
WXK_H	=	72
WXK_I	=	73
WXK_J	=	74
WXK_K	=	75
WXK_L	=	76
WXK_M	=	77
WXK_N	=	78
WXK_O	=	79
WXK_P	=	80
WXK_Q	=	81
WXK_R	=	82
WXK_S	=	83
WXK_T	=	84
WXK_U	=	85
WXK_V	=	86
WXK_W	=	87
WXK_X	=	88
WXK_Y	=	89
WXK_Z	=	90
WXK_DEL  =       127
WXK_DOT  = ord(".")
WXK_COMMA = ord(",")

ZOOM_IN = "ZOOM_IN"
ZOOM_OUT = "ZOO_OUT"
LEFT = "LEFT"
RIGHT = "RIGHT"
UP = "UP"
DOWN = "DOWN"
ANCHOR = "ANCHOR"

commands = {ZOOM_IN   :{"key": WXK_W, "desc" : "zoom in"},
            ZOOM_OUT  :{"key": WXK_S, "desc" : "zoom out"},
            LEFT      :{"key": WXK_A, "desc" : "move left"},
            RIGHT     :{"key": WXK_D, "desc" : "move right"},
            UP        :{"key": WXK_F, "desc" : "move up"},
            DOWN      :{"key": WXK_V, "desc" : "move down"},
            ANCHOR    :{"key": WXK_Q, "desc" : "un/anchor camera to selected object"}
           }
def getCommand(keyCode):
    for a in commands.iterkeys():
        if commands[a]["key"] == keyCode:
            return a
    return None

if __name__ == "__main__":
    keyCode = 92
    i= 0
    for i in range (0, 256):
    	print 'keycode %d is "%s"' % ( i, chr(i))

    a =  getCommand(keyCode)
    print "key %d is '%s'" % (keyCode, chr(keyCode))
    if a:
        print "command " + str(a) + " desc: " + commands[a]["desc"]
    else:
        print " key %s is not a command" % keyCode
