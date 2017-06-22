import urllib
import urllib2
import os
import sys
import logging


username = 'mayuanfx'
password = 'W4@intel'
# username = 'cts-buildbot'
# password = 'W1@intel'


class DownLoad(object):

    def __init__(self):
        '''
        Constructor
        '''

    def handle_url(self, url):
        print "------> handle url"
        if ".zip" in url:
            return "zip"
        if ".tar" in url:
            return "tar"
        if ".tar.gz" in url:
            return "tar.gz"
        if ".7z" in url:
            return "7z"

    def download_url(self, url, ext, path):
        print "------> download_url: download image"
        filename = os.path.join(path, "source.%s" % ext)
        urllib.urlretrieve(url, filename)

    def download_url2_bigfile(self, url, ext, path):
        print "------> download_url2_bigfile: download image"
        # Pass empty dictionary to bypass proxy
        proxy = urllib2.ProxyHandler({})
        opener = urllib2.build_opener(proxy)
        urllib2.install_opener(opener)
        f = urllib2.urlopen(url)
        buff = 16 * 1024
        filename = os.path.join(path, "source.%s" % ext)
        with open(filename, "wb") as code:
            while True:
                block = f.read(buff)
                if len(block) == 0:
                    break
                code.write(block)

    def download_url2(self, url, ext, path):
        print "------> download_url2: download image"
        # username = "cts-buildbot@intel.com"
        # password = "W1@intel"
        p = urllib2.HTTPPasswordMgrWithDefaultRealm()
        p.add_password(None, url, username, password)
        handler = urllib2.HTTPBasicAuthHandler(p)
        opener = urllib2.build_opener(handler)
        urllib2.install_opener(opener)
        f = urllib2.urlopen(url)
        data = f.read()
        filename = os.path.join(path, "source.%s" % ext)
        with open(filename, "wb") as code:
            code.write(data)

    def download_wget(self, url, ext, path):
        print "------> download_wget: download image"
        filename = os.path.join(path, "source.%s" % ext)
        # os.popen("wget -q --no-proxy %s -O %s" % (url, filename))
        os.popen("wget -q --no-check-certificate --no-proxy --user %s --password %s %s -O %s" % (username, password, url, filename))

    def extract(self, ext, path):
        print "------> extract folder"
        f = os.path.join(path, "source.%s" % ext)
        if os.path.exists(f) and os.path.isfile(f):
            if ext == "zip":
                os.popen("unzip -o -j -d %s %s" % (path, f))
            if ext == "tar.gz":
                os.system("tar zxvf %s -C %s" % (f, path))
            if ext == "tar":
                os.system("tar xvf %s -C %s" % (f, path))
            if ext == "7z":
                os.system("7z x %s" % f)


def download(url, image_path):
    ext = DownLoad().handle_url(url)
    try:
        # DownLoad().download_url2(url, ext, image_path)
        DownLoad().download_wget(url, ext, image_path)
    except Exception as ex:
        logging.warn(ex)
        try:
            DownLoad().download_url(url, ext, image_path)
        except Exception as ex:
            logging.warn(ex)
            try:
                DownLoad().download_url2_bigfile(url, ext, image_path)
            except Exception as ex:
                logging.error("Download error")
                sys.exit(1)
    DownLoad().extract(ext, image_path)


if __name__ == "__main__":
    url = "https://mcg-depot.intel.com/artifactory/cactus-absp-jf/chunshen_st-release_candidate/6/r2_Sf3gr_mrd_n1/userdebug/r2_Sf3gr_mrd_n1-flashfiles-chunshen_st-rc-6.zip"
    download(url, "/home/jenkins/")
