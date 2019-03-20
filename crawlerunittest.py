import random
import unittest
import insight
import pathlib
import datetime
from openalpr import Alpr
import os

class CrawlerTest(unittest.TestCase):

    def test_postimg(self):
        alpr = Alpr("eu", "conf/openalpr.conf", "runtime_data")
        imageFileName = "samples/eu-3.jpg"
        jpeg_bytes = open(imageFileName, "rb").read()
        results = alpr.recognize_array(jpeg_bytes)
        post = insight.postimg(imageFileName, "1231231231231231231", results, "http://localhost:8080", "admin", "admin")
        open(imageFileName, "rb").close()
        self.assertTrue(post)

    def test_extract_data(self):
        alpr = Alpr("eu", "conf/openalpr.conf", "runtime_data")
        crawlDir = os.getcwd() + "/source_test"
        jsonFiles = pathlib.Path(crawlDir).glob("*.json")
        for file in jsonFiles:
            data = insight.extract_data(crawlDir, file, "download_test", alpr,  "http://localhost:8080", "admin", "admin")
            self.assertTrue(os.path.isfile(data))
            os.rename(data, crawlDir+"/"+file.name)

    def test_date(self):
        now = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M')
        print(now)
if __name__ == '__main__':
    unittest.main()