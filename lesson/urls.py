from django.urls import path 
from django.views.generic import TemplateView
from lesson.views import *
from django.views.decorators.csrf import csrf_exempt 


urlpatterns = [

    path('events_json', events_json, name='events_json'), 
    path('create_event', create_event, name='create_event'),
    path('update_event/<int:id>/', csrf_exempt(update_event), name='update_event'),
    path('show_event', show_event, name='show_event'),
    path('delete_event/<int:id>/', delete_event, name='delete_event'), 
    path('shift_event', csrf_exempt(shift_event), name='shift_event'), 
    path('calendar_show/<int:id>', calendar_show, name='calendar_show'),
    path('add_students_to_my_lesson_group', add_students_to_my_lesson_group, name='add_students_to_my_lesson_group'),
    path('delete_student_to_my_lesson_group/<int:id>', delete_student_to_my_lesson_group, name='delete_student_to_my_lesson_group'),
    path('dashboard_parent', dashboard_parent, name='dashboard_parent'),   
    path('detail_student_lesson/<int:id>', detail_student_lesson, name='detail_student_lesson'),
    path('ask_lesson/<int:id>', ask_lesson, name='ask_lesson'),

    path('ajax_display_calendar', ajax_display_calendar, name='ajax_display_calendar'),




 ]

