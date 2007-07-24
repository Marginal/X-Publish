import os
from os import getenv, listdir
from os.path import abspath, expanduser, exists, isdir, join, normpath, sep
from sys import exit, platform
import types
import unicodedata
from urllib import quote

from version import appname, appversion

if not 'startfile' in dir(os):
    import webbrowser

if platform=='win32':# or platform=='darwin':
    import wx	# tkFileDialog can't handle non-ascii directories
    app=wx.PySimpleApp()
elif platform=='darwin':
    from EasyDialogs import AskFolder, Message, ProgressBar
    try:
        import __main__
        import tkMessageBox	# not on Panther
    except:
        pass
else:
    import Tkinter, tkMessageBox, tkFileDialog
    app=Tkinter.Tk()
    app.withdraw()


def choosefolder():
    if platform=='win32':
        # tkFileDialog doesn't handle unicode
        home=unicodeify(getenv("USERPROFILE", ""))
        for folder in [u'C:\\X-Plane\\Custom Scenery',
                       join(home, "Desktop", "X-Plane", "Custom Scenery")]:
            if isdir(folder): break
        else:
            folder=u'C:\\'

        style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER
        if 'DD_DIR_MUST_EXIST' in dir(wx): style|=wx.DD_DIR_MUST_EXIST
        dlg=wx.DirDialog(None, 'Choose the folder that contains the aircraft or scenery that you want to publish', folder, style)
        if dlg.ShowModal()!=wx.ID_OK: exit(1)
        folder=dlg.GetPath()
        dlg.Destroy()

    else:
        home=unicodeify(expanduser('~'))	# Unicode so paths listed as unicode
        for folder in [join(home, 'X-Plane', 'Custom Scenery'),
                       join(home, 'Desktop', 'X-Plane', 'Custom Scenery'),
                       join(sep, 'Applications', 'X-Plane', 'Custom Scenery')]:
            if isdir(folder): break
        else:
            folder=home

        if platform=='darwin':
            folder=AskFolder('Choose the folder that contains the aircraft or scenery that you want to publish', defaultLocation=folder, wanted=unicode)
        else:
            folder=tkFileDialog.askdirectory(parent=app, initialdir=folder, title='Choose the folder that contains the aircraft or scenery', mustexist=True)
            
    if not folder: exit(0)
    return unicodeify(folder)

if platform=='win32':
    class Progress(wx.ProgressDialog):
        def __init__(self, message):
            wx.ProgressDialog.__init__(self, appname, message, 105, None, wx.PD_SMOOTH)
            self.Update(1)	# show some progress

        def update(self, message, newval):
            if not self.Update(2+newval, message):
                raise KeyboardInterrupt

elif platform=='darwin':
    class Progress(ProgressBar):
        def __init__(self, message):
            ProgressBar.__init__(self, appname, 102, message)
            self.inc()

        def update(self, message, newval):
            self.label(message.encode('utf-8'))
            self.set(2+newval)

else:	# no progress dialog in tk
    class Progress:
        def __init__(self, message):
            pass

        def update(self, message, newval):
            return True

        def done(self):
            pass
            
    
def die(message):
    if platform=='win32':
        wx.MessageBox(message, appname, wx.ICON_ERROR|wx.OK)
    elif 'tkMessageBox' in dir(__main__):
        tkMessageBox._show("Error", message, icon="question", type="ok")
    else:	# Panther
        Message(message.encode('utf-8'))	# only does ASCII
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

def dosection(h, heading, folder, files, doref, err=False):
    if err:
        col='tomato'
    else:
        col='lightskyblue'
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
            refstring=(', '.join(['<a href="file:///%s">%s</a>' % (quote(join(folder,ref).encode('utf-8').replace('\\','/')), ref.encode('utf-8').replace('&','&amp;').replace('\\','\\<wbr>').replace('/','/<wbr>')) for ref in refs if ref!='?']))
        h.write('    <tr>\n'
                '      <td><a href="%s">%s</a></td>\n'
                '      <td>%s</td>\n'
                '    </tr>\n' % ('file:///'+quote(join(folder,key).encode('utf-8').replace('\\','/')), key.encode('utf-8').replace('&','&amp;').replace('\\','\\<wbr>').replace('/','/<wbr>'), refstring))
    h.write('    <tr>\n'
            '      <td>&nbsp;</td>\n'
            '      <td></td>\n'
            '    </tr>\n')
