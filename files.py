from HTMLParser import HTMLParser
from os.path import basename, dirname, exists, join, normpath, pardir
from struct import unpack
from urllib import unquote

from utils import casepath, die, unicodeify


def parseapt(folder, secondary, missing, names, f, parent):

    try:
        h=file(join(folder, f), 'rU')
    except:
        die("Can't read %s" % f)
    try:
        if not h.readline().strip()[0] in ['I','A']:
            raise IOError
        if not h.readline().split()[0] in ['600','703','715','810','850']:
            raise IOError
        h.close()
    except:
        die("%s is not in X-Plane format!\n\nDid you forget to add the X-Plane header after saving in TaxiDraw?" % f)


def parseacf(folder, secondary, missing, names, f, parent):
    try:
        h=file(join(folder, f), 'rb')
        c=h.read(1)
        if c=='a':
            fmt='>'
        elif c=='i':
            fmt='<'
        else:
            die("%s isn't a v7 or v8 X-Plane file! " % f)
        (version,)=unpack(fmt+'i', h.read(4))
        if version==8000:
            version=800	# v8.00 format was labelled 8000
        elif version<600 or version>=900:
            die("%s isn't a v7 or v8 X-Plane file! " % f)
        elif version<740:
            die("%s is in X-Plane %4.2f format! \n\nPlease re-save it using Plane-Maker 7.63. " % (f, version/100.0))
        elif version not in [740,810,815,830,840,860]:
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
            h.seek(part+i*partSTRIDE)
            (eq,)=unpack(fmt+'i', h.read(4))
            if not eq: continue	# airfoil names not cleared if doesn't exist
            for b in [Rafl0,Rafl1,Tafl0,Tafl1]:
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
            h.seek(wpn+i*wpnSTRIDE)
            name=unicodeify(h.read(txtLEN).split('\0')[0].strip())
            if not name: continue
            thing=casepath(folder,join('weapons',name))
            if exists(join(folder,thing)):
                if not thing in secondary:
                    secondary[thing]=[f]
                    # XXX weapon airfoils!
                    for ext in ['.png','.bmp']:
                        tex2=casepath(folder,join('weapons',name[:-4]+ext))
                        if exists(join(folder,tex2)):
                            secondary[tex2]=[thing]
                            break
                    else:
                        missing[join('weapons',name[:-4]+'.png')]=[thing]
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
            h.seek(obj+i*objSTRIDE)
            name=unicodeify(h.read(txtLEN).split('\0')[0].strip())
            if not name: continue
            thing=casepath(folder,join('objects',name))
            if exists(join(folder,thing)):
                if not thing in secondary:
                    secondary[thing]=[f]
                    parseobj(folder, secondary, missing, {}, thing, f)
                elif f not in secondary[thing]:
                    secondary[thing].append(f)
            elif thing not in missing:
                missing[thing]=[f]
            elif f not in missing[thing]:
                missing[thing].append(f)
        
    except:
        die("Can't read %s" % f)
        

def parselib(folder, secondary, missing, names, f, parent):
    try:
        h=file(join(folder, f), 'rU')
        if not h.readline().strip()[0] in ['I','A']:
            raise IOError
        if not h.readline().split()[0]=='800':
            raise IOError
        if not h.readline().split()[0]=='LIBRARY':
            raise IOError
        for line in h:
            line=line.strip()
            l=min(line.find(' '), line.find('\t'))
            if l<0: continue
            cmd=line[:l]
            line=line[l:].strip()
            if cmd in ['EXPORT', 'EXPORT_RATIO', 'EXPORT_EXTEND', 'EXPORT_BACKUP']:
                if cmd=='EXPORT_RATIO':
                    l=min(line.find(' '), line.find('\t'))
                    line=line[l:].strip()
                l=min(line.find(' '), line.find('\t'))
                line=line[l:].strip()
                obj=casepath(folder, unicodeify(line.replace(':','/')))
                if obj not in secondary:
                    if not obj[-4:].lower() in ['.bmp', '.png']:
                        # eg A0 LHA Scenery System exports textures!
                        parseobj(folder, secondary, missing, names, obj, f)
                    else:
                        secondary[obj]=[f]
                elif f not in secondary[obj]:
                    secondary[obj].append(f)
        h.close()
    except:
        die("Can't read %s" % f)


def scanlib(names, f):
    try:
        h=file(f, 'rU')
        if not h.readline().strip()[0] in ['I','A']:
            raise IOError
        if not h.readline().split()[0]=='800':
            raise IOError
        if not h.readline().split()[0]=='LIBRARY':
            raise IOError
        for line in h:
            c=line.split()
            if not c: continue
            if c[0] in ['EXPORT', 'EXPORT_RATIO', 'EXPORT_EXTEND', 'EXPORT_BACKUP']:
                if c[0]=='EXPORT_RATIO': c.pop(1)
                name=unicodeify(c[1])
                name=name.replace(':','/')
                name=name.replace('\\','/')
                names[name]=None
        h.close()
    except:
        die("Can't read %s" % f)


