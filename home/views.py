import json
from glob import glob
import profile
import datetime
from tkinter.messagebox import NO
from tokenize import Comment
from unittest import result
from django.shortcuts import render
from email import message
from django.shortcuts import render,redirect,HttpResponseRedirect,reverse
from django.http import JsonResponse
from django.http import HttpResponse
from pymongo import MongoClient
import requests
import gridfs
from sympy import content
from bson.objectid import ObjectId
from googletrans import Translator


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


class igmDBConnect:
   __instance = None
   @staticmethod 
   def getInstance():
      if igmDBConnect.__instance == None:
        igmDBConnect()
      return igmDBConnect.__instance
   def __init__(self):
      if igmDBConnect.__instance != None:
        raise Exception("This class is a singleton!")
      else:
        cluster = MongoClient("mongodb+srv://root:1234@cluster1.8jmyghr.mongodb.net/?retryWrites=true&w=majority")
        db = cluster["ethicaPhotos"]

        igmDBConnect.__instance = db

def addActivity(nid,activity):
    db=DBConnect.getInstance()
    collection=db["user"]
    if(len(activity)==0):
        return

    usr=collection.find_one({"nid":nid})
    usr['activityLog'].append(activity)

    collection.delete_one({"nid":nid})
    collection.insert_one(usr)


def addNotification(nid,notification):
    db=DBConnect.getInstance()
    collection=db["user"]
    if(len(notification)==0):
        return

    usr=collection.find_one({"nid":nid})
    usr['notification'].append(notification)

    collection.delete_one({"nid":nid})
    collection.insert_one(usr)


def rechargeFunc(nid,tk):
    db=DBConnect.getInstance()
    collection=db["user"]
    usr=collection.find_one({"nid":nid})
    usr['balance']+=tk
    collection.delete_one({"nid":nid})
    collection.insert_one(usr)
    
    


def translate_(text,dest_='bn'):
    translator = Translator()
    out= translator.translate(text,dest=dest_)
    return out.text


def getUsr(nid):
    db=DBConnect.getInstance()
    collection=db["user"]
    usr=collection.find_one({"nid":nid})
    return usr

def uploadPhoto(photo):
    cluster = MongoClient("mongodb+srv://root:1234@cluster1.8jmyghr.mongodb.net/?retryWrites=true&w=majority")
    db = cluster["ethicaPhotos"]
    fs=gridfs.GridFS(db)
    fs.put(photo,filename="1.jpg")

def getImg(nid):
    #db connection 
    db=DBConnect.getInstance()
    collection=db["user"]

    data=collection.find_one({"nid":nid})
    imgName=data['dp']

    # image db collection
    db=igmDBConnect.getInstance()
    fs=gridfs.GridFS(db)
    data=db.fs.files.find_one({"filename":imgName})
    id_=data['_id']
    outputdata=fs.get(id_).read()
    output=open(imgName,"wb")
    output.write(outputdata)
    output.close()

    return imgName

def getAllComment(post):
    allComment=[]
    db=DBConnect.getInstance()
    collection=db["user"]
    for i in post['comment']:
        commenterNid=i[0]
        commenter=collection.find_one({"nid":commenterNid})
        commenterName=commenter['name']
        allComment.append({
            "commenterName":commenterName,
            "commenterNid":commenterNid,
            "comment":i[1]})
    return allComment

def notification(request):
    nid=request.session['nid']

    db=DBConnect.getInstance()
    collection=db["user"]

    usr=collection.find_one({"nid":nid})
    activity={
        "usrActivity":usr['notification']
        }
    return render(request, 'html/activityLog.html',activity)
    


def activityLog(request):
    nid=request.session['nid']

    db=DBConnect.getInstance()
    collection=db["user"]

    usr=collection.find_one({"nid":nid})
    activity={
        "usrActivity":usr['activityLog']
        }
    
    return render(request, 'html/activityLog.html',activity)

def newsFeed(request):
    nid=request.session['nid']
    return render(request, 'html/newsFeed.html')

def settings(request):
    return render(request, 'html/settings.html')

def logout(request):
    del request.session['nid']
    return redirect("/login")

