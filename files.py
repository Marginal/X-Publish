from HTMLParser import HTMLParser
from os import listdir
from os.path import basename, dirname, exists, isdir, join, normpath, pardir, splitext
from struct import unpack
from urllib import unquote
if __debug__: from traceback import print_exc

from utils import casepath, die, unicodeify

textypes=['.dds','.png','.bmp']

def parseapt(folder, secondary, missing, nobackup, names, f, parent):

    try:
        h=file(join(folder, f), 'rU')
    except:
        die("Can't read %s" % f)
        if __debug__: print_exc()
    try:
        if not h.readline().strip(' \t\xef\xbb\xbf')[0] in ['I','A']:	# Also strip UTF-8 BOM
            raise IOError
        if not h.readline().split()[0] in ['600','703','715','810','850','1000','1050','1100']:
            raise IOError
        h.close()
    except:
        die("%s is not in X-Plane format!" % f)


def parseacf(folder, secondary, missing, nobackup, names, f, parent):
    newacf={}
    try:
        h=file(join(folder, f), 'rb')
        c=h.read(1)
        if c=='a':
            fmt='>'
        elif c=='i':
            fmt='<'
        elif c in ['I','A']:
            # >1000 style?
            h.seek(0)
            try:
                if not h.readline().strip()[0] in ['I','A']: raise IOError
                version=int(h.readline().split()[0])
                if version<=1000 or h.readline().split()[0]!='ACF': raise IOError
                for line in h:
                    line=line.split('#')[0].strip()
                    if not line: continue
                    line=line.split(None,2)
                    if line[0]=='P':
                        newacf[line[1]]=line[2].strip()
            except:
                die("%s isn't a v7, v8, v9 or v10 X-Plane file! " % f)
        else:
            die("%s isn't a v7, v8, v9 or v10 X-Plane file! " % f)

        if newacf:
            aflDIM=int(newacf['_wing/count'])
            Rafl0='_afl_file_R0'
            Rafl1='_afl_file_R1'
            Tafl0='_afl_file_T0'
            Tafl1='_afl_file_T1'
            wpnDIM=int(newacf['_wpna/count'])
            objDIM=int(newacf['_obja/count'])
        else:
            (version,)=unpack(fmt+'i', h.read(4))
            if version==8000:
                version=800	# v8.00 format was labelled 8000
            elif version<600 or version>1000:
                die("%s isn't a v7, v8, v9 or v10 X-Plane file! " % f)
            elif version<740:
                die("%s is in X-Plane %4.2f format! \n\nPlease re-save it using Plane-Maker 7.63. " % (f, version/100.0))
            elif version not in [740,810,815,830,840,860,900,901,902,920,941]:
                die("%s is in X-Plane %4.2f format! \n\nI can't read %4.2f format planes. " % (f, version/100.0, version/100.0))

            txtLEN=40
            if version<800:
                aflDIM=44
                partSTRIDE=4
                part=0x2acd
                aflSTRIDE=0x28
                Rafl0=0x02bf1
                Rafl1=0x03759
                Tafl0=0x042c1
                Tafl1=0x04e29
                wpnDIM=24
                wpnSTRIDE=500
                wpn=0x098c29
            elif version==800:
                version=800
                aflDIM=56
                aflSTRIDE=0x6cc
                Rafl0=0x26ae9
                Rafl1=0x26b11
                Tafl0=0x26b39
                Tafl1=0x26b61
                partSTRIDE=0x2ee4
                part=0x3e77d
                wpnDIM=24
                wpnSTRIDE=0x48
                wpn=0x155251
            else:	# version>800
                aflDIM=56
                aflSTRIDE=0x8b4
                Rafl0=0x26ae9
                Rafl1=0x26b11
                Tafl0=0x26b39
                Tafl1=0x26b61
                partSTRIDE=0x2ee4
                part=0x4523d
                wpnDIM=24
                wpnSTRIDE=0x48
                wpn=0x15bd11
                objDIM=24
                objSTRIDE=0x48	# 8.40 and later
                obj=0x15ee31

        for i in range(aflDIM):
            if newacf:
                eq='_wing/%d/' % i
            else:
                h.seek(part+i*partSTRIDE)
                (eq,)=unpack(fmt+'i', h.read(4))
                if not eq: continue	# airfoil names not cleared if doesn't exist
            for b in [Rafl0,Rafl1,Tafl0,Tafl1]:
                if newacf:
                    if not eq+b in newacf: continue
                    name=newacf[eq+b]
                else:
                    h.seek(b+i*aflSTRIDE)
                    name=unicodeify(h.read(txtLEN).split('\0')[0].strip())
                if not name: continue
                thing=casepath(folder,join('airfoils',name))
                if exists(join(folder,thing)):
                    if not thing in secondary:
                        secondary[thing]=[f]
                    elif f not in secondary[thing]:
                        secondary[thing].append(f)
                elif name.lower() in names:
                    pass
                elif thing not in missing:
                    missing[thing]=[f]
                elif f not in missing[thing]:
                    missing[thing].append(f)

        for i in range(wpnDIM):
            if newacf:
                eq='_wpna/%d/_v10_att_file_stl' % i
                if not eq in newacf: continue
                name=newacf[eq]
            else:
                h.seek(wpn+i*wpnSTRIDE)
                name=unicodeify(h.read(txtLEN).split('\0')[0].strip())
            if not name: continue
            thing=casepath(folder,join('weapons',name))
            if exists(join(folder,thing)):
                if not thing in secondary:
                    secondary[thing]=[f]
                    # XXX weapon airfoils!
                    found=False
                    for ext in textypes:
                        tex2=casepath(folder,join('weapons',name[:-4]+ext))
                        if exists(join(folder,tex2)):
                            found=True
                            secondary[tex2]=[thing]
                    if not found: missing[join('weapons',name[:-4]+'.png')]=[thing]
                elif f not in secondary[thing]:
                    secondary[thing].append(f)
            elif name.lower() in names:
                pass
            elif thing not in missing:
                missing[thing]=[f]
            elif f not in missing[thing]:
                missing[thing].append(f)

        if version<840: return

        for i in range(objDIM):
            if newacf:
                eq='_obja/%d/_v10_att_file_stl' % i
                if not eq in newacf: continue
                name=newacf[eq]
            else:
                h.seek(obj+i*objSTRIDE)
                name=unicodeify(h.read(txtLEN).split('\0')[0].strip())
            if not name: continue
            thing=casepath(folder,join('objects',name))
            if exists(join(folder,thing)):
                if not thing in secondary:
                    secondary[thing]=[f]
                    parseobj(folder, secondary, missing, nobackup, {}, thing,f)
                elif f not in secondary[thing]:
                    secondary[thing].append(f)
            elif thing not in missing:
                missing[thing]=[f]
            elif f not in missing[thing]:
                missing[thing].append(f)
        
    except:
        if __debug__:
            print f
            print_exc()
        die("Can't read %s" % f)
        

