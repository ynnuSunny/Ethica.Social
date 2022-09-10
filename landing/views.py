import smtplib, random
from email import message
from typing import Collection
from django.shortcuts import redirect, render
from django.http import HttpResponse
from pymongo import MongoClient
import requests
import json


class DBConnect:
    __instance = None

    @staticmethod
    def getInstance():
        if DBConnect.__instance == None:
            DBConnect()
        return DBConnect.__instance

    def __init__(self):
        if DBConnect.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            cluster = MongoClient("mongodb+srv://root:1234@cluster1.8jmyghr.mongodb.net/?retryWrites=true&w=majority")
            db = cluster["ethica"]

            DBConnect.__instance = db


def sendMail(request, to_):
    email_addr = 'ethica.social@gmail.com'
    email_passwd = 'kdagmfctdgqyxifl'
    smtpserver = smtplib.SMTP("smtp.gmail.com", 587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo()
    smtpserver.login(email_addr, email_passwd)
    SUBJECT = "Password Recovery"
    otp = str(random.randint(1000, 9999))
    request.session['otp'] = otp
    TEXT = "your OTP is " + otp
    smtpserver.sendmail(from_addr=email_addr, to_addrs=to_, msg='Subject: {}\n\n{}'.format(SUBJECT, TEXT))


# backend of every page at landing

def changePassword(request):
    email = request.POST['email']
    password1 = request.POST['password1']
    password2 = request.POST['password2']
    if (len(password1) < 6):
        return render(request, 'html/changePassword.html', {"msg": "password length must be atleast 6"})
    if (password1 != password2):
        return render(request, 'html/changePassword.html', {"msg": "password doesn't match"})

    db = DBConnect.getInstance()
    collection = db["user"]
    usr = collection.find_one({"email": email})
    usr['password'] = password2

    collection.delete_one({"email": email})
    collection.insert_one(usr)
    request.session["nid"] = usr['nid']
    return redirect("/home")


def recoveryPassword(request):
    to_email = request.POST['email']
    givenotp = request.POST['otpGiven']
    actualOtp = request.session['otp']
    if (len(givenotp) == 0 or actualOtp != givenotp):
        return render(request, 'html/recoveryPassword.html', {"msg": "otp doesn't match"})

    return render(request, 'html/changePassword.html', {"email": to_email})


def getEmail(request):
    try:
        usrEmail = request.GET['usremail']
    except:
        return render(request, 'html/getEmail.html')
    db = DBConnect.getInstance()
    collection = db["user"]
    if (collection.count_documents({"email": usrEmail}) != 1):
        return render(request, 'html/getEmail.html', {"msg": "invalid email"})
    sendMail(request, usrEmail)
    return render(request, 'html/recoveryPassword.html', {"email": usrEmail})


def logIn(request):
    # if already logged in, send to homepage
    try:
        request.session['nid']
        return redirect("/home")
    except:
        return render(request, 'html/login.html', {"msg": None})


def createAccoutn(request):
    try:
        request.session['nid']
        return redirect("/home")
    except:
        message = {}
        message = {'msg': None}
        return render(request, 'html/createAccount.html', message)


def validateLogin(request):
    # came in the right way
    if (request.method == 'POST'):
        db = DBConnect.getInstance()
        collection = db["user"]
        email = request.POST["email"]
        password = request.POST["password"]

        # invalid try
        if (collection.count_documents({"email": email, "password": password}) != 1):
            message = {"msg": "invalid email or password"}
            return render(request, 'html/login.html', message)

        # valid user
        data = collection.find_one({"email": email, "password": password})
        nid = data["nid"]

        # save session
        request.session['nid'] = nid

        return redirect("/home")

    # came from somewere else
    return render(request, 'html/createAccount.html', message)


def createAccountDb(request):
    if (request.method == 'POST'):
        # database connection
        db = DBConnect.getInstance()
        collection = db["user"]

        # validating evrything
        hasError = False
        msg = None

        # name validation
        name = request.POST['name']
        if (len(name) < 2):
            hasError = True
            msg = "invalid name. must be atleast 2 character long"

        # nid validation
        nid = request.POST['nid']
        if (len(nid) < 5 or not (nid.isdigit())):
            hasError = True
            msg = "invalid nid. must be a digit and 5 character long"

        # nid already taken
        elif (collection.count_documents({"nid": nid}) != 0):
            hasError = True
            msg = "nid already in use"

        # password validation

        password = request.POST['password']
        if (len(password) < 6):
            hasError = True
            msg = "password too short"

        email = request.POST['email']

        # email validation
        if (collection.count_documents({"email": email}) != 0):
            hasError = True
            msg = "email alrady in use"

        # has some error
        if (hasError):
            message = {"msg": msg}
            return render(request, 'html/createAccount.html', message)

        # generating random data
        response_API = requests.get('https://randomuser.me/api/')

        data = response_API.text
        parse_json = json.loads(data)
        data = parse_json['results'][0]

        userInfo = {
            "name": name,
            "nid": nid,
            "email": email,
            "password": password,
            "gender": data['gender'],
            "location": data['location'],
            "dob": data['dob'],
            "phone_number": data['phone'],
            "bio": "",
            "balance": 0,
            "bloodGroup": None,
            "sellData": True,
            "maxUseLimit": 1e9,
            "maxPostView": 1e9,
            "todayUse": 0,
            "todayPostView": 0,
            "followers": [],
            "followings": [],
            "activityLog": [],
            "notification": [],
            "reactions": [],
            "interest": [],
            "dp": "nodp.jpg",

        }
        request.session['nid'] = nid
        # save data to cloud
        collection.insert_one(userInfo)

        return redirect("/home");

    # came from somewere else
    return render(request, 'html/createAccount.html', message)
