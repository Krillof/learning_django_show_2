from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', index, name='index'),
    path('register/', register, name='register'),
    path('enter/', enter, name='enter'),
    path('exit/', exit, name='exit'),
    path('dirs/<str:username>/<str:dir>/', dirs, name='dirs'),
    path('createdir/', createdir, name='createdir'),
    path('addallowtouser/<str:dir>/', addallowtouser, name='addallowtouser'),
    path('addpicturetodir/<str:dir>/', addpicturetodir, name='addpicturetodir')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)