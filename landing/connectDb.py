from pymongo import MongoClient
class Singleton:
   __instance = None
   @staticmethod 
   def getInstance():
      if Singleton.__instance == None:
        Singleton()
      return Singleton.__instance
   def __init__(self):
      if Singleton.__instance != None:
        raise Exception("This class is a singleton!")
      else:
        cluster = MongoClient("mongodb+srv://root:1234@cluster1.8jmyghr.mongodb.net/?retryWrites=true&w=majority")
        db = cluster["ethica"]

        Singleton.__instance = db


db= Singleton.getInstance()
collection=db["user"]
post={
    "nid":1234234333333534,
    "name" : "abcdasdfwer",
    "password": "qerqewr"
}
collection.insert_one(post)