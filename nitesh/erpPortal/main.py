from flask import Flask, render_template,request,session
from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import *
from flask_mail import Mail,Message
import pymysql.cursors,random
import base64,datetime
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random
import runpy
import os

app=Flask(__name__)

connection = pymysql.connect(host='192.168.43.127',
                             user='root',
                             password='Niteshgarg@1312',
                             db='erpportal',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

mycursor = connection.cursor()

app.config.update(
    DEBUG=True,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='',
    MAIL_PASSWORD=''
)
mail=Mail(app)

@app.route("/")
def index():
        # -*- coding: utf-8 -*-
    # from __future__ import print_function
    return render_template("index.html")



def encrypt(key, source, encode=True):
    key = SHA256.new(key).digest()  # use SHA-256 over our key to get a proper-sized AES key
    IV = Random.new().read(AES.block_size)  # generate IV
    encryptor = AES.new(key, AES.MODE_CBC, IV)
    padding = AES.block_size - len(source) % AES.block_size  # calculate needed padding
    source += bytes([padding]) * padding  # Python 2.x: source += chr(padding) * padding
    data = IV + encryptor.encrypt(source)  # store the IV at the beginning and encrypt
    return base64.b64encode(data).decode("latin-1") if encode else data


def decrypt(key, source, decode=True):
    if decode:
        source = base64.b64decode(source.encode("latin-1"))
    key = SHA256.new(key).digest()  # use SHA-256 over our key to get a proper-sized AES key
    IV = source[:AES.block_size]  # extract the IV from the beginning
    decryptor = AES.new(key, AES.MODE_CBC, IV)
    data = decryptor.decrypt(source[AES.block_size:])  # decrypt
    padding = data[-1]  # pick the padding value from the end; Python 2.x: ord(data[-1])
    if data[-padding:] != bytes([padding]) * padding:  # Python 2.x: chr(padding) * padding
        raise ValueError("Invalid padding...")
    return data[:-padding]  # remove the padding

@app.route("/login", methods=['POST'])
def login():
    emailId=request.form.get("emailId")
    password=request.form.get("password")
    try:
        my_password = b"secret_AES_key_string_to_encrypt/decrypt_with"
        password = password.encode('utf-8')
        mycursor.callproc('sp_login', ('login', 'null', emailId))
        data = mycursor.fetchone()
        print(data)
        if(data!=None):
            decrypted = decrypt(my_password, data['Password'])
            print("dec:  {}".format(decrypted))
            print(password)
            s=("{}".format(password == decrypted))
            print(s)
            if(s=="True"):
                return render_template("afterLogin.html",id=data['Pk_User_Id'])
            else:
                return render_template("index.html",msg="Wrong Password!!!")
        else:
            return render_template("index.html",msg1="User Not Exist!!!")

    except Exception as e:
        print(e)

@app.route("/viewForget")
def viewForget():
    return render_template("forgetPassword.html")

@app.route("/checkEmail",methods=['POST'])
def checkEmail():
    emailId=request.form.get("emailid")
    try:
        mycursor.callproc('sp_login', ('login', 'null', emailId))
        data = mycursor.fetchone()
        if(data!=None):
            return render_template("otp.html")
        else:
            return render_template("forgetPassword.html",msg="Email Not Exist!!!")

    except Exception as e:
        print(e)

@app.route("/attendancePage",methods=['POST'])
def attendancePage():
    id=request.form.get("id")
    timeTable={
        "Monday":[],
        "Tuesday":[],
        "Wednesday":[],
        "Thrusday":[],
        "Friday":[],
        "Saturaday":[]
    }

    try:
        mycursor.callproc('sp_login', ('getTimetable', 'null', id))
        data = mycursor.fetchall()
        if(data!=None):
            print(data)
            for i in data:
                if(i['Day']=='Monday'):
                    s=i['Start_Time']+"-"+i['End_Time']
                    i.update(TIming=s)
                    timeTable['Monday'].append(i)
                if (i['Day'] == 'Tuesday'):
                    s=i['Start_Time']+"-"+i['End_Time']
                    i.update(TIming=s)
                    timeTable['Tuesday'].append(i)
                if (i['Day'] == 'Wednesday'):
                    s = i['Start_Time'] + "-" + i['End_Time']
                    i.update(TIming=s)
                    timeTable['Wednesday'].append(i)
                if (i['Day'] == 'Thrusday'):
                    s = i['Start_Time'] + "-" + i['End_Time']
                    i.update(TIming=s)
                    timeTable['Thrusday'].append(i)
                if (i['Day'] == 'Friday'):
                    s = i['Start_Time'] + "-" + i['End_Time']
                    i.update(TIming=s)
                    timeTable['Friday'].append(i)
                if (i['Day'] == 'Saturaday'):
                    s = i['Start_Time'] + "-" + i['End_Time']
                    i.update(TIming=s)
                    timeTable['Saturaday'].append(i)
            print(timeTable)
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M:%S")
            print("Current Time =", current_time)
            return render_template("attendance.html",data=timeTable,current_time=current_time)
        else:
            return render_template("forgetPassword.html",msg="Email Not Exist!!!")

    except Exception as e:
        print(e)
    return render_template("attendance.html")

@app.route("/markTheAttendance",methods=['POST'])
def markTheAttendance():
    import click
    import os
    import re
    import face_recognition.api as face_recognition
    import multiprocessing
    import itertools
    import sys
    import PIL.Image
    import numpy as np
    # print('Hello World')

    global_name_list=[]
    def scan_known_people(known_people_folder):
        known_names = []
        known_face_encodings = []

        for file in image_files_in_folder(known_people_folder):
            basename = os.path.splitext(os.path.basename(file))[0]
            img = face_recognition.load_image_file(file)
            encodings = face_recognition.face_encodings(img)

            if len(encodings) > 1:
                click.echo("WARNING: More than one face found in {}. Only considering the first face.".format(file))

            if len(encodings) == 0:
                click.echo("WARNING: No faces found in {}. Ignoring file.".format(file))
            else:
                known_names.append(basename)
                known_face_encodings.append(encodings[0])

        return known_names, known_face_encodings


    def print_result(filename, name, distance, show_distance=False):
        if show_distance:
            print("{},{},{}".format(filename, name, distance))
        
        else:
            # print("{},{}".format(filename, name))
            print(name)
            if name!='unknown_person':
                global_name_list.append(name)


    def test_image(image_to_check, known_names, known_face_encodings, tolerance=0.6, show_distance=False):
        unknown_image = face_recognition.load_image_file(image_to_check)

        # Scale down image if it's giant so things run a little faster
        if max(unknown_image.shape) > 1600:
            pil_img = PIL.Image.fromarray(unknown_image)
            pil_img.thumbnail((1600, 1600), PIL.Image.LANCZOS)
            unknown_image = np.array(pil_img)

        unknown_encodings = face_recognition.face_encodings(unknown_image)

        for unknown_encoding in unknown_encodings:
            distances = face_recognition.face_distance(known_face_encodings, unknown_encoding)
            result = list(distances <= tolerance)

            if True in result:
                [print_result(image_to_check, name, distance, show_distance) for is_match, name, distance in zip(result, known_names, distances) if is_match]
            else:
                print_result(image_to_check, "unknown_person", None, show_distance)

        if not unknown_encodings:
            # print out fact that no faces were found in image
            print_result(image_to_check, "no_persons_found", None, show_distance)


    def image_files_in_folder(folder):
        return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]


    def process_images_in_process_pool(images_to_check, known_names, known_face_encodings, number_of_cpus, tolerance, show_distance):
        if number_of_cpus == -1:
            processes = None
        else:
            processes = number_of_cpus

        # macOS will crash due to a bug in libdispatch if you don't use 'forkserver'
        context = multiprocessing
        if "forkserver" in multiprocessing.get_all_start_methods():
            context = multiprocessing.get_context("forkserver")

        pool = context.Pool(processes=processes)

        function_parameters = zip(
            images_to_check,
            itertools.repeat(known_names),
            itertools.repeat(known_face_encodings),
            itertools.repeat(tolerance),
            itertools.repeat(show_distance)
        )

        pool.starmap(test_image, function_parameters)

    # known_people_folder='/root/Desktop/tyrant/known'
    # # image_to_check='/root/Desktop/tyrant/a.jpg'
    # @click.command()
    # # @click.argument('known_people_folder')
    # # @click.argument('image_to_check')
    # @click.option('--cpus', default=1, help='number of CPU cores to use in parallel (can speed up processing lots of images). -1 means "use all in system"')
    # @click.option('--tolerance', default=0.6, help='Tolerance for face comparisons. Default is 0.6. Lower this if you get multiple matches for the same person.')
    # @click.option('--show-distance', default=False, type=bool, help='Output face distance. Useful for tweaking tolerance setting.')
    def main():
        # print("hello")
        cpus=1
        tolerance=0.5
        show_distance=False
        known_people_folder='/root/Desktop/tyrant/known'
        image_to_check='/root/Desktop/tyrant/a.jpg'
        known_names, known_face_encodings = scan_known_people(known_people_folder)
        # print("hello1")
        # Multi-core processing only supported on Python 3.4 or greater
        if (sys.version_info < (3, 4)) and cpus != 1:
            click.echo("WARNING: Multi-processing support requires Python 3.4 or greater. Falling back to single-threaded processing!")
            cpus = 1

        if os.path.isdir(image_to_check):
            if cpus == 1:
                [test_image(image_file, known_names, known_face_encodings, tolerance, show_distance) for image_file in image_files_in_folder(image_to_check)]
            else:
                process_images_in_process_pool(image_files_in_folder(image_to_check), known_names, known_face_encodings, cpus, tolerance, show_distance)
        else:
            test_image(image_to_check, known_names, known_face_encodings, tolerance, show_distance)

        
        try:
            for i in global_name_list:
                mycursor.callproc('sp_login', ('markAttendance',i,'null'))
            connection.commit()    

        except Exception as e:
            print(e)


    main()
    return render_template('click.html',msg=global_name_list)
    
app.run(debug=True)
