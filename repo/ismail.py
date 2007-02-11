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

#
# TODO:
# * component tanımları, component.xml check
# * class_ çirkin duruyor
# * default attr çalışsın
# * objeden xml çıktıyı vermeyi de ekle
# * başka?
#

import piksemel
import inspect


class InvalidDocument(Exception):
    pass


class AutoPiksemelType:
    def __init__(self, type, name, is_multiple, is_mandatory, class_, default, choices, contains):
        if class_ and contains:
            raise TypeError("Using both class_ and contains is not supported")
        self.type = type
        self.name = name
        self.is_multiple = is_multiple
        self.is_mandatory = is_mandatory
        self.class_ = class_
        self.default = default
        self.choices = choices
        self.contains = contains
        if contains and not contains.is_multiple:
            raise TypeError("Container should have multiple entries")


def tag_data():
    return AutoPiksemelType("data", None, None, None, None, None, None, None)

def attribute(name, default=None, choices=None):
    return AutoPiksemelType("attr", name, None, True, None, default, choices, None)

def optional_attribute(name, default=None, choices=None):
    return AutoPiksemelType("attr", name, None, False, None, default, choices, None)

def tag(name, class_=None, contains=None):
    return AutoPiksemelType("tag", name, False, True, class_, None, None, contains)

def optional_tag(name, class_=None, contains=None):
    return AutoPiksemelType("tag", name, False, False, class_, None, None, contains)

def zero_or_more_tag(name, class_=None):
    return AutoPiksemelType("tag", name, True, False, class_, None, None, None)

def one_or_more_tag(name, class_=None):
    return AutoPiksemelType("tag", name, True, True, class_, None, None, None)

def piksError(doc, errors, msg):
    path = []
    while doc:
        path.append(doc.name())
        doc = doc.parent()
    path.reverse()
    errors.append("%s: %s" % ("/".join(path), msg))


class AutoPiksemel:
    def __init__(self, path=None, xmlstring=None):
        doc = None
        if path:
            if xmlstring:
                raise TypeError("Dont use both path and xmlstring in AutoPiksemel()")
            doc = piksemel.parse(path)
        elif xmlstring:
            doc = piksemel.parseString(xmlstring)
        if doc:
            errors = []
            self._autoPiks(doc, errors)
            if len(errors) > 0:
                raise InvalidDocument("\n".join(errors))
    
    def _autoPiks(self, doc, errors):
        data = None
        tags = {}
        attributes = {}
        # Collect validation info
        for name, obj in inspect.getmembers(self, lambda x: isinstance(x, AutoPiksemelType)):
            obj.varname = name
            if obj.type == "data":
                data = obj
            elif obj.type == "tag":
                tags[obj.name] = obj
                if obj.is_multiple or obj.contains:
                    tmp = []
                else:
                    tmp = None
                setattr(self, name, tmp)
            else:
                attributes[obj.name] = obj
        # Check character data
        if data:
            if len(tags) > 0:
                raise TypeError("Class %s defined both tag_data() and tag()s" % self.__class__)
            node = doc.firstChild()
            if node.type() != piksemel.DATA or node.next() != None:
                piksError(doc, errors, "this tag should only contain character data")
            else:
                setattr(self, data.varname, node.data())
        # Check attributes
        for key in doc.attributes():
            if not attributes.has_key(key):
                piksError(doc, errors, "unknown attribute '%s'" % key)
        for key in attributes:
            obj = attributes[key]
            value = doc.getAttribute(key)
            if obj.is_mandatory and value == None:
                piksError(doc, errors, "required attribute '%s' is missing" % key)
            if value and obj.choices and not value in obj.choices:
                piksError(doc, errors, "keyword '%s' is not accepted for attribute '%s'" % (value, key))
            setattr(self, obj.varname, value)
        # Check tags
        counts = {}
        for tag in doc.tags():
            name = tag.name()
            obj = tags.get(name, None)
            if obj:
                counts[name] = counts.get(name, 0) + 1
                if not obj.is_multiple and counts[name] > 1:
                    piksError(doc, errors, "tag <%s> should not appear more than once" % name)
                    # No need to examine or collect unwanted tags
                    continue
                if obj.contains:
                    subobj = obj.contains
                    temp = []
                    for subtag in tag.tags():
                        if subtag.name() != subobj.name:
                            piksError(tag, errors, "this is a collection of <%s> tags, not <%s>" % (subobj.name, subtag.name()))
                        if subobj.class_:
                            c = subobj.class_()
                            c._autoPiks(subtag, errors)
                            temp.append(c)
                        else:
                            node = subtag.firstChild()
                            if node.type() != piksemel.DATA or node.next() != None:
                                piksError(doc, errors, "this tag should only contain character data")
                            temp.append(node.data())
                    if subobj.is_mandatory and len(temp) == 0:
                        piksError(tag, errors, "should have at least one <%s> child" % subobj.name)
                    setattr(self, obj.varname, temp)
                elif obj.class_:
                    c = obj.class_()
                    c._autoPiks(tag, errors)
                    if obj.is_multiple:
                        tmp = getattr(self, obj.varname)
                        tmp.append(c)
                        setattr(self, obj.varname, tmp)
                    else:
                        setattr(self, obj.varname, c)
                else:
                    node = tag.firstChild()
                    if node.type() != piksemel.DATA or node.next() != None:
                        piksError(doc, errors, "this tag should only contain character data")
                    if obj.is_multiple:
                        tmp = getattr(self, obj.varname)
                        tmp.append(node.data())
                        setattr(self, obj.varname, tmp)
                    else:
                        setattr(self, obj.varname, node.data())
            else:
                piksError(doc, errors, "unknown tag <%s>" % name)
        for name in tags:
            obj = tags[name]
            count = counts.get(name, 0)
            if obj.is_mandatory and count == 0:
                piksError(doc, errors, "missing tag <%s>" % name)
        # Custom validation
        if len(errors) == 0:
            # Since validater functions access members without checking
            # we dont call them if there is already an error.
            validater = None
            try:
                validater = self.validate
            except AttributeError:
                pass
            if validater:
                validater(doc, errors)


