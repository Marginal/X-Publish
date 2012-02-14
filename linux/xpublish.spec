Summary: X-Plane package publisher
Name: xpublish
License: Creative Commons Attribution-ShareAlike 2.5
Group: Amusements/Games
URL: http://marginal.org.uk/x-planescenery
Icon: X-Publish.xpm
Vendor: Jonathan Harris <x-plane@marginal.org.uk>
Prefix: /usr/local
Requires: bash, python >= 2.4, wxPython >= 2.6
# python-tkinter on Suse!

%description
This tool packages up an X-Plane aircraft or scenery package folder into a cross-platform .zip archive for publication.
The tool archives only the required files (skipping source files eg Photoshop or Blender files) and produces a report listing which files it has included and warning about any missing files.

%files
%defattr(644,root,root,755)
%attr(755,root,root) /usr/local/bin/xpublish
/usr/local/lib/xpublish


%post
# see http://standards.freedesktop.org/basedir-spec/latest/ar01s03.html
DESKDIR=`echo $XDG_DATA_DIRS|sed -e s/:.*//`
if [ ! "$DESKDIR" ]; then
    if [ -d /usr/local/share/applications ]; then
        DESKDIR=/usr/local/share;
    elif [ -d /usr/share/applications ]; then
        DESKDIR=/usr/share;
    elif [ -d /opt/kde3/share/applications ]; then
        DESKDIR=/opt/kde3/share;
    else
        DESKDIR=$RPM_INSTALL_PREFIX/share;
    fi;
fi
mkdir -p "$DESKDIR/applications"
cp -f "$RPM_INSTALL_PREFIX/lib/xpublish/xpublish.desktop" "$DESKDIR/applications/xpublish.desktop"

# KDE<3.5.5 ignores XDG_DATA_DIRS - http://bugs.kde.org/show_bug.cgi?id=97776
if [ -d /opt/kde3/share/icons/hicolor ]; then
    ICONDIR=/opt/kde3/share/icons/hicolor;	# suse
else
    ICONDIR=$DESKDIR/icons/hicolor;
fi
mkdir -p "$ICONDIR/48x48/apps"
cp -f "$RPM_INSTALL_PREFIX/lib/xpublish/X-Publish.png" "$ICONDIR/48x48/apps/X-Publish.png"
gtk-update-icon-cache -f -q -t $ICONDIR &>/dev/null
exit 0	# ignore errors from updating icon cache


%postun
DESKDIR=`echo $XDG_DATA_DIRS|sed -e s/:.*//`
rm -f "$DESKDIR/applications/xpublish.desktop"
rm -f /usr/local/share/applications/xpublish.desktop
rm -f /usr/share/applications/xpublish.desktop
rm -f /usr/share/applications/xpublish.desktop
rm -f /usr/local/share/icons/hicolor/48x48/apps/X-Publish.png
rm -f /usr/share/icons/hicolor/48x48/apps/X-Publish.png
rm -f /opt/kde3/share/icons/hicolor/48x48/apps/X-Publish.png
exit 0	# ignore errors from updating icon cache