def parselib(folder, secondary, missing, nobackup, names, f, parent):
    try:
        h=file(join(folder, f), 'rU')
        if not h.readline().strip(' \t\xef\xbb\xbf')[0] in ['I','A']:	# Also strip UTF-8 BOM
            raise IOError
        if not h.readline().split()[0]=='800':
            raise IOError
        if not h.readline().split()[0]=='LIBRARY':
            raise IOError
        for line in h:
            line=line.split('#')[0].strip()
            if not line: continue
            cmd=line.split()[0]
            line=line[len(cmd):].strip()
            if cmd in ['EXPORT', 'EXPORT_RATIO', 'EXPORT_EXTEND', 'EXPORT_BACKUP']:
                if cmd=='EXPORT_RATIO':
                    line=line[len(line.split()[0]):].strip()
                elif cmd=='EXPORT_BACKUP':
                    names[line.split()[0]]=None	# Override exported name
                line=line[len(line.split()[0]):].strip()
                obj=casepath(folder, unicodeify(line.replace(':','/').replace('\\','/')))
                if obj not in secondary:
                    if not obj[-4:].lower() in textypes:
                        # eg A0 LHA Scenery System exports textures!
                        parseobj(folder, secondary, missing, nobackup, names, obj, f)
                    else:
                        secondary[obj]=[f]
                elif f not in secondary[obj]:
                    secondary[obj].append(f)
        h.close()
    except:
        if __debug__:
            print f
            print_exc()
        die("Can't read %s" % f)


