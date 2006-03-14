#!/bin/bash

cd ..
find -name pspec.xml | xargs sed -i -e "s~\t~    ~g"
find -name actions.py | xargs sed -i -e "s~\t~    ~g"
find -name pspec.xml | xargs sed -i -e "s~^    <Desc~        <Desc~g"
find -name pspec.xml | xargs sed -i -e "s~^    <Sum~        <Sum~g"
find -name pspec.xml | xargs sed -i -e "s~^    <IsA~        <IsA~g"
