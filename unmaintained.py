#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import socket
import smtplib

from pisi.specfile import SpecFile

# Do the proper adjustments here before using the script.

smtp_user = "USERNAME"
smtp_password = "PASSWORD"
smtp_server = "SMTP SERVER"
mail_from = "EMAIL ADDRESS"
mail_from_name = "YOUR NAME"
devel_path = "FULL PATH TO REPOSITORY"

# Mail template

mail_template = """
From: %(mail_from_name)s <%(mail_from)s>
To: %(mail_to)s
Subject: [Pardus] About your packages/Paketleriniz hakkında
Content-Type: text/plain;
            charset="utf-8"

Dear Pardus contributor,

    Below, you will find the list of packages in devel/ that you are the maintainer.
As we are trying to determine unmaintained packages, please reply to this automatic
email 'only' with a list of your packages that you will not maintain anymore.

Note that, if you don't reply to this email until 01 November 2008, all of your packages
will be automatically marked as 'unmaintained'.

Best Regards,
%(mail_from_name)s <%(mail_from)s>

--

Değerli Pardus katkıcısı,

    Aşağıda, devel/ deposunda paketçisi olduğunuz paketlerin bir listesi bulunmaktadır.
İlgilenilmeyen paketlerin işaretlenebilmesi için lütfen bu e-postaya, 'ilgilenmeyeceğiniz'
paketlerin listesi kalacak şekilde cevap veriniz.

Eğer bu e-postaya, 1 Kasım 2008'e kadar cevap vermezseniz, tüm paketleriniz 'bakıcısız'
olarak işaretlenecektir.

Saygılar,
%(mail_from_name)s <%(mail_from)s>

----------------------------------------
Packager name: %(packager_name)s
Packager e-mail: %(mail_to)s
Number of total packages: %(total_packages)d
----------------------------------------

%(packages)s
"""

def send_mails(messages):

    if not smtp_user or not smtp_password:
        print "No SMTP authentication information found. Aborting.."
        return

    # Socket timeout
    socket.setdefaulttimeout(10)

    try:
        session = smtplib.SMTP(smtp_server)
    except:
        print "Failed opening session on SMTP server %s. Aborting.."
        return

    try:
        session.login(smtp_user, smtp_password)
    except smtplib.SMTPAuthenticationError:
        print "Authentication failed. Check your credentials."
        return

    result = None

    for recipient, mail in messages.items():
        try:
            result = session.sendmail(mail_from, "ozan@pardus.org.tr", mail)
        except:
            print "Problem occured when sending e-mail to %s" % recipient

    session.quit()

    print "Failed sending e-mails to following recipients:\n"
    print "\n".join(result.keys())

def get_specs(path):
    specs = []
    for root, dirs, files in os.walk(path):
        if "pspec.xml" in files:
            # A source package is found
            specs.append(root)
        if ".svn" in dirs:
            dirs.remove(".svn")

    return specs

if __name__ == "__main__":

    # Get pspec's found in devel_path
    specs = get_specs(devel_path)

    authors = {}
    templates = {}

    for s in specs:
        specfile = SpecFile(s + '/pspec.xml')
        packager_name = specfile.source.packager.name
        packager_mail = specfile.source.packager.email
        if not authors.has_key(packager_mail):
            authors[packager_mail] = [packager_name]
            authors[packager_mail].append([])

        authors[packager_mail][1].append(s.partition(devel_path)[-1])

    result = open("templates", "wb")

    for k,v in authors.items():
        # Key is email
        # Value is a list, e.g. ['name', [p1,p2,p3..pn]]

        template_values = {'mail_from'      : mail_from,
                           'mail_from_name' : mail_from_name,
                           'mail_to'        : k,
                           'packager_name'  : v[0],
                           'total_packages' : len(v[1]),
                           'packages'       : "\n".join(v[1])}


        templates[k] = mail_template % template_values
        result.write(templates[k])
        result.write("\n\n")

    #send_mails(templates)