def scanlib(names, f, lib):
    try:
        h=file(f, 'rU')
        if not h.readline().strip(' \t\xef\xbb\xbf')[0] in ['I','A']:	# Also strip UTF-8 BOM
            raise IOError
        if not h.readline().split()[0]=='800':
            raise IOError
        if not h.readline().split()[0]=='LIBRARY':
            raise IOError
        for line in h:
            c=line.split()
            if not c: continue
            if c[0] in ['EXPORT', 'EXPORT_RATIO', 'EXPORT_EXTEND']:
                if c[0]=='EXPORT_RATIO': c.pop(1)
                name=unicodeify(c[1])
                name=name.replace(':','/')
                name=name.replace('\\','/')
                if name not in names:
                    names[name]=lib
        h.close()
    except:
        if __debug__:
            print f
            print_exc()
        die("Can't read %s" % f)


def parsegtc(folder, secondary, missing, nobackup, names, f, parent):
    try:
        doingtrain = doinghighway = False
        h=file(join(folder, f), 'rU')
        for passtype in ['route', 'train']:	# have to do two passes since train may be defined after route
            h.seek(0)
            for line in h:
                line=line.strip()
                if not line:
                    doingtrain = doinghighway = False
                    continue
                line=line.split('#')[0].strip()
                if not line: continue
                cmd=line.split()[0]
                if cmd==passtype=='route' or doingtrain or doinghighway:
                    line = line.split(None, (doinghighway and 2) or (doingtrain and 3) or 4)
                    if doinghighway:
                        if len(line) != 3:
                            doinghighway = False	# on to waypoints
                            continue
                    else:
                        if len(line) != (doingtrain and 4 or 5):
                            continue		# syntax error
                    obj = unicodeify(line[-1].replace(':','/'))
                    obj2 = casepath(folder, obj)
                    if exists(join(folder,obj2)):
                        if obj not in secondary:
                            parseobj(folder, secondary, missing, nobackup, names, obj2, f)
                        elif f not in secondary[obj2]:
                            secondary[obj2].append(f)
                    elif obj in names:	# library obj
                        if names[obj]:
                            if obj not in nobackup:
                                nobackup[obj]=[f]
                            elif f not in nobackup[obj]:
                                nobackup[obj].append(f)
                    elif obj not in missing:
                        missing[obj]=[f]
                    elif f not in missing[obj]:
                        missing[obj].append(f)
                elif cmd==passtype=='train':
                    doingtrain=True
                    obj=line.split(None,1)[-1].replace(':','/')
                    if obj in missing:
                        missing[obj].remove(f)
                        if not missing[obj]:
                            missing.pop(obj)
                elif cmd=='highway' and passtype=='route':
                    doinghighway=True
        h.close()
    except:
        if __debug__:
            print f
            print_exc()
        die("Can't read %s" % f)


