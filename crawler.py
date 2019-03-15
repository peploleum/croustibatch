# -*- coding: UTF-8 -*-
import os.path
import pathlib

import requests
# pip install requests
from openalpr import Alpr
import time
import insight

from argparse import ArgumentParser

parser = ArgumentParser(description='OpenALPR Python Test Program')

parser.add_argument("-c", "--country", dest="country", action="store", default="eu",
                     help="License plate Country")

parser.add_argument("--config", dest="config", action="store", default="conf/openalpr.conf",
                    help="Path to openalpr.conf config file")

parser.add_argument("--runtime_data", dest="runtime_data", action="store", default="runtime_data",
                    help="Path to OpenALPR runtime_data directory")

parser.add_argument("--endpoint", dest="endpoint", help="Insight's endpoint", action="store", default="http://localhost:8080")

parser.add_argument("--typesource", dest="dataSource", help="Source Image or JSON", action="store", default="json")

parser.add_argument("--source", dest="directory", help="Directory source Image or JSON", action="store", default="source")

parser.add_argument("--store", dest="store", help="Directory store Image", action="store", default="download")

parser.add_argument("--login", dest="login", help="Login", action="store", default="admin")
parser.add_argument("--password", dest="password", help="Password", action="store", default="admin")

#--debug That will draw a square around the plate.?
options = parser.parse_args()

def isSourceDirectoryEmpty(path):
    return len(os.listdir(path) ) == 1


try:
    lastCrawl = None
    jsonFiles = None
    alpr = None
    print('croustibatch')
    alpr = Alpr(options.country, options.config, options.runtime_data)
    alpr.set_detect_region("d")

    if not alpr.is_loaded():
        print("Error loading OpenALPR")
    else:
        print("Using OpenALPR " + alpr.get_version())

        alpr.set_top_n(5)
        #alpr.set_default_region("wa")
        alpr.set_detect_region(True)
        if not os.path.isdir(options.directory):
            os.mkdir(options.directory)
        if not os.path.isdir(options.directory):
            os.mkdir(options.store)
        sourceDirectory = options.directory
        targetDirectory = options.store

        if not os.path.exists(targetDirectory):
            os.makedirs(targetDirectory)
        cwd = os.getcwd()
        if options.dataSource == "image":
            type = "*.jpg"
        else:
            type = "*.json"
        crawlDir = cwd + "/" + sourceDirectory
        jsonFiles = pathlib.Path(crawlDir).glob(type)
        if not os.path.isdir(crawlDir+"/processedData"):
            os.makedirs(crawlDir+"/processedData")

        while True:
            if not isSourceDirectoryEmpty(crawlDir):
                jsonFiles = pathlib.Path(crawlDir).glob(type)
                if options.dataSource == "json":
                    for file in jsonFiles:
                        print(file)
                        insight.extract_data(crawlDir, file, targetDirectory, alpr, options.endpoint, options.login, options.password)

                elif options.dataSource == "image":
                    for file in jsonFiles:
                        print(file.name)
                        strFileName = targetDirectory + "/" + file.name
                        insight.postimg(strFileName, file.name.rsplit('.', 1)[0], file, insight.get_plates(alpr, strFileName), options.endpoint, options.login, options.password)
                else:
                    print("Wrong --typesource arg")
            else:
                time.sleep(5)
except Exception as e:
    print("ERROR : ", e)

finally:
    print(" Out ")
    exit(0)
