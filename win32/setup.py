#!/usr/bin/python

from distutils.core import setup
from os import getcwd, listdir, name
from sys import platform
from glob import glob

import sys
sys.path.insert(0, getcwd())

from version import appname, appversion


# bogus crud to get WinXP "Visual Styles"
manifest=('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'+
          '<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">\n'+
          '<assemblyIdentity\n'+
          '    version="%4.2f.0.0"\n' % appversion +
          '    processorArchitecture="X86"\n'+
          '    name="%s"\n' % appname +
          '    type="win32"\n'+
          '/>\n'+
          '<description>X-Plane package publisher.</description>\n'+
          '<dependency>\n'+
          '    <dependentAssembly>\n'+
          '        <assemblyIdentity\n'+
          '            type="win32"\n'+
          '            name="Microsoft.Windows.Common-Controls"\n'+
          '            version="6.0.0.0"\n'+
          '            processorArchitecture="X86"\n'+
          '            publicKeyToken="6595b64144ccf1df"\n'+
          '            language="*"\n'+
          '        />\n'+
          '    </dependentAssembly>\n'+
          '</dependency>\n'+
          '<dependency>\n'+
          '    <dependentAssembly>\n'+
          '        <assemblyIdentity\n'+
          '            type="win32"\n'+
          '            name="Microsoft.VC90.CRT"\n'+
          '            version="9.0.30729.1"\n'+
          '            processorArchitecture="X86"\n'+
          '            publicKeyToken="1fc8b3b9a1e18e3b"\n'+
          '            language="*"\n'+
          '        />\n'+
          '    </dependentAssembly>\n'+
          '</dependency>\n'+
          '</assembly>\n')

if platform=='win32':
    # http://www.py2exe.org/  Invoke with: setup.py py2exe
    import py2exe

setup(name='X-Publish',
      version=("%4.2f" % appversion),
      description='X-Plane package publisher.',
      author='Jonathan Harris',
      author_email='x-plane@marginal.org.uk',
      url='http://marginal.org.uk/xplanescenery',
      data_files = [('Microsoft.VC90.CRT',
                     ['win32/Microsoft.VC90.CRT.manifest',
                      'win32/msvcp90.dll',
                      'win32/msvcr90.dll'
                      ]),
                    ],
      options = {'py2exe': {'ascii':True,	# suppresss encodings?
                            'dll_excludes':['w9xpopen.exe'],
                            'bundle_files':True,
                            'compressed':True,
                            'excludes':['Carbon', 'tcl', 'Tkinter', 'mx', 'webbrowser'],
                            'packages':['encodings.ascii','encodings.mbcs','encodings.latin_1','encodings.utf_8','encodings.utf_16','encodings.cp437','encodings.cp850'],
                            'optimize':2,
                            },
                 },

      # comment out for Mac
      zipfile = None,
      
      # win32
      windows = [{'script':'xpublish.py',
                  'icon_resources':[(1,'win32/X-Publish.ico')],
                  'other_resources':[(24,1,manifest)],
                  'dest_base':'X-Publish',	# executable name
                  }],

)
