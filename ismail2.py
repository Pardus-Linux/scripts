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

import piksemel
import inspect


class InvalidDocument(Exception):
    pass


class AutoPiksemelType:
    def __init__(self, type, name, is_multiple, is_mandatory, class_, default, choices):
        self.type = type
        self.name = name
        self.is_multiple = is_multiple
        self.is_mandatory = is_mandatory
        self.class_ = class_
        self.default = default
        self.choices = choices
        if type == "tag" and "/" in name:
            self.name, self.subname = name.split("/", 1)
        else:
            self.subname = None


def tag_data():
    return AutoPiksemelType("data", None, None, None, None, None, None)

def attribute(name, default=None, choices=None):
    return AutoPiksemelType("attr", name, None, True, None, default, choices)

def optional_attribute(name, default=None, choices=None):
    return AutoPiksemelType("attr", name, None, False, None, default, choices)

def tag(name, class_=None):
    return AutoPiksemelType("tag", name, False, True, class_, None, None)

def optional_tag(name, class_=None):
    return AutoPiksemelType("tag", name, False, False, class_, None, None)

def zero_or_more_tag(name, class_=None):
    return AutoPiksemelType("tag", name, True, False, class_, None, None)

def one_or_more_tag(name, class_=None):
    return AutoPiksemelType("tag", name, True, True, class_, None, None)


class AutoPiksemel:
    def __init__(self, path=None, xmlstring=None):
        doc = None
        if path:
            if xmlstring:
                raise ValueError("Dont use both path and xmlstring in AutoPiksemel()")
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
                if obj.class_:
                    # Recurse into sub classes
                    c = obj.class_()
                    if obj.subname:
                        for subtag in tag.tags(obj.subname):
                            c._autoPiks(subtag, errors)
                    else:
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
    description =  one_or_more_tag("Description")
    isa         = zero_or_more_tag("IsA")
    partof      =     optional_tag("PartOf")
    icon        =     optional_tag("Icon")
    license     =  one_or_more_tag("License")
    archive     =              tag("Archive", class_=Archive)
    patches     = zero_or_more_tag("Patches/Patch", class_=Patch)
    build_deps  = zero_or_more_tag("BuildDependencies/Dependency", class_=Dependency)
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
    packageDependencies   = zero_or_more_tag("RuntimeDependencies/Dependency", class_=Dependency)
    componentDependencies = zero_or_more_tag("RuntimeDependencies/Component", class_=Component)
    files                 =  one_or_more_tag("Files/Path", class_=Path)
    conflicts             = zero_or_more_tag("Conflicts/Package")
    provides              = zero_or_more_tag("Provides/COMAR", class_=ComarProvide)
    additionals           = zero_or_more_tag("AdditionalFiles/AdditionalFile", class_=AdditionalFile)
    history               = zero_or_more_tag("History/Update", class_=Update)


class SpecFile(AutoPiksemel):
    source   =             tag("Source", class_=Source)
    packages = one_or_more_tag("Package", class_=Package)
    history  = one_or_more_tag("History/Update", class_=Update)



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
                    print pspec_path
                    print e
            # dont walk into the versioned stuff
            if ".svn" in dirs:
                dirs.remove(".svn")
    else:
        spec = SpecFile(args[0])

if __name__ == "__main__":
    main(sys.argv[1:])