def parseobj(folder, secondary, missing, names, f, parent):
    try:
        h=file(join(folder,f), 'rU')
        secondary[f]=[parent]	# file at least is readable - ship it
        if not h.readline().strip()[0] in ['I','A']:
            raise IOError
        version=h.readline().split()[0]
        if not version in ['2', '700','800','850']:
            raise IOError
        if version in ['2','700']:
            if version!='2' and not h.readline().split()[0]=='OBJ':
                raise IOError
            for line in h:
                tex=line.strip()
                if tex:
                    if '//' in tex: tex=tex[:tex.index('//')].strip()
                    tex=unicodeify(tex.replace(':','/'))
                    if tex.lower()=='none':
                        h.close()
                        return
                    break
            else:
                raise IOError

            if tex[-4:].lower() in ['.png', '.bmp']:
                tex1=tex[:-4]
                seq=[tex2[-4:]]
            else:
                tex1=tex
                seq=['.png', '.bmp']
            for d in [dirname(f), 'custom object textures']:
                for ext in seq:
                    tex2=casepath(folder, join(d, tex1+ext))
                    if exists(join(folder, tex2)):
                        if not tex2 in secondary:
                            secondary[tex2]=[f]
                        elif f not in secondary[tex2]:
                            secondary[tex2].append(f)
                        for lit in ['_lit', 'lit']:
                            for d in [dirname(f), 'custom object textures']:
                                for ext in ['.png', '.bmp']:
                                    tex2=casepath(folder, join(d, tex1+lit+ext))
                                    if exists(join(folder, tex2)):
                                        if not tex2 in secondary:
                                            secondary[tex2]=[f]
                                        elif f not in secondary[tex2]:
                                            secondary[tex2].append(f)
                                        break
                                else:
                                    continue	# next dir
                                break		# found matching ext
                            else:
                                continue	# next lit
                            break		# found matching dir
                        break	# found daytime
                else:
                    continue	# next dir
                break		# found matching ext
            else:
                if f.lower().startswith('custom objects'):
                    tex2=normpath(tex1+seq[0])
                else:
                    tex2=normpath(join(dirname(f), tex1+seq[0]))
                if tex2 not in missing:
                    missing[tex2]=[f]
                elif f not in missing[tex2]:
                    missing[tex2].append(f)

        else:
            kind=h.readline().split()[0]
            if not kind in ['FACADE','FOREST','LINE_PAINT','ROADS','OBJ','DRAPED_POLYGON','OBJECT_STRING','TERRAIN']:
                raise IOError
            for line in h:
                c=line.split('#')[0].split('//')[0].split()
                if not c: continue
                if kind=='OBJ' and c[0]=='POINT_COUNTS': break	# early exit
                if c[0] in ['TEXTURE','TEXTURE_LIT'] or (kind=='DRAPED_POLYGON' and c[0] in ['TEXTURE_NOWRAP','TEXTURE_LIT_NOWRAP']) or (kind=='TERRAIN' and c[0] in ['BASE_TEX','BASE_TEX_NOWRAP','LIT_TEX','LIT_TEX_NOWRAP','BORDER_TEX','BORDER_TEX_NOWRAP','COMPOSITE_TEX','COMPOSITE_TEX_NOWRAP']):
                    tex=line.strip()[len(c[0]):].strip()
                    if kind=='OBJ' and '//' in tex: tex=tex[:tex.index('//')].strip()
                    tex=unicodeify(tex.replace(':','/'))
                    if not tex: continue
                    for d in [dirname(f), 'custom object textures']:
                        tex2=casepath(folder, join(d, tex))
                        if exists(join(folder, tex2)):
                            if not tex2 in secondary:
                                secondary[tex2]=[f]
                            elif f not in secondary[tex2]:
                                secondary[tex2].append(f)
                            break
                    else:
                        if kind!='OBJ' or c[0]!='TEXTURE_LIT':
                            if f.lower().startswith('custom objects'):
                                tex2=normpath(tex)
                            else:
                                tex2=normpath(join(dirname(f), tex))
                            if tex2 not in missing:
                                missing[tex2]=[f]
                            elif f not in missing[tex2]:
                                missing[tex2].append(f)

        h.close()
    except:
        if f not in missing:
            missing[f]=[parent]
        elif parent not in missing[f]:
            missing[f].append(parent)


def parsedsf(folder, secondary, missing, names, f, parent):
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
                    obj=unicodeify(o.replace(':','/'))
                    for d in ['', 'custom objects']:
                        obj2=casepath(folder, join(d, obj))
                        if exists(join(folder, obj2)):
                            if obj2 not in secondary:
                                parseobj(folder, secondary, missing, names, obj2, f)
                            elif f not in secondary[obj2]:
                                secondary[obj2].append(f)
                            break
                    else:
                        if obj in names:
                            pass	# terrain_Water or library object
                        elif obj not in missing:
                            missing[obj]=[f]
                        elif f not in missing[obj]:
                            missing[obj].append(f)
                        
                h.read(1)
            else:
                h.seek(l-8, 1)

        h.close()
    except:
        die("Can't read %s" % f)


def parsehtm(folder, secondary, misc, missing, f, parent):

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
                                    parsehtm(folder, secondary, misc, missing, f2, f)
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

