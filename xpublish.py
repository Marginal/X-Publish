#!/usr/bin/python

from os import getenv, listdir
from os.path import expanduser, exists, isdir, join, normpath
import sys	# for path, version
from sys import argv, exit, platform, getfilesystemencoding

if platform.lower().startswith('linux') and not getenv("DISPLAY"):
    print "Can't run: DISPLAY is not set"
    exit(1)

try:
    if platform=='darwin': sys.path.insert(0, join(sys.path[0],sys.version[:3]))
    import wx
except:
    import Tkinter, tkMessageBox
    Tkinter.Tk().withdraw()
    tkMessageBox.showerror("Error", "wxPython is not installed.\nThis application requires wxPython 2.8 or later.")
    exit(1)


from dopublish import publish
from utils import *
from version import appname, appversion


# wx 3 requires a MainLoop for Dialogs to work - so hack up a dummy frame and invoke MainLoop.
class MyApp(wx.App):

    def __init__(self):
        wx.App.__init__(self, redirect=not __debug__)
        self.folder = None
        self.dummy = wx.Frame(None)
        self.SetTopWindow(self.dummy)
        if platform=='win32':	# wx 3 ProgressDialog on windows cannot be hidden and has annoying disabled Close button
            self.progress = wx.GenericProgressDialog(appname, "Initializing", parent=self.dummy, style=wx.PD_APP_MODAL|wx.PD_SMOOTH)
        else:
            self.progress = wx.ProgressDialog(appname, "Initializing", parent=self.dummy, style=wx.PD_APP_MODAL|wx.PD_SMOOTH)
        if not platform.startswith('linux'): self.progress.Hide()	# can't be unhidden on wxGTK
        self.progress.SetDimensions(-1, -1, 320, -1, wx.SIZE_USE_EXISTING)
        self.Bind(wx.EVT_IDLE, self.activate)

    def activate(self, event):
        self.Unbind(wx.EVT_IDLE)
        if platform=='win32':
            from _winreg import OpenKey, QueryValueEx, HKEY_CURRENT_USER, REG_SZ, REG_EXPAND_SZ
            progs=getenv("PROGRAMFILES", '\\').decode('mbcs')
            for i in listdir(progs):
                if i.lower().startswith("x-plane") and isdir(join(progs, i, "Custom Scenery")):
                    folder=join(progs, i)
                    break
            else:
                folder=getenv("USERPROFILE", '\\').decode('mbcs')	# fallback
                try:
                    handle=OpenKey(HKEY_CURRENT_USER, 'Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\User Shell Folders')
                    (v,t)=QueryValueEx(handle, 'Desktop')
                    handle.Close()
                    if t==REG_EXPAND_SZ:
                        dirs=v.rstrip('\0').decode('mbcs').strip().split('\\')
                        for i in range(len(dirs)):
                            if dirs[i][0]==dirs[i][-1]=='%':
                                dirs[i]=getenv(dirs[i][1:-1],dirs[i]).decode('mbcs')
                        v='\\'.join(dirs)
                    if t in [REG_SZ,REG_EXPAND_SZ] and isdir(v):
                        folder=desktop=v
                        for i in listdir(desktop):
                            if i.lower().startswith("x-plane") and isdir(join(desktop, i, "Custom Scenery")):
                                folder=join(desktop, i)
                                break
                except:
                    pass
        else:
            try:
                home=expanduser('~').decode(getfilesystemencoding() or 'utf-8')	# Unicode so paths listed as unicode
                desktop=join(home, "Desktop")
            except:
                home=desktop=u'/'
            for i in listdir(desktop):
                if i.lower().startswith("x-plane") and isdir(join(desktop, i, "Custom Scenery")):
                    folder=join(desktop, i)
                    break
            else:
                for i in listdir(home):
                    if i.lower().startswith("x-plane") and isdir(join(home, i, "Custom Scenery")):
                        folder=join(home, i)
                        break
                else:
                    folder=home

        if not self.folder:
            style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER
            if 'DD_DIR_MUST_EXIST' in dir(wx): style|=wx.DD_DIR_MUST_EXIST
            if not platform.startswith('linux'):
                dlg=wx.DirDialog(self.dummy, 'Choose the folder that contains the aircraft or scenery that you want to publish', folder, style)
            else:	# displayed in title on linux
                dlg=wx.DirDialog(self.dummy, 'Select aircraft or scenery folder', folder, style)
            if dlg.ShowModal()!=wx.ID_OK: exit(1)
            self.folder = dlg.GetPath()

        publish(unicodeify(self.folder), self)
        exit(0)


app = MyApp()
if len(argv)>1:
    app.folder = unicodeify(argv[1])
app.MainLoop()
exit(0)
