from glob import glob
from os import listdir, unlink, walk
from os.path import basename, dirname, exists, isdir, join, normpath, pardir, sep
from sys import exit
from urllib.parse import quote
from zipfile import ZipFile, ZIP_DEFLATED

from files import *
from utils import *

def publish(folder, app):
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

    app.progress.Show()
    if not app.progress.Update(10, 'Analysing'): exit(1)

    flen=len(folder)+1

    acf=dict([(f[flen:],[None]) for f in glob(join(folder, '*.[aA][cC][fF]'))])

    lib=dict([(f[flen:],[None]) for f in glob(join(folder, '[lL][iI][bB][rR][aA][rR][yY].[tT][xX][tT]'))])
    gtc=dict([(f[flen:],[None]) for f in glob(join(folder, '[gG][rR][oO][uU][nN][dD][tT][rR][aA][fF][fF][iI][cC].[tT][xX][tT]'))])
    apt=dict([(f[flen:],[None]) for f in glob(join(folder, '[eE][aA][rR][tT][hH] [nN][aA][vV] [dD][aA][tT][aA]', '[aA][pPtT][tTcC].[dD][aA][tT]'))])
    dsf=dict([(f[flen:],[None]) for f in glob(join(folder, '[eE][aA][rR][tT][hH] [nN][aA][vV] [dD][aA][tT][aA]', '[+-][0-9]0[+-][01][0-9]0', '[+-][0-9][0-9][+-][01][0-9][0-9].[dD][sS][fF]'))])

    htm=dict([(f[flen:],[None]) for f in glob(join(folder, '*.[hH][tT][mM][lL]'))+glob(join(folder, '*.[hH][tT][mM]'))])
    txt=dict([(f[flen:],[None]) for f in glob(join(folder, '[rR][eE][aA][dD][mM][eE]'))+glob(join(folder, '*.[tT][xX][tT]'))+glob(join(folder, '*.[pP][dD][fF]'))+glob(join(folder, '*.[jJ][pP][gG]'))+glob(join(folder, '*.[jJ][pP][eE][gG]'))+glob(join(folder, '*.[dD][oO][cC]'))+glob(join(folder, '*.[rR][tT][fF]'))+glob(join(folder, '*.[dD][aA][tT]'))+glob(join(folder, '*.[iI][nN][iI]'))])
    for f in list(lib.keys()) + list(gtc.keys()):
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
        if not app.progress.Update(20, 'Analysing'): exit(1)
        primary.update(lib)
        if not app.progress.Update(30, 'Analysing'): exit(1)
        primary.update(gtc)
        if not app.progress.Update(40, 'Analysing'): exit(1)
        primary.update(dsf)
        if not app.progress.Update(50, 'Analysing'): exit(1)
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

        for f in list(acf.keys()):
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

        # SASL
        avionics='?'
        for thing in listdir(folder):
            if thing.lower()=='avionics.lua':
                avionics = unicodeify(join(folder,thing)[flen:])
                secondary[avionics]=['?']
        sasl=casepath(folder,'custom avionics')
        if exists(join(folder,sasl)):
            for path, dirs, files in walk(join(folder,sasl)):
                for thing in files:
                    if thing[-4:].lower() in ['.lua','.png','.tga']:
                        secondary[unicodeify(join(path,thing)[flen:])]=[avionics]

        # Gizmo
        gizmo=casepath(folder,'scripts')
        if exists(join(folder,gizmo)):
            for path, dirs, files in walk(join(folder,gizmo)):
                for thing in files:
                    if thing[-4:].lower() in ['.key','.lua','.png','.tga']:
                        secondary[unicodeify(join(path,thing)[flen:])]=['?']

        #if exists(join(folder,'plane.txt')) and exists(join(folder,'plane.jpg')):
        #    misc['plane.jpg']=['plane.txt']

    else:
        # get names so we don't complain about use of library objects
        names={'terrain_Water':None}
        for f in glob(join(folder, pardir, pardir, '[rR][eE][sS][oO][uU][rR][cC][eE][sS]', '[dD][eE][fF][aA][uU][lL][tT] [sS][cC][eE][nN][eE][rR][yY]', '*', '[lL][iI][bB][rR][aA][rR][yY].[tT][xX][tT]')):
            scanlib(names, normpath(f), None)		# Don't need placeholder for system libraries
        for f in glob(join(folder, '[lL][iI][bB][rR][aA][rR][yY].[tT][xX][tT]')):
            scanlib(names, normpath(f), None)		# Don't need placeholder for this pkg
        for f in glob(join(folder, pardir, '*', '[lL][iI][bB][rR][aA][rR][yY].[tT][xX][tT]')):
            if basename(dirname(f))!=basename(folder):
                scanlib(names, normpath(f), normpath(f))

        # for f in list(apt.keys()):
        #     parseapt(folder, secondary, missing, nobackup, names, f, None)
        for f in list(lib.keys()):
            parselib(folder, secondary, missing, nobackup, names, f, None)
        for f in list(gtc.keys()):
            parsegtc(folder, secondary, missing, nobackup, names, f, None)
        for f in list(dsf.keys()):
            parsedsf(folder, secondary, missing, nobackup, names, f, None)

    for plugin in glob(join(folder,'[pP][lL][uU][gG][iI][nN][sS]','*')):
        if isdir(plugin):
            for path, dirs, files in walk(plugin):
                for thing in files:
                    if thing[-4:].lower() in ['.dll','.lua','.png','.tga','.txt','.xpl']:
                        secondary[unicodeify(join(path,thing)[flen:])]=[plugin[flen:]]

    # last so don't double-count stuff already in misc
    for f in list(htm.keys()):
        parsehtm(folder, secondary, misc, missing, nobackup, f, None)

    # Check file name sanity
    keys=list(primary.keys())+list(misc.keys())+list(secondary.keys())
    for key in keys:
        try:
            key.encode('ascii')
        except:
            print_exc()
            die('The file name %s \ncan\'t reliably be stored in a .zip file. \n\nRename the file avoiding accented characters \nand the characters  \\ / : * ? " < > |' % key)
        for c in '\\/:*?"<>|':
            if c in key.replace(sep,''):
                die('The file name %s \ncan\'t reliably be stored in a .zip file. \n\nRename the file avoiding accented characters \nand the characters  \\ / : * ? " < > |' % key)

    # unused
    for path, dirs, files in walk(folder):
        for thing in files:
            if not thing.startswith('._') and thing[-4:].lower() in ['.acf', '.afl', '.agb', '.agp', '.ags', '.bch', '.bmp', '.dat', '.dcl', '.dds', '.dsf', '.fac', '.for', '.lin', '.lua', '.net', '.obj', '.pol', '.png', '.str', '.ter', '.tga', '.txt', '.wav', '.wpn'] and join(path,thing)[flen:] not in keys:
                unused[unicodeify(join(path,thing)[flen:])]=['?']

    # Do output

    safefolder=basename(folder)
    for c in '\\/:*?"<>|':
        safefolder.replace(c,'_')
    zipname=join(dirname(folder),safefolder+'.zip')
    print(zipname)
    try:
        if exists(join(dirname(folder),safefolder+'.html')):
            unlink(join(dirname(folder),safefolder+'.html'))
        h=ZipFile(zipname, 'w', ZIP_DEFLATED)
    except:
        print_exc()
        die("Can't write %s\n" % zipname)
    else:
        try:
            sortfolded(keys)
            l=len(keys)
            for i in range(l):
                if not app.progress.Update(50+(50.0*i)/l, 'Writing %s.zip' % safefolder): exit(1)
                key=keys[i]
                h.write(join(folder,key), join(safefolder,key).encode('cp850'))
            h.close()
        except KeyboardInterrupt:
            h.close()
            if exists(zipname): unlink(zipname)
            exit(0)
        except:
            h.close()
            print_exc()
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
        dosection(h, folder, primary, True, False, False, 'lightgreen', '<abbr title="These files have been included in the .zip archive">Aircraft</abbr>')
    else:
        dosection(h, folder, primary, True, False, False, 'lightgreen', '<abbr title="These files have been included in the .zip archive">Primary files</abbr>')
    if misc: dosection(h, folder, misc, True, False, False, 'lightgreen', '<abbr title="These files look like documentation and so have been included in the .zip archive.">Documentation</abbr>')
    if acf:
        if secondary: dosection(h, folder, secondary, True, True, False, 'lightgreen', '<abbr title="These files are referenced by the Aircraft .acf and so have been included in the .zip archive.">Included files</abbr>')
    else:
        if secondary: dosection(h, folder, secondary, True, True, False, 'lightgreen', '<abbr title="These files are referenced by the &ldquo;Primary files&rdquo; and so have been included in the .zip archive.">Included files</abbr>')
    if unused: dosection(h, folder, unused, True, False, False, 'darkgray', '<abbr title="These files are not referenced by the files above, and so have been omitted from the .zip archive.">Unused X-Plane files</abbr>')
    if missing: dosection(h, folder, missing, False, True, False, 'red', '<abbr title="These files are referenced by the files above but are missing or unreadable, and so have been omitted from the .zip archive. X-Plane will complain if you don\'t provide these files.">Missing or Unreadable</abbr>')
    if nobackup: dosection(h, folder, nobackup, False, True, names, 'orange', '<abbr title="You have used these third-party library files, and have not provided &ldquo;placeholders&rdquo; for them. X-Plane will complain unless the user has installed the library or libraries which provide these files. Consider creating a &ldquo;placeholder&rdquo; library.txt for these files.">Third-party library files</abbr>')
    h.write('  </table>\n'
            '</body>\n'
            '</html>\n')
    h.close()

    viewer(join(dirname(folder),safefolder+'.html'))
    #unlink(join(dirname(folder),safefolder+'.zip'))

    app.progress.Destroy()
