#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

# weekly cron
os.system("all-bugs-report.py > all-bugs-repot.rst")
os.system("detailed-bug-report.py > detailed-bug-report.rst")
os.system("weekly-bug-report.py > weekly-bug-report.rst")

# monthly cron
os.system("mountly-bug-report.py > monthly-bug-report.rst")

# half yearly cron
os.system("half-yearly-bug-report.py > half-yearly-bug-report.rst")

# yearly cron
os.system("yearly-bug-repot.py > yearly-bug-report.rst")
