#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

# weekly cron
os.system("all-bugs-report.py > all-bugs-repot.rst")
os.system("detailed-bug-report.py > detailed-bug-report.rst")
os.system("time-based-bug-report.py weekly > weekly-bug-report.rst")

# monthly cron
os.system("time-based-bug-report.py monthly > monthly-bug-report.rst")

# half yearly cron
os.system("time-based-bug-report.py half-yearly > half-yearly-bug-report.rst")

# yearly cron
os.system("time-based-bug-report.py yearly > yearly-bug-report.rst")
