#!/bin/sh

APP=`basename $0`

while test "$1" != ""; do
    case $1 in
    --no-date)
        NO_DATE=1
        ;;
    --no-commit-id)
        NO_COMMIT_ID=1
        ;;
    -p|--pre-release)
        PRE_RELEASE=pre
        ;;
    -n)
        PROJECT_NAME=$2
        shift
        ;;
    -b)
        BRANCH=$2
        shift
        ;;
    *)
        VERSION=$1
    esac
    shift
done

if [ -z "$VERSION" ]; then
    echo "Usage: $APP [--no-date] [--no-commit-id] [-p|--pre-release] [-n PROJECT_NAME] [-b BRANCH] <version>"
    exit
fi

if [ -z "$PROJECT_NAME" ]; then
    PROJECT_NAME=$(basename `pwd`)
fi

if [ -z "$BRANCH" ]; then
    BRANCH=$(git branch | sed -n "/\* /{s/^..//; p}")
fi

if [ -z "$NO_DATE" ]; then
    DATE=_$PRE_RELEASE$(date +%Y%m%d)
fi

if [ -z "$NO_COMMIT_ID" ]; then
    COMMIT_ID=git$(git show $BRANCH | head -1 | cut -d" " -f 2 | head -c 7)
fi

DIRNAME="$PROJECT_NAME-$VERSION$DATE"
ARCHIVE_FILE="$DIRNAME$COMMIT_ID.tar.bz2"

echo Creating archive from $BRANCH branch...
git archive --format=tar --prefix=$DIRNAME/ $BRANCH | bzip2 > $ARCHIVE_FILE
sha1sum $ARCHIVE_FILE
