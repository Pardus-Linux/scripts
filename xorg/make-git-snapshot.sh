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
    -o)
        OBJECT=$2
        shift
        ;;
    *)
        VERSION=$1
    esac
    shift
done

if [ -z "$VERSION" ]; then
    echo "Usage: $APP [--no-date] [--no-commit-id] [-p|--pre-release] [-n PROJECT_NAME] [-o OBJECT] <version>"
    exit
fi

test -z "$PROJECT_NAME" && PROJECT_NAME=$(basename `pwd`)
test -z "$OBJECT" && OBJECT=HEAD
test -z "$NO_DATE" && DATE=_$PRE_RELEASE$(date +%Y%m%d)
test -z "$NO_COMMIT_ID" &&
    COMMIT_ID=git$(git log $OBJECT | head -1 | cut -d" " -f 2 | head -c 7)

DIRNAME="$PROJECT_NAME-$VERSION$DATE"
ARCHIVE_FILE="$DIRNAME$COMMIT_ID.tar.bz2"

echo Creating archive from $OBJECT ...
git archive --format=tar --prefix=$DIRNAME/ $OBJECT | bzip2 > $ARCHIVE_FILE
sha1sum $ARCHIVE_FILE
