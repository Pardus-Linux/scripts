#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Analyzes new, assigned or reopened bugs of 
# developers with pardus mailed address.
#
# Copyright 2009, Semen Cirit <scirit@pardus.org.tr>
#

import MySQLdb

## Configs
db_server = ""
db_user   = ""
db_pass   = ""
db_name   = ""

bugzilla_user_id = 1
##

db = MySQLdb.connect(db_server, db_user, db_pass, db_name)

# filter bugs
c = db.cursor()

N_allBugs = c.execute("SELECT * FROM `bugs`")
print "%s bugs found in total" % N_allBugs

N_allNotResolvedBugs = c.execute("SELECT * FROM `bugs` where bug_status = 'NEW' or bug_status = 'ASIGNED' or bug_status = 'REOPENED'")
print "%s bugs new, assigned or reopened." % N_allNotResolvedBugs

N_pardusMailedBugs = c.execute("SELECT userid FROM `profiles` where login_name like '%pardus.org.tr%'")

print "%s user login with pardus mail." % N_pardusMailedBugs

bugs = {}

for userid in c.fetchall():

    #print userid
    N_bug = c.execute("SELECT * FROM `bugs` where assigned_to = %s and (bug_status = 'NEW' or bug_status = 'ASIGNED' or bug_status = 'REOPENED')" % userid[0])
    c.execute("SELECT login_name FROM `profiles` where userid = %s" % userid[0])
    loginName = c.fetchone()[0]
    print loginName
    print "%s bugs new, assigned or reopened." % (N_bug)
    N_bug_stopper = c.execute("SELECT * FROM `bugs` where assigned_to = %s and (bug_status = 'NEW' or bug_status = 'ASIGNED' or bug_status = 'REOPENED') and bug_severity = 'engelleyici'" % userid[0])
    print "%s of bugs show stopper" % N_bug_stopper
    N_bug_critic = c.execute("SELECT * FROM `bugs` where assigned_to = %s and (bug_status = 'NEW' or bug_status = 'ASIGNED' or bug_status = 'REOPENED') and bug_severity = 'kritik'" % userid[0])
    print "%s of bugs critic" % N_bug_critic
    N_bug_high = c.execute("SELECT * FROM `bugs` where assigned_to = %s and (bug_status = 'NEW' or bug_status = 'ASIGNED' or bug_status = 'REOPENED') and bug_severity = 'büyük'" % userid[0])
    print "%s of bugs high severity" % N_bug_high
    N_bug_normal = c.execute("SELECT * FROM `bugs` where assigned_to = %s and (bug_status = 'NEW' or bug_status = 'ASIGNED' or bug_status = 'REOPENED') and bug_severity = 'normal'" % userid[0])
    print "%s of bugs normal severity" % N_bug_normal
    N_bug_enhancement = c.execute("SELECT * FROM `bugs` where assigned_to = %s and (bug_status = 'NEW' or bug_status = 'ASIGNED' or bug_status = 'REOPENED') and bug_severity = 'iyileştirme'" % userid[0])
    print "%s of bugs enhancement" % N_bug_enhancement

    bugFile = open("public_html/misc/bugsAnalyze","a")
    if N_bug != 0:
        bugFile.writelines("%s %s %s %s %s %s %s\n" % (loginName, N_bug, N_bug_stopper, N_bug_critic, N_bug_high, N_bug_normal, N_bug_enhancement))

        N_bug_id = c.execute("SELECT bug_id FROM `bugs` where assigned_to = %s and (bug_status = 'NEW' or bug_status = 'ASIGNED' or bug_status = 'REOPENED') order by bug_id" % userid[0])

        #bugId = open("public_html/misc/%sIdOld"  % loginName.split("@")[0], "w")
        bugId = open("public_html/misc/%sIdNew" % loginName.split("@")[0], "w")

        for bugid in c.fetchall():
            print bugid[0]
            bugId.write("%s\n" % bugid[0])

        bugId.close()

    bugFile.close()
