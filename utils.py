import os
from os import listdir
from os.path import abspath, basename, dirname, join, normpath, sep
from sys import exit
import types
import unicodedata
from urllib.parse import quote
import wx

from version import appname, appversion


if not 'startfile' in dir(os):
    import webbrowser


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
        return s
    else:
        return s.decode()


# View contents of file
def viewer(filename):
    try:
        if 'startfile' in dir(os):
            os.startfile(filename)
        else:
            filename=abspath(filename)
            if type(filename)==str:
                filename=filename.encode('utf-8')
            webbrowser.open("file:"+quote(filename))
    except:
        pass

def dosection(h, folder, files, dolink, doref, dolib, col, heading):
    h.write('    <tr>\n'
            '      <th style="background-color: %s;">%s</th>\n' % (col, heading))
    if doref:
        h.write('      <th style="background-color: %s;">Referenced by</th>\n' % col)
    else:
        h.write('      <th style="background-color: %s;"></th>\n' % col)
    h.write('    </tr>\n')
    
    keys=list(files.keys())
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
        if dolib:
            linkstring = '<a href="%s">%s</a>' % ('file:///'+quote(dolib[key].encode('utf-8').replace('\\','/')), basename(dirname(dolib[key])).encode('utf-8').replace('&','&amp;')) + ' : ' + key.encode('utf-8').replace('&','&amp;')
        elif dolink:
            linkstring = '<a href="%s">%s</a>' % ('file:///'+quote(join(folder,key).encode('utf-8').replace('\\','/')), key.encode('utf-8').replace('&','&amp;'))
        else:
            linkstring=key.encode('utf-8').replace('&','&amp;')
        h.write('    <tr>\n'
                '      <td>%s</td>\n'
                '      <td>%s</td>\n'
                '    </tr>\n' % (linkstring, refstring))
    h.write('    <tr>\n'
            '      <td>&nbsp;</td>\n'
            '      <td></td>\n'
            '    </tr>\n')
