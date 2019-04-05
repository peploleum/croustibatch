import face_recognition
import glob, os

try:
    # Load the jpg files into numpy arrays
    chuck_image = face_recognition.load_image_file("face_recognition_source/trump.jpg")
    obama_image = face_recognition.load_image_file("face_recognition_source/obama.jpg")
    unknown_image = face_recognition.load_image_file("face_recognition_source/obama2.jpg")

    list_of_unknown_image = []
    list_of_unknown_face_encoding = []

    chuck_face_encoding = face_recognition.face_encodings(chuck_image)[0]
    obama_face_encoding = face_recognition.face_encodings(obama_image)[0]
    unknown_face_encoding = face_recognition.face_encodings(unknown_image)[0]

    known_faces = [
        obama_face_encoding
    ]

    os.chdir("face_recognition_source/president")
    for file in glob.glob("*.jpg"):
        print(file)
        #list_of_unknown_face_encoding.append(face_recognition.face_encodings(face_recognition.load_image_file(file))[0])
        # results is an array of True/False telling if the unknown face matched anyone in the known_faces array
        results = face_recognition.compare_faces(known_faces, face_recognition.face_encodings(face_recognition.load_image_file(file))[0])

        print("Is the unknown face a picture of Obama? {}".format(results[0]))
        #print("Is the unknown face a picture of Obama? {}".format(results[1]))
        print("Is the unknown face a new person that we've never seen before? {}".format(not True in results))

# Get the face encodings for each face in each image file
# Since there could be more than one face in each image, it returns a list of encodings.
# But since I know each image only has one face, I only care about the first encoding in each image, so I grab index 0.


except IndexError:
    print("I wasn't able to locate any faces in at least one of the images. Check the image files. Aborting...")
    quit()



