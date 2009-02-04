#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

for i in os.listdir("/var/cache/pisi/packages-test/"):
    if not os.path.exists("/var/cache/pisi/packages-stable/%s" % i):
        print i
