from django.urls import path
#from .views import anasayfaView
#bu dizinden fonk import etmek için
from . import views

urlpatterns= [

    path('', views.homepage, name=""),

    path('register', views.register, name="register"),

    path('my-login', views.my_login, name="my-login"),
    
    path('dashboard', views.dashboard, name="dashboard"),

    path('user-logout', views.user_logout, name="user-logout"),

    path('upload-image', views.handle_upload, name="upload-image"),

    path('analysis-results', views.user_analysis_results, name="analysis_results"),

]
#ilk tırnağa bir şey yazılmasa kullanıcı direkt anasayfayı görür