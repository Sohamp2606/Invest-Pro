from . import views
from django.urls import path , include
from . import models

urlpatterns = [

    path('',views.home,name="home"),
    path('test/',views.test,name="test"),
    

    path('prediction/<str:ticker>/',views.predictionchart,name="predictionchart"),
    path('searchticker/<slug:slug>',views.searchticker,name="gettiker"),
    path('livechart/<str:ticker>',views.livechart,name="livechart"),
    path('analysis/<str:ticker>',views.analysischart,name="analysischart"),
    path('prediction/<str:ticker>/nextday',views.nextday,name="nextday"),

    path('searchticker/',views.choseticker,name="searchticker"),
    
   
]
