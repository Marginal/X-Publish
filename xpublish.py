from glob import glob
from os import listdir, unlink, walk
from os.path import basename, dirname, exists, isdir, join, pardir, sep
from sys import argv, exit
from urllib import quote
from zipfile import ZipFile, ZIP_DEFLATED

from files import *
from utils import *

if len(argv)>1:
    folder=unicodeify(argv[1])
else:
    folder=choosefolder()

try:
    # Windows uses cp850 (not 437 or 1252) and doesn't support utf-8.
    # Mac uses mac_roman or utf-8
    basename(folder).encode('ascii')	
except:
    die("The folder name %s \ncan't reliably be stored in a .zip file.\n\nRename the folder using only unaccented characters." % basename(folder))

progress=Progress('Analysing')

flen=len(folder)+1

acf=dict([(unicodeify(f[flen:]),[None]) for f in glob(join(folder, '*.[aA][cC][fF]'))])

lib=dict([(unicodeify(f[flen:]),[None]) for f in glob(join(folder, '[lL][iI][bB][rR][aA][rR][yY].[tT][xX][tT]'))])
apt=dict([(unicodeify(f[flen:]),[None]) for f in glob(join(folder, '[eE][aA][rR][tT][hH] [nN][aA][vV] [dD][aA][tT][aA]', '[aA][pP][tT].[dD][aA][tT]'))])
dsf=dict([(unicodeify(f[flen:]),[None]) for f in glob(join(folder, '[eE][aA][rR][tT][hH] [nN][aA][vV] [dD][aA][tT][aA]', '[+-][0-9]0[+-][01][0-9]0', '[+-][0-9][0-9][+-][01][0-9][0-9].[dD][sS][fF]'))])

htm=dict([(unicodeify(f[flen:]),[None]) for f in glob(join(folder, '*.[hH][tT][mM][lL]'))+glob(join(folder, '*.[hH][tT][mM]'))])
txt=dict([(unicodeify(f[flen:]),[None]) for f in glob(join(folder, '*.[tT][xX][tT]'))+glob(join(folder, '*.[pP][dD][fF]'))+glob(join(folder, '*.[jJ][pP][gG]'))+glob(join(folder, '*.[jJ][pP][eE][gG]'))+glob(join(folder, '*.[dD][oO][cC]'))+glob(join(folder, '*.[rR][tT][fF]'))])
for f in lib.keys():
    if f in txt: txt.pop(f)	# don't list library.txt twice
txt.pop('summary.txt',None)	# skip FS2XPlane summary

if glob(join(folder, '[eE][aA][rR][tT][hH] [nN][aA][vV] [dD][aA][tT][aA]', '[+-][0-9]0[+-][01][0-9]0', '[+-][0-9][0-9][+-][01][0-9][0-9].[eE][nN][vV]')):
    die("The folder %s \ncontains .env files.\n\nI can't handle .env files!" % folder)
elif not (acf or lib or apt or dsf):
    die("The folder %s \ndoesn't appear to contain either aircraft or scenery. \n\nI don't know what you want to publish!" % folder)
elif acf and (lib or apt or dsf):
    die("The folder %s \nappears to contain both aircraft and scenery. \n\nI don't know which you want to publish! " % folder)


if acf:
    primary=dict(acf)
else:
    primary=dict(apt)
    primary.update(lib)
    primary.update(dsf)
misc=dict(txt)
misc.update(htm)
secondary={}
unused={}
missing={}

if acf:
    names={}
    for top in [join(pardir,pardir),join(pardir,pardir,pardir),join(pardir,pardir,pardir,pardir),join(pardir,pardir,pardir,pardir,pardir)]:
        names.update(dict([(unicodeify(basename(f).lower()),[None]) for f in glob(join(folder, top, '[aA][iI][rR][fF][oO][iI][lL][sA]','*.[aA][fF][lL]'))+glob(join(folder, top, '[wW][eE][aA][pP][oO][nN][sS]','*.[wW][pP][nN]'))]))

    for f in acf.keys():
        base=f[:-4]
        for thing in ['_paint', '_paint_lit', '_paint2', '_paint2_lit',
                      '_panel', '_panel_lit', '_panel-1','_panel-1_lit',
                      '_panel_b', '_panel_l', '_panel_lb', '_panel_lf', '_panel_r', '_panel_rb', '_panel_rf',
                      '_test_linear', '_test_linear_lit', '_test_nearest', '_test_nearest_lit',
                      '_blend_linear', '_compass_rose', '_HSI_rose', '_prop', '_flame']:
            for ext in ['.png','.bmp']:
                tex2=casepath(folder,base+thing+ext)
                if exists(join(folder,tex2)):
                    secondary[tex2]=[f]
                    break
            # liveries
            for d in listdir(folder):
                livdir=join(folder,d)
                if not isdir(livdir): continue
                for ext in ['.png','.bmp']:
                    tex2=casepath(livdir,base+thing+ext)
                    if exists(join(livdir,tex2)):
                        secondary[join(livdir,tex2)[flen:]]=[f]
                        break
                    
        for thing in ['_cockpit.obj','_cockpit_INN.obj','_cockpit_OUT.obj']:
            obj=casepath(folder,base+thing)
            if exists(join(folder,obj)):
                secondary[obj]=[f]
                parseobj(folder, secondary, missing, {}, obj, f)
        parseacf(folder, secondary, missing, names, f, None)

    sounds=casepath(folder,'sounds')
    if exists(join(folder,sounds)):
        for path, dirs, files in walk(join(folder,sounds)):
            for thing in files:
                if thing[-4:].lower()=='.wav':
                    secondary[unicodeify(join(path,thing)[flen:])]=['?']

    cockpit=casepath(folder,'cockpit')
    if exists(join(folder,cockpit)):
        for path, dirs, files in walk(join(folder,cockpit)):
            for thing in files:
                if thing[-4:].lower() in ['.bmp','.png','.txt']:
                    secondary[unicodeify(join(path,thing)[flen:])]=['?']

    #if exists(join(folder,'plane.txt')) and exists(join(folder,'plane.jpg')):
    #    misc['plane.jpg']=['plane.txt']
                