#
# Real part of ismail.py, above code will be in 'import autopiksemel'
# Not much stuff below as you see, interestingly there isn't much stuff above either :p
#

import sys
import os
import pisi.version
import time


class Packager(AutoPiksemel):
    name  = tag("Name")
    email = tag("Email")


class Patch(AutoPiksemel):
    filename    =           tag_data()
    compression = optional_attribute("compressionType")
    level       = optional_attribute("level", default="0")
    target      = optional_attribute("target")


class Dependency(AutoPiksemel):
    package     =           tag_data()
    version     = optional_attribute("version")
    versionFrom = optional_attribute("versionFrom")
    versionTo   = optional_attribute("versionTo")
    release     = optional_attribute("release")
    releaseFrom = optional_attribute("releaseFrom")
    releaseTo   = optional_attribute("releaseTo")


class Archive(AutoPiksemel):
    uri     =  tag_data()
    type    = attribute("type")
    sha1sum = attribute("sha1sum")


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
    path      =           tag_data()
    filetype  =          attribute("fileType", choices=filetypes)
    permanent = optional_attribute("permanent", choices=("true", "false"))


class AdditionalFile(AutoPiksemel):
    filename   =           tag_data()
    target     =          attribute("target")
    owner      = optional_attribute("owner")
    group      = optional_attribute("group")
    permission = optional_attribute("permission")


class ComarProvide(AutoPiksemel):
    om     =  tag_data()
    script = attribute("script")


class Component(AutoPiksemel):
    name = tag("Name")


class Source(AutoPiksemel):
    name        =              tag("Name")
    homepage    =              tag("Homepage")
    packager    =              tag("Packager", class_=Packager)
    summary     =  one_or_more_tag("Summary")
    description = zero_or_more_tag("Description")
    isa         = zero_or_more_tag("IsA")
    partof      =     optional_tag("PartOf")
    icon        =     optional_tag("Icon")
    license     =  one_or_more_tag("License")
    archive     =              tag("Archive", class_=Archive)
    patches     =     optional_tag("Patches", contains=one_or_more_tag("Patch", class_=Patch))
    build_deps  =     optional_tag("BuildDependencies",
                                  contains=one_or_more_tag("Dependency", class_=Dependency))
    # Following are found in the index, not in pspecs
    version     =     optional_tag("Version")
    release     =     optional_tag("Release")
    sourceuri   =     optional_tag("SourceURI")
    
    def validate(self, doc, errors):
        valid_isas = (
            "app", "app:console", "app:gui", "app:web",
            "library", "service", "kernel", "driver",
            "data", "data:doc", "data:font",
            "locale", "locale:tr", "locale:en", "locale:es", "locale:nl",
            "locale:de", "locale:it", "locale:fr"
        )
        
        for isa in self.isa:
            if isa not in valid_isas:
                piksError(doc, errors, "invalid IsA value '%s'" % isa)


