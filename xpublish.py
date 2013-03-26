#!/usr/bin/python

from glob import glob
from os import listdir, unlink, walk
from os.path import basename, dirname, exists, isdir, join, pardir, sep
from sys import argv, exit
from urllib import quote
from zipfile import ZipFile, ZIP_DEFLATED

from files import *
from utils import *

if platform.lower().startswith('linux') and not getenv("DISPLAY"):
    print "Can't run: DISPLAY is not set"
    exit(1)

if len(argv)>1:
    folder=unicodeify(argv[1])
else:
    folder=choosefolder()

try:
    # Windows uses cp850 (not 437 or 1252) and doesn't support utf-8.
    # Mac uses mac_roman or utf-8
    basename(folder).encode('ascii')
except:
    die('The folder name %s \ncan\'t reliably be stored in a .zip file.\n\nRename the folder avoiding accented characters \nand the characters  \\ / : * ? " < > |' % basename(folder))

for c in '\\/:*?"<>|':	# not allowed on Windows
    if c in basename(folder):
        die('The folder name %s \ncan\'t reliably be stored in a .zip file.\n\nRename the folder avoiding accented characters \nand the characters  \\ / : * ? " < > |' % basename(folder))

if basename(folder)!=basename(folder).strip():
    # Mac allows trailing spaces. Windows not.
    die('The folder name "%s" \ncan\'t reliably be stored in a .zip file.\n\nRename the folder to remove the trailing space.' % basename(folder))

progress=Progress('Analysing')

flen=len(folder)+1

acf=dict([(unicodeify(f[flen:]),[None]) for f in glob(join(folder, '*.[aA][cC][fF]'))])

lib=dict([(unicodeify(f[flen:]),[None]) for f in glob(join(folder, '[lL][iI][bB][rR][aA][rR][yY].[tT][xX][tT]'))])
gtc=dict([(unicodeify(f[flen:]),[None]) for f in glob(join(folder, '[gG][rR][oO][uU][nN][dD][tT][rR][aA][fF][fF][iI][cC].[tT][xX][tT]'))])
apt=dict([(unicodeify(f[flen:]),[None]) for f in glob(join(folder, '[eE][aA][rR][tT][hH] [nN][aA][vV] [dD][aA][tT][aA]', '[aA][pPtT][tTcC].[dD][aA][tT]'))])
dsf=dict([(unicodeify(f[flen:]),[None]) for f in glob(join(folder, '[eE][aA][rR][tT][hH] [nN][aA][vV] [dD][aA][tT][aA]', '[+-][0-9]0[+-][01][0-9]0', '[+-][0-9][0-9][+-][01][0-9][0-9].[dD][sS][fF]'))])

htm=dict([(unicodeify(f[flen:]),[None]) for f in glob(join(folder, '*.[hH][tT][mM][lL]'))+glob(join(folder, '*.[hH][tT][mM]'))])
txt=dict([(unicodeify(f[flen:]),[None]) for f in glob(join(folder, '*.[tT][xX][tT]'))+glob(join(folder, '*.[pP][dD][fF]'))+glob(join(folder, '*.[jJ][pP][gG]'))+glob(join(folder, '*.[jJ][pP][eE][gG]'))+glob(join(folder, '*.[dD][oO][cC]'))+glob(join(folder, '*.[rR][tT][fF]'))+glob(join(folder, '*.[dD][aA][tT]'))+glob(join(folder, '*.[iI][nN][iI]'))])
for f in lib.keys() + gtc.keys():
    if f in txt: txt.pop(f)	# don't list library.txt or groundtraffic.txt twice
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
    primary.update(gtc)
    primary.update(dsf)
misc=dict(txt)
misc.update(htm)
secondary={}
unused={}
missing={}
nobackup={}

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
                      '_blend_linear', '_compass_rose', '_HSI_rose',
                      '_prop', '_flame', '_chute', '_icon']:
            for ext in textypes:
                tex2=casepath(folder,base+thing+ext)
                if exists(join(folder,tex2)):
                    secondary[tex2]=[f]
                    break
            # v8 unofficial liveries
            for d in listdir(folder):
                livdir=join(folder,d)
                if not isdir(livdir): continue
                for ext in textypes:
                    tex2=casepath(livdir,base+thing+ext)
                    if exists(join(livdir,tex2)):
                        secondary[join(livdir,tex2)[flen:]]=[f]
                        break
            # v9 liveries
            for d in listdir(folder):
                if d.lower()!='liveries' or not isdir(join(folder,d)):
                    continue
                for d2 in listdir(join(folder,d)):
                    livdir=join(folder,d,d2)
                    if not isdir(livdir): continue
                    for ext in textypes:
                        tex2=casepath(livdir,base+thing+ext)
                        if exists(join(livdir,tex2)):
                            secondary[join(livdir,tex2)[flen:]]=[f]
                            break
                    
        for thing in ['_cockpit.obj','_cockpit_INN.obj','_cockpit_OUT.obj', '_slung_load.obj']:
            obj=casepath(folder,base+thing)
            if exists(join(folder,obj)):
                secondary[obj]=[f]
                parseobj(folder, secondary, missing, nobackup, {}, obj, f)
        parseacf(folder, secondary, missing, nobackup, names, f, None)

    sounds=casepath(folder,'sounds')
    if exists(join(folder,sounds)):
        for path, dirs, files in walk(join(folder,sounds)):
            for thing in files:
                if thing[-4:].lower()=='.wav':
                    secondary[unicodeify(join(path,thing)[flen:])]=['?']

    cocktypes=textypes+['.txt']
    for cockpit in [casepath(folder,'cockpit'), casepath(folder,'cockpit_3d')]:
        if exists(join(folder,cockpit)):
            for path, dirs, files in walk(join(folder,cockpit)):
                for thing in files:
                    if thing[-4:].lower() in cocktypes:
                        secondary[unicodeify(join(path,thing)[flen:])]=['?']

    #if exists(join(folder,'plane.txt')) and exists(join(folder,'plane.jpg')):
    #    misc['plane.jpg']=['plane.txt']
                
