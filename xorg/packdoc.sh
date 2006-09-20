#!/bin/bash

VERSION="xorg-doc-7.1"
MIRROR="http://ftp.gwdg.de/pub/x11/x.org/pub/individual/doc/"

PACKAGES="xorg-docs-1.2.tar.bz2 
xorg-sgml-doctools-1.1.tar.bz2"

mkdir $VERSION/
cd $VERSION

for i in $PACKAGES
do
    wget $MIRROR"/"$i
    tar jxvf $i
    rm -f $i
done

cd ..
tar cjvf -$VERSION.tar.bz2 $VERSION/
rm -rf $VERSION/
