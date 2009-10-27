#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2006-2007, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version. Please read the COPYING file.
#

import sys
import os
import pisi.version
import time
import string

from autopiks import *


class Packager(AutoPiksemel):
    name  = Tag("Name")
    email = Tag("Email")


class Patch(AutoPiksemel):
    filename    = CharacterData()
    compression = Attribute("compressionType", optional)
    level       = Attribute("level", optional)
    target      = Attribute("target", optional)


class Dependency(AutoPiksemel):
    package     = CharacterData()
    version     = Attribute("version", optional)
    versionFrom = Attribute("versionFrom", optional)
    versionTo   = Attribute("versionTo", optional)
    release     = Attribute("release", optional)
    releaseFrom = Attribute("releaseFrom", optional)
    releaseTo   = Attribute("releaseTo", optional)


class Archive(AutoPiksemel):
    uri     = CharacterData()
    type    = Attribute("type")
    sha1sum = Attribute("sha1sum")


class Path(AutoPiksemel):
    filetypes = (
        "executable",
        "library",
        "data",
        "config",
        "doc",
        "man",
        "info",
        "localedata",
        "header",
    )
    path      = CharacterData()
    filetype  = Attribute("fileType", filetypes)
    permanent = Attribute("permanent", optional, ("true", "false"))


class AdditionalFile(AutoPiksemel):
    filename   = CharacterData()
    target     = Attribute("target")
    owner      = Attribute("owner", optional)
    group      = Attribute("group", optional)
    permission = Attribute("permission", optional)


class ComarProvide(AutoPiksemel):
    om     = CharacterData()
    script = Attribute("script")


class Component(AutoPiksemel):
    name = Tag("Name")


class Source(AutoPiksemel):
    name        = Tag("Name")
    homepage    = Tag("Homepage")
    packager    = Tag("Packager", Packager)
    summary     = TagLocalized("Summary")
    description = TagLocalized("Description", optional)
    isa         = Tag("IsA", optional, multiple)
    partof      = Tag("PartOf", optional)
    icon        = Tag("Icon", optional)
    license     = Tag("License", multiple)
    archive     = Tag("Archive", Archive)
    patches     = TagCollection("Patches", "Patch", Patch, optional)
    build_deps  = TagCollection("BuildDependencies","Dependency", Dependency, optional)
    # Following are found in the index, not in pspecs
    version     = Tag("Version", optional)
    release     = Tag("Release", optional)
    sourceuri   = Tag("SourceURI", optional)
    
    def validate(self, ctx):
        valid_isas = (
            "app", "app:console", "app:gui", "app:web",
            "library", "service", "kernel", "driver",
            "data", "data:doc", "data:font",
            "locale", "locale:tr", "locale:en", "locale:es", "locale:nl",
            "locale:de", "locale:it", "locale:fr"
        )
        for isa in self.isa:
            if isa not in valid_isas:
                ctx.error("invalid IsA value '%s'" % isa)


class Update(AutoPiksemel):
    release = Attribute("release")
    type    = Attribute("type", optional, ("security", "bug"))
    date    = Tag("Date")
    version = Tag("Version")
    name    = Tag("Name")
    email   = Tag("Email")
    comment = Tag("Comment")
    
    def validate(self, ctx):
        #NOTE: this should be in pisi.version.Version, but situation is
        # a bit hairy there
        if "-" in self.version:
            ctx.error("invalid version '%s': no '-' allowed" % self.version)
        try:
            pisi.version.Version(self.version)
        except Exception, e:
            ctx.error("invalid version '%s': %s" % (self.version, e))
        try:
            self.release = int(self.release)
        except:
            ctx.error("bad release number '%s'" % self.release)
        
        if len(self.date) != 10:
            ctx.error("invalid date '%s'" % self.date)
        
        try:
            date = time.strptime(self.date, "%Y-%m-%d")
            if date[0] < 2003:
                ctx.error("invalid date '%s'" % self.date)
        except Exception, e:
            ctx.error("invalid date '%s': %s" % (self.date, e))


class RuntimeDeps(AutoPiksemel):
    packages   = Tag("Dependency", Dependency, optional, multiple)
    components = Tag("Component", Component, optional, multiple)


class Package(AutoPiksemel):
    name           = Tag("Name")
    summary        = TagLocalized("Summary", optional)
    description    = TagLocalized("Description", optional)
    isa            = Tag("IsA", optional, multiple)
    partof         = Tag("PartOf", optional)
    icon           = Tag("Icon", optional)
    license        = Tag("License", optional, multiple)
    runtime_deps   = Tag("RuntimeDependencies", RuntimeDeps, optional)
    files          = TagCollection("Files", "Path", Path)
    conflicts      = TagCollection("Conflicts", "Package", optional)
    replaces       = TagCollection("Replaces", "Package", optional)
    provides       = TagCollection("Provides", "COMAR", ComarProvide, optional)
    additionals    = TagCollection("AdditionalFiles",
                                   "AdditionalFile", AdditionalFile, optional)
    history        = TagCollection("History", "Update", Update, optional)
    
    def validate(self, ctx):
        valid_name_chars = string.ascii_letters + string.digits + "_-+"
        for c in self.name:
            if not c in valid_name_chars:
                ctx.error("package name '%s' has invalid char '%s'" % (self.name, c))
        for part in self.name.split("-")[1:]:
            if part[0] in string.digits:
                ctx.error("package name '%s' has a number after '-'" % self.name)
        
        for additional in self.additionals:
            filename = additional.target
            flag = False
            for path in self.files:
                if filename.startswith(path.path):
                    flag = True
                    break
            if not flag:
                ctx.error("additional file '%s' not included in package %s" % (filename, self.name))


