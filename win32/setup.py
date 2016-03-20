#!/usr/bin/python

from distutils.core import setup
from os import getcwd, listdir, name
from sys import platform
from glob import glob

import sys
sys.path.insert(0, getcwd())

from version import appname, appversion


# bogus crud to get WinXP "Visual Styles"
manifest='''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" xmlns:asmv3="urn:schemas-microsoft-com:asm.v3" manifestVersion="1.0">
        <assemblyIdentity
                version="{APPVERSION:4.2f}.0.0"
                processorArchitecture="{CPU}"
                name="{APPNAME}"
                type="win32"
        />
        <description>DSF overlay editor.</description>
        <asmv3:application>
                <asmv3:windowsSettings xmlns="http://schemas.microsoft.com/SMI/2005/WindowsSettings">'
                        <dpiAware>true</dpiAware>
                </asmv3:windowsSettings>
        </asmv3:application>
        <dependency>
                <dependentAssembly>
                        <assemblyIdentity
                                type="win32"
                                name="Microsoft.Windows.Common-Controls"
                                version="6.0.0.0"
                                processorArchitecture="{CPU}"
                                publicKeyToken="6595b64144ccf1df"
                                language="*"
                        />
                </dependentAssembly>
        </dependency>
        <dependency>
                <dependentAssembly>
                        <assemblyIdentity
                                type="win32"
                                name="Microsoft.VC90.CRT"
                                version="9.0.30729.4940"
                                processorArchitecture="{CPU}"
                                publicKeyToken="1fc8b3b9a1e18e3b"
                                language="*"
                        />
                </dependentAssembly>
        </dependency>
</assembly>
'''.format(APPNAME=appname, APPVERSION=appversion, CPU='x86')


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
                            #'bundle_files':True,	# not compatible with DEP
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
