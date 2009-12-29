#!/usr/bin/python
# -*- coding: utf-8 -*-
# A python script for analyze weekly bug changes
# of pardus mailed people


import os
import matplotlib

assignedTo = []
N_bug_all = []
def parseBugsAnalyzeFile():
    if not os.path.exists("bugsAnalyze"):
        os.system("wget http://cekirdek.pardus.org.tr/~semen/bugFiles/bugsAnalyze")
    bugFile = open("bugsAnalyze", "r")
    for line in bugFile.readlines():
        bugVar = line.split(" ")
        #print bugVar[0]
        assignedTo.append(bugVar[0].split("@")[0])
        N_bug_all.append(bugVar[1])


def getOldNewBugFiles():
    for i in range(len(assignedTo)):
        #print assignedTo
         if not os.path.exists("%sIdOld" % assignedTo[i]) and not os.path.exists("%sIdNew" % assignedTo[i]):
            os.system("wget  http://cekirdek.pardus.org.tr/~semen/bugFiles/%sIdOld" % assignedTo[i])
            os.system("wget  http://cekirdek.pardus.org.tr/~semen/bugFiles/%sIdNew" % assignedTo[i])

def getDiff():
     for i in range(len(assignedTo)):
         os.system("diff -Nuar %sIdOld %sIdNew > %sDiff" % (assignedTo[i], assignedTo[i], assignedTo[i]))

def parseDiff():
    for i in range(len(assignedTo)):
        diffFile = open("%sDiff" % assignedTo[i], "r")
        fixed = 0
        notFixed = 0
        for line in diffFile.readlines():
            if line.startswith("-"):
                fixed = fixed + 1
            if line.startswith("+"):
                notFixed = notFixed + 1
        #print "%s fixed %s bugs and %s new bugs assigned.\n" % (assignedTo[i], fixed, notFixed)
        print "%s & %s & %s &  %s \\\ " % (assignedTo[i], N_bug_all[i], fixed, notFixed)

if __name__ == "__main__":
    """ main """
    parseBugsAnalyzeFile()
    getOldNewBugFiles()
    getDiff()
    parseDiff()
