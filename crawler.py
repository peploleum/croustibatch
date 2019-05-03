# -*- coding: UTF-8 -*-

import logging
from openalpr import Alpr
import time
import insight
from ftplib import FTP

import re
import os

from argparse import ArgumentParser

parser = ArgumentParser(description='OpenALPR Python Test Program')

parser.add_argument("-c", "--country", dest="country", action="store", default="eu",
                     help="License plate Country")

parser.add_argument("-v", "--verbosity",action="store_true", help="show debug logs")

parser.add_argument("--config", dest="config", action="store", default="conf/openalpr.conf",
                    help="Path to openalpr.conf config file")

parser.add_argument("--runtime_data", dest="runtime_data", action="store", default="runtime_data",
                    help="Path to OpenALPR runtime_data directory")

parser.add_argument("--endpoint", dest="endpoint", help="Insight's endpoint", action="store", default="http://localhost:8080")

parser.add_argument("--i", dest="dataSource", help="Source Image or JSON", action="store", default="json")

parser.add_argument("--source", dest="directory", help="Directory source Image or JSON", action="store", default="source")

parser.add_argument("--store", dest="store", help="Directory store Image", action="store", default="download")

parser.add_argument("--login", dest="login", help="Login", action="store", default="admin")
parser.add_argument("--password", dest="password", help="Password", action="store", default="admin")

parser.add_argument("--to", dest="timeout", help="Timeout in second", action="store", default="0")

parser.add_argument("--ftp", dest="ftphost", help="connect to host, default port", action="store", default="192.168.0.10")

parser.add_argument("--pathtosource", dest="pathtosource", help="Path to directory source Image or JSON", action="store", default="dev/croustibatch/docker")

parser.add_argument("--loginftp", dest="loginftp", help="Login to ftp_host", action="store", default="nimir")
parser.add_argument("--passwordftp", dest="passwordftp", help="Password for ftp_host", action="store", default="@soleil1")

parser.add_argument("-p", "--preprocess",dest="preprocess", type=str, default="thresh",
                    help="type of preprocessing to be done")

parser.add_argument("-t", "--tesseract",action="store_true", help="active tesseract")

#--debug That will draw a square around the plate.?
options = parser.parse_args()

def isSourceDirectoryEmpty(path):
    #return len(os.listdir(path) ) == 1
    filelist = []
    ftp.retrlines('LIST',filelist.append)
    return len(filelist ) == 1

def directory_exists(dir):
    filelist = []
    ftp.retrlines('LIST',filelist.append)
    for f in filelist:
        if f.split()[-1] == dir and f.upper().startswith('D'):
            return True
    return False

def crdir(dir):
    if len(dir.rsplit("/", 1))==2:
        ftp.cwd(dir.rsplit("/", 1)[0])
        dir = dir.rsplit("/", 1)[1]
    if directory_exists(dir) is False: # (or negate, whatever you prefer for readability)
        ftp.mkd(dir)

try:
    lastCrawl = None
    jsonFiles = None

    start = time.time()


    logging.basicConfig(level=logging.INFO)
    if options.verbosity:
        logging.getLogger().setLevel(logging.DEBUG)
    logging.info('Lancement de croustibatch')

    if not options.tesseract:
        algo = Alpr(options.country, options.config, options.runtime_data)
        algo.set_detect_region("d")
        algo.set_top_n(5)
        algo.set_detect_region(True)
        logging.info("Using OpenALPR " + algo.get_version())
    else:
        algo = "thresh"

    # if not algo.is_loaded():
    #     logging.error("Error loading OpenALPR")
    # else:

    ftp = FTP(options.ftphost)
    ftp.login(options.loginftp, options.passwordftp)

    #if not os.path.isdir(options.directory):
    #    os.mkdir(options.directory)
    ftp.cwd(options.pathtosource)

    cwd = ftp.pwd()
    crdir(str(options.directory))
    if not os.path.isdir(options.store):
        os.mkdir(options.store)

    sourceDirectory = options.directory
    targetDirectory = options.store

    #cwd = os.getcwd()
    cwd = ftp.pwd()
    if options.dataSource == "image":
        type = ".*\.jpg$"
    else:
        type = "^(?!\.).*\.json$"
    crawlDir = cwd + "/" + sourceDirectory
    #jsonFiles = pathlib.Path(crawlDir).glob(type)
    #if not os.path.isdir(crawlDir+"/processedData"):
    #    os.makedirs(crawlDir+"/processedData")
    ftp.cwd(sourceDirectory)
    crdir("processedData")


    while True:
        if not isSourceDirectoryEmpty(crawlDir):
            filelist = []
            ftp.retrlines('LIST',filelist.append)
            filelistsplitted = [i.split()[-1] for i in filelist]
            r = re.compile(type)
            jsonFiles = list(filter(r.match, filelistsplitted))
            if options.dataSource == "json":
                for file in jsonFiles:
                    logging.debug(file)
                    if not str(file).startswith('.'):
                        insight.extract_data(crawlDir, file, ftp,  targetDirectory, algo, options.endpoint, options.login, options.password)
                    else:
                        logging.debug("file temp : "+ str(file))

            elif options.dataSource == "image":
                for file in jsonFiles:
                    logging.debug(file)
                    strFileName = targetDirectory + "/" + file
                    imageFile = open(strFileName, 'wb')
                    ftp.retrbinary('RETR '+str(file), imageFile.write, 1024)
                    targetImageFileName = crawlDir + "/processedData/" + file
                    test =  str(file).rsplit('.', 1)[0]

                    if not isinstance(algo, str):
                        if not str(file).startswith('.'):
                            if insight.postimg(strFileName, str(file).rsplit('.', 1)[0], insight.get_plates(algo, strFileName), options.endpoint, options.login, options.password):
                                os.remove(strFileName)
                    else:
                        if not str(file).startswith('.'):
                            if insight.postimg(strFileName, str(file).rsplit('.', 1)[0], insight.get_text(strFileName, algo), options.endpoint, options.login, options.password):
                                os.remove(strFileName)

                    if not insight.file_exists(targetImageFileName, ftp):
                        ftp.rename(file, targetImageFileName)
                    else:
                        ftp.delete(file)
            else:
                logging.error("Wrong --typesource arg")
        else:
            if (int(options.timeout) != 0) & ((time.time()-start) < float(options.timeout)):
                time.sleep(5)
            elif int(options.timeout) == 0:
                time.sleep(5)
            else:
                break
except Exception as e:
    logging.error("ERROR : ", e)



finally:
    logging.info(" Fin de croustibatch ")
    exit(0)
