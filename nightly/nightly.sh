#!/bin/bash

#set -x

# Defaults
TITLE="Pardus Nightly"
DISTRO_URL="http://svn.pardus.org.tr/uludag/trunk/distribution/2011"
PROJECT=installation.xml
REPO_URI=
DESTDIR=$PWD

KEEP_WORKDIR=

if [ -z "$1" ]; then
    echo "Usage: $0 [--keep-workdir] <config file>"
    exit 0
fi

if [ "x$1" = "x--keep-workdir" ]; then
    KEEP_WORKDIR=1
    shift
fi

# Source config file
if [ -f "$1" ]; then
    . "$1"
else
    echo "Cannot open $1"
    exit 1
fi

XDELTA=$(which xdelta 2>/dev/null| sed 's|^[^/]*||' 2>/dev/null)

TODAY=$(date +%Y%m%d)

echo "========== Preparing nightly build for $PROJECT on $TODAY =========="

# Create a temp dir
TMPDIR=`mktemp -d /tmp/nightly-build.XXXXXXXXXX`

pushd $TMPDIR

echo "Checking out distribution project..."
svn co $DISTRO_URL .

echo "Checking out pardusman..."
svn co http://svn.pardus.org.tr/uludag/trunk/kde/pardusman
PARDUSMAN=$PWD/pardusman/pardusman.py

echo "Downloading cd-diff script..."
wget http://svn.pardus.org.tr/uludag/trunk/scripts/cd-diff
chmod +x cd-diff
CDDIFF=$PWD/cd-diff

PROJECT_FILE=project-files/$PROJECT

if [ ! -f $PROJECT_FILE ]; then
    echo "Cannot open $PROJECT_FILE"
    exit 1
fi

if [ ! -d media-content ]; then
    echo "Cannot find release files"
    exit 1
fi

# Set title in $PROJECT_FILE
sed -i "s:<Title>.*<\/Title>:<Title>$TITLE [$TODAY]</Title>:" $PROJECT_FILE

if [ -n "$REPO_URI" ]; then
    # Replace repo_uri
    sed -i 's#<PackageSelection repo_uri=".*">#<PackageSelection repo_uri="$REPO_URI">#' $PROJECT_FILE
fi

WORKDIR=$(grep "<WorkDir>" $PROJECT_FILE | sed 's/^ *<WorkDir>\(.*\)<\/WorkDir>/\1/')

#if [ -z "$KEEP_WORKDIR" ]; then
#    # Clean up WorkDir
#    echo "Cleaning $WORKDIR"
#    test -d $WORKDIR && rm -rf $WORKDIR
#fi

# Create working directory
mkdir -p $WORKDIR

echo "Running pardusman..."
PARDUSMAN_FAILED=
python $PARDUSMAN make $PROJECT_FILE || PARDUSMAN_FAILED=1

popd  # $TMPDIR

ISO=$(basename $WORKDIR/*.iso)

if [ -n "$PARDUSMAN_FAILED" -o ! -f "$ISO" ]; then
    # Remove temp dir
    rm -rf $TMPDIR

    exit 1
fi

mkdir -p $DESTDIR/$TODAY

pushd $DESTDIR

# Get the ISO file
mv $WORKDIR/$ISO $TODAY/

if [ -z "$KEEP_WORKDIR" ]; then
    # Clean up WorkDir
    rm -rf $WORKDIR
fi

test -L current && YESTERDAY=$(readlink current) || YESTERDAY=

if [ -n "$YESTERDAY" -a "$YESTERDAY" != "$TODAY" ]; then
    # Create ISO diff from previous snapshot
    echo "Generating CHANGES between incremental ISO images.."
    YESTERDAY_ISO="$YESTERDAY/$(basename `ls $YESTERDAY/*.iso`)"
    $CDDIFF $YESTERDAY_ISO $TODAY/$ISO || echo "$CDDIFF failed!"

    if [ -f stats.html ]; then
        # Sed some stuff
        sed -i -e 's#http://www.pardus.org.tr/eng/download.html#..#' stats.html

        # Move changes
        mv stats.html $TODAY/Changes-$YESTERDAY-$TODAY.html
    fi

    # Create incremental xdelta
    if [[ -x $XDELTA ]]; then
        echo "Generating xdelta between incremental ISO images.."
        $XDELTA delta -9 $YESTERDAY_ISO $TODAY/$ISO $TODAY/${ISO/$TODAY/$YESTERDAY-$TODAY}.xdelta
    fi
fi

pushd $TODAY
FILES=$(ls *.iso *.xdelta 2>/dev/null)
if test -n "$FILES"; then
    echo "Generating SHA1SUMS..."
    sha1sum $FILES > SHA1SUMS
fi
popd  # $TODAY

echo "Updating current link..."
test -e current && rm -f current
ln -sf $TODAY current

echo "Removing the oldest image..."
for i in 8 7 6 5 4 3; do
    OLDDIR=$(date +%Y%m%d --date="$i days ago")
    if test -d "$OLDDIR"; then
        rm -rf "$OLDDIR"
        break
    fi
done

popd  # $DESTDIR

echo "Removing temporary files..."
rm -rf $TMPDIR
