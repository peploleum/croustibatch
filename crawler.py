# -*- coding: UTF-8 -*-
import json
import os.path
import pathlib
from pprint import pprint

import requests
# pip install requests
from openalpr import Alpr
import base64


def postimg(imagefilename, dataid, datadata):
    jpeg_bytes = open(imagefilename, "rb").read()
    results = alpr.recognize_array(jpeg_bytes)

    # Uncomment to see the full results structure
    # import pprint
    # pprint.pprint(results)

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

    # r = requests.post("http://localhost:8091", data={'rawDataName': str(data['id']), 'rawDataType': 'image', 'rawDataContent': results['results'][0], 'rawDataData': block })
    # print(r.status_code, r.reason)

    accountUrl = "http://localhost:8080/api/account"
    authenticationUrl = "http://localhost:8080/api/authentication"
    # url = "http://localhost:8080/api/raw-data/5c48cf9969f04e27882e32a7"
    url = "http://localhost:8080/api/raw-data"
    payload = {
        'j_username': 'admin',
        'j_password': 'admin',
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
                with open(imageFileName, "rb") as image:
                    f = image.read()
                    b = bytearray(f)
                    decode = base64.b64encode(b).decode('UTF-8')

                # utf8_str = b.decode('utf-8')
                # dataBytes = json.dumps(b)
                # base64EncodedStr = ""
                # base64EncodedStr = str(base64.b64encode(b))
                #
                # print(base64EncodedStr)
                # type(base64EncodedStr)
                #
                # print('DBL1', b)

                # print('decoded', base64.b64decode(base64EncodedStr))

                # print('caca', json.dumps(base64EncodedStr.decode("utf-8")))
                # type(json.dumps(base64EncodedStr.decode("utf-8")))
                rawData = {
                    "rawDataName": dataid,
                    "rawDataType": "image",
                    "rawDataContent": str(results['results']),
                    "rawDataDataContentType": "image/jpeg",
                    "rawDataData": decode
                }

                basic_get_response = session.post(url=url, json=rawData, headers=headersRawData)
                if basic_get_response.ok:
                    j_data = json.loads(basic_get_response.content)
                    print("The response contains {0} properties".format(len(j_data)))
                    print("\n")
                    for key in j_data:
                        print(key + " : " + j_data[key])
                else:
                    # If response code is not ok (200), print the resulting http error code with description
                    basic_get_response.raise_for_status()
            else:
                print("Auth failed")
        else:
            # For successful API call, response code will be 200 (OK)
            if myResponse.ok:
                j_data = json.loads(myResponse.content)
                print("The response contains {0} properties".format(len(j_data)))
                print("\n")
                for key in j_data:
                    print(key + " : " + j_data[key])
            else:
                # If response code is not ok (200), print the resulting http error code with description
                myResponse.raise_for_status()


try:
    alpr = None
    print('croustibatch')
    alpr = Alpr("us", "conf/openalpr.conf", "runtime_data")

    if not alpr.is_loaded():
        print("Error loading OpenALPR")
    else:
        print("Using OpenALPR " + alpr.get_version())

        alpr.set_top_n(7)
        alpr.set_default_region("wa")
        alpr.set_detect_region(False)

        sourceDirectory = "source"
        targetDirectory = "download"
        if not os.path.exists(targetDirectory):
            os.makedirs(targetDirectory)
        cwd = os.getcwd()
        crawlDir = cwd + "/" + sourceDirectory
        jsonFiles = pathlib.Path(crawlDir).glob("*.json")
        for file in jsonFiles:
            print(file)
            with open(file) as f:
                data = json.load(f)
            imageFileName = targetDirectory + "/" + str(data['id']) + ".jpg"
            for media in data['entities']['media']:
                pprint(media['media_url'])
                with open(imageFileName, 'wb') as handle:
                    response = requests.get(media['media_url'], stream=True)

                    if not response.ok:
                        print(response)

                    for block in response.iter_content(1024):
                        if not block:
                            break

                        handle.write(block)

                # os.system("main.py --config conf/openalpr.conf --runtime_data runtime_data " + targetDirectory+"/"+imageFileName)
                # ------ plate treatment -------
                postimg(imageFileName, str(data['id']), handle)

except Exception as e:
    print(e)

finally:
    print(" Out ")
    exit(0)
