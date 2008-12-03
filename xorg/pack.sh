#!/bin/bash

VERSION="7.5_${VERSION_DATE:-`date +%Y%m%d`}"

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
    echo "Use with $0 --mirror=http://ftp.gwdg.de/pub/x11/x.org/pub/individual/{app/doc/driver/font/input/proto/util}"
    exit
fi

if [ "$PACKAGE" == "" ]; then
    echo "Use with $0 --package={xorg-app/xorg-doc/xorg-font/xorg-input/xorg-proto/xorg-util/xorg-video}"
    exit
fi

if [ "$FILELIST" == "" ]; then
    echo "Use with $0 --filelist={app/doc/font/input/proto/util/video}"
    exit
fi

ARCHIVES_DIR=~/xorg-archives

if [ ! -e $ARCHIVES_DIR ]; then
    mkdir $ARCHIVES_DIR
fi

SCRIPT_DIR=`pwd`
TEMP_DIR=$SCRIPT_DIR/$PACKAGE-$VERSION

mkdir $TEMP_DIR
cd $ARCHIVES_DIR

for i in `cat $SCRIPT_DIR/$FILELIST`
do
    if [ ! -e $i ]; then
        wget $MIRROR"/"$i || exit 1
        echo "$i" > $FILELIST.changes
    fi
    tar xvf $i -C $TEMP_DIR
done

cd $SCRIPT_DIR
tar cjvf $PACKAGE-$VERSION.tar.bz2 -C $TEMP_DIR .
rm -rf  $TEMP_DIR
