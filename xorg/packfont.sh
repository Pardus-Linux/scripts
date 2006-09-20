#!/bin/bash

VERSION="xorg-font-7.1"
MIRROR="http://ftp.gwdg.de/pub/x11/x.org/pub/individual/font/"

PACKAGES="encodings-1.0.0.tar.bz2
font-adobe-100dpi-1.0.0.tar.bz2
font-adobe-75dpi-1.0.0.tar.bz2
font-adobe-utopia-100dpi-1.0.1.tar.bz2
font-adobe-utopia-75dpi-1.0.1.tar.bz2
font-adobe-utopia-type1-1.0.1.tar.bz2
font-alias-1.0.1.tar.bz2
font-arabic-misc-1.0.0.tar.bz2
font-bh-100dpi-1.0.0.tar.bz2
font-bh-75dpi-1.0.0.tar.bz2
font-bh-lucidatypewriter-100dpi-1.0.0.tar.bz2
font-bh-lucidatypewriter-75dpi-1.0.0.tar.bz2
font-bh-ttf-1.0.0.tar.bz2
font-bh-type1-1.0.0.tar.bz2
font-bitstream-100dpi-1.0.0.tar.bz2
font-bitstream-75dpi-1.0.0.tar.bz2
font-bitstream-speedo-1.0.0.tar.bz2
font-bitstream-type1-1.0.0.tar.bz2
font-cronyx-cyrillic-1.0.0.tar.bz2
font-cursor-misc-1.0.0.tar.bz2
font-daewoo-misc-1.0.0.tar.bz2
font-dec-misc-1.0.0.tar.bz2
font-ibm-type1-1.0.0.tar.bz2
font-isas-misc-1.0.0.tar.bz2
font-jis-misc-1.0.0.tar.bz2
font-micro-misc-1.0.0.tar.bz2
font-misc-cyrillic-1.0.0.tar.bz2
font-misc-ethiopic-1.0.0.tar.bz2
font-misc-meltho-1.0.0.tar.bz2
font-misc-misc-1.0.0.tar.bz2
font-mutt-misc-1.0.0.tar.bz2
font-schumacher-misc-1.0.0.tar.bz2
font-screen-cyrillic-1.0.0.tar.bz2
font-sony-misc-1.0.0.tar.bz2
font-sun-misc-1.0.0.tar.bz2
font-winitzki-cyrillic-1.0.0.tar.bz2
font-xfree86-type1-1.0.0.tar.bz2"

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
