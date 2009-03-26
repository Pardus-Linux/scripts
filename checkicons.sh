#!/bin/bash

echo "Finding packages tagged as app:gui.."

for p in $(grep -rl --exclude-dir=.svn --exclude=pisi-index* --exclude=checkicons.sh "app:gui" *); do
    grep -q "<Icon>" $p
    if [ $? == 1 ]; then
        echo "$p doesn't have an <Icon> tag"
    fi
done
