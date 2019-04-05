import subprocess
import sys
import os
import urllib.request
import json
import re
import shutil

name = sys.argv[1]

def download_img_from_metadata(user):

    #json_path = "logs/{}.json".format(name)


    with open('download/Moundir.json') as json_file:
        data = json.load(json_file)
        for p in data :
            print(p['image_description'])

    # output_directory = "google/rawdatas/" + name
    #
    # if not os.path.exists(output_directory):
    #
    #     os.makedirs(output_directory)

    # with open("{}.json".format(name), "r") as json_file:
    #     data = json.load(json_file)
    #     index = 0
    #     for img_data in data:
    #         index += 1
    #         img_filename = re.sub('[^a-zA-Z]+', '', img_data['image_description'])
    #         img_filename = str(index) + "-" + img_filename + ".jpg"
    #         try:
    #             get_image_and_add_metadata(img_data['image_link'], output_directory, img_filename)
    #         except:
    #             try:
    #                 get_image_and_add_metadata(img_data['image_thumbnail_url'], output_directory, img_filename)
    #             except:
    #                 pass


def get_image_and_add_metadata(source, output_directory, img_filename):
    urllib.request.urlretrieve(source, output_directory + "/" + img_filename)

subprocess.call(["googleimagesdownload", "-l 5", "-k {}".format(name), "-e", "-nd"])


download_img_from_metadata(name)
