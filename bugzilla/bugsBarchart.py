#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Script to analyze New, Reopened and Assigned bugs according to their severity

import numpy as np
import matplotlib.pyplot as plt
import pylab
import os
from matplotlib.patches import Polygon
from matplotlib.ticker import MaxNLocator

bugs = {}
scoreLabelsAll = []
scoreLabelsStopper = []
scoreLabelsCritic = []
scoreLabelsHigh = []
scoreLabelsNormal = []
scoreLabelsEnhancement = []

def parseBugsAnalyzeFile():
    if not os.path.exists("bugsAnalyze"):
        os.system("wget http://cekirdek.pardus.org.tr/~semen/bugFiles/bugsAnalyze")
    bugFile = open("bugsAnalyze", "r")
    for line in bugFile.readlines():
        bugVar = line.split(" ")
        #print bugVar[0]
        assignedTo = bugVar[0].split("@")[0]
        N_bug_all = bugVar[1]
        N_bug_stopper = bugVar[2]
        N_bug_critic = bugVar[3]
        N_bug_high = bugVar[4]
        N_bug_normal = bugVar[5]
        N_bug_enhancement = bugVar[6].strip()
        bugs[assignedTo] = [N_bug_all, N_bug_stopper, N_bug_critic, N_bug_high, N_bug_normal, N_bug_enhancement]
    return bugs


def drawChart(bugKey, bugValue, title, xTitle, yTitle, image):
    fig = plt.figure(figsize=(20,30))
    ax1 = fig.add_subplot(111)
    plt.subplots_adjust(left=0.115, right=0.88)
    fig.canvas.set_window_title(title)
    pos = np.arange(len(bugKey))+0.5    #Center bars on the Y-axis ticks
    print len(bugKey)

    print bugValue
    rects = ax1.barh(pos, bugValue, align='center', height=0.5, color='m')

    ax1.axis([0,200,0,0])
    pylab.yticks(pos, bugKey)
    ax1.set_title(title)

    # Set the right-hand Y-axis ticks and labels and set X-axis tick marks at the
    # deciles
    ax2 = ax1.twinx()
    ax2.plot([1000,1000], [0, 5], 'white', alpha=0.1)
    ax2.xaxis.set_major_locator(MaxNLocator(11))
    ax2.xaxis.grid(True, linestyle='--', which='major', color='grey', alpha=0.25)

    #Plot a solid vertical gridline to highlight the median position
    plt.plot([50,50], [0, 5], 'grey', alpha=0.25)

    ax2.set_ylabel(yTitle)
    ##Make list of numerical suffixes corresponding to position in a list
    ax2.set_xlabel(xTitle)

    # Lastly, write in the ranking inside each bar to aid in interpretation
    for rect in rects:
       # Rectangle widths are already integer-valued but are floating
       # type, so it helps to remove the trailing decimal point and 0 by
       # converting width to int type
       width = int(rect.get_width())

       # Figure out what the last digit (width modulo 10) so we can add
       # the appropriate numerical suffix (e.g. 1st, 2nd, 3rd, etc)
       lastDigit = width % 10

       rankStr = str(width)
       if (width < 5): # The bars aren't wide enough to print the ranking inside
            xloc = width + 1 # Shift the text to the right side of the right edge
            clr = 'black' # Black against white background
            align = 'left'
       else:
            xloc = 0.98*width # Shift the text to the left side of the right edge
            clr = 'white' # White on magenta
            align = 'right'

       yloc = rect.get_y()+rect.get_height()/2.0 #Center the text vertically in the bar
       ax1.text(xloc, yloc, rankStr, horizontalalignment=align, verticalalignment='center', color=clr, weight='bold')

    plt.savefig(image)
    plt.show()


if __name__ == "__main__":
    """ main """

    bugAnalyze = parseBugsAnalyzeFile()
    for k, v in bugAnalyze.items():
        scoreLabelsAll.append(int(v[0]))
        scoreLabelsStopper.append(int(v[1]))
        scoreLabelsCritic.append(int(v[2]))
        scoreLabelsHigh.append(int(v[3]))
        scoreLabelsNormal.append(int(v[4]))
        scoreLabelsEnhancement.append(int(v[5]))


    drawChart(bugAnalyze.keys(), scoreLabelsAll, 'Analysis for All New, Reopened and Assigned bugs', 'All Bugs', 'People', 'allBugs.jpeg')
    drawChart(bugAnalyze.keys(), scoreLabelsStopper, 'Analysis for New, Reopened and Assigned bugs with Severity Stopper', 'All Stopper Bugs', 'People', 'stopperBugs.jpeg')
    drawChart(bugAnalyze.keys(), scoreLabelsCritic, 'Analysis for New, Reopened and Assigned bugs with Severity Critic', 'All Critic Bugs', 'People', 'criticBugs.jpeg')
    drawChart(bugAnalyze.keys(), scoreLabelsHigh, 'Analysis for New, Reopened and Assigned bugs with Severity High', 'All High Severity Bugs', 'People', 'highBugs.jpeg')
    drawChart(bugAnalyze.keys(), scoreLabelsNormal, 'Analysis for New, Reopened and Assigned bugs with Severity Normal', 'All Normal Severity Bugs', 'People', 'normalBugs.jpeg')
    drawChart(bugAnalyze.keys(), scoreLabelsHigh, 'Analysis for New, Reopened and Assigned bugs with Severity Ehancement', 'All Enhancement Bugs', 'People', 'enhancementBugs.jpeg')
