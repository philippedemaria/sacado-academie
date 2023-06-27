from django.urls import path, re_path
from .views import *
 

urlpatterns = [
 
 
    path('holidaybooks', holidaybooks, name='holidaybooks'),
    path('try_it/<int:idg>', try_it, name='try_it'),
    path('buy_it/<int:idg>', buy_it, name='buy_it'),
    path('show_this_hbook_exercise/<int:ide>', show_this_hbook_exercise, name='show_this_hbook_exercise'),


    path('engage_holidaybooks', engage_holidaybooks, name='engage_holidaybooks'),
 


]
