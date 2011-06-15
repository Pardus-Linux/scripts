#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Analyzes new, assigned or reopened bugs of 
# developers with pardus mailed address.
#
# Copyright 2009, Semen Cirit <scirit@pardus.org.tr>
#

import MySQLdb
from operator import itemgetter
import os
import sys
from sets import Set
import base64
import numpy as np
import matplotlib.pyplot as plt

## Configs
## Configs
db_server = ""
db_user   = ""
db_pass   = ""
db_name   = ""

bugzilla_user_id = 1
##

def autolabel(rects):
    # attach some text labels
    for rect in rects:
        height = rect.get_height()
        plt.text( 1.05*rect.get_width(), rect.get_y()+rect.get_height()/2., '%d'%int(rect.get_width()), ha='center', va='bottom')

def  main(argv):
    if len(sys.argv) != 2:
        print 'Usage: python time-based-bug-report.py <time-interval> (weekly, monthly, half-yearly, yearly)' 
        sys.exit(1)

    if sys.argv[1] == "weekly":
        title = "Weekly Bug Report"
        underline1 = "~~~~~~~~~~~~~~~~~\n"
        timeinterval = "1 WEEK"
        resolvedBugTitle = "Number of Bugs Fixed Since Last Week"
        underline2 = "====================================="
        resolvedBugChartName = "Number of bugs fixed since last week"
        resolvedBugImage = "fixed_bugs_lw.png"
        commentedBugTitle = "\nNumber of Bugs Commented Since Last Week"
        underline3 = "========================================"
        commentedBugChartName = "Number of commented bugs since last week"
        commentedBugImage = "commented_bugs_lw.png"
        triagedBugTitle = "\nNumber of Bugs Triaged Since Last Week"
        underline4 = "========================================"
        triagedBugChartName = "Number of triaged bugs since last week"
        triagedBugImage = "triaged_bugs_lw.png"
    if sys.argv[1] == "monthly":
        title = "Monthly Bug Report"
        underline1 = "~~~~~~~~~~~~~~~~~~~~\n"
        timeinterval = "1 MONTH"
        resolvedBugTitle = "Number of Bugs Fixed Since Last Month"
        underline2 = "======================================"
        resolvedBugChartName = "Number of bugs fixed since last month"
        resolvedBugImage = "fixed_bugs_lm.png"
        commentedBugTitle = "\nNumber of Bugs Commented Since Last Month"
        underline3 = "========================================="
        commentedBugChartName = "Number of commented bugs since last month"
        commentedBugImage = "commented_bugs_lm.png"
        triagedBugTitle = "\nNumber of Bugs Triaged Since Last Month"
        underline4 = "========================================="
        triagedBugChartName = "Number of triaged bugs since last month"
        triagedBugImage = "triaged_bugs_lm.png"
    if sys.argv[1] == "half-yearly":
        title = "Half Yearly Bug Report"
        underline1 = "~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
        timeinterval = "6 MONTH"
        resolvedBugTitle = "Number of Bugs Fixed Since Last 6 Month"
        underline2 = "========================================"
        resolvedBugChartName = "Number of bugs fixed since last 6 month"
        resolvedBugImage = "fixed_bugs_l6m.png"
        commentedBugTitle = "\nNumber of Bugs Commented Since Last 6 Month"
        underline3 = "==========================================="
        commentedBugChartName = "Number of commented bugs since last 6 month"
        commentedBugImage = "commented_bugs_l6m.png"
        triagedBugTitle = "\nNumber of Bugs Triaged Since Last 6 month"
        underline4 = "==========================================="
        triagedBugChartName = "Number of triaged bugs since last 6 month"
        triagedBugImage = "triaged_bugs_l6m.png"
    if sys.argv[1] == "yearly":
        title = "Yearly Bug Report"
        underline1 = "~~~~~~~~~~~~~~~~~~~~~~~\n"
        timeinterval = "1 Year"
        resolvedBugTitle = "Number of Bugs Fixed Since Last Year"
        underline2 = "====================================="
        resolvedBugChartName = "Number of bugs fixed since last year"
        resolvedBugImage = "fixed_bugs_ly.png"
        commentedBugTitle = "\nNumber of Bugs Commented Since Last Year"
        underline3 = "========================================"
        commentedBugChartName = "Number of commented bugs since last year"
        commentedBugImage = "commented_bugs_ly.png"
        triagedBugTitle = "\nNumber of Bugs Triaged Since Last Year"
        underline4 = "========================================"
        triagedBugChartName = "Number of triaged bugs since last year"
        triagedBugImage = "triaged_bugs_ly.png"

    db = MySQLdb.connect(db_server, db_user, db_pass, db_name)

    # filter bugs
    c = db.cursor()

    devNames = []
    totalOpenedBugs = []
    openedBugsLW = []
    fixedBugsLW = []
    activityLW = []
    activityTriage = []

    print title
    print underline1

    if not os.path.exists("accounts"):
        os.system("wget http://svn.pardus.org.tr/uludag/trunk/common/accounts")
    devFile = open("accounts", "r")


    for line in devFile.readlines():
        if "#" not in line.strip() and ":" in line.strip():
            devName = line.split(":")[1]
            #print devName
            #N_pardusMailedBugs = c.execute("SELECT userid FROM `profiles` where login_name like '%@pardus.org.tr'")
            N_DevBugs = c.execute("SELECT userid FROM `profiles` where realname like '%s'" % ("%"+devName+"%"))
            #print "%s user are Pardus Developper." % N_pardusMailedBugs

            for userid in c.fetchall():
                #print userid
                N_bug = c.execute("SELECT * FROM `bugs` where assigned_to = %s and (bug_status = 'NEW' or bug_status = 'ASSIGNED' or bug_status = 'REOPENED')" % userid[0])
                login = c.execute("SELECT login_name FROM `profiles` where userid = %s" % userid[0])
                #print userid[0]

                loginName = c.fetchone()[0]
                #print loginName

                if N_bug != 0:

                    # how many bugs the person fix since last week
                    # bugs_activity.fieldid = 8 means bug_status was changed.
                    # bugs_activity.fieldid = 11 means resolution was changed

                    queryFixedBug= """
                    (
                    SELECT bugs.bug_id
                    FROM bugs, bugs_activity
                    WHERE bugs.bug_id = bugs_activity.bug_id
                    AND (
                    bugs_activity.fieldid =8
                    OR bugs_activity.fieldid =11
                    )
                    AND bugs.bug_status = 'RESOLVED'
                    AND bugs_activity.who = $$userid$$
                    AND bugs.delta_ts = bugs_activity.bug_when
                    AND bugs_activity.bug_when >= DATE_SUB( CURDATE( ) , INTERVAL $$TimeInterval$$)
                    )
                    UNION (

                    SELECT bugs.bug_id
                    FROM longdescs, bugs_activity, bugs
                    WHERE longdescs.bug_id = bugs_activity.bug_id
                    AND bugs.bug_id = bugs_activity.bug_id
                    AND (
                    bugs_activity.fieldid =8
                    OR bugs_activity.fieldid =11
                    )
                    AND bugs.bug_status = 'RESOLVED'
                    AND longdescs.who =6726
                    AND longdescs.thetext LIKE '%$$devname$$%'
                    AND bugs.delta_ts = bugs_activity.bug_when
                    AND bugs_activity.bug_when >= DATE_SUB( CURDATE( ) , INTERVAL $$TimeInterval$$)
                    )"""

                    #AND bugs_activity.bug_when >= DATE_SUB( CURDATE( ) , INTERVAL $$Interval$$)
                    queryFixedBug = queryFixedBug.replace("$$userid$$", str(userid[0]))
                    queryFixedBug = queryFixedBug.replace("$$devname$$", devName)
                    queryFixedBug = queryFixedBug.replace("$$TimeInterval$$", timeinterval)


                    fixedBug_N = c.execute(queryFixedBug)

                    queryBugActivity = """
                    SELECT bugs.bug_id
                    FROM bugs, longdescs
                    WHERE longdescs.bug_id = bugs.bug_id
                    AND (
                            (
                                longdescs.who =6726
                                AND longdescs.thetext LIKE '%$$devname$$%'
                            )
                            OR longdescs.who = $$userid$$
                            )
                    AND longdescs.bug_when >= DATE_SUB( CURDATE( ) , INTERVAL $$TimeInterval$$)"""

                    queryBugActivity = queryBugActivity.replace("$$devname$$", devName)
                    queryBugActivity = queryBugActivity.replace("$$userid$$", str(userid[0]))
                    queryBugActivity = queryBugActivity.replace("$$TimeInterval$$", timeinterval)

                    bugActivity = c.execute(queryBugActivity)

                    queryBugTriaged= """
                    (
                    SELECT bugs.bug_id
                    FROM bugs, bugs_activity
                    WHERE bugs.bug_id = bugs_activity.bug_id
                    AND bugs_activity.fieldid =10
                    AND bugs.keywords = 'TRIAGED'
                    AND bugs_activity.who = $$userid$$
                    AND bugs.delta_ts = bugs_activity.bug_when
                    AND bugs_activity.bug_when >= DATE_SUB( CURDATE( ) , INTERVAL $$TimeInterval$$)
                    )"""

                    #AND bugs_activity.bug_when >= DATE_SUB( CURDATE( ) , INTERVAL $$Interval$$)
                    queryBugTriaged = queryBugTriaged.replace("$$userid$$", str(userid[0]))
                    queryBugTriaged = queryBugTriaged.replace("$$devname$$", devName)
                    queryBugTriaged = queryBugTriaged.replace("$$TimeInterval$$", timeinterval)

                    bugTriaged = c.execute(queryBugTriaged)

                    devNames.append(devName.decode('utf-8'))
                    fixedBugsLW.append(fixedBug_N)
                    activityLW.append(bugActivity)
                    activityTriage.append(bugTriaged)
    """
    print devNames
    print totalOpenedBugs
    print openedBugsLW
    print fixedBugsLW
    print activityLW
    """
    print resolvedBugTitle
    print underline2


    fig = plt.figure(figsize=(20,30))

    N = len(devNames)
    ind = np.arange(N)  # the x locations for the groups
    width = 0.5       # the width of the bars

    devStd =[]
    for devName in devNames:
      devStd.append(0)

    rects2 = plt.bar(0, 0.5, fixedBugsLW , ind+width, width,
                    color='y',
                    xerr=devStd,
                    error_kw=dict(elinewiadth=6, ecolor='yellow'), orientation="horizontal", align="center")

    # add some
    plt.xlabel('Number of Bugs')
    plt.title(resolvedBugChartName)
    plt.yticks(ind+width, devNames )

    autolabel(rects2)

    plt.savefig(resolvedBugImage)
    print(".. image:: %s" % resolvedBugImage)

    print commentedBugTitle
    print underline3


    fig = plt.figure(figsize=(20,30))

    N = len(devNames)
    ind = np.arange(N)  # the x locations for the groups
    width = 0.5       # the width of the bars

    devStd =[]
    for devName in devNames:
        devStd.append(0)

    rects3 = plt.bar(0, 0.5, activityLW, ind+width, width,
                    color='y',
                    xerr=devStd,
                    error_kw=dict(elinewiadth=6, ecolor='yellow'), orientation="horizontal", align="center")

    # add some
    plt.xlabel('Number of Bugs')
    plt.title(commentedBugChartName)
    plt.yticks(ind+width, devNames )


    autolabel(rects3)

    plt.savefig(commentedBugImage)
    print(".. image:: %s" % commentedBugImage)

    print triagedBugTitle
    print underline4


    fig = plt.figure(figsize=(20,30))

    N = len(devNames)
    ind = np.arange(N)  # the x locations for the groups
    width = 0.5       # the width of the bars

    devStd =[]
    for devName in devNames:
        devStd.append(0)

    rects3 = plt.bar(0, 0.5, activityTriage, ind+width, width,
                    color='y',
                    xerr=devStd,
                    error_kw=dict(elinewiadth=6, ecolor='yellow'), orientation="horizontal", align="center")

    # add some
    plt.xlabel('Number of Bugs')
    plt.title(triagedBugChartName)
    plt.yticks(ind+width, devNames )


    autolabel(rects3)

    plt.savefig(triagedBugImage)
    print(".. image:: %s" % triagedBugImage)

if __name__ == '__main__':
    main(sys.argv)

