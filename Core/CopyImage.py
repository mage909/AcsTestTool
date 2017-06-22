'''
Created on Feb 4, 2015

@author: jenkins
'''
import os


def copy_fls(src, des):
    print "------> copy fls files"
    roots = []
    for root, subFolders, files in os.walk("%s" % src):
        if "JenkinsProject" in subFolders:
            subFolders.remove("JenkinsProject")
        for f in files:
            if f.find(".fls") != -1:
                path_fls = os.path.join(root, f)
                os.system("mv -f %s %s" % (path_fls, des))
