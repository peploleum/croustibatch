# -*- coding: UTF-8 -*-

import json
import os.path
from pprint import pprint

import requests
# pip install requests

import base64
import insight

def postimg(imagefilename, dataid, results, endpoint, login, password):


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
                    "rawDataContent": str(results['results']),
                    "rawDataDataContentType": "image/jpeg",
                    "rawDataData": str(decode)
                }

                basic_get_response = session.post(url=url, json=rawData, headers=headersRawData)

                if basic_get_response.ok:
                    # j_data = json.loads(basic_get_response.content)
                    # print("The response contains {0} properties".format(len(str(j_data))))
                    print("\n")
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
    print("getting media url")
    with open(str(imageFileName), 'wb') as handle:
        response = requests.get(media['media_url'], stream=True)

        if not response.ok:
            print(response)

        for block in response.iter_content(1024):
            if not block:
                break

            handle.write(block)


def extract_data(crawlDir, file, targetDirectory, alpr, endpoint, login, password):
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
        for media in data['entities']['media']:
            pprint(media['media_url'])
            if not media['media_url']:
                pprint("There is no media")
            else:
                extension = media['media_url'].rsplit('.', 1)[1]
                imageFileName = targetDirectory + "/" + str(data['id']) + "." + extension

                get_media_url(imageFileName, media)

                if not os.path.isfile(targetImageFileName):
                    os.rename(str(file), targetImageFileName)

                insight.postimg(imageFileName, str(data['id']), get_plates(alpr, imageFileName), endpoint, login, password)
    return targetImageFileName

def get_plates(alpr, strFileName):
    jpeg_bytes = open(str(strFileName), "rb").read()
    results = alpr.recognize_array(jpeg_bytes)
    return results
