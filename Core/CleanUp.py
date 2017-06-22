'''
Created on Feb 4, 2015

@author: jenkins
'''
import os


def cleanUp(fileOrpath, IncludeStr=[], ExceptStr=""):
    if ExceptStr == "":
        for i in IncludeStr:
            os.system("rm -rf *%s*" % i)
        # print "jobTrig"

    else:
        fileName = os.popen("ls  %s | grep  -v '%s'" % (fileOrpath, ExceptStr)).read().split("\n")
        filePath = []
        for f in fileName:
            filePath.append(os.path.join(os.path.abspath("%s" % fileOrpath), f))
        # print filePath
        for InStr in IncludeStr:
            for fp in filePath:
                if InStr in fp:
                    os.remove(fp)
if __name__ == "__main__":
    cleanUp("./", IncludeStr=[".fls"], ExceptStr=".img")
