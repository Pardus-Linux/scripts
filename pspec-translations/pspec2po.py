#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2006, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version. Please read the COPYING file.

import os
import sys
import re
import xml.dom.minidom as dom

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


def find_packages(path):
    paks = []
    for root, dirs, files in os.walk(path):
        if "pspec.xml" in files:
            paks.append(root)
        # dont walk into the versioned stuff
        if ".svn" in dirs:
            dirs.remove(".svn")
    return paks

getDataByTagName = lambda x, y: x.getElementsByTagName(y)[0].firstChild.data

def extract_from_translationsxmls(path, language, old_messages = []):
    if not path.endswith('/'):
        path += '/'
    messages = []
    paks = find_packages(path)

    def strp(msg):
        if msg:
            return msg.strip()
        return ""

    def set_fuzzy_flag(msg):
        for old_msg in old_messages:
            if old_msg.reference == msg.reference:
                if len(old_msg.msgstr) and old_msg.msgstr == msg.msgstr:
                    if ('fuzzy' in old_msg.flags) or (strp(old_msg.msgid) != strp(msg.msgid)):
                        msg.flags.append("fuzzy")
                if (old_msg.msgid == msg.msgid) and (strp(old_msg.msgstr) != strp(msg.msgstr)):
                        msg.msgstr = old_msg.msgstr
        return msg

    for pak in paks:
        def get_translation(section, tag, name):
            if not os.path.exists(pak + "/translations.xml"):
                return ""
            translations = dom.parse(pak + "/translations.xml")
            for t_node in translations.getElementsByTagName(section):
                if getDataByTagName(t_node, "Name") == name:
                    for t_item in t_node.getElementsByTagName(tag):
                        t_lang = t_item.getAttribute("xml:lang")
                        if t_lang == language:
                            return t_item.firstChild.data
                    return ""
        spec = dom.parse(pak + "/pspec.xml")
        for section in ["Package", "Source"]:
            for node in spec.getElementsByTagName(section):
                for tag in ["Summary", "Description"]:
                    msg = Message()
                    for item in node.getElementsByTagName(tag):
                        lang = item.getAttribute("xml:lang")
                        if not lang or lang == "en":
                            msg.msgid = item.firstChild.data
                        msg.msgstr = get_translation(section, tag, getDataByTagName(node, "Name"))

                        if section == "Package":
                            msg.reference = pak[len(path):] + ":" + getDataByTagName(node, "Name") + ":" + tag.lower()
                        else:
                            msg.reference = pak[len(path):] + "::" + tag.lower()

                    if msg.msgid:
                        msg = set_fuzzy_flag(msg)
                        messages.append(msg)

    return messages


def update_translationsxmls(path, language, po):

    finished_packages = []

    def get_sourcepackage(type, name):
        source_node = Element(type)
        name_node = Element("Name")
        name_txt = Text(name)
        name_node.appendChild(name_txt)
        source_node.appendChild(name_node)
        return source_node

    def get_sumdesc(type, content):
        node = Element(type)
        node.setAttribute("xml:lang", language)
        cnt = Text(content)
        node.appendChild(cnt)
        return node

    def has_item(doc, item, package_name):
        if len(doc.getElementsByTagName(item)) == 0:
            return False
        for i in doc.getElementsByTagName(item):
            if getDataByTagName(i, "Name") == package_name:
                return True
        return False

    def has_lang(item, tag, language):
        for s in item.getElementsByTagName(tag):
            if s.getAttribute("xml:lang") == language:
                return True
        return False

    Element = lambda x: dom.Document().createElement(x)
    Text = lambda x: dom.Document().createTextNode(x)

    for msg in po.messages:
        if not msg.msgstr:
            continue
        if "fuzzy" in msg.flags:
            continue

        current_name, type_flag, tag = msg.reference.split(':')
        tag = tag.title()

        if not os.path.exists(os.path.join(path, current_name)):
            #package may be removed to another place or deleted from repository..
            continue

        if current_name in finished_packages:
            continue
        else:
            finished_packages.append(current_name)

        translations = os.path.join(path, current_name, "translations.xml")
        if os.path.exists(translations):
            doc = dom.parse(translations)
            pisi = doc.getElementsByTagName("PISI")[0]
        else:
            doc = dom.Document()
            pisi = Element("PISI")

        for msg in po.messages:
            if not msg.msgstr:
                continue
            if "fuzzy" in msg.flags:
                continue

            name, type_flag, tag = msg.reference.split(':')
            tag = tag.title()

            if name != current_name:
                continue

            if not type_flag:
                item = "Source"
                package_name = os.path.basename(name)
            else:
                item = "Package"
                package_name = type_flag

            if os.path.exists(translations):
                # if not, we need to create one, with fabricated content
                if has_item(doc, item, package_name):
                    # if not, it means there is no entry for 'item' in translations.xml
                    # we're gonna need to create that entry first
                    for i in doc.getElementsByTagName(item):
                        if getDataByTagName(i, "Name") == package_name:
                            if has_lang(i, tag, language):
                                # if not, it means we have item with the correct package
                                # name, but we need to insert a new 'tag' into the item node
                                # with the correct language attribute instead of changing
                                # the existing one.
                                for s in i.getElementsByTagName(tag):
                                    if s.getAttribute("xml:lang") == language:
                                        s.firstChild.data = msg.msgstr
                            else:
                                sumdesc = get_sumdesc(tag, msg.msgstr)
                                i.appendChild(sumdesc)
                else:
                    entry = get_sourcepackage(item, package_name)
                    sumdesc = get_sumdesc(tag, msg.msgstr)
                    entry.appendChild(sumdesc)
                    pisi.appendChild(entry)
            else:
                entry = get_sourcepackage(item, package_name)
                sumdesc = get_sumdesc(tag, msg.msgstr)
                entry.appendChild(sumdesc)
                pisi.appendChild(entry)
                doc.appendChild(pisi)


        # we can't use .toprettyxml() here. Because it also adds newlines and tabs
        # before and after of sum/desc data. Result looks like this:
        #
        # (...)
        # <Description xml:lang="mi">
        #     Lorem ipsum dolor sit amet..
        # </Description>
        # (...)
        #
        # and we don't want that.
        xml = doc.toxml()
        xml = xml.replace("\n    <", "<")
        xml = xml.replace("\n\n    <", "<")
        xml = xml.replace("\n        <", "<")
        xml = xml.replace("\n        <", "<")
        xml = xml.replace("\n<", "<")
        xml = xml.replace("\n\n<", "<")
        xml = xml.replace("<PISI>", "\n<PISI>")
        xml = xml.replace("</PISI>", "\n</PISI>")
        xml = xml.replace("<Source>", "\n    <Source>")
        xml = xml.replace("<Package>", "\n\n    <Package>")
        xml = xml.replace("</Source>", "\n    </Source>")
        xml = xml.replace("</Package>", "\n    </Package>")
        xml = xml.replace("<Name>", "\n        <Name>")
        xml = xml.replace("<Description ", "\n        <Description ")
        xml = xml.replace("<Summary ", "\n        <Summary ")
        if xml[-1] != "\n":
            xml += "\n"
        open(translations, "w").write(xml)


def extract(path, language, pofile):
    if os.path.exists(pofile):
        old_po = Po()
        old_po.load(pofile)
        po = Po(header = old_po.header)
        po.messages = extract_from_translationsxmls(path, language, old_po.messages)
        po.save(pofile)
    else:
        po = Po()
        po.messages = extract_from_translationsxmls(path, language)
        po.save(pofile)

def update(path, language, pofile):
    po = Po()
    po.load(pofile)
    update_translationsxmls(path, language, po)

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
