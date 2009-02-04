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
            print "\033[01;32m * Copying :\033[0m %s" % i
            os.system ("cp /var/cache/pisi/packages-test/%s /var/cache/pisi/packages-stable/%s" % (i, i))
    print "\033[01;32m * Creating repo index :\033[0m"
    os.system ("pisi index /root/2008/ /var/cache/pisi/packages-stable/ --skip-signing --skip-sources -o /var/cache/pisi/packages-stable/pisi-index.xml")
