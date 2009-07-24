#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import pisi

installdb = pisi.db.installdb.InstallDB()
packagedb = pisi.db.packagedb.PackageDB()
d = {}

for p in [_p for _p in pisi.api.list_installed() if not _p.startswith("cursor-theme")]:
    iconlist = ["/%s" % f.path for f in installdb.get_files(p).list if f.path.startswith(("usr/share/icons", "usr/share/pixmaps"))]
    if iconlist and not packagedb.get_package(p).icon:
        appgui = "app:gui" in packagedb.get_package(p).isA
        print "\n%s (app:gui=%s)\n\n\t%s" % (p, appgui, "\n\t".join(iconlist))
