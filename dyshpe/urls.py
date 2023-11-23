from django.urls import path, re_path
from .views import *
 

urlpatterns = [
 
    path('', indexdys, name='indexdys'),
    path('register_dys', register_dys, name='register_dys'),

]
