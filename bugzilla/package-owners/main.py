#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mysql
import listRepoPackages
import sys
import os

# Pardus Technologies' packages will be removed from the distribution products
packTech = ["boot-manager", "network-manager", "comar", "disk-manager", "kaptan", "user-manager", "mudur", "package-manager", "pisi", "service-manager", "system-manager", "tasma", "yali4", "yali", "display-settings", "firewall-manager"]

try:
    # get pisi index file full path
    index_file = sys.argv[1]
except:
    print """
Usage: python main.py <full_path_of_pisi_index_file>
"""
    sys.exit(0)

# Product Id of "Packages"
if "2009" in index_file:
    pId=50
if "2011" in index_file:
    pId=51
if "corporate2" in index_file:
    pId=52

# Connect DB
print "---connecting DB"
db = mysql.connect(**dict([line.split("=") for line in open("\x61\x75\x74\x68").read().strip().split("\n") if line != "" and not line.startswith("#")]))

# Get package names and maintainer addresses
print "---parse index file"
packDict = listRepoPackages.getFullList(index_file)

#for value in packDict.itervalues():
#    print value

errors= []
procs = {'update':0, 'insert':0}

for pack, user in packDict.iteritems():
    if pack in packTech and not numRows == 0:
        cPackage = db.cursor()

        userrow = cPackage.execute("SELECT userid FROM profiles where login_name='%s'" % user)

        if userrow==1:
            for row in cPackage.fetchall():
               userid = row[0]

            numRows = cPackage.execute("SELECT id FROM components WHERE name = '%s' and product_id = '%s'" % (pack, str(pId)))

            if not numRows == 0:
                print "---updating %s package, package owner is %s" % (pack, user)
                cPackage.execute("UPDATE components SET initialowner = '%s' WHERE name = '%s' and product_id = '%s'" % (userid, str(pack), str(pId)))
                procs['update'] += 1
            else:
                print "---inserting %s package, package owner is %s" % (pack, user)
                cPackage.execute("INSERT INTO components(name, product_id, initialowner, description) VALUES (%s, %s, %s, %s)",(str(pack), str(pId), userid, str(pack)))
                procs['insert'] += 1

            db.commit()
        else:
            errors.append(user)

print "\n"
print errors
print "are not added to database please add these people first and rerun the script."
print "\nThere are %s packages in repo" % packDict.keys().__len__()
print "%s packages inserted, %s packages updated\n" % (procs["insert"], procs["update"])
