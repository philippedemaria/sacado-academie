from django.urls import path, re_path
from .views import *
 

urlpatterns = [
 
 
    path('holidaybooks', holidaybooks, name='holidaybooks'),
    path('try_it/<int:idl>', try_it, name='try_it'),
    path('buy_it/<int:idl>', buy_it, name='buy_it'),

]
