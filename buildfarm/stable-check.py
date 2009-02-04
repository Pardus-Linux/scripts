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
            os.system ("ls -1 /var/www/localhost/htdocs/pardus-2008-test/%s | grep 'Böyle'" % i)