else:
    # get names so we don't complain about use of library objects
    names={'terrain_Water':None}
    for f in glob(join(folder, pardir, pardir, '[rR][eE][sS][oO][uU][rR][cC][eE][sS]', '[dD][eE][fF][aA][uU][lL][tT] [sS][cC][eE][nN][eE][rR][yY]', '*', '[lL][iI][bB][rR][aA][rR][yY].[tT][xX][tT]')):
        scanlib(names, f, None)		# Don't need placeholder for system libraries
    for f in glob(join(folder, pardir, '*', '[lL][iI][bB][rR][aA][rR][yY].[tT][xX][tT]')):
        pkgname=basename(dirname(f))
        if pkgname==basename(folder):
            scanlib(names, f, None)	# Don't need placeholder for this pkg
        else:
            scanlib(names, f, pkgname)

    for f in apt.keys():
        parseapt(folder, secondary, missing, nobackup, names, f, None)
    for f in lib.keys():
        parselib(folder, secondary, missing, nobackup, names, f, None)
    for f in gtc.keys():
        parsegtc(folder, secondary, missing, nobackup, names, f, None)
    for f in dsf.keys():
        parsedsf(folder, secondary, missing, nobackup, names, f, None)

plugins=casepath(folder,'plugins')
if exists(join(folder,plugins)):
    for path, dirs, files in walk(join(folder,plugins)):
        for thing in files:
            if thing[-4:].lower()=='.xpl':
                secondary[unicodeify(join(path,thing)[flen:])]=['?']

# last so don't double-count stuff already in misc
for f in htm.keys():
    parsehtm(folder, secondary, misc, missing, nobackup, f, None)

# Check file name sanity
keys=primary.keys()+misc.keys()+secondary.keys()
for key in keys:
    try:
        key.encode('ascii')
    except:
        die('The file name %s \ncan\'t reliably be stored in a .zip file. \n\nRename the file avoiding accented characters \nand the characters  \\ / : * ? " < > |' % key)
    for c in '\\/:*?"<>|':
        if c in key.replace(sep,''):
            die('The file name %s \ncan\'t reliably be stored in a .zip file. \n\nRename the file avoiding accented characters \nand the characters  \\ / : * ? " < > |' % key)

# unused
for path, dirs, files in walk(folder):
    for thing in files:
        if thing[-4:].lower() in ['.acf', '.afl', '.agp', '.bch', '.bmp', '.dat', '.dds', '.dsf', '.fac', '.for', '.lin', '.net', '.obj', '.pol', '.png', '.str', '.ter', '.txt', '.wav', '.wpn'] and join(path,thing)[flen:] not in keys:
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
        '    abbr { cursor: help; }\n'
        '  </style>\n'
        '</head>\n'
        '\n'
        '<body>\n'
        '  <h1><a href="file:///%s"><abbr title="This is the location of the created .zip archive for publication">%s</abbr></a></h1>\n'
        '  <table width="100%%" border="0" cellpadding="2">\n' % (title, quote(zipname.encode('utf-8').replace('\\','/')), zipname.encode('utf-8').replace(' ','&nbsp;')))
if acf:
    dosection(h, folder, primary, False, 'lightskyblue', '<abbr title="These files have been included in the .zip archive">Aircraft</abbr>')
else:
    dosection(h, folder, primary, False, 'lightskyblue', '<abbr title="These files have been included in the .zip archive">Primary files</abbr>')
if misc: dosection(h, folder, misc, False, 'lightskyblue', '<abbr title="These files look like documentation and so have been included in the .zip archive.">Documentation</abbr>')
if acf:
    if secondary: dosection(h, folder, secondary, True, 'lightskyblue', '<abbr title="These files are referenced by the Aircraft .acf and so have been included in the .zip archive.">Included files</abbr>')
else:
    if secondary: dosection(h, folder, secondary, True, 'lightskyblue', '<abbr title="These files are referenced by the &ldquo;Primary files&rdquo; and so have been included in the .zip archive.">Included files</abbr>')
if unused: dosection(h, folder, unused, False, 'darkgray', '<abbr title="These files are not referenced by the files above, and so have been omitted from the .zip archive.">Unused X-Plane files</abbr>')
if missing: dosection(h, folder, missing, True, 'red', '<abbr title="These files are referenced by the files above but are missing or unreadable, and so have been omitted from the .zip archive.">Missing or Unreadable</abbr>')
if nobackup: dosection(h, folder, nobackup, True, 'tomato', '<abbr title="This package will cause X-Plane to crash unless the user has installed a library which provides these objects. Consider adding a &ldquo;placeholder&rdquo; library.txt that covers these files.">Missing from a Placeholder Library</abbr>')
h.write('  </table>\n'
        '</body>\n'
        '</html>\n')
h.close()

progress=None

viewer(join(dirname(folder),safefolder+'.html'))
#unlink(join(dirname(folder),safefolder+'.zip'))
