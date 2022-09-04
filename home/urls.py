from django.urls import path,include
from . import views
from landing import views as views2

urlpatterns = [
    path('login/', views2.logIn,name="login"),
    path('', views.newsFeed,name="newsFeed"),
    path('profile/', views.profilePage,name="profile"),
    path('message/', views.message,name="message"),
    path('settings/', views.settings,name="settings"),
    path('bloodDonatin/', views.bloodDonatin,name="bloodDonatin"),
    path('shop/', views.shop,name="shop"),
    path('jobs/', views.jobs,name="jobs"),
    path('news/', views.news,name="news"),
    path('followersPost/', views.followersPost,name="followersPost"),
    path('followers/', views.followers,name="followers"),
    path('followings/', views.followings,name="followings"),
    path('othersProfile/<nid>/', views.othersProfile,name="othersProfile"),
    path('othersProfile/', views.othersProfile,name="othersProfile"),
    path('createPost/', views.createPost,name="createPost"),
    path('createPostHandle/', views.createPostHandle,name="createPostHandle"),
    path('logout/', views.logout,name="logout"),
    path('addComment/', views.addComment,name="addComment"),
    path('followAction/', views.followAction,name="followAction"),
    path('showBasicInfo/', views.showBasicInfo,name="showBasicInfo"),
    path('changeBasicInfo/', views.changeBasicInfo,name="changeBasicInfo"),
    path('makeOtherComment/', views.makeOtherComment,name="makeOtherComment"),
    path('recharge/', views.recharge,name="recharge"),
    path('tip/', views.tip,name="tip"),
    path('search/', views.search,name="search"),
    path('activityLog/', views.activityLog,name="activityLog"),
    path('seeTranslated/<postId>/', views.seeTranslated,name="seeTranslated"),
    path('seeTranslated/', views.seeTranslated,name="seeTranslated"),
    path('buyData/', views.buyData,name="buyData"),
    path('buyDataHandle/', views.buyDataHandle,name="buyDataHandle"),
    path('notification/', views.notification,name="notification"),
    
    

       
]