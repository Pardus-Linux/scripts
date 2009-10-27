#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import itertools

f= open("component")
os.mkdir("newcomponent")
os.chdir("newcomponent")

for line in f:
    if line.startswith("|--"):
        parent1= line.split(" ")
        os.mkdir(parent1[1].strip())
    if line.startswith("|   |--"):
        parent2= line.split("|-- ")
        os.mkdir(parent1[1].strip() + "/" + parent2[1].strip())
    if line.startswith("|   |   |--"):
        child= line.split("|-- ")
        os.mkdir(parent1[1].strip() + "/" + parent2[1].strip() + "/" + child[1].strip())
