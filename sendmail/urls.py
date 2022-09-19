from django.urls import path, re_path
from .views import *

urlpatterns = [

    path('', list_emails, name='emails'),
    path('new', create_email, name='create_email'),
    path('delete/<int:id>/', delete_email, name='delete_email'),
    path('ajax/show_email/', show_email, name='show_email'),
 

    path('communications', list_communications, name='communications'),
    path('new_communication', create_communication, name='create_communication'),
    path('update_communication/<int:id>/', update_communication, name='update_communication'),
    path('delete_communication/<int:id>/', delete_communication, name='delete_communication'),
    path('ajax/show_communication/', show_communication, name='show_communication'),
    path('ajax/show_communication/', show_communication, name='show_communication'),
    path('ajax/reader_communication/', reader_communication, name='reader_communication'),


    path('ajax/pending_notification/', pending_notification, name='pending_notification'),

    path('create_discussion', create_discussion, name='create_discussion'),
    path('show_discussion/<int:idd>/show', show_discussion, name='show_discussion'),
    path('delete_message/<int:idd>/<int:id>/', delete_message, name='delete_message'),
  



    path('ajax_notification_group', ajax_notification_group, name='ajax_notification_group'),
    path('ajax_notification_student', ajax_notification_student, name='ajax_notification_student'),


    path('list_discussion_lesson/<int:idu>', list_discussion_lesson, name='list_discussion_lesson'),
    path('list_discussion_lesson_parent/<int:idu>', list_discussion_lesson_parent, name='list_discussion_lesson_parent'), 
       
    path('create_discussion_lesson', create_discussion_lesson, name='create_discussion_lesson'),
    path('show_discussion_lesson/<int:idd>/show', show_discussion_lesson, name='show_discussion_lesson'),
    path('delete_message_lesson/<int:idd>/<int:id>/', delete_message_lesson, name='delete_message_lesson'),
  
  
]
