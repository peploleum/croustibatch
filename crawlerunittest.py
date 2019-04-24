import datetime
import os
import unittest
import re
import sys

from openalpr import Alpr

import insight
from ftplib import FTP


class CrawlerTest(unittest.TestCase):

    def test_postimg(self):
        alpr = Alpr("eu", "conf/openalpr.conf", "runtime_data")
        imageFileName = "samples_test/eu-3.jpg"
        jpeg_bytes = open(imageFileName, "rb").read()
        results = alpr.recognize_array(jpeg_bytes)
        post = insight.postimg(imageFileName, "1231231231231231231", str(results['results']), "http://localhost:8080", "admin", "admin")
        open(imageFileName, "rb").close()
        self.assertTrue(post)

    def test_extract_data(self):
        alpr = Alpr("eu", "conf/openalpr.conf", "runtime_data")
        # crawlDir = os.getcwd() + "/source_test"
        # jsonFiles = pathlib.Path(crawlDir).glob("*.json")
        print("\n" + self.IP)
        ftp = FTP(self.IP)
        ftp.login(self.USERNAME, self.PASSWORD)
        ftp.cwd("dev/croustibatch/docker/source_test")
        crawlDir = ftp.pwd()
        filelist = []
        ftp.retrlines('LIST',filelist.append)
        filelistsplitted = [i.split()[-1] for i in filelist]
        r = re.compile("^(?!\.).*\.json$")
        jsonFiles = list(filter(r.match, filelistsplitted))
        for file in jsonFiles:
            data = insight.extract_data(crawlDir, file, ftp, "download_test", alpr, "http://localhost:8080", "admin", "admin")
            ftp.cwd("processedData")
            filename = data.split("/")[-1]
            self.assertTrue(file_exists(filename, ftp))
            ftp.rename(data, crawlDir + "/" + file)
            # os.rename(data, crawlDir + "/" + file.name)

    def test_date(self):
        now = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        print(now)

def file_exists(file, ftp):
    filelist = []
    ftp.retrlines('LIST',filelist.append)
    for f in filelist:
        if f.split()[-1] == file and f.upper().startswith('-'):
            return True
    return False

if __name__ == '__main__':
    if len(sys.argv) > 1:
        CrawlerTest.PASSWORD = sys.argv.pop()
        CrawlerTest.USERNAME = sys.argv.pop()
        CrawlerTest.IP = sys.argv.pop()
    unittest.main()
