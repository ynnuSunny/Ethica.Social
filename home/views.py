import json
from glob import glob
import profile
import datetime
from tkinter.messagebox import NO
from tokenize import Comment
from unittest import result
from cv2 import FileStorage
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
from django.core.files.storage import FileSystemStorage
import spacy
import nltk
nltk.download("stopwords")
from nltk.corpus import stopwords


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

    updateUsr(usr)


def addNotification(nid,notification):
    db=DBConnect.getInstance()
    collection=db["user"]
    if(len(notification)==0):
        return

    usr=collection.find_one({"nid":nid})
    try:
        usr['notification'].append(notification)
    except:
        usr['notification']= notification

    updateUsr(usr)


def rechargeFunc(nid,tk):
    db=DBConnect.getInstance()
    collection=db["user"]
    usr=collection.find_one({"nid":nid})
    usr['balance']+=tk
    collection.delete_one({"nid":nid})
    collection.insert_one(usr)
    
    
def updateUsr(usr):
    db=DBConnect.getInstance()
    collection=db["user"]
    collection.delete_one({"nid":usr["nid"]})
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

def getSimillarity(interest,tags):
    sw = stopwords.words('english')
    nlp = spacy.load('en_core_web_sm')
    interest= [ w for w in interest if w not in stopwords.words('english')]
    tags = [ w for w in tags if w not in stopwords.words('english')]
    
    build = " ".join(interest)
    s2= " ".join(tags)
    doc1 = nlp(build)
    doc2 = nlp(s2)


    return doc1.similarity(doc2)

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


def showOnePost(request):
    try:
        nid=request.session['nid']
        usr=getUsr(nid)
        usr['todayPostView']+=1
        global showPost
        global postNo
        global maxReached
        
        if(usr['todayPostView']>=usr['maxPostView']):
            updateUsr(usr)    
            return render(request, 'html/showOnePost.html',{"msg":"you have reached maximum view limit"})

        if(postNo==len(showPost)):
            postNo=0
        updateUsr(usr)
        db=DBConnect.getInstance()
        collection=db["post"]
        allPost=[]
        p=collection.find_one({"_id":ObjectId(showPost[postNo][1])})
        allPost.append(p)
        postNo+=1
        postShowAll=[]
        allPosts=[]
        collection=db["user"]
        fs= FileSystemStorage()
        for i in allPost:
            comments=getAllComment(i)
            posterNid=i["nid"]
            usr=collection.find_one({"nid":posterNid})
            postShow={
                "posterName":usr['name'],
                "dp":fs.url(usr['dp']),
                "posterNid":i["nid"],
                "postNo":i["_id"],
                "content": i['content'],
                "likes":len(i["reactors"]),
                "comment":comments,
                "viewers":i["audience"],
                "type":i["type"],
                "date":i['date'],
                "reactTypes":list(i["reactionCount"].keys()),
                "photo":None,
                "nid":i['nid'],
                "seeingNid":nid,
                }
            
            if(i['photo']):
                postShow['photo']=fs.url(i['photo'])
            allPosts.append(postShow)
            
        return render(request, 'html/showOnePost.html',{"posts":allPosts})

    except:
        return redirect(newsFeed)

def newsFeed(request):
    nid=request.session['nid']
    usr=getUsr(nid)
    db=DBConnect.getInstance()
    collection=db["post"]
    global maxReached
    

    allPosts= collection.find({})
    global showPost
    showPost=[]
    global postNo
    
    postNo=0
    for i in allPosts:
        if(i['nid']==nid):
            continue

        match= getSimillarity(usr['interest'], i['tags'])
        showPost.append([match,i['_id']])
    showPost.sort()

    return redirect(showOnePost)


def toggleCellData(request):
    nid=request.session['nid']
    
    db=DBConnect.getInstance()
    collection=db["user"]
    usr=collection.find_one({"nid":nid})
    usr['sellData'] = not usr['sellData']
    updateUsr(usr)

    
    return redirect(settings)

def buyReaction(request):
    nid=request.session['nid']
    
    db=DBConnect.getInstance()
    collection=db["user"]
    usr=collection.find_one({"nid":nid})

    reactionPrice=500
    global cannotBuyReaction
    if(usr['balance']<reactionPrice):
        cannotBuyReaction=True
        return redirect(settings)


    reaction=request.GET['buyReaction']
    usr['balance']-=reactionPrice
    usr['reactions'].append(reaction)
    updateUsr(usr)
    return redirect(settings)



