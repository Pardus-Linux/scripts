#!/usr/bin/python
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

import os
import sys

sys.path.append('.')

import pisi.api
import pisi.uri
import pisi.context as ctx
import pisi.specfile
import pisi.util as util
from pisi.fetcher import fetch_url
from pisi.mirrors import Mirrors

#Dummy method for gettext
def _(x):
    return x

def scanPSPEC(folder):
    packages = []
    for root, dirs, files in os.walk(folder):
        if "pspec.xml" in files:
            packages.append(root)
        # dont walk into the versioned stuff
        if ".svn" in dirs:
            dirs.remove(".svn")
    return packages

def isCached(file, sha1sum):
    try:
        return util.check_file_hash(os.path.join(ctx.config.archives_dir(), file), sha1sum)
    except:
        pass

def fetch_from_mirror():
    uri = URI.get_uri()
    sep = uri[len("mirrors://"):].split("/")
    name = sep.pop(0)
    archive = "/".join(sep)

    mirrors = Mirrors().get_mirrors(name)
    if not mirrors:
        raise Error(_("%s mirrors are not defined.") % name)

    for mirror in mirrors:
        try:
            url = os.path.join(mirror, archive)
            ctx.ui.warning(_('Fetching source from mirror: %s') % url)
            fetch_url(url, ctx.config.archives_dir())
            return
        except pisi.fetcher.FetchError:
            pass

    raise pisi.fetcher.FetchError(_('Could not fetch source from %s mirrors.') % name);


if __name__ == "__main__":
    pisi.api.init(database=False, options='')
    try:
        packages = scanPSPEC(sys.argv[1])
    except:
        print "Usage: fetchAll.py path2repo"
        sys.exit(1)
        
    for package in packages:
        spec = pisi.specfile.SpecFile()
        spec.read(os.path.join(package, "pspec.xml"))

        URI = pisi.uri.URI(spec.source.archive.uri)

        if not isCached(URI.filename(), spec.source.archive.sha1sum):
            print URI, " -> " , os.path.join(ctx.config.archives_dir(), URI.filename())
            try:
                if URI.get_uri().startswith("mirrors://"):
                    fetch_from_mirror()
                else:
                    fetch_url(URI, ctx.config.archives_dir())
            except pisi.fetcher.FetchError, e:
                print e
                pass
        else:
            print URI, "already downloaded..."
    pisi.api.finalize()
