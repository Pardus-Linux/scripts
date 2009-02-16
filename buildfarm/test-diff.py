#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

packages = []
for i in os.listdir("/var/cache/pisi/packages-test/"):
    if not os.path.exists("/var/cache/pisi/packages-stable/%s" % i) and not 'delta.pisi' in i:
        packages.append(i)

if (packages):
    packages.sort()
    for i in packages:
        print i
