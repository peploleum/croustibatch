# -*- coding: UTF-8 -*-

import json

import requests

try:
    accountUrl = "http://localhost:8080/api/account"
    authenticationUrl = "http://localhost:8080/api/authentication"
    url = "http://localhost:8080/api/raw-data/5c48cf9969f04e27882e32a7"
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
                'X-XSRF-TOKEN': token
            }
            authResponse = session.post(url=authenticationUrl, data=payload, verify=True, headers=headers)
            if authResponse.ok:
                print("Authenticated")
                basicGetResponse = session.get(url=url)
                if basicGetResponse.ok:
                    jData = json.loads(basicGetResponse.content)
                    print("The response contains {0} properties".format(len(jData)))
                    print("\n")
                    for key in jData:
                        print(key + " : " + jData[key])
                else:
                    # If response code is not ok (200), print the resulting http error code with description
                    basicGetResponse.raise_for_status()
            else:
                print("Auth failed")
        else:
            # For successful API call, response code will be 200 (OK)
            if myResponse.ok:
                jData = json.loads(myResponse.content)
                print("The response contains {0} properties".format(len(jData)))
                print("\n")
                for key in jData:
                    print(key + " : " + jData[key])
            else:
                # If response code is not ok (200), print the resulting http error code with description
                myResponse.raise_for_status()
finally:
    print(" Out ")
    exit(0)
