#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

def loadFile(_file):
    f = file(_file)
    data = f.read().split("\n")
    f.close()
    return data

if __name__ == "__main__":

    acked = loadFile("/root/ack.txt")
    for i in acked :
        if (i):
            if not os.path.exists("/var/cache/pisi/packages-test/%s" % i):
                print "\033[01;32m * Missing binary in test repo :\033[0m %s" % i
