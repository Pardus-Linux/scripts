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

import os
import sys
import re
import piksemel as iks

po_header = """# SOME DESCRIPTIVE TITLE.
# Copyright (C) YEAR THE PACKAGE'S COPYRIGHT HOLDER
# This file is distributed under the same license as the PACKAGE package.
# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.
#
#, fuzzy
msgid ""
msgstr ""
"Project-Id-Version: PACKAGE VERSION\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2006-03-08 12:58+0200\\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
"Language-Team: LANGUAGE <LL@li.org>\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"""

po_entry = """
#: %(ref)s
msgid %(id)s
msgstr %(str)s
"""

class Message:
    def __init__(self):
        self.reference = None
        self.flags = []
        self.msgid = None
        self.msgstr = None


class Po:
    def __init__(self, messages = None):
        self.messages = []
        if messages:
            self.messages = messages
    
    def _escape(self, str):
        if not str:
            return '""'
        
        str = re.sub('"', '\\"', str)
        
        parts = str.split("\n")
        
        if len(parts) == 1:
            return '"%s"' % parts[0]
        
        if str.endswith("\n"):
            parts = parts[:-1]
        
        ret = '""' + "".join(map(lambda x: '\n"%s\\n"' % x, parts))
        
        return ret
    
    def save(self, filename):
        f = file(filename, "w")
        f.write(po_header)
        for msg in self.messages:
            dict = {}
            dict["ref"] = msg.reference
            dict["id"] = self._escape(msg.msgid)
            dict["str"] = self._escape(msg.msgstr)
            f.write(po_entry % dict)
        f.close()
    
    def _unescape(self, str):
        str = re.sub('\\\\"', '"', str)
        str = re.sub('\\\\n', '\n', str)
        return str
    
    def load(self, filename):
        sHeader, sSkip, sComment, sId, sMsg = range(5)
        self.messages = []
        msg = None
        state = sHeader
        # Silly state machines are easier to code than dealing with regexps
        for line in file(filename):
            line = line.rstrip("\n")
            
            if state == sHeader:
                if len(line.split()) == 0:
                    state = sSkip
                continue
            
            if state == sSkip:
                if len(line.split()) != 0:
                    msg = Message()
                    state = sComment
                else:
                    continue
            
            if state == sComment:
                if line.startswith("#: "):
                    msg.reference = line[3:]
                    continue
                elif line.startswith("#, "):
                    msg.flags = line[3:].split(',')
                    continue
                elif line.startswith("msgid "):
                    state = sId
                else:
                    continue
            
            if state == sId:
                if line.startswith("msgstr "):
                    state = sMsg
                else:
                    if line == 'msgid ""':
                        continue
                    if not msg.msgid:
                        msg.msgid = ""
                    msg.msgid += line[line.find('"')+1:line.rfind('"')]
            
            if state == sMsg:
                if len(line.split()) == 0:
                    msg.msgid = self._unescape(msg.msgid)
                    msg.msgstr = self._unescape(msg.msgstr)
                    self.messages.append(msg)
                    state = sSkip
                else:
                    if not msg.msgstr:
                        msg.msgstr = ""
                    if line == 'msgstr ""':
                        continue
                    msg.msgstr += line[line.find('"')+1:line.rfind('"')]
        
        if msg:
            msg.msgid = self._unescape(msg.msgid)
            msg.msgstr = self._unescape(msg.msgstr)
            self.messages.append(msg)


def find_pspecs(path):
    paks = []
    for root, dirs, files in os.walk(path):
        if "pspec.xml" in files:
            paks.append(root)
        # dont walk into the versioned stuff
        if ".svn" in dirs:
            dirs.remove(".svn")
    return paks

def extract_pspecs(path, language):
    messages = []
    paks = find_pspecs(path)
    for pak in paks:
        msg = Message()
        msg.reference = pak[len(path):] + ":summary"
        doc = iks.parse(pak + "/pspec.xml")
        source = doc.getTag("Source")
        for item in source.tags("Summary"):
            lang = item.getAttribute("xml:lang")
            if not lang or lang == "en":
                msg.msgid = item.firstChild().data()
            elif lang == language:
                msg.msgstr = item.firstChild().data()
        messages.append(msg)
        
        msg = Message()
        msg.reference = pak[len(path):] + ":description"
        doc = iks.parse(pak + "/pspec.xml")
        source = doc.getTag("Source")
        for item in source.tags("Description"):
            lang = item.getAttribute("xml:lang")
            if not lang or lang == "en":
                msg.msgid = item.firstChild().data()
            elif lang == language:
                msg.msgstr = item.firstChild().data()
        messages.append(msg)
    
    return messages

pspec_header = """<?xml version="1.0" ?>
<!DOCTYPE PISI
  SYSTEM "http://www.pardus.org.tr/projeler/pisi/pisi-spec.dtd">
"""

def update_pspecs(path, language, po):
    for msg in po.messages:
        if not msg.msgstr:
            continue
        if "fuzzy" in msg.flags:
            continue
        
        done = 0
        
        name, tag = msg.reference.split(':')
        name = os.path.join(path, name, "pspec.xml")
        tag = tag.title()
        tag_start = "<%s" % tag
        tag_end = "</%s>" % tag
        
        data = file(name).read()
        data2 = []
        inseek = 0
        for line in data.split('\n'):
            useline = 1
            if inseek == 0:
                i = line.find(tag_start)
                if i != -1:
                    j = line.find("xml:lang=", i + len(tag_start))
                    if j != -1:
                        lang = line[j + 10:]
                        if lang.startswith(language):
                            k = line.find(">", j + 10)
                            m = line.find(tag_end, k + 1)
                            useline = 0
                            done = 1
                            if m != -1:
                                data2.append(line[:k+1] + msg.msgstr + line[m:])
                            else:
                                inseek = 1
                                data2.append(line[:k+1] + msg.msgstr)
            else:
                useline = 0
                i = line.find(tag_end)
                if i != -1:
                    inseek = 0
                    if data2[-1].endswith("\n"):
                        data2[-1] = data2[-1][:-1]
                    data2[-1] += line[i:]
            if useline == 1:
                data2.append(line[:])
        
        data2 = "\n".join(data2)
        if data != data2:
            done = 1
            data = data2
        
        if done == 0:
            pos = data.find("<Archive")
            if not pos:
                print "Problem in", name
            else:
                data = data[:pos] + '<%s xml:lang="%s">%s</%s>\n        ' % (tag, language, msg.msgstr, tag) + data[pos:]
        
        f = file(name, "w")
        f.write(data)
        f.close()


def extract(path, language, pofile):
    po = Po()
    po.messages = extract_pspecs(path, language)
    po.save(pofile)

def update(path, language, pofile):
    po = Po()
    po.load(pofile)
    update_pspecs(path, language, po)

def usage():
        print "Extract translatable strings into a po file:"
        print "  pspec2po extract repopath language output_po_file"
        print "Update pspec translations from a po file:"
        print "  pspec2po update repopath language input_po_file"

if __name__ == "__main__":
    if len(sys.argv) == 1 or sys.argv[1] == "help":
        usage()
    
    elif len(sys.argv) == 5 and sys.argv[1] == "extract":
        extract(sys.argv[2], sys.argv[3], sys.argv[4])
    
    elif len(sys.argv) == 5 and sys.argv[1] == "update":
        update(sys.argv[2], sys.argv[3], sys.argv[4])
    
    else:
        usage()
