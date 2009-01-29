#!/bin/bash

VERSION="2008"

for option in $*; do
    case $option in
        --mirror=*)
            MIRROR="`echo $option | awk -F= '{print $2;}'`"
        ;;
        --mirror-core*)
            MIRRORCORE="`echo $option | awk -F= '{print $2;}'`"
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
    echo "Use with $0 --mirror=http://ftp.linux.org.tr/pub/gentoo/distfiles/"
    exit
fi

if [ "$MIRRORCORE" == "" ]; then
    echo "Use with $0 --mirror-core=ftp://tug.org/texlive/historic/2008/"
    exit
fi

if [ "$PACKAGE" == "" ]; then
    echo "Use with $0 --package=texlive-core-modules"
    exit
fi

if [ "$FILELIST" == "" ]; then
    echo "Use with $0 --filelist=modulelist"
    exit
fi

ARCHIVES_DIR=~/texlive-archives

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
    tar --lzma -xv -f $i -C $TEMP_DIR
done

k="texlive-20080816-source.tar.lzma"
wget $MIRRORCORE"/"$k || exit 1
tar --lzma -xv -f $k -C $TEMP_DIR

cd $SCRIPT_DIR
tar cjvf $PACKAGE-$VERSION.tar.bz2 -C $TEMP_DIR .
rm -rf  $TEMP_DIR

sha1sum $PACKAGE-$VERSION.tar.bz2