class Update(AutoPiksemel):
    release =          attribute("release")
    type    = optional_attribute("type", choices=("security", "bug"))
    date    =                tag("Date")
    version =                tag("Version")
    name    =                tag("Name")
    email   =                tag("Email")
    comment =                tag("Comment")
    
    def validate(self, doc, errors):
        #NOTE: this should be in pisi.version.Version, but situation is
        # a bit hairy there
        if "-" in self.version:
            piksError(doc, errors, "invalid version '%s': no '-' allowed" % self.version)
        try:
            pisi.version.Version(self.version)
        except Exception, e:
            piksError(doc, errors, "invalid version '%s': %s" % (self.version, e))
        try:
            self.release = int(self.release)
        except:
            piksError(doc, errors, "bad release number '%s'" % self.release)
        
        if len(self.date) != 10:
            piksError(doc, errors, "invalid date '%s'" % self.date)
        
        try:
            date = time.strptime(self.date, "%Y-%m-%d")
            if date[0] < 2003:
                piksError(doc, errors, "invalid date '%s'" % self.date)
        except Exception, e:
            piksError(doc, errors, "invalid date '%s': %s" % (self.date, e))


class Package(AutoPiksemel):
    name                  =              tag("Name")
    summary               = zero_or_more_tag("Summary")
    description           = zero_or_more_tag("Description")
    isa                   = zero_or_more_tag("IsA")
    partof                =     optional_tag("PartOf")
    icon                  =     optional_tag("Icon")
    license               = zero_or_more_tag("License")
    packageDependencies   =     optional_tag("RuntimeDependencies",
                                            contains=one_or_more_tag("Dependency", class_=Dependency))
    componentDependencies =     optional_tag("RuntimeDependencies",
                                            contains=one_or_more_tag("Component", class_=Component))
    files                 =              tag("Files", contains=one_or_more_tag("Path", class_=Path))
    conflicts             =     optional_tag("Conflicts", contains=one_or_more_tag("Package"))
    provides              =     optional_tag("Provides",
                                            contains=one_or_more_tag("COMAR", class_=ComarProvide))
    additionals           =     optional_tag("AdditionalFiles",
                                            contains=one_or_more_tag("AdditionalFile", class_=AdditionalFile))
    history               =     optional_tag("History", contains=one_or_more_tag("Update", class_=Update))
    
    def validate(self, doc, errors):
        for additional in self.additionals:
            filename = additional.target
            flag = False
            for path in self.files:
                if filename.startswith(path.path):
                    flag = True
                    break
            if not flag:
                piksError(doc, errors, "additional file '%s' not included in package %s" % (filename, self.name))


class SpecFile(AutoPiksemel):
    source   =             tag("Source", class_=Source)
    packages = one_or_more_tag("Package", class_=Package)
    history  =             tag("History", contains=one_or_more_tag("Update", class_=Update))
    
    def all_deps(self):
        deps = self.source.build_deps[:]
        for pak in self.packages:
            deps.extend(pak.packageDependencies)
        return deps
    
    def validate(self, doc, errors):
        prev = None
        prev_date = None
        for update in self.history:
            if prev_date:
                date = map(int, update.date.split("-"))
                date = date[0] * 10000 + date[1] * 100 + date[2]
                if prev_date < date:
                    piksError(doc.getTag("History"), errors, "out of order date at release %d" % update.release)
            if prev:
                prev -= 1
                if update.release != prev:
                    piksError(doc.getTag("History"), errors, "out of order release numbers")
            prev = update.release
            prev_date = map(int, update.date.split("-"))
            prev_date = prev_date[0] * 10000 + prev_date[1] * 100 + prev_date[2]
        if prev != 1:
            piksError(doc.getTag("History"), errors, "missing release numbers")


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
    
    def validate(self):
        no_errors = True
        packages = {}
        
        for pspec in all_pspecs(self.path):
            try:
                spec = SpecFile(pspec)
                for pak in spec.packages:
                    packages[pak.name] = "ok"
                for dep in spec.all_deps():
                    want = packages.get(dep.package, [])
                    if want != "ok":
                        if not spec.source.name in want:
                            want.append(spec.source.name)
                            packages[dep.package] = want
            except InvalidDocument, e:
                print "----- %s -----" % pspec[len(self.path):]
                print e
                print
                no_errors = False
        
        missing = {}
        for pak in packages:
            if packages[pak] != "ok":
                missing[pak] = packages[pak]
        if len(missing) > 0:
            no_errors = False
            print "----- Missing dependencies -----"
            for pak in missing:
                print "%s depends on missing package '%s'" % (", ".join(missing[pak]), pak)
        
        return no_errors


#
# Command line driver
#

def main(args):
    if os.path.isdir(args[0]):
        repo = Repository(args[0])
        if not repo.validate():
            sys.exit(1)
    else:
        try:
            spec = SpecFile(args[0])
        except InvalidDocument, e:
            print e
            sys.exit(1)

if __name__ == "__main__":
    main(sys.argv[1:])
