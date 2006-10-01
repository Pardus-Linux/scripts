#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2006, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version. Please read the COPYING file.
#

#
# TODO:
# * tagları da setattr ile değişkenlerine yaz
# * hatalarda /a/b/c şeklinde tam tag path göster
# * component tanımları, component.xml check
# * class_ çirkin duruyor
# * default attr çalışsın
# * tarih vs gibi ince kontrolleri koy
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
            else:
                attributes[obj.name] = obj
        # Check attributes
        for key in doc.attributes():
            if not attributes.has_key(key):
                errors.append("unknown attribute '%s'" % key)
        for key in attributes:
            obj = attributes[key]
            value = doc.getAttribute(key)
            if obj.is_mandatory and value == None:
                errors.append("required attribute '%s' is missing" % key)
            if value and obj.choices and not value in obj.choices:
                errors.append("keyword '%s' is not accepted for attribute '%s'" % (value, key))
            setattr(self, key, value)
        # Check tags
        counts = {}
        for tag in doc.tags():
            name = tag.name()
            obj = tags.get(name, None)
            if obj:
                counts[name] = counts.get(name, 0) + 1
                if obj.contains:
                    for subtag in tag.tags(obj.contains.name):
                        if obj.contains.class_:
                            c = obj.contains.class_()
                            c._autoPiks(subtag, errors)
                elif obj.class_:
                    c = obj.class_()
                    c._autoPiks(tag, errors)
            else:
                errors.append("unknown tag <%s>" % name)
        for name in tags:
            obj = tags[name]
            count = counts.get(name, 0)
            if obj.is_mandatory:
                if count == 0:
                    errors.append("missing tag <%s>" % name)
                if not obj.is_multiple and count > 1:
                    errors.append("tag <%s> should not appear more than once" % name)
            else:
                if not obj.is_multiple and count > 1:
                    errors.append("optional tag <%s> should not appear more than once" % name)


#
# Real part of ismail.py, above code will be in 'import autopiksemel'
# Not much stuff below as you see, interestingly there isn't much stuff above either :p
#

import sys
import os


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


class Update(AutoPiksemel):
    release =          attribute("release")
    type    = optional_attribute("type", choices=("security", "bug"))
    date    =                tag("Date")
    version =                tag("Version")
    name    =                tag("Name")
    email   =                tag("Email")
    comment =                tag("Comment")


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


class SpecFile(AutoPiksemel):
    source   =             tag("Source", class_=Source)
    packages = one_or_more_tag("Package", class_=Package)
    history  =             tag("History", contains=one_or_more_tag("Update", class_=Update))


#
# Command line driver
#

def main(args):
    if os.path.isdir(args[0]):
        for root, dirs, files in os.walk(args[0]):
            if "pspec.xml" in files:
                pspec_path = os.path.join(root, "pspec.xml")
                try:
                    spec = SpecFile(pspec_path)
                except InvalidDocument, e:
                    print "----- %s -----" % pspec_path[len(args[0]):]
                    print e
            # dont walk into the versioned stuff
            if ".svn" in dirs:
                dirs.remove(".svn")
    else:
        spec = SpecFile(args[0])

if __name__ == "__main__":
    main(sys.argv[1:])
