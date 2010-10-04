#!/bin/sh

# 2009
rm -f pisi-index-*
rm -f pisi-index.xml*
wget http://svn.pardus.org.tr/pardus/2009/devel/pisi-index.xml.bz2
bunzip2 pisi-index.xml.bz2
cp -f pisi-index.xml pisi-index-2009.xml
python main.py pisi-index-2009.xml
# 2009 Contrib
rm -f pisi-index-*
rm -f pisi-index.xml*
wget http://svn.pardus.org.tr/contrib/2009/devel/pisi-index.xml.bz2
bunzip2 pisi-index.xml.bz2
cp -f pisi-index.xml pisi-index-2009.xml
python main.py pisi-index-2009.xml
# 2011
rm -f pisi-index-*
rm -f pisi-index.xml*
wget http://svn.pardus.org.tr/pardus/2011/devel/pisi-index.xml.bz2
bunzip2 pisi-index.xml.bz2
cp -f pisi-index.xml pisi-index-2011.xml
python main.py pisi-index-2011.xml
# Corporate 2
rm -f pisi-index-*
rm -f pisi-index.xml*
wget http://svn.pardus.org.tr/pardus/corporate2/devel/pisi-index.xml.bz2
bunzip2 pisi-index.xml.bz2
cp -f pisi-index.xml pisi-index-corporate2.xml
python main.py pisi-index-corporate2.xml
rm -f pisi-index-*
rm -f pisi-index.xml*
