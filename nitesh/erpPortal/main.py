from flask import Flask, render_template,request,session
from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import *
from flask_mail import Mail,Message
import pymysql.cursors,random
import base64,datetime
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random

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
    a='/root/Desktop/tyrant/m/face_detection_cli.py'
    exec(open(a).read())
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
app.run(debug=True)
