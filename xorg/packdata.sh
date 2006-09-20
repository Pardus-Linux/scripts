#!/bin/bash

VERSION="xorg-data-7.1"
MIRROR="http://ftp.gwdg.de/pub/x11/x.org/pub/individual/data/"

PACKAGES="xbitmaps-1.0.1.tar.bz2
xcursor-themes-1.0.1.tar.bz2
xkbdata-1.0.1.tar.bz2"

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
