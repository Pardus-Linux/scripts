#!/bin/bash

VERSION="7.2"

for option in $*; do
    case $option in
        --mirror=*)
            MIRROR="`echo $option | awk -F= '{print $2;}'`"
        ;;
        --version=*)
            VERSION="`echo $option | awk -F= '{print $2;}'`"
        ;;
        --package=*)
            PACKAGE="`echo $option | awk -F= '{print $2;}'`"
        ;;
        --filelist=*)
            FILELIST="`echo $option | awk -F= '{print $2;}'`"
        ;;
    esac
done

if [ "$MIRROR" == "" ]; then
    echo "Use with $0 --mirror=http://ftp.gwdg.de/pub/x11/x.org/pub/individual/{app/data/doc/driver/font/input/proto/util}"
    exit
fi

if [ "$PACKAGE" == "" ]; then
    echo "Use with $0 --package={xorg-app/xorg-data/xorg-doc/xorg-font/xorg-input/xorg-proto/xorg-util/xorg-video}"
    exit
fi

if [ "$FILELIST" == "" ]; then
    echo "Use with $0 --filelist={app/data/doc/font/input/proto/util/video}"
    exit
fi

if [ ! -e xorg ]; then
    mkdir xorg
fi

mkdir $PACKAGE-$VERSION
cd xorg

for i in `cat ../$FILELIST`
do
    if [ ! -e $i ]; then
        wget $MIRROR"/"$i
        echo "$i" > $FILELIST.changes
    fi
    tar xvf $i -C ../$PACKAGE-$VERSION
done

cd ..
tar cjvf $PACKAGE-$VERSION.tar.bz2 $PACKAGE-$VERSION
rm -rf  $PACKAGE-$VERSION