# read object
# if names, this is a scenery object
# if not names, this is an aircraft misc object, so also look in liveries
def parseobj(folder, secondary, missing, nobackup, names, f, parent):
    try:
        objs = []	# Sub-objects
        h=file(join(folder,f), 'rU')
        secondary[f]=[parent]	# file at least is readable - ship it
        if not h.readline().strip(' \t\xef\xbb\xbf')[0] in ['I','A']:	# Also strip UTF-8 BOM
            raise IOError
        version=h.readline().split()[0]
        if not version in ['2', '700','800','850','1000']:
            raise IOError
        if version in ['2','700']:
            if version!='2' and not h.readline().split()[0]=='OBJ':
                raise IOError
            for line in h:
                tex=line.strip()
                if tex:
                    if '//' in tex: tex=tex[:tex.index('//')].strip()
                    tex=unicodeify(tex.replace(':','/').replace('\\','/'))
                    if tex.lower()=='none':
                        h.close()
                        return
                    break
            else:
                raise IOError

            if not names:
                # Misc Object
                liverytex(folder, secondary, missing, nobackup, tex, f, True)
                h.close()
                return
            (tex,origext)=splitext(tex)
            for d in [dirname(f), 'custom object textures']:
                # look for alternate extensions before custom object textures
                for ext in textypes:
                    tex2=casepath(folder, join(d, tex+ext))
                    if exists(join(folder, tex2)):
                        if not tex2 in secondary:
                            secondary[tex2]=[f]
                        elif f not in secondary[tex2]:
                            secondary[tex2].append(f)
                        for lit in ['_lit', 'lit']:
                            for d in [dirname(f), 'custom object textures']:
                                found=False
                                for ext in textypes:
                                    tex2=casepath(folder, join(d, tex+lit+ext))
                                    if exists(join(folder, tex2)):
                                        found=True
                                        if not tex2 in secondary:
                                            secondary[tex2]=[f]
                                        elif f not in secondary[tex2]:
                                            secondary[tex2].append(f)
                                if found: break	# found matching ext
                            else:
                                continue	# next lit
                            break		# found matching dir
                        break	# found daytime
                else:
                    continue	# next dir
                break		# found matching ext
            else:	# missing
                if f.lower().startswith('custom objects'):
                    tex2=normpath(tex+origext)
                else:
                    tex2=normpath(join(dirname(f), tex+origext))
                if tex2 not in missing:
                    missing[tex2]=[f]
                elif f not in missing[tex2]:
                    missing[tex2].append(f)
            h.close()
            return

        else:
            kind=h.readline().split()[0]
            if not kind in ['AG_BLOCK', 'AG_POINT', 'AG_STRING', 'BEACH','DECAL','FACADE','FOREST','LINE_PAINT','ROADS','OBJ','DRAPED_POLYGON','OBJECT_STRING','TERRAIN']:
                raise IOError
            for line in h:
                c=line.split('#')[0].split('//')[0].split()
                if not c: continue
                if kind=='OBJ' and c[0]=='VT':
                    break	# early exit
                elif c[0] == 'TEXTURE' and len(c) == 1:
                    pass	# empty TEXTURE statement
                elif (c[0] in ['TEXTURE','TEXTURE_LIT','TEXTURE_NORMAL','TEXTURE_DRAPED','TEXTURE_DRAPED_NORMAL',
                               'TEXTURE_CONTROL','TEXTURE_CONTROL_NOWRAP','TEXTURE_DETAIL','TEXTURE_TERRAIN','TEXTURE_TILE',
                               'DECAL','DECAL_RGBA','DECAL_PARAMS','DECAL_PARAMS_PROJ'] or
                    (kind=='DRAPED_POLYGON' and c[0] in ['TEXTURE_NOWRAP','TEXTURE_LIT_NOWRAP']) or
                    (kind=='BEACH' and c[0] in ['BASE_TEX','LIT_TEX']) or
                    (kind=='TERRAIN' and c[0] in ['BASE_TEX','BASE_TEX_NOWRAP','LIT_TEX','LIT_TEX_NOWRAP','NORMAL_TEX','NORMAL_TEX_NOWRAP','BORDER_TEX','BORDER_TEX_WRAP','BORDER_TEX_NOWRAP','COMPOSITE_TEX','COMPOSITE_TEX_NOWRAP'])):
                    # Texture - allow spaces in filenames
                    if kind != 'OBJ' and c[0]=='TEXTURE_NORMAL':
                        tex = line.strip().split(None,2)[-1]
                    elif c[0] in ['DECAL','DECAL_RGBA']:
                        tex = line.strip().split(None,2)[-1]
                    elif c[0] in ['TEXTURE_DETAIL','TEXTURE_TERRAIN']:
                        tex = line.strip().split(None,3)[-1]
                    elif c[0]=='TEXTURE_TILE':
                        tex = line.strip().split(None,5)[-1]
                    elif c[0] == 'DECAL_PARAMS':
                        tex = line.strip().split(None,11)[-1]
                    elif c[0] == 'DECAL_PARAMS_PROJ':
                        tex = line.strip().split(None,16)[-1]
                    else:
                        tex = line.strip().split(None,1)[-1]
                    if not tex: continue
                    tex = unicodeify(tex.replace(':','/').replace('\\','/'))

                    if not names:
                        # Misc Object
                        liverytex(folder, secondary, missing, nobackup, tex, f)
                        continue
                    (tex,origext)=splitext(tex)
                    for d in [dirname(f), 'custom object textures']:
                        # look for alternate extensions before custom object textures
                        found=False
                        for ext in textypes:
                            tex2=casepath(folder, join(d, tex+ext))
                            if not tex2.startswith('..') and exists(join(folder, tex2)):
                                found=True
                                if not tex2 in secondary:
                                    secondary[tex2]=[f]
                                elif f not in secondary[tex2]:
                                    secondary[tex2].append(f)
                        if found: break	# found matching ext
                    else:	# missing
                        if kind=='OBJ' and c[0]=='TEXTURE_LIT':
                            pass	# don't warn on missing obj lit tex
                        else:
                            if kind=='OBJ' and f.lower().startswith('custom objects'):
                                tex2=normpath(tex+origext)
                            else:
                                tex2=normpath(join(dirname(f), tex+origext))
                            if tex2 not in missing:
                                missing[tex2]=[f]
                            elif f not in missing[tex2]:
                                missing[tex2].append(f)

                # Sub-objects
                elif ((kind in ['AG_BLOCK', 'AG_POINT', 'AG_STRING'] and c[0] in ['FACADE', 'VEGETATION', 'OBJECT']) or
                      (kind=='FACADE' and c[0]=='OBJ') or
                      (c[0] == 'DECAL_LIB')):
                      objs.append(line.strip().split(None,1)[-1])
                elif kind=='OBJECT_STRING' and c[0]=='OBJECT':
                      objs.append(line.strip().split(None,3)[-1])
                elif kind=='FACADE' and c[0] == 'FACADE_SCRAPER_MODEL':
                      objs.append(c[1])
                      if c[2] != '-': objs.append(c[2])
                elif kind=='FACADE' and c[0] == 'FACADE_SCRAPER_MODEL_OFFSET':
                      objs.append(c[4])
                      if c[10] != '-': objs.append(c[10])
                elif kind=='FACADE' and c[0] == 'FACADE_SCRAPER_PAD':
                      objs.append(c[5])

        h.close()

        # Add sub-objects
        for obj in objs:
            obj = unicodeify(obj.replace(':','/').replace('\\','/'))
            obj2 = casepath(folder, join(dirname(f),obj))
            if not obj2.startswith('..') and exists(join(folder, obj2)):
                if obj2 not in secondary:
                    parseobj(folder, secondary, missing, nobackup, names, obj2, f)
                elif f not in secondary[obj2]:
                    secondary[obj2].append(f)
            else:
                if obj in names:	# terrain_Water or library obj
                    if names[obj]:
                        if obj not in nobackup:
                            nobackup[obj]=[f]
                        elif f not in nobackup[obj]:
                            nobackup[obj].append(f)
                elif obj not in missing:
                    missing[obj]=[f]
                elif f not in missing[obj]:
                    missing[obj].append(f)

    except:
        if __debug__:
            print f
            print_exc()
        if f not in missing:
            missing[f]=[parent]
        elif parent not in missing[f]:
            missing[f].append(parent)


