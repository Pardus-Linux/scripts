#!/bin/sh

cd /var/www/bugzilla/scripts/bzilla-paketler
rm -f pisi-index.xml*
wget http://svn.pardus.org.tr/pardus/2009/devel/pisi-index.xml.bz2
bunzip2 pisi-index.xml.bz2
python main.py pisi-index.xml
rm -f pisi-index.xml*
wget http://svn.pardus.org.tr/contrib/2009/devel/pisi-index.xml.bz2
bunzip2 pisi-index.xml.bz2
python main.py pisi-index.xml
rm -f pisi-index.xml*
