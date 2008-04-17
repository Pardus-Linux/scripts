#!/bin/sh

if [ $# -lt 3 ]; then
    echo "Usage: $0 <project path> <version> <git branch>"
    exit
fi

PROJECT_PATH=$1
VERSION=$2
BRANCH=$3

PROJECT_NAME=$(basename $PROJECT_PATH)
DIRNAME="$PROJECT_NAME-${VERSION}_$(date +%Y%m%d)"

rm -rf $DIRNAME
git clone git://git.freedesktop.org/git/xorg/$PROJECT_PATH $DIRNAME
cd $DIRNAME

git log | head -1 | cut -d" " -f 2 > commit
git-archive --format=tar --prefix=$DIRNAME/ $BRANCH | bzip2 > ../$DIRNAME.tar.bz2

cd ..
rm -rf $DIRNAME