def liverytex(folder, secondary, missing, nobackup, tex, parent, dolit=False):
    base=dirname(parent)
    found=False
    (tex,origext)=splitext(tex)
    for ext in textypes:
        tex2=casepath(folder, join(base,tex+ext))
        if exists(join(folder, tex2)):
            found=True
            if not tex2 in secondary:
                secondary[tex2]=[parent]
            elif parent not in secondary[tex2]:
                secondary[tex2].append(parent)
    if not found:
        tex2=join(base, tex)
        if tex not in missing:
            missing[tex+origext]=[parent]
        elif parent not in missing[tex]:
            missing[tex+origext].append(parent)

    if dolit:
        for lit in ['_lit', 'lit']:
            found=False
            for ext in textypes:
                tex2=casepath(folder, join(base, tex+lit+ext))
                if exists(join(folder, tex2)):
                    found=True
                    if not tex2 in secondary:
                        secondary[tex2]=[parent]
                    elif parent not in secondary[tex2]:
                        secondary[tex2].append(parent)
            if found: break
        
    livdir=casepath(folder, 'liveries')
    if not isdir(join(folder, livdir)): return
    for objbase in listdir(join(folder, livdir)):
        if base:
            objdir=join(livdir, objbase, casepath(join(folder, livdir, objbase), base))
        else:
            objdir=join(livdir, objbase)
        if not isdir(join(folder, objdir)): continue
        for ext in textypes:
            tex2=join(objdir, casepath(join(folder, objdir), tex+ext))
            if exists(join(folder, tex2)):
                if not tex2 in secondary:
                    secondary[tex2]=[parent]
                elif parent not in secondary[tex2]:
                    secondary[tex2].append(parent)
    
        if dolit:
            for lit in ['_lit', 'lit']:
                found=False
                for ext in textypes:
                    tex2=join(objdir, casepath(join(folder, objdir), tex+lit+ext))
                    if exists(join(folder, tex2)):
                        found=True
                        if not tex2 in secondary:
                            secondary[tex2]=[parent]
                        elif parent not in secondary[tex2]:
                            secondary[tex2].append(parent)
                if found: break


