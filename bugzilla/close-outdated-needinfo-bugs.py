#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb
import os
import sys

bugzilla_user_id = 1
how_many_days = 30

message = """\
Bu hata raporu, kullanıcıdan %(days)s gün boyunca geri bildirim alınamadığı için GEÇERSİZ olarak işaretlenmiştir. Hatayı tekrarlayabiliyorsanız, tekrar açmaktan çekinmeyiniz.

This bug report is closed as INVALID due to the lack of feedback from the reporter for %(days)s days. Feel free to reopen it if you can still reproduce it.
""" % {'days': str(how_many_days)}

##
print message

db = mysql.connect(**dict([line.split("=") for line in open("%s/\x61\x75\x74\x68" % os.path.dirname(sys.argv[0])).read().strip().split("\n") if line != "" and not line.startswith("#")]))

# filter bugs
c = db.cursor()

q = c.execute("SELECT * FROM `bugs` WHERE KEYWORDS LIKE '%%NEEDINFO%%' and bug_status != 'RESOLVED' and lastdiffed < DATE_SUB(CURDATE(), INTERVAL %d DAY)" % how_many_days)

print "%s bug found" % q

for result in c.fetchall():
    bug_id = result[0]
    print bug_id

    # update STATUS and RESOLUTION
    c.execute("UPDATE bugs SET bug_status = 'RESOLVED', resolution = 'INVALID' WHERE bug_id = %d" % bug_id)

    # add activity info
    c.execute("INSERT INTO bugs_activity(bug_id, who, bug_when, fieldid, added) VALUES (%d, %d, NOW(), 12, 'INVALID')" % (bug_id, bugzilla_user_id))

    # add comment
    c.execute("INSERT INTO longdescs(bug_id, who, bug_when, thetext) VALUES (%d, %d, NOW(), '%s')" % (bug_id, bugzilla_user_id, message))

    db.commit()
    os.chdir("/var/www/bugzilla.pardus.org.tr/bugzilla-3.2/")
    os.system("perl -T contrib/sendbugmail.pl %s admins@pardus.org.tr" % bug_id)
