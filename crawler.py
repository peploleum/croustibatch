# -*- coding: UTF-8 -*-
import os.path
import pathlib

try:
    sourceDirectory = "source"
    targetDirectory = "download"
    cwd = os.getcwd()
    print("current directory: " + cwd)
    crawlDir = cwd + "/" + sourceDirectory
    jsonFiles = pathlib.Path(crawlDir).glob("*.json")
    for file in jsonFiles:
        print("handling " + file)

finally:
    print(" Out ")
    exit(0)
