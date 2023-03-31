#################################
#### Auteur : philipe Demaria 
#### pour SACADO
#################################
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import path

from account.views import *

urlpatterns = [

    path('creation_auto', view=creation_auto, name='creation_auto'),



    path('login', view=LoginView.as_view(template_name='registration/login.html', redirect_authenticated_user=True), name='login'),
    #path('logout', LogoutView.as_view(template_name='home.html'), name='logout'),
    path('logout', logout_view, name='logout'),

    path('dashboard', view=DashboardView.as_view(), name='dashboard'),


    #path('password/reset/', PasswordResetView.as_view(), name='password_reset'),
    #path('password/reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    #path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    #path('reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('end_of_adhesion', end_of_adhesion, name='end_of_adhesion'),

    path('password/reset/', passwordResetView, name='password_reset'),
    path('password/reset/done/', passwordResetDoneView, name='password_reset_done'),
    path('newpassword/<slug:code>', passwordResetConfirmView, name='password_reset_confirm'),
 
    path('init_password_teacher/<int:id>', init_password_teacher, name='init_password_teacher'),

    path('ebep/<int:id>/<int:idg>', ebep, name='ebep'),

    path('update_teacher/<int:pk>', update_teacher, name='update_teacher'),
    path('delete_teacher/<int:id>', delete_teacher, name='delete_teacher'),
    path('dissociate_teacher/<int:id>', dissociate_teacher, name='dissociate_teacher'),


    path('list_teacher', list_teacher, name='list_teacher'),

    path('close_my_account', close_my_account, name='close_my_account'),

    path('avatar', avatar, name='avatar'),
    path('create_avatar/<int:id>', create_avatar, name='create_avatar'),
    path('delete_avatar/<int:id>', delete_avatar, name='delete_avatar'),
    path('list_avatars', list_avatars, name='list_avatars'),
    path('change_avatar/<int:ids>', change_avatar, name='change_avatar'),
    path('change_backtitle/<int:ids>', change_backtitle, name='change_backtitle'),
    
    path('background', background, name='background'),
    path('create_background/<int:id>', create_background, name='create_background'),
    path('delete_background/<int:id>', delete_background, name='delete_background'),
    path('list_backgrounds', list_backgrounds, name='list_backgrounds'),


    path('updatepassword', updatepassword, name='updatepassword'),

    path('register_student', register_student, name='register_student'),

    path('detail_student/<int:id>', detail_student, name='detail_student'),
    path('detail_student_parcours/<int:id>/<int:idp>', detail_student_parcours, name='detail_student_parcours'),
    path('detail_student_theme/<int:id>/<int:idt>', detail_student_theme, name='detail_student_theme'),

    path('detail_student_all_views/<int:id>', detail_student_all_views, name='detail_student_all_views'),


    path('detail_student_academy/<int:id>', detail_student_academy, name='detail_student_academy'),

    path('student_profil/<int:ids>', student_profil, name='student_profil'),
    path('change_password/<int:ids>', change_password, name='change_password'),
    
    path('newpassword_student/<int:id>/<int:idg>', newpassword_student, name='newpassword_student'),
    path('update_student/<int:id>/<int:idg>', update_student, name='update_student'),
    path('update_student_by_ajax', update_student_by_ajax, name='update_student_by_ajax'),
    path('delete_student/<int:id>/<int:idg>', delete_student, name='delete_student'),

    path('update_student_by_admin/<int:id>', update_student_by_admin, name='update_student_by_admin'),

    path('send_to_teachers', send_to_teachers, name='send_to_teachers'),
    path('message_to_teachers_sent', message_to_teachers_sent, name='message_to_teachers_sent'),

    path('register_teacher', register_teacher, name='register_teacher'),
    path('register_teacher_from_admin', register_teacher_from_admin, name='register_teacher_from_admin'),
    path('register_by_csv/<int:key>/<int:idg>', register_by_csv, name='register_by_csv'),
    path('register_users_by_csv/<int:key>', register_users_by_csv, name='register_users_by_csv'),

    path('profile', my_profile, name='profile'),

    path('ajax/userinfo/', ajax_userinfo, name='ajax_userinfo'),
    path('ajax/userinfomail/', ajax_userinfomail, name='ajax_userinfomail'),

    path('ajax/courseinfo/', ajax_courseinfo, name='ajax_courseinfo'),
    path('ajax/control_code_student/', ajax_control_code_student, name='ajax_control_code_student'),

    path('ajax_detail_student/', ajax_detail_student, name='ajax_detail_student'),
    path('ajax_detail_student_exercise/', ajax_detail_student_exercise, name='ajax_detail_student_exercise'),
    path('ajax_detail_student_parcours/', ajax_detail_student_parcours, name='ajax_detail_student_parcours'),
    
    path('ajax_get_details_graph/', ajax_get_details_graph, name='ajax_get_details_graph'),


    path('register_parent', register_parent, name='register_parent'),
    path('update_parent/<int:id>', update_parent, name='update_parent'),
    path('delete_parent/<int:id>', delete_parent, name='delete_parent'),

    path('usertype/', ask_usertype, name='ask_usertype'),

    path('register_student_from_admin/', register_student_from_admin, name='register_student_from_admin'), 

    # quand on répond à un élève pour un exercice défaillant
    path('response_from_mail/<int:user_id>', response_from_mail, name='response_from_mail'),
    path('check_response_from_mail', check_response_from_mail, name='check_response_from_mail'),

    path('switch_teacher_student/<int:idg>', switch_teacher_student, name='switch_teacher_student'),
    path('switch_student_teacher', switch_student_teacher, name='switch_student_teacher'),

    path('aggregate_child', aggregate_child, name='aggregate_child'),
]