def addComment(request):
    content=request.POST["comment"]
    postid=request.POST["postid"]
    commenter=request.session['nid']
    if(len(content)==0):
        return redirect("profile")
    
    
    db=DBConnect.getInstance()
    collection=db["post"]
    postData=collection.find_one({"_id":ObjectId(postid)})
    allComments=postData["comment"]
    allComments.append([commenter, content])
    postData["comment"]=allComments
    collection.delete_one({"_id":ObjectId(postid)})
    collection.insert_one(postData)
    addActivity(commenter,"made a comment \""+content+"\" on your post at "+str(datetime.datetime.now()))
    return redirect(request.META.get('HTTP_REFERER'))
    

def seeTranslated(request):
    nid=request.session['nid']
    postId=request.GET['postId']
    db=DBConnect.getInstance()
    collection=db["post"]
    i=collection.find_one({"_id":ObjectId(postId)})
    comments=getAllComment(i)
    
    postShow={
            "translatedContent":translate_(i["content"]),
            "postNo":i["_id"],
            "content": i['content'],
            "likes":len(i["reaction"]["like"]),
            "comment":comments,
            "viewers":i["audience"],
            "type":i["type"],
            "date":i['date'],
        }
    
    return render(request, 'html/seeTranslatedPost.html',postShow)
    


def profilePage(request):
    nid=request.session['nid']
    db=DBConnect.getInstance()
    collection=db["user"]
    usr=collection.find_one({"nid":nid})
    dp=getImg(nid)
    userInfo={
        "dp":dp,
        "name":usr["name"],
        "bio":usr['bio']
    }
    
    collection=db["post"]
    posts=collection.find({"nid":nid})
    allPosts=[]
    for i in posts:
        comments=getAllComment(i)
        postShow={
            "postNo":i["_id"],
            "content": i['content'],
            "likes":len(i["reaction"]["like"]),
            "comment":comments,
            "viewers":i["audience"],
            "type":i["type"],
            "date":i['date'],
        }
        
        allPosts.append(postShow)
        
    
    userInfo["posts"]=allPosts
    

    return render(request, 'html/profile.html',userInfo)

def createPost(request):
    return render(request, 'html/createPost.html')

def makeOtherComment(request):
    ownerOfPost=request.GET['nid']
    commenter=request.GET['commenter']
    postid=request.GET['postid']
    comment=request.GET['comment']
    if(len(comment)==0):
        redirect(request.META.get('HTTP_REFERER'))
    
    db=DBConnect.getInstance()
    collection=db["post"]
    postData=collection.find_one({"_id":ObjectId(postid)})
    allComments=postData["comment"]
    allComments.append([commenter,comment])
    postData["comment"]=allComments
    collection.delete_one({"_id":ObjectId(postid)})
    collection.insert_one(postData)
    own=getUsr(postData['nid'])
    print(own)
    addActivity(commenter, "made a comment \""+comment+"\" on "+own['name']+"'s post at "+str(datetime.datetime.now()))

    return redirect(request.META.get('HTTP_REFERER'))

def buyData(request):
    db=DBConnect.getInstance()
    collection=db["user"]
    instances=collection.count_documents({})
    metaData={
        "maxData":instances
    }
    global noAmountToBuyData
    if(noAmountToBuyData):
        noAmountToBuyData=False
        metaData["msg"]= "not enough amount to buy data. please recharge"
    return render(request,"html/buyData.html",metaData)


