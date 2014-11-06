Summary: X-Plane package publisher
Name: xpublish
Version: %{version}
Release: %{release}
License: GPLv2
Group: Amusements/Games
URL: http://marginal.org.uk/x-planescenery
Vendor: Jonathan Harris <x-plane@marginal.org.uk>
Prefix: /usr/local
Requires: bash, python >= 2.4, wxPython >= 2.6
BuildArch: noarch

%description
This tool packages up an X-Plane aircraft or scenery package folder into a cross-platform .zip archive for publication.
The tool archives only the required files (skipping source files eg Photoshop or Blender files) and produces a report listing which files it has included and warning about any missing files.

%files
%defattr(-,root,root,-)
%attr(755,root,root) /usr/local/bin/xpublish
/usr/local/share/applications/xpublish.desktop
/usr/local/share/icons/hicolor/48x48/apps/xpublish.png
/usr/local/share/icons/hicolor/128x128/apps/xpublish.png
/usr/local/lib/xpublish

%post
gtk-update-icon-cache -f -q -t $ICONDIR &>/dev/null
exit 0	# ignore errors from updating icon cache
