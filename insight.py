# -*- coding: UTF-8 -*-

import json
import os.path
from pprint import pprint

import requests
# pip install requests

import base64
import insight

# -*- coding: UTF-8 -*-
from PIL import Image
import pytesseract
import argparse
import cv2
import os

import os.path
import pathlib

import requests
# pip install requests
from openalpr import Alpr
import time
import insight

def postimg(imagefilename, dataid, results, endpoint, login, password):

    print("Sending picture and results to Insight...")

    accountUrl = endpoint + "/api/account"
    authenticationUrl = endpoint + "/api/authentication"
    # url = "http://localhost:8080/api/raw-data/5c48cf9969f04e27882e32a7"
    url = endpoint + "/api/raw-data"
    payload = {
        'j_username': login,
        'j_password': password,
        'remember-me': 'true',
        'submit': 'Login'
    }
    with requests.Session() as session:
        myResponse = session.get(accountUrl, verify=True)
        if myResponse.status_code == 401:
            token = session.cookies.get("XSRF-TOKEN")
            headers = {
                'Accept': 'application/json',
                'Connection': 'keep-alive',
                'X-XSRF-TOKEN': token,
            }
            authResponse = session.post(url=authenticationUrl, data=payload, verify=True, headers=headers)
            if authResponse.ok:
                print("Authenticated")
                # request to insight
                headersRawData = {
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Content-type': 'application/json',
                    'X-XSRF-TOKEN': authResponse.cookies.get("XSRF-TOKEN")
                }

                with open(imagefilename, "rb") as image:
                    f = image.read()
                    b = bytearray(f)
                    decode = base64.b64encode(b).decode('UTF-8')

                rawData = {
                    "rawDataName": dataid,
                    "rawDataType": "image",
                    "rawDataContent": results,
                    "rawDataDataContentType": "image/jpeg",
                    "rawDataData": str(decode)
                }

                urlGet = url+"/filter?page=0&query="+dataid+"&size=20&filter=&sort=rawDataCreationDate,desc&sort=id"
                basic_get_response = session.get(url=urlGet)
                if basic_get_response.ok:
                    j_data = json.loads(basic_get_response.content.decode('utf-8'))
                    # print("The response contains {0} properties".format(len(str(j_data))))
                    print("\n")
                    if not j_data:
                        basic_post_response = session.post(url=url, json=rawData, headers=headersRawData)

                        if basic_post_response.ok:
                            print("\n")
                        else:
                            # If response code is not ok (200), print the resulting http error code with description
                            basic_post_response.raise_for_status()
                    else:
                        rawData = {
                            "id":j_data[0].get("id"),
                            "rawDataName": dataid,
                            "rawDataType": "image",
                            "rawDataContent": results,
                            "rawDataDataContentType": "image/jpeg",
                            "rawDataData": str(decode)
                        }
                        basic_put_response = session.put(url=url, json=rawData, headers=headersRawData)
                        if basic_put_response.ok:
                            print("\n")
                        else:
                            basic_put_response.raise_for_status()

                else:
                    # If response code is not ok (200), print the resulting http error code with description
                    basic_get_response.raise_for_status()
            else:
                print("Auth failed")
        else:
            # For successful API call, response code will be 200 (OK)
            if myResponse.ok:
                # j_data = json.loads(myResponse.content)
                # print("The response contains {0} properties".format(len(j_data)))
                print("\n")
            else:
                # If response code is not ok (200), print the resulting http error code with description
                myResponse.raise_for_status()

    return True

def get_media_url(imageFileName, media):
    print("getting media url...")
    with open(str(imageFileName), 'wb') as handle:

        response = requests.get(media['media_url'], stream=True)

        if not response.ok:
            print(response)

        else:
            for block in response.iter_content(1024):
                if not block:
                    break

                handle.write(block)


def extract_data(crawlDir, file, targetDirectory, required, endpoint, login, password):
    with open(str(file), encoding="utf8") as f:
        data = json.load(f)
    targetImageFileName = crawlDir + "/processedData/" + file.name
    if not os.path.isdir(crawlDir+"/processedData/"):
        os.mkdir(crawlDir+"/processedData/")
    if 'media' not in data['entities']:
        pprint("There is no media")
        if not os.path.isfile(targetImageFileName):
            os.rename(str(file), targetImageFileName)
        else:
            os.remove(str(file))
    else:
        for media in data['entities']['media']:
            pprint(media['media_url'])
            if not media['media_url']:
                pprint("There is no media")
            else:
                extension = media['media_url'].rsplit('.', 1)[1]
                imageFileName = targetDirectory + "/" + str(data['id']) + "." + extension

                get_media_url(imageFileName, media)

                # si le fichier json existe deja dans le dossier "processedData", on le supprime, si non on le déplace
                if not os.path.isfile(targetImageFileName):
                    os.rename(str(file), targetImageFileName)
                else:
                    os.remove(str(file))

                # required: arguments requis pour extraire un résultat (alpr ou tesseract)-> dataContent à push dans insight
                if not isinstance(required, str):
                    insight.postimg(imageFileName, str(data['id']), get_plates(required, imageFileName), endpoint, login, password)
                else:
                    insight.postimg(imageFileName, str(data['id']), get_text(imageFileName, required), endpoint, login, password)
    return targetImageFileName

def get_plates(alpr, strFileName):

    try:
        jpeg_bytes = open(str(strFileName), "rb").read()
        results = alpr.recognize_array(jpeg_bytes)

        print("Image size: %dx%d" % (results['img_width'], results['img_height']))
        print("Processing Time: %f" % results['processing_time_ms'])

        i = 0
        for plate in results['results']:
            i += 1
            print("Plate #%d" % i)
            print("   %12s %12s" % ("Plate", "Confidence"))
            for candidate in plate['candidates']:
                prefix = "-"
                if candidate['matches_template']:
                    prefix = "*"

                print("  %s %12s%12f" % (prefix, candidate['plate'], candidate['confidence']))
        return str(results['results'])

    except:
        print("File corrupted")
        return "File corrupted"

def get_text(image, preprocess):
    ### TESSERACT ###
    try:
        # load the example image and convert it to grayscale
        image = cv2.imread(image)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # check to see if we should apply thresholding to preprocess the
        # image
        if preprocess == "thresh":
            gray = cv2.threshold(gray, 0, 255,
                                 cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        # make a check to see if median blurring should be done to remove
        # noise
        elif preprocess == "blur":
            gray = cv2.medianBlur(gray, 3)

        # write the grayscale image to disk as a temporary file so we can
        # apply OCR to it
        filename = "{}.png".format(os.getpid())
        cv2.imwrite(filename, gray)


        # load the image as a PIL/Pillow image, apply OCR, and then delete
        # the temporary file
        pytesseract.pytesseract.tesseract_cmd = r'C:\Users\nicmir\AppData\Local\Tesseract-OCR\tesseract.exe'
        text = pytesseract.image_to_string(Image.open(filename))
        os.remove(filename)
        print(text)

        # show the output images
        #cv2.imshow("Image", image)
        #cv2.imshow("Output", gray)
        cv2.waitKey(0)

        ### End TESSERACT ###
        return text
    except:
        print("File corrupted")
        return "File corrupted"
