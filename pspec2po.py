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

po_header_tmpl = """# SOME DESCRIPTIVE TITLE.
# Copyright (C) YEAR THE PACKAGE'S COPYRIGHT HOLDER
# This file is distributed under the same license as the PACKAGE package.
# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.
#
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

class Message:
    def __init__(self):
        self.reference = None
        self.flags = []
        self.msgid = None
        self.msgstr = None


class Po:
    def __init__(self, messages = None, header = None):
        self.messages = messages or []
        self.header = header or po_header_tmpl

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
        f.write(self.header)
        for msg in self.messages:
            po_entry = "\n#: %s\n" % msg.reference
            if msg.flags:
                po_entry += "#, " + ", ".join(msg.flags) + "\n"
            po_entry += "msgid %s\n" % self._escape(msg.msgid)
            po_entry += "msgstr %s\n" % self._escape(msg.msgstr)
            f.write(po_entry)
        f.close()

    def _unescape(self, str):
        str = re.sub('\\\\"', '"', str)
        str = re.sub('\\\\n', '\n', str)
        return str

    def load(self, filename):
        sHeader, sSkip, sComment, sId, sMsg = range(5)
        self.messages = []
        self.header = ""
        msg = None
        state = sHeader
        # Silly state machines are easier to code than dealing with regexps
        for line in file(filename):
            line = line.rstrip("\n")

            if state == sHeader:
                if len(line.split()) == 0:
                    state = sSkip
                else:
                    self.header += line + "\n"
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

def extract_pspecs(path, language, old_messages = []):
    # otherwise, reference gets an extra / prefix
    # and update_pspecs does a os.path.join('/...', '/...', '...')
    if not path.endswith('/'):
        path += '/'
    messages = []
    paks = find_pspecs(path)

    def strp(msg):
        if msg:
            return msg.strip()
        return ""

    def set_fuzzy_flag(msg):
        for old_msg in old_messages:
            if old_msg.reference == msg.reference:
                if old_msg.msgstr == msg.msgstr:
                    if ('fuzzy' in old_msg.flags) or (strp(old_msg.msgid) != strp(msg.msgid)):
                        msg.flags.append("fuzzy")
                if (old_msg.msgid == msg.msgid) and (strp(old_msg.msgstr) != strp(msg.msgstr)):
                        msg.msgstr = old_msg.msgstr
        return msg

    for pak in paks:
        print pak
        doc = iks.parse(pak + "/pspec.xml")
        for section in ["Package", "Source"]:
            for node in doc.tags(section):
                msg = Message()
                for tag in ["Summary", "Description"]:
                    for item in node.tags(tag):
                        lang = item.getAttribute("xml:lang")
                        if not lang or lang == "en":
                            msg.msgid = item.firstChild().data()
                        elif lang == language:
                            msg.msgstr = item.firstChild().data()

                        if section == "Package":
                            msg.reference = pak[len(path):] + ":" + node.getTagData("Name") + ":" + tag.lower()
                        else:
                            msg.reference = pak[len(path):] + "::" + tag.lower()

                msg = set_fuzzy_flag(msg)

                if msg.msgid:
                    messages.append(msg)

    return messages

def update_pspecs(path, language, po):
    """a small tribute to CSLParser"""
    for msg in po.messages:
        if not msg.msgstr:
            continue
        if "fuzzy" in msg.flags:
            continue

        name, type_flag, tag = msg.reference.split(':')
        tag = tag.title()
        name = os.path.join(path, name, "pspec.xml")

        if not os.path.exists(name):
            continue

        tag_start = "<%s>" % tag
        tag_end = "</%s>" % tag

        if not type_flag:
            block = "Source"
            block_start, block_end = "<%s>" % block, "</%s>" % block
        else:
            block = "Package"
            block_start, block_end, package_name = "<%s>" % block, "</%s>" % block, type_flag

        data = file(name).readlines()

        def check_l(l, block_end):
            if data[l].find('xml:lang="%s"' % language) != -1:
                return 1
            if data[l].find(block_end) != -1:
                return 0
            return check_l(l+1, block_end)

        in_block, checked = 0, 0

        for lnum in range(0, len(data)):
            if block == "Source":
                if data[lnum].find(block_start) != -1:
                    in_block = 1

                if in_block and data[lnum].find(block_end) != -1:
                    in_block, checked = 0, 0
                    continue

                if in_block and data[lnum].find(tag) != -1:
                    if (not checked) and (not check_l(lnum, block_end)):
                        data.insert(lnum + 1, '        <%s xml:lang="%s">%s</%s>\n' % (tag, language, msg.msgstr, tag))
                        checked = 1
                        continue
                    if data[lnum].find('xml:lang="%s"' % language) != -1 and data[lnum][data[lnum].find(">") + 1:data[lnum].rfind("<")] != msg.msgstr:
                        data[lnum] = data[lnum][:data[lnum].find(">") + 1] + msg.msgstr + data[lnum][data[lnum].rfind("<"):]

            if block == "Package":
                if data[lnum].find(block_start) != -1:
                    in_block = 1

                if in_block and data[lnum].find(block_end) != -1:
                    in_block, checked = 0, 0
                    continue

                if in_block and data[lnum].find("<Name>") != -1 and data[lnum].strip()[6:-7] != package_name:
                    in_block, checked = 0, 0
                    continue

                if in_block and data[lnum].find(tag) != -1:
                    if (not checked) and (not check_l(lnum, block_end)):
                        data[lnum] += '        <%s xml:lang="%s">%s</%s>\n' % (tag, language, msg.msgstr, tag)
                        checked = 1
                        continue
                    if data[lnum].find('xml:lang="%s"' % language) != -1 and data[lnum][data[lnum].find(">") + 1:data[lnum].rfind("<")] != msg.msgstr:
                        data[lnum] = data[lnum][:data[lnum].find(">") + 1] + msg.msgstr + data[lnum][data[lnum].rfind("<"):]

        f = file(name, "w")
        for l in data:
            f.writelines(l)
        f.close()

def extract(path, language, pofile):
    if os.path.exists(pofile):
        old_po = Po()
        old_po.load(pofile)
        po = Po(header = old_po.header)
        po.messages = extract_pspecs(path, language, old_po.messages)
        po.save(pofile)
    else:
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