else:
    # get names so we don't complain about use of library objects
    names={'terrain_Water':None}
    for f in glob(join(folder, pardir, '*', '[lL][iI][bB][rR][aA][rR][yY].[tT][xX][tT]'))+glob(join(folder, pardir, pardir, '[rR][eE][sS][oO][uU][rR][cC][eE][sS]', '[dD][eE][fF][aA][uU][lL][tT] [sS][cC][eE][nN][eE][rR][yY]', '*', '[lL][iI][bB][rR][aA][rR][yY].[tT][xX][tT]')):
        scanlib(names, f)

    for f in apt.keys():
        parseapt(folder, secondary, missing, names, f, None)
    for f in lib.keys():
        parselib(folder, secondary, missing, names, f, None)
    for f in dsf.keys():
        parsedsf(folder, secondary, missing, names, f, None)

# last so don't double-count stuff already in misc
for f in htm.keys():
    parsehtm(folder, secondary, misc, missing, f, None)

# Check file name sanity
keys=primary.keys()+misc.keys()+secondary.keys()
for key in keys:
    try:
        key.encode('ascii')
    except:
        die("The filename %s \ncan't reliably be stored in a .zip file. \n\nRename the file using only unaccented characters." % key)
    for c in '\\/:*?"<>|':
        if c in key.replace(sep,''):
            die("The filename %s \ncan't be stored in a .zip file. \n\nRename the file avoiding the characters \\/:*?\"<>| " % key)

# unused
for path, dirs, files in walk(folder):
    for thing in files:
        if thing[-4:].lower() in ['.acf', '.afl', '.bch', '.bmp', '.dat', '.dsf', '.fac', '.for', '.lin', '.net', '.obj', '.pol', '.png', '.str', '.ter', '.txt', '.wav', '.wpn'] and join(path,thing)[flen:] not in keys:
            unused[unicodeify(join(path,thing)[flen:])]=['?']

# Do output

safefolder=basename(folder)
for c in '\\/:*?"<>|':
    safefolder.replace(c,'_')
zipname=join(dirname(folder),safefolder+'.zip')

try:
    if exists(join(dirname(folder),safefolder+'.html')):
        unlink(join(dirname(folder),safefolder+'.html'))
    h=ZipFile(zipname, 'w', ZIP_DEFLATED)
except:
    die("Can't write %s\n" % zipname)
else:
    try:
        sortfolded(keys)
        l=len(keys)
        for i in range(l):
            progress.update('Writing %s.zip' % safefolder, (100.0*i)/l)
            key=keys[i]
            h.write(join(folder,key), join(safefolder,key).encode('cp850'))
        h.close()
    except KeyboardInterrupt:
        h.close()
        if exists(zipname): unlink(zipname)
        exit(0)
    except:
        h.close()
        if exists(zipname): unlink(zipname)
        die("Can't write %s\n" % zipname)


h=file(join(dirname(folder),safefolder+'.html'),'wt')
title=safefolder.encode('utf-8').replace('&','&amp;')+'.zip'
h.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">\n'
        '<html>\n'
        '\n'
        '<head>\n'
        '  <meta http-equiv="content-type" content="text/html; charset=utf-8">\n'
        '  <title>%s</title>\n'
        '  <style type="text/css">\n'
        '    h1 { font-family: Arial,Helvetica,sans-serif; }\n'
        '    th { width: 50%%; font-family: Arial,Helvetica,sans-serif; font-weight: bold; text-align: left; vertical-align: top; }\n'
        '    td { text-align: left; vertical-align: top; }\n'
        '  </style>\n'
        '</head>\n'
        '\n'
        '<body>\n'
        '  <h1><a href="file:///%s">%s</a></h1>\n'
        '  <table width="100%%" border="0" cellpadding="2">\n' % (title, quote(zipname.encode('utf-8').replace('\\','/')), title))
if acf:
    dosection(h, 'Aircraft', folder, primary, False, 'lightskyblue')
else:
    dosection(h, 'Primary files', folder, primary, False, 'lightskyblue')
if misc: dosection(h, 'Documentation', folder, misc, False, 'lightskyblue')
if secondary: dosection(h, 'Included files', folder, secondary, True, 'lightskyblue')
if unused: dosection(h, 'Unused X-Plane files', folder, unused, False, 'darkgray')
if missing: dosection(h, 'Missing or Unreadable', folder, missing, True, 'tomato')
h.write('  </table>\n'
        '</body>\n'
        '</html>\n')
h.close()

progress=None

viewer(join(dirname(folder),safefolder+'.html'))
#unlink(join(dirname(folder),safefolder+'.zip'))
