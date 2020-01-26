import face_recognition
from PIL import Image
# import face_recognition
known_image = face_recognition.load_image_file("pragati.jpg")
unknown_image = face_recognition.load_image_file("a.jpg")
face_locations = face_recognition.face_locations(unknown_image, number_of_times_to_upsample=0, model="cnn")
# print("I found {} face(s) in this photograph.".format(len(face_locations)))
for i in range(0,len(face_locations)-1):
        biden_encoding = face_recognition.face_encodings(known_image)[0]
        # print(biden_encoding)

        unknown_encoding = face_recognition.face_encodings(unknown_image)[i]
        # print(unknown_encoding)
        results = face_recognition.compare_faces([biden_encoding], unknown_encoding)
        print(results)
        if(results[0]==True):
            # print(known_image)
            # top, right, bottom, left = face_locations
            # face_image = known_image[top:bottom, left:right]
            pil_image = Image.fromarray(known_image)
            pil_image.show()
            # break

