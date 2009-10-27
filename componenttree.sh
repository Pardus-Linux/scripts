#!/bin/bash

# Generate component tree
# Example: componenttree ~/pardus/devel > component_devel

tree $1 -n -P pspec.xml -I files | egrep -v "pspec.xml|files|comar"