def updateUsrMaxPostView(request):
    nid=request.session['nid']
    usr=getUsr(nid)
    maxPView=int(request.GET['maxPostLimit'])
    usr['maxPostView']=maxPView
    updateUsr(usr)
    return redirect(settings)


def settings(request):
    nid=request.session['nid']
    reactions=["haha", "love", "angry","dislike","sad","surprised", "fear","surprised"]
    
    db=DBConnect.getInstance()
    collection=db["user"]
    usr=collection.find_one({"nid":nid})
    buyAvailable=[]

    for i in reactions:
        if(i not in usr["reactions"]):
            buyAvailable.append(i)


    dataAction="stop"
    
    if(not usr['sellData']):
        dataAction="allow"
    send={"toggle":dataAction, "reactionBuy":buyAvailable}
    msg=None
    global cannotBuyReaction
    if(cannotBuyReaction):
        cannotBuyReaction=False
        msg="not enough money to buy reaction"
    send['msg']=msg
    
    return render(request, 'html/settings.html',send)

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
    fs=FileSystemStorage()
    postShow={
            "translatedContent":translate_(i["content"]),
            "postNo":i["_id"],
            "content": i['content'],
            "likes":len(i['reactors']),
            "comment":comments,
            "viewers":i["audience"],
            "type":i["type"],
            "date":i['date'],
            "photo":None,
        }
    if(i['photo']):
        postShow['photo']=fs.url(i["photo"])

    
    return render(request, 'html/seeTranslatedPost.html',postShow)
    

def viewReactions(request):
    postid=request.GET['postid']
    db=DBConnect.getInstance()
    collection=db["post"]
    post=collection.find_one({"_id":ObjectId(postid)})
    reacCount=[]
    fs=FileSystemStorage()
    for i in post['reactionCount'].keys():
        reacCount.append({
            "reactName":i,
            "reactorInfo":[] })
        for us in post['reactionCount'][i]:
            usr=getUsr(us)
            reacCount[-1]["reactorInfo"].append({
                "reactName":usr['name'],
                "reactNid":usr['nid'],
                "dp":fs.url(usr["dp"])
            })
            
    return render(request, 'html/viewPostReact.html',{"react":reacCount})
    

def meReact(request):
    postid=request.GET['postid']
    reactName=request.GET['reactName']
    db=DBConnect.getInstance()
    collection=db["post"]
    post=collection.find_one({"_id":ObjectId(postid)})
    
    nid=None
    myNid=request.session['nid']
    try:
        nid=request.GET['reactorNid']
    except:
        nid=myNid
    if(nid!=myNid and nid not in post["reactors"]):
        usr=getUsr(post['nid'])
        addActivity(nid,"reacted on "+usr['name']+" post at "+ str(datetime.datetime.now()))
        usr=getUsr(nid)
        addNotification(post['nid'],usr['name']+ " "+reactName+"d on your post")

    
    if(nid not in post["reactors"]):
        post['reactors'].append(nid)
    
    
    for react in post['reactionCount'].keys():
        if(nid in post['reactionCount'][react]):
            post['reactionCount'][react].remove(nid)
        
        if(react==reactName ):
            post['reactionCount'][react].append(nid)

    collection.delete_one({"_id":ObjectId(postid)})
    collection.insert_one(post)
    

    return redirect(request.META.get('HTTP_REFERER'))
    



def profilePage(request):
    nid=request.session['nid']
    db=DBConnect.getInstance()
    collection=db["user"]
    usr=collection.find_one({"nid":nid})
    fs=FileSystemStorage()
    # dp=getImg(nid)
    profileViewers=usr['viewedMyPorfile']
    if(len(profileViewers)>5):
        profileViewers=profileViewers[-5:]
    if(len(profileViewers)==0):
        profileViewers.append(nid)
    
    profileViewers= set(profileViewers)
    profileViewers = list(profileViewers)
    profileViewInfo=[]
    for i in profileViewers:
        u= getUsr(i)
        profileViewInfo.append({
            'viewerNid':i,
            "viewerName":u['name']
        })

    userInfo={
        "viewedMyProfile":profileViewInfo,
        'cover':fs.url(usr['cover']),
        "dp":fs.url(usr['dp']),
        "name":usr["name"],
        "bio":usr['bio'],
        "noOfFollowers":len(usr['followers']),
        "noOfFollowings":len(usr['followings'])
    }
    
    
    collection=db["post"]
    posts=collection.find({"nid":nid})
    allPosts=[]
    for i in posts:
        comments=getAllComment(i)
        reactionCount=len(i['reactors'])
        postShow={
            "postNo":i["_id"],
            "content": i['content'],
            "reactions":reactionCount,
            "comment":comments,
            "viewers":i["audience"],
            "type":i["type"],
            "date":i['date'],
            "reactTypes":list(i["reactionCount"].keys()),
            "photo":None
        }
        
        if(i['photo']):
            postShow['photo']=fs.url(i['photo'])
            
        
        allPosts.append(postShow)
        
    
    userInfo["posts"]=allPosts
    

    return render(request, 'html/profile.html',userInfo)

