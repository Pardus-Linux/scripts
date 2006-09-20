#!/bin/bash

VERSION="xorg-util-7.1"
MIRROR="http://ftp.gwdg.de/pub/x11/x.org/pub/individual/util/"

PACKAGES="gccmakedep-1.0.2.tar.bz2 
imake-1.0.2.tar.bz2 
lndir-1.0.1.tar.bz2 
makedepend-1.0.0.tar.bz2 
xorg-cf-files-1.0.2.tar.bz2"

mkdir $VERSION/
cd $VERSION

for i in $PACKAGES
do
    wget $MIRROR"/"$i
    tar jxvf $i
    rm -f $i
done

cd ..
tar cjvf $VERSION.tar.bz2 $VERSION/
rm -rf $VERSION/
