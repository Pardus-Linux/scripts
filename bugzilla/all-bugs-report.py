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
from sets import Set
import base64

## Configs
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

devNames = []
totalOpenedBugs = []
openedBugsLW = []
fixedBugsLW = []
activityLW = []

print "All Opened, Reopened or Assigned Bugs"
print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"


if not os.path.exists("accounts"):
    os.system("wget http://svn.pardus.org.tr/uludag/trunk/common/accounts")

devFile = open("accounts", "r")

for line in devFile.readlines():
    if "#" not in line.strip() and ":" in line.strip():
        devName = line.split(":")[1]
        #print devName

        N_DevBugs = c.execute("SELECT userid FROM `profiles` where realname like '%s'" % ("%"+devName+"%"))
        bugs = {}

        for userid in c.fetchall():

            #print userid
            N_bug = c.execute("SELECT * FROM `bugs` where assigned_to = %s and (bug_status = 'NEW' or bug_status = 'ASSIGNED' or bug_status = 'REOPENED')" % userid[0])

            if N_bug != 0:

                devNames.append(devName.decode('utf-8'))
                totalOpenedBugs.append(N_bug)

c.execute("SELECT * FROM `versions`")
openBugsVersionDict = {}

# Remove duplicate versions
differentVersionsSet = Set([])
for version in c.fetchall():
    differentVersionsSet.add(version[0])

# Add versions to dict if there exist open, reopened or assigned bugs
for dversion in differentVersionsSet:
    N_openBug = c.execute("SELECT * FROM `bugs` where (bug_status = 'NEW' or bug_status = 'ASSIGNED' or bug_status = 'REOPENED') and version='%s'" % dversion)
    if N_openBug!=0:
        openBugsVersionDict[dversion] = N_openBug

print "\nAll Opened, Reopened or Assigned Bugs for Different Versions"
print "=============================================================\n"

# draw the pie chart for all open bugs according to different version for all open bugs according to different versions
from pylab import *
import matplotlib.pyplot as plt

fig = plt.figure(figsize=(10,10))

openBugsVersionA = []
for key in openBugsVersionDict:
    openBugsVersionA.append(key + ":" + str(openBugsVersionDict[key]))

labels = openBugsVersionA
fracs = openBugsVersionDict.values()

explode=(0, 0.05, 0, 0)
pie(fracs, labels=labels, autopct='%1.1f%%', shadow=True)
title('All Open Bugs According to Different Versions', bbox={'facecolor':'0.8', 'pad':5})

savefig("all_open_bugs_for_version.png")
print("     .. image:: all_open_bugs_for_version.png")
print("         :align: center")

print "\nAll Opened, Reopened or Assigned for All Contributors"
print "=====================================================\n"

# Draw the bar chart of all open bugs of all contributors
import numpy as np
import matplotlib.pyplot as plt

fig = plt.figure(figsize=(20,30))

N = len(devNames)
ind = np.arange(N)  # the x locations for the groups
width = 0.5       # the width of the bars

devStd =[]
for devName in devNames:
    devStd.append(0.5)

rects2 = plt.bar(0,0.5 , totalOpenedBugs , ind+width, width,
                    color='y',
                    xerr=devStd,
                    error_kw=dict(elinewiadth=6, ecolor='yellow'), orientation="horizontal", align="center")

# add some
plt.xlabel('Number of Bugs')
plt.title('All Open Bugs of a Contributor')
plt.yticks(ind+width, devNames )



def autolabel(rects):
    # attach some text labels
    for rect in rects:
        plt.text( 1.05*rect.get_width(), rect.get_y()+rect.get_height()/2., '%d'%int(rect.get_width()), ha='center', va='bottom')

autolabel(rects2)

plt.savefig("all_open_bugs.png")
print("     .. image:: all_open_bugs.png")
