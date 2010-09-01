#!/bin/bash

set -e
#set -x

# Paths
PARDUSMAN="/uludag/trunk/kde/pardusman/pardusman.py"
CDDIFF="/uludag/trunk/scripts/cd-diff"

# Defaults
TITLE="Pardus Nightly"
DISTRO_URL="http://svn.pardus.org.tr/uludag/trunk/distribution/2011"
PROJECT=installation.xml
DESTDIR=$PWD

if [ -z "$1" ]; then
    echo "Usage: $0 <config file>"
    exit 0
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

# a head symlink must be created to the first ISO
#HEAD=$(readlink head)

#############################################
echo "Preparing nightly build for $TODAY"

# Create a temp dir
TMPDIR=`mktemp -d /tmp/nightly-build.XXXXXXXXXX`

pushd $TMPDIR

# Checkout distro directory
svn co $DISTRO_URL .

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

# Set ReleaseFiles in $PROJECT_FILE
#sed -i "s:<ReleaseFiles>.*<\/ReleaseFiles>:<ReleaseFiles>$PWD/media-content</ReleaseFiles>:" $PROJECT_FILE

WORKDIR=$(grep "<WorkDir>" $PROJECT_FILE | sed 's/^ *<WorkDir>\(.*\)<\/WorkDir>/\1/')

# Clean up WorkDir
echo "Cleaning $WORKDIR"
test -d $WORKDIR && rm -rf $WORKDIR

# Create working directory
mkdir -p $WORKDIR

# Run pardusman
python $PARDUSMAN make $PROJECT_FILE

popd  # $TMPDIR

ISO=$(basename $WORKDIR/*.iso)
mkdir -p $DESTDIR$TODAY

pushd $DESTDIR

# Get the ISO file
mv $WORKDIR/$ISO $TODAY/

# Clean up WorkDir
rm -rf $WORKDIR

test -L current && YESTERDAY=$(readlink current) || YESTERDAY=

if [[ x$YESTERDAY != "x" ]]; then
    # Create ISO diff from previous snapshot
    echo "Generating CHANGES between incremental ISO images.."
    YESTERDAY_ISO="$YESTERDAY/$(basename `ls $YESTERDAY/*.iso`)"
    $CDDIFF $YESTERDAY_ISO $TODAY/$ISO

    # Sed some stuff
    sed -i -e 's#http://www.pardus.org.tr/eng/download.html#..#' stats.html

    # Move changes
    mv stats.html $TODAY/CHANGES.$YESTERDAY.html

    #if [[ $HEAD != $YESTERDAY ]]; then
    #    # Create changes between the new one and the very first iso
    #    HEAD_ISO="$HEAD/$(basename `ls $HEAD/*.iso`)"
    #    $CDDIFF $HEAD_ISO $TODAY/$ISO
    #
    #    # Sed some stuff
    #    sed -i -e 's#http://www.pardus.org.tr/eng/download.html#..#' stats.html
    #
    #    # Move the file
    #    mv stats.html $TODAY/CHANGES.$HEAD.html
    #fi

    # Create incremental xdelta
    if [[ -x $XDELTA ]]; then
        echo "Generating xdelta between incremental ISO images.."
        $XDELTA delta -9 $YESTERDAY_ISO $TODAY/$ISO $TODAY/$ISO.xdelta
    fi
fi

pushd $TODAY
sha1sum $(ls *.iso *.xdelta) > SHA1SUMS
popd  # $TODAY

set +e

# Update the current symlink
unlink current
ln -sf $TODAY current

# Remove old images
OLDDIR=$(date +%Y%m%d --date="3 days ago")
test -d $OLDDIR && rm -rf $OLDDIR

popd  # $DESTDIR

# Remove temp dir
rm -rf $TMPDIR