def buyDataHandle(request):
    buyerNid=request.session['nid']
    global noAmountToBuyData

    perDataPrice=10
    usrData=[]
    
    maxUsrLimit=int(request.GET['maxUsr'])
    ageLimit=int(request.GET['age'])
    gender=request.GET['gender']
    location=request.GET["location"]



    db=DBConnect.getInstance()
    collection=db["user"]
    
    buyer=collection.find_one({"nid":buyerNid})

    if(buyer['balance']<perDataPrice*maxUsrLimit):
        noAmountToBuyData=True
        return redirect(buyData)
    

    usrs=collection.find({})



    
    collection=db["post"]
    for usr in usrs:
        if(len(usrData)==maxUsrLimit):
            break

        if(usr["nid"]==buyerNid):
            pass
        if(not usr['sellData']):
            pass
        if(usr['dob']["age"]>ageLimit):
            pass
        if(gender!="any" and gender!=usr['gender']):
            pass

        if(location!="any" and len(location)!=0 and (usr['location']['city'] != location or usr['location']['country'] != location  ) ):
            pass

        posts=collection.find({"nid":usr['nid']})
        allPosts=[]
        for i in posts:
            comments=getAllComment(i)
            i["comment"]=comments    
            del i['_id']  
            del i['date']  
            allPosts.append(i)


        addNotification(usr["nid"],"your data has been sold. you recieved tk "+ str(perDataPrice//2))
        rechargeFunc(usr["nid"],perDataPrice//2)

        usr['posts']=allPosts
        del usr["nid"]
        del usr['email']
        del usr['password']
        del usr['_id']
        del usr['dob']['date']
        del usr['phone_number']

        usrData.append(usr)


    rechargeFunc(buyer["nid"],-1*perDataPrice*len(usrData))
    addActivity(buyer["nid"],"you bought data of amount tk"+ str(perDataPrice*len(usrData)))
    return HttpResponse(json.dumps(usrData), content_type="application/force-download")





def changeBasicInfo(request):
    nid=request.session['nid']
    db=DBConnect.getInstance()
    collection=db["user"]
    usr=collection.find_one({"nid":nid})
    newName=request.GET['name']
    if(len(newName)>=6):
        usr['name']=newName
    
    newCity=request.GET['city']
    if(len(newCity)>4):
        usr['location']['city']=newCity

    newCountry=request.GET['country']
    if(len(newCountry)>4):
        usr['location']['country']=newCountry
    
    newBio=request.GET['bio']

    
    usr['email']=request.GET['email']
    usr['bloodGroup'] = request.GET['bloodGroup']
    usr['bio']=newBio
    collection.delete_one({"nid":nid})
    collection.insert_one(usr)
    
    return redirect("profile")
    


def showBasicInfo(request):
    nid=request.session['nid']
    db=DBConnect.getInstance()
    collection=db["user"]
    usr=collection.find_one({"nid":nid})
    usrData={
    "balance":usr['balance'],
    "name":usr['name'],
    "gender":usr['gender'],
    "age":usr["dob"]['age'],
    "city":usr['location']['city'],
    "country":usr['location']['country'],
    "email":usr['email'],
    "bloodGroup":usr['bloodGroup'],
    "bio":usr["bio"],
    }

    return render(request, 'html/showBasicInfo.html',usrData)

def recharge(request):
    nid=request.session['nid']
    
    db=DBConnect.getInstance()
    collection=db["user"]
    usr=collection.find_one({"nid":nid})
    
    amount=request.GET['rechargeAmount']
    usr['balance']+=int(amount)
    
    collection.delete_one({"nid":nid})
    collection.insert_one(usr)
    addActivity(nid,"recharged tk "+ str(amount) +" at "+ str(datetime.datetime.now()))
    return redirect(request.META.get('HTTP_REFERER'))

def createPostHandle(request):
    #came from unknown source
    if(request.method!='POST'):
        return redirect("createPost")


    photo=None
    try:
        photo=request.POST['img']
    except:
        pass
    
    react=None
    try:
        react=request.POST['hideReaction']
    except:
        pass
    price=0
    try:
        price=int(request.POST['price'])
        if(price<0):
            price=0
    except:
        pass
    
    
    
    postContent=request.POST['postcontent']
    
    #empty post
    if(len(postContent)==0):
        return render(request, 'html/createPost.html',{"msg":"post cannot be empty"})
    

    

    
    tags=request.POST['tags'].split(" ")
    audience=request.POST["audience"]
    
    post={
        "nid":request.session['nid'],
        "content":postContent,
        "photo":None,
        "reaction":{
            "like":[],
        },
        "comment":[],
        "audience":audience,
        "type":"regular",
        "price":price,
        "tags":tags,
        "date":datetime.datetime.now(),
    }
    db=DBConnect.getInstance()
    collection=db["post"]
    collection.insert_one(post)
      

    return redirect(profilePage)


def followAction(request):
    isFollowing=request.GET['isFollowing']=="True"
    ownernid=request.GET['nid']
    viewernid=request.GET['viewerNid']

    db=DBConnect.getInstance()
    collection=db["user"]
    usr=collection.find_one({"nid":viewernid})
    usr2=collection.find_one({"nid":ownernid})
    

    
    if(isFollowing):
        usr['followings'].remove(ownernid)
        usr2['followers'].remove(viewernid)
        addActivity(viewernid,"unfollowed "+usr2['name']+" at "+ str(datetime.datetime.now()))
        
    else:
        usr["followings"].append(ownernid)
        usr2['followers'].append(viewernid)
        addActivity(viewernid,"started following "+usr2['name']+" at "+ str(datetime.datetime.now()))
    
    collection.delete_one({"nid":viewernid})
    collection.insert_one(usr)

    collection.delete_one({"nid":ownernid})
    collection.insert_one(usr2)
    page=request.META.get('HTTP_REFERER')
    url="othersProfile/?nid="+ownernid
    
    return redirect(request.META.get('HTTP_REFERER'))

    

        


def followers(request):
    nid=request.session['nid']
    db=DBConnect.getInstance()
    collection=db["user"]
    usr=collection.find_one({"nid":nid})

    followerShow=[]
    for i in usr['followers']:
        follower=collection.find_one({"nid":i})
        followerShow.append(
            {
            "nid":i,
            "name":follower['name'],
            "city":follower['location']['city'],
            "country":follower['location']['country']
            }
            )

    followersInfo={
        "allFollowers":followerShow,
    }
    return render(request, 'html/followers.html',followersInfo)

def followings(request):
    nid=request.session['nid']
    db=DBConnect.getInstance()
    collection=db["user"]
    usr=collection.find_one({"nid":nid})

    followerShow=[]
    for i in usr['followings']:
        follower=collection.find_one({"nid":i})
        followerShow.append(
            {
            "nid":i,
            "name":follower['name'],
            "city":follower['location']['city'],
            "country":follower['location']['country']
            }
            )

    followersInfo={
        "allFollowers":followerShow,
    }
    return render(request, 'html/followingList.html',followersInfo)

def othersProfile(request,nid=None):
    if(nid is None):
        nid=request.GET["nid"]
    
    mynid=request.session['nid']
    if(mynid==nid):
        return redirect("profile")

    # USER
    db=DBConnect.getInstance()
    collection=db["user"]
    usr=collection.find_one({"nid":nid})
    me=collection.find_one({"nid":mynid})
    #posts
    collection=db["post"]
    posts=collection.find({"nid":nid})

    allPosts=[]
    for i in posts:
        if(i["audience"]=="onlyme"):
            continue
        comments=getAllComment(i)
        postShow={
            "postNo":i["_id"],
            "content": i['content'],
            "likes":len(i["reaction"]["like"]),
            "comment":comments,
            "viewers":i["audience"],
            "type":i["type"],
            "date":i['date'],
        }
        
        allPosts.append(postShow)
    
    isFollowing=nid in me['followings']
    followBtn="follow"
    if(isFollowing):
        followBtn="unfollow"
    
    userInfo={
        "name":usr["name"],
        "bio":usr['bio'],
        "nid":nid,
        "seeingNid":mynid,
        "gender": usr["gender"],
        "isFollowing":isFollowing,
        "posts": allPosts,
        "age":usr['dob']['age'],
        "city":usr['location']['city'],
        "country":usr['location']['country'],
        "followBtn":followBtn,
        "isFollowing":isFollowing,
    }
    global noAmountToDonate
    if(noAmountToDonate):
        userInfo['msg']='not enough amount to donate'
        noAmountToDonate=False
    

    return render(request, 'html/othersProfile.html',userInfo)

def tip(request):
    donater=request.GET['viewer']
    reciever=request.GET['reciever']
    amountTk=int(request.GET['tipamount'])
    global noAmountToDonate

    db=DBConnect.getInstance()
    collection=db["user"]
    donaterAc=collection.find_one({"nid":donater})
    if(donaterAc['balance']<=amountTk):
        noAmountToDonate=True
        return redirect(othersProfile,nid=reciever)
    
    donaterAc['balance']-=amountTk+1
    collection.delete_one({"nid":donater})
    collection.insert_one(donaterAc)
    
    recieverAc=collection.find_one({"nid":reciever})
    recieverAc['balance']+=amountTk
    collection.delete_one({"nid":reciever})
    collection.insert_one(recieverAc)
    
    addActivity(donater,"donated tk "+str(amountTk)+ " to "+ recieverAc['name'] + " at "+str(datetime.datetime.now()))
    
    return redirect(request.META.get('HTTP_REFERER'))


    



    
    



def message(request):
    return HttpResponse("this is message")

def bloodDonatin(request):
    return HttpResponse("this is blood donation")

def shop(request):
    return HttpResponse("this is shop")
def jobs(request):
    return HttpResponse("this is jobs")
def news(request):
    return HttpResponse("this is news")
def followersPost(request):
    nid=request.session['nid']
    db=DBConnect.getInstance()
    collection=db["user"]
    usr=collection.find_one({"nid":nid})
    collection=db["post"]
    allPost=collection.find()
    allPosts=[]
    collection=db["user"]
    for i in allPost:
        if((i["nid"]in usr['followings'] or i["nid"]in usr['followers']  ) and (i["audience"]!="onlyme")):
            comments=getAllComment(i)
            posterNid=i["nid"]
            usr=collection.find_one({"nid":posterNid})
            postShow={
                "posterName":usr['name'],
                "posterNid":i["nid"],
                "postNo":i["_id"],
                "content": i['content'],
                "likes":len(i["reaction"]["like"]),
                "comment":comments,
                "viewers":i["audience"],
                "type":i["type"],
                "date":i['date'],
                
                
                }
            allPosts.append(postShow)


    postShowAll={
        "nid":i['nid'],
        "seeingNid":nid,
        "posts": allPosts,
        
    }
    return render(request,"html/followersPost.html",postShowAll)

def search(request):
    searchBy=request.GET['searchBy']
    searchValue=request.GET['searchValue']
    nid=request.session["nid"]
    
    
    if(len(searchValue)==0):
        return redirect(request.META.get('HTTP_REFERER'))
    
    addActivity(nid,"searched for "+ searchValue+" at "+str(datetime.datetime.now()) )

    results=[]
    db=DBConnect.getInstance()
    collection=db["user"]
    if(searchBy=='nid'):
        usr=collection.find_one({"nid":searchValue})
        results.append({
            "nid":usr['nid'],
            "name":usr["name"],
            "city":usr['location']['city'],
            "country":usr['location']['country']
            
        })
    elif(searchBy=='name'):
        usrs=collection.find({"name":{"$regex": searchValue,"$options":'i'}})
        for usr in usrs:
            results.append({
            "nid":usr['nid'],
            "name":usr["name"],
            "city":usr['location']['city'],
            "country":usr['location']['country']
            
        })
    
    elif(searchBy=='location'):
        usrs=collection.find({"location.city":{"$regex": searchValue,"$options":'i'}})
        for usr in usrs:
            results.append({
            "nid":usr['nid'],
            "name":usr["name"],
            "city":usr['location']['city'],
            "country":usr['location']['country']
            
        })
        usrs=collection.find({"location.country":{"$regex": searchValue,"$options":'i'}})
        for usr in usrs:
            rslt=({
            "nid":usr['nid'],
            "name":usr["name"],
            "city":usr['location']['city'],
            "country":usr['location']['country']
            
        })
        if(rslt not in results):
            results.append(rslt)
    

    searchResult={
        "people":results
    }
        
    if(searchBy!="post"):
        return render(request,'html/searchResult.html',searchResult)
    
    db=DBConnect.getInstance()
    collection=db["post"]
    
    posts=collection.find({"content":{"$regex": searchValue,"$options":'i'}})
    collection=db["user"]
    for i in posts:
        if(i["audience"]!="onlyme"):
            comments=getAllComment(i)
            posterNid=i["nid"]
            usr=collection.find_one({"nid":posterNid})
            results.append({
                "posterName":usr['name'],
                "posterNid":i["nid"],
                "postNo":i["_id"],
                "content": i['content'],
                "likes":len(i["reaction"]["like"]),
                "comment":comments,
                "viewers":i["audience"],
                "type":i["type"],
                "date":i['date'],
                
                
                })
    


    searchResult={
        "posts":results
    }
    return render(request,'html/searchPost.html',searchResult)

noAmountToDonate=False
noAmountToBuyData=False