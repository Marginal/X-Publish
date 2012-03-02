import os
from os import getenv, listdir
from os.path import abspath, expanduser, exists, isdir, join, normpath, sep
from sys import exit, platform, getfilesystemencoding
import types
import unicodedata
from urllib import quote

from version import appname, appversion

if not 'startfile' in dir(os):
    import webbrowser

try:
    import wx
except:
    import Tkinter, tkMessageBox
    Tkinter.Tk().withdraw()
    tkMessageBox.showerror("Error", "wxPython is not installed.\nThis application requires wxPython 2.5.3 or later.")
    exit(1)

app=wx.App()

def choosefolder():
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
                    dirs=v.rstrip('\0').strip().split('\\')
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
        
    style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER
    if 'DD_DIR_MUST_EXIST' in dir(wx): style|=wx.DD_DIR_MUST_EXIST
    if platform=='win32':
        dlg=wx.DirDialog(None, 'Choose the folder that contains the aircraft or scenery that you want to publish', folder, style)
    else:	# displayed in title on linux
        dlg=wx.DirDialog(None, 'Select aircraft or scenery folder', folder, style)
    if dlg.ShowModal()!=wx.ID_OK: exit(1)
    folder=dlg.GetPath()
    dlg.Destroy()
            
    if not folder: exit(0)
    return unicodeify(folder)


class Progress(wx.ProgressDialog):
    def __init__(self, message):
        wx.ProgressDialog.__init__(self, appname, message, 105, None, wx.PD_SMOOTH)
        # wx.PD_CAN_ABORT is unresponsive (no event loop?)
        # hack to make wider:
        (x,y)=self.GetClientSize()
        self.SetClientSize((320,y))
        self.Update(1)	# show some progress

    def update(self, message, newval):
        if not self.Update(2+newval, message):
            raise KeyboardInterrupt

    
def die(message):
    wx.MessageBox(message, appname, wx.ICON_ERROR|wx.OK)
    exit(1)


# Locate file case-insensitively
# assumes root already case corrected
def casepath(root, path):
    elems=normpath(path).split(sep)
    path=''
    while elems:
        try:
            for f in listdir(join(root,path)):
                n=unicodeify(f)
                if elems[0].lower()==n.lower():
                    path=join(path,n)
                    elems.pop(0)
                    break
            else:
                raise IOError
        except:
            return join(path,*elems)
    return path


# 2.3 version of case-insensitive sort
# 2.4-only version is faster: sort(cmp=lambda x,y: cmp(x.lower(), y.lower()))
def sortfolded(seq):
    seq.sort(lambda x,y: cmp(x.lower(), y.lower()))


# Turn 8-bit string into unicode
def unicodeify(s):
    if type(s)==str:
        return s.decode('latin_1')
    else:
        return unicodedata.normalize('NFC',s)


# View contents of file
def viewer(filename):
    try:
        if 'startfile' in dir(os):
            os.startfile(filename)
        else:
            filename=abspath(filename)
            if type(filename)==types.UnicodeType:
                filename=filename.encode('utf-8')
            webbrowser.open("file:"+quote(filename))
    except:
        pass

def dosection(h, folder, files, doref, col, heading):
    h.write('    <tr>\n'
            '      <th style="background-color: %s;">%s</th>\n' % (col, heading))
    if doref:
        h.write('      <th style="background-color: %s;">Referenced by</th>\n' % col)
    else:
        h.write('      <th style="background-color: %s;"></th>\n' % col)
    h.write('    </tr>\n')
    
    keys=files.keys()
    sortfolded(keys)
    for key in keys:
        refs=files[key]
        if not doref:
            refstring=''
        elif len(refs)>30:
            refstring='<small>(many files)</small>'
        elif refs==['?']:
            refstring=''
        else:
            sortfolded(refs)
            refstring=(', '.join(['<a href="file:///%s">%s</a>' % (quote(join(folder,ref).encode('utf-8').replace('\\','/')), ref.encode('utf-8').replace('&','&amp;')) for ref in refs if ref!='?']))
        h.write('    <tr>\n'
                '      <td><a href="%s">%s</a></td>\n'
                '      <td>%s</td>\n'
                '    </tr>\n' % ('file:///'+quote(join(folder,key).encode('utf-8').replace('\\','/')), key.encode('utf-8').replace('&','&amp;'), refstring))
    h.write('    <tr>\n'
            '      <td>&nbsp;</td>\n'
            '      <td></td>\n'
            '    </tr>\n')
