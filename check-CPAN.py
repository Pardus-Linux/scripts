#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version. Please read the COPYING file.
#
# Author:
#   Serdar Dalgıç <serdar_at_pardus.org.tr>
#

"""
Script that checks daily cpan updates mail list
manually if there is an update on any perl packages
in Pardus repositories.
"""

import urllib2
import sys
import datetime as dt

from BeautifulSoup import BeautifulSoup
from optparse import OptionParser

from pisi.db.componentdb import ComponentDB

def get_perl_packages():
    """ Return the list of perl packages in Pardus"""
    return ComponentDB().get_union_packages( \
            "programming.language.perl", walk=True)

def find_html_basename(_date):
    """ Find the html basename for the cpan mail """

    # Dec 29 2010 - 000983
    # CPAN_URL for Dec 29 2010 is
# http://theoryx5.uwinnipeg.ca/pipermail/cpan-daily/2010-December/000983.html
    reference = dt.datetime(2010, 12, 29)

    difference = (reference - dt.datetime(_date.year, \
                                          _date.month, \
                                          _date.day)).days

    # Shame on you CPAN, Sent two mails @ 7 November 2010
    # This ugly hack is because of that.
    if _date.year == 2010:
        if _date.month < 11:
            html_basename = "%0006d" % (983 - int(difference) - 1)
        elif _date.month == 11 and _date.day < 7:
            html_basename = "%0006d" % (983 - int(difference) - 1)
        else:
            html_basename = "%0006d" % (983 - int(difference) )
    else:
        html_basename = "%0006d" % (983 - int(difference) )

    return html_basename

def create_cpan_url(days_before):
    """
    creates and returns the cpan url
    """
    url_body = "http://theoryx5.uwinnipeg.ca/pipermail/cpan-daily/"
    target_date = dt.date.today() - dt.timedelta(days=days_before)

    strdate = dt.datetime.strptime(str(target_date), "%Y-%m-%d")
    month_name = strdate.strftime("%B")

    return url_body + "%s-%s/%s.html" % (target_date.year, month_name, \
                                    find_html_basename(target_date))

def get_pkg_infos(_page_element):
    """ Return CPAN pkg names and whether
    they are updated or not information.
        returns orig_pkg_list and _updated_pkgs
    """

    perl_pkgs = get_perl_packages()

    orig_pkg_list = []
    _updated_pkgs = {}

    for url in _page_element.findAll():
        orig_pkg_name = str(url.contents[0].split("/")[-1])
        orig_pkg_list.append(orig_pkg_name)

        if not orig_pkg_name.startswith("perl"):
            pkg_name = "perl-" + orig_pkg_name

        if pkg_name in perl_pkgs:
            _updated_pkgs[orig_pkg_name] = url.contents[0]

    return orig_pkg_list, _updated_pkgs

def argument():
    """Command line argument parsing"""

    parser = OptionParser(usage = "Usage: %prog [-n days]", prog = sys.argv[0])

    parser.add_option("-n", "--days_before",
                action = "store",
                type = "int",
                dest = "days_before",
                help = "Specify how many days before today you want to check")

    return parser.parse_args()

if __name__ == "__main__":
    '''
    Python script that checks CPAN daily mail
    for possible perl updates in Pardus.
    '''

    ARG = argument()
    option = ARG[0]

    if not option.days_before:
        option.days_before = 0
        print "Checking todays updates: %s" % dt.date.today()
    else:
        print "Checking %s days ago: %s" % (option.days_before, \
                                (dt.date.today() - \
                                 dt.timedelta(days=option.days_before)))


    CPAN_URL = create_cpan_url(option.days_before)
    print "CPAN_URL: " + CPAN_URL + "\n"

    try:
        URLFILE = urllib2.urlopen(CPAN_URL)
    except urllib2.HTTPError:
        print "Cpan_URL can not be reached"
        print "Double check your parameters"
        sys.exit(1)


    SOUP = BeautifulSoup(URLFILE.read())

    # PAGE_ELEMENT consists of the part which includes
    # daily CPAN Update information
    PAGE_ELEMENT = SOUP.find('pre')

    WHOLE_PKGS, UPDATED_PKGS = get_pkg_infos(PAGE_ELEMENT)

    if not UPDATED_PKGS:
        print "None of Pardus perl packages are updated" \
                + " according to CPAN daily update list"
        sys.exit(1)
    else:
        print "These pkgs have updates:\n"
        for pkg, p_url in UPDATED_PKGS.iteritems():
            if not pkg.startswith("perl-"):
                print "perl-" + pkg + " ----> " + p_url
            else:
                print pkg + " ----> " + p_url
            print
