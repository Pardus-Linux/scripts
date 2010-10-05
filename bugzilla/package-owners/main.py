#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mysql
import listRepoPackages
import sys
import os

# Pardus Technologies' packages will be removed from the distribution products
packTech = ["boot-manager", "network-manager", "comar", "disk-manager", "kaptan", "user-manager", "mudur", "package-manager", "pisi", "service-manager", "system-manager", "tasma", "yali", "display-settings", "firewall-manager"]

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

# Get all profiles from db to find userids of maintaners
print "---match bugzilla users and package maintainers"
profiles = {}

cProfiles = db.cursor()
cProfiles.execute("SELECT userid, login_name FROM profiles")

for id, mail in cProfiles.fetchall():
    profiles[mail] = id

#print profiles

# Execute a query to insert/update components infos
# packDict = {"package_name":"maintainer@foo.bar"}
# profiles = {"maintainer@foo.bar":id}

errors = {'db':[], 'mail':[]}
procs = {'update':0, 'insert':0}

#cPackage = db.cursor()
#cPackage.execute("INSERT INTO components(name, product_id, initialowner, description) VALUES ('Paket listede yok / Package is not in the list', %s, 4981, 'Paket listede yok / Package is not in the list')", (str(pId)))
#db.commit()

for pack in packDict.iterkeys():
    cPackage = db.cursor()

    # pack = package name
    # profiles[ packDict[pack] ] = userid

    try:
       id = profiles[packDict[pack]]

       numRows = cPackage.execute("SELECT id FROM components WHERE name = '%s' and product_id = '%s'" % (pack, str(pId)))


       if not numRows == 0:
           print "---updating %s package, package owner is %s" % (pack, packDict[pack])
           cPackage.execute("UPDATE components SET initialowner = '%s' WHERE name = '%s'" % (id, str(pack)))
           procs['update'] += 1
       else:
           print "---inserting %s package, package owner is %s" % (pack, packDict[pack])
           cPackage.execute("INSERT INTO components(name, product_id, initialowner, description) VALUES (%s, %s, %s, %s)",(str(pack), str(pId), id, str(pack)))
           procs['insert'] += 1

       if pack in packTech and not numRows == 0:
           cPackage.execute("delete from components where name = '%s' and product_id = '%s'" % (pack, str(pId)))
       db.commit()

    except mysql.Error, e:
        errors['db'].append(e.__str__())
    except KeyError, e:
        errors['mail'].append(str(e))


print "\nThere are %s packages in repo" % packDict.keys().__len__()
print "%s packages inserted, %s packages updated\n" % (procs["insert"], procs["update"])

print "---DB Errors (%s)" % errors['db'].__len__()
print "\n".join(errors['db'])

print "---Unknown Mail Addresses (%s)" % errors['mail'].__len__()
print "\n".join(list(set(errors['mail'])))