class SpecFile(AutoPiksemel):
    source   = Tag("Source", Source)
    packages = Tag("Package", Package, multiple)
    history  = TagCollection("History", "Update", Update)
    
    def all_deps(self):
        deps = self.source.build_deps[:]
        for pak in self.packages:
            if pak.runtime_deps:
                deps.extend(pak.runtime_deps.packages)
        return deps
    
    def validate(self, ctx):
        prev = None
        prev_date = None
        for update in self.history:
            if prev_date:
                date = map(int, update.date.split("-"))
                date = date[0] * 10000 + date[1] * 100 + date[2]
                if prev_date < date:
                    ctx.error("out of order date at release %d" % update.release)
            if prev:
                prev -= 1
                if update.release != prev:
                    ctx.error("out of order release numbers")
            prev = update.release
            prev_date = map(int, update.date.split("-"))
            prev_date = prev_date[0] * 10000 + prev_date[1] * 100 + prev_date[2]
        if prev != 1:
            ctx.error("missing release numbers")
        
        for pak in self.packages:
            deps = map(lambda x: x.package, self.source.build_deps)
            if pak.name in deps:
                ctx.error("package name '%s' is in source '%s' build dependencies" % (pak.name, self.source.name))
            if pak.runtime_deps:
                deps = map(lambda x: x.package, pak.runtime_deps.packages)
                if pak.name in deps:
                    ctx.error("package name '%s' is in self dependencies" % pak.name)


def all_pspecs(path):
    for root, dirs, files in os.walk(path):
        if "pspec.xml" in files:
            yield os.path.join(root, "pspec.xml")
        # dont walk into the versioned stuff
        if ".svn" in dirs:
            dirs.remove(".svn")


class Repository:
    def __init__(self, path):
        self.path = path
        self.paker_names = {}
        self.paker_mails = {}
        self.sources = {}
        self.binaries = {}
        self.depends = {}
        self.no_errors = True
    
    def error(self, pspec, msg):
        print "----- %s -----" % pspec[len(self.path):]
        print msg
        print
        self.no_errors = False
    
    def validate_pspec(self, pspec):
        try:
            spec = SpecFile("PISI", pspec)
        except InvalidDocument, e:
            self.error(pspec, e)
            return
        
        name, email = spec.source.packager.name, spec.source.packager.email
        if self.paker_names.has_key(name):
            if email != self.paker_names[name]:
                self.error(pspec, "Packager '%s' has email '%s', but used '%s' here" %
                    (name, self.paker_names[name], email))
        else:
            self.paker_names[name] = email
        if self.paker_mails.has_key(email):
            if name != self.paker_mails[email]:
                self.error(pspec, "Email '%s' is used by both '%s' and '%s'" %
                    (email, self.paker_mails[email], name))
        else:
            self.paker_mails[email] = name
        
        if self.sources.has_key(spec.source.name):
            self.error(pspec, "This is a duplicate source package of '%s'" % self.sources[spec.source.name])
        else:
            self.sources[spec.source.name] = pspec
        
        for pak in spec.packages:
            if self.binaries.has_key(pak.name):
                self.error(pspec, "This source has duplicate binary package '%s' also in '%s'" %
                    (pak.name, self.binaries[pak.name]))
            else:
                self.binaries[pak.name] = pspec
            self.depends[pak.name] = "ok"
        
        for dep in spec.all_deps():
            want = self.depends.get(dep.package, [])
            if want != "ok":
                if not spec.source.name in want:
                    want.append(spec.source.name)
                    self.depends[dep.package] = want
    
    def validate(self):
        for pspec in all_pspecs(self.path):
            self.validate_pspec(pspec)
        
        missing = {}
        for pak in self.depends:
            if self.depends[pak] != "ok":
                missing[pak] = self.depends[pak]
        if len(missing) > 0:
            self.no_errors = False
            print "----- Missing dependencies -----"
            for pak in missing:
                print "%s depends on missing package '%s'" % (", ".join(missing[pak]), pak)
        
        return self.no_errors
    
    def validate_another(self, path):
        self.path = path
        return self.validate()


#
# Command line driver
#

def main(args):
    if os.path.isdir(args[0]):
        repo = Repository(args[0])
        if not repo.validate():
            sys.exit(1)
        if len(args) > 1:
            for arg in args[1:]:
                if not repo.validate_another(arg):
                    sys.exit(1)
    else:
        try:
            spec = SpecFile("PISI", args[0])
        except InvalidDocument, e:
            print e
            sys.exit(1)

if __name__ == "__main__":
    main(sys.argv[1:])