def updateDp(request):
    nid=request.session['nid']
    usr=getUsr(nid)
    try:
        uploaded_file = request.FILES["dp"]
        fs = FileSystemStorage()   
        photo_name=fs.save(uploaded_file.name, uploaded_file)
        usr['dp']=photo_name
        updateUsr(usr)
    except:
        pass
    return redirect(profilePage)
def updateCover(request):
    nid=request.session['nid']
    usr=getUsr(nid)
    try:
        uploaded_file = request.FILES["cover"]
        fs = FileSystemStorage()   
        photo_name=fs.save(uploaded_file.name, uploaded_file)
        usr['cover']=photo_name
        updateUsr(usr)
    except:
        pass
    return redirect(profilePage)

def createPost(request):
    nid=request.session['nid']
    
    usr=getUsr(nid)
    usrData={
        "reactions":usr['reactions']
    }

    return render(request, 'html/createPost.html',usrData)


def makeOtherComment(request):
    ownerOfPost = request.GET['nid']
    commenter = request.GET['commenter']
    postid = request.GET['postid']
    comment = request.GET['comment']

    if (commenter == '' or ownerOfPost == '' or postid == '' or len(comment) == 0):
        redirect(request.META.get('HTTP_REFERER'))

    db = DBConnect.getInstance()
    collection = db["post"]
    postData = collection.find_one({"_id": ObjectId(postid)})
    allComments = postData["comment"]
    allComments.append([commenter, comment])
    postData["comment"] = allComments
    collection.delete_one({"_id": ObjectId(postid)})
    collection.insert_one(postData)
    own = getUsr(postData['nid'])
    commenterData = getUsr(commenter)
    notificationTxt = postData['content']
    if (len(notificationTxt) > 10):
        notificationTxt = postData['content'][:10]
    addActivity(commenter,
                "made a comment \"" + comment + "\" on " + own['name'] + "'s post at " + str(datetime.datetime.now()))
    addNotification(own['nid'], commenterData['name'] + " made a comment on your post " + notificationTxt + "...")
    commenterData["interest"].extend(postData['tags'])
    updateUsr(commenterData)
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
    
def deletePost(request):
    postid=request.GET['postid']

    db=DBConnect.getInstance()
    collection=db["post"]
    collection.delete_one({"_id":ObjectId(postid)})
    
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
    updateUsr(usr)
    addActivity(nid,"recharged tk "+ str(amount) +" at "+ str(datetime.datetime.now()))
    return redirect(request.META.get('HTTP_REFERER'))

