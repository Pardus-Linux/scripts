#!/usr/bin/python
# -*- coding: utf-8 -*-

# Find packages with no translations.xml

import os

for root, dirs, files in sorted(os.walk(".")):
    if "pspec.xml" in files and "translations.xml" not in files:
        print root[2:]