def parsedsf(folder, secondary, missing, nobackup, names, f, parent):
    try:
        h=file(join(folder,f), 'rb')
        if h.read(8)!='XPLNEDSF' or unpack('<I',h.read(4))!=(1,) or h.read(4)!='DAEH':
            raise IOError
        (l,)=unpack('<I', h.read(4))
        headend=h.tell()+l-8
        if h.read(4)!='PORP':
            raise IOError
        h.seek(headend)

        # Definitions Atom
        if h.read(4)!='NFED':
            raise IOError
        (l,)=unpack('<I', h.read(4))
        defnend=h.tell()+l-8
        while h.tell()<defnend:
            c=h.read(4)
            (l,)=unpack('<I', h.read(4))
            if l==8:
                pass	# empty
            elif c in ['TRET','TJBO','YLOP','WTEN']:
                objs=h.read(l-9).split('\0')
                for o in objs:
                    obj=unicodeify(o.replace(':','/').replace('\\','/'))
                    if c=='TJBO':
                        seq=['', 'custom objects']	# v7 style for objs only
                    else:
                        seq=['']
                    for d in seq:
                        obj2=casepath(folder, join(d, obj))
                        if not obj2.startswith('..') and exists(join(folder, obj2)):
                            if obj2 not in secondary:
                                parseobj(folder, secondary, missing, nobackup, names, obj2, f)
                            elif f not in secondary[obj2]:
                                secondary[obj2].append(f)
                            break
                    else:
                        if obj in names:	# terrain_Water or library obj
                            if names[obj]:
                                if obj not in nobackup:
                                    nobackup[obj]=[f]
                                elif f not in nobackup[obj]:
                                    nobackup[obj].append(f)
                        elif obj not in missing:
                            missing[obj]=[f]
                        elif f not in missing[obj]:
                            missing[obj].append(f)
                        
                h.read(1)
            else:
                h.seek(l-8, 1)

        h.close()
    except:
        if __debug__:
            print f
            print_exc()
        die("Can't read %s" % f)


def parsehtm(folder, secondary, misc, missing, nobackup, f, parent):

    class MyHTMLParser(HTMLParser):
    
        def handle_starttag(self, tag, attrs):
            if tag in ['a', 'link', 'img']:
                for (n,v) in attrs:
                    if (tag=='img' and n=='src') or n=='href':
                        if ':' in v or v[0]=='#': continue
                        f2=normpath(join(dirname(f), unquote(v)))
                        if f==f2: continue
                        if exists(join(folder, f2)):
                            if f2 in misc:
                                pass
                            elif f2 not in secondary:
                                secondary[f2]=[f]
                                if tag!='img' and f2[-4:].lower() in ['html', '.htm']:
                                    parsehtm(folder, secondary, misc, missing, nobackup, f2, f)
                            elif f not in secondary[f2]:
                                secondary[f2].append(f)
                        else:
                            if f2 not in missing:
                                missing[f2]=[f]
                            elif f not in missing[f2]:
                                missing[f2].append(f)

        def unknown_decl(self, data):
            pass	# just ignore and hope it can recover

    try:
        h=file(join(folder,f), 'rU')
        parser=MyHTMLParser()
        parser.feed(h.read())
        parser.close()
        h.close()
    except:
        if f not in missing:
            missing[f]=[parent]
        elif parent not in missing[f]:
            missing[f].append(parent)