def createPostHandle(request):
    #came from unknown source
    if(request.method!='POST'):
        return redirect("createPost")

    posterNid =request.session['nid']
    usr = getUsr(posterNid)
    photo_name=None
    reactions= request.POST.getlist('reaction')
    reactions.append("like")
    reactionCount={}
    for i in reactions:
        reactionCount[i]=[]
    
    try:
        uploaded_file = request.FILES["photo"]
        fs = FileSystemStorage()   
        photo_name=fs.save(uploaded_file.name, uploaded_file)
    except:
        pass
    
    react=None
    
    price=0
    
    
    
    
    postContent=request.POST['postcontent']
    
    #empty post
    if(len(postContent)==0):
        return render(request, 'html/createPost.html',{"msg":"post cannot be empty",'reactions':usr['reactions']})
    

    

    
    tags=request.POST['tags'].split(" ")
    audience=request.POST["audience"]
    
    post={
        "nid": posterNid,
        "content":postContent,
        "photo":photo_name,
        "reaction":{
            "like":[],
        },
        "reactors":[],
        "reactionCount":reactionCount,
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
    
    updateUsr(usr)

    updateUsr(usr2)

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
    
    fs=FileSystemStorage()
    # USER
    db=DBConnect.getInstance()
    collection=db["user"]
    usr=collection.find_one({"nid":nid})
    me=collection.find_one({"nid":mynid})
    usr['viewedMyPorfile'].append(mynid)
    updateUsr(usr)
    #posts
    collection=db["post"]
    posts=collection.find({"nid":nid})
    fs= FileSystemStorage()
    allPosts=[]
    for i in posts:
        if(i["audience"]=="onlyme"):
            continue
        comments=getAllComment(i)
        postShow={
            "postNo":i["_id"],
            "content": i['content'],
            "likes":len(i['reactors']),
            "comment":comments,
            "viewers":i["audience"],
            "type":i["type"],
            "date":i['date'],
            "reactTypes":list(i["reactionCount"].keys()),
            "photo":None,
        }
        if(i['photo']):
            postShow['photo']=fs.url(i['photo'])
        
        
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
        "dp":fs.url(usr['dp']),
        'cover':fs.url(usr['cover']),
        'followers':len(usr['followers']),
        'followings':len(usr['followings']),
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
    usr=getUsr(nid)
    db=DBConnect.getInstance()
    collection=db["post"]
    allPost= collection.find({})
    allPosts=[]
    collection=db["user"]
    fs= FileSystemStorage()
    for i in allPost:
        if((i["nid"]in usr['followings']) and (i["audience"]!="onlyme") and i['nid']!=nid):
            comments=getAllComment(i)
            posterNid=i["nid"]
            usr=collection.find_one({"nid":posterNid})
            postShow={
                "posterName":usr['name'],
                "posterNid":i["nid"],
                "postNo":i["_id"],
                "content": i['content'],
                "likes":len(i["reactors"]),
                "comment":comments,
                "viewers":i["audience"],
                "type":i["type"],
                "date":i['date'],
                "reactTypes":list(i["reactionCount"].keys()),
                "photo":None,
                "dp":fs.url(usr['dp'])
                }
            
            if(i['photo']):
                postShow['photo']=fs.url(i['photo'])
        
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
    
    fs= FileSystemStorage()
    if(len(searchValue)==0):
        return redirect(request.META.get('HTTP_REFERER'))
    
    addActivity(nid,"searched for "+ searchValue+" at "+str(datetime.datetime.now()) )

    results=[]
    db=DBConnect.getInstance()
    collection=db["user"]
    if(searchBy=='nid'):
        usr=collection.find_one({"nid":searchValue})
        results.append({
            "dp":fs.url(usr['dp']),
            "nid":usr['nid'],
            "name":usr["name"],
            "city":usr['location']['city'],
            "country":usr['location']['country']
            
        })
    elif(searchBy=='name'):
        usrs=collection.find({"name":{"$regex": searchValue,"$options":'i'}})
        for usr in usrs:
            results.append({
            "dp":fs.url(usr['dp']),
            "nid":usr['nid'],
            "name":usr["name"],
            "city":usr['location']['city'],
            "country":usr['location']['country']
            
        })
    
    elif(searchBy=='location'):
        usrs=collection.find({"location.city":{"$regex": searchValue,"$options":'i'}})
        for usr in usrs:
            results.append({
            "dp":fs.url(usr['dp']),
            "nid":usr['nid'],
            "name":usr["name"],
            "city":usr['location']['city'],
            "country":usr['location']['country']
            
        })
        usrs=collection.find({"location.country":{"$regex": searchValue,"$options":'i'}})
        for usr in usrs:
            rslt=({
            "dp":fs.url(usr['dp']),
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
                "dp":fs.url(usr['dp']),
                "posterName":usr['name'],
                "posterNid":i["nid"],
                "postNo":i["_id"],
                "content": i['content'],
                "likes":len(i["reactors"]),
                "comment":comments,
                "viewers":i["audience"],
                "type":i["type"],
                "date":i['date'],
                "reactTypes":list(i["reactionCount"].keys()),
                "photo":None
                })

        if(i['photo']):
            results[-1]['photo']=fs.url(i['photo'])
        


    searchResult={
        "posts":results
    }
    return render(request,'html/searchPost.html',searchResult)

noAmountToDonate=False
noAmountToBuyData=False
cannotBuyReaction=False
showPost=[]
postNo=0
maxReached= False