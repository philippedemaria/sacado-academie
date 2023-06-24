
from django.urls import path, re_path
from .views import *

urlpatterns = [


    path('dashboard/<int:id>', dashboard_group, name='dashboard_group'),

    path('', list_groups, name='groups'),
    path('new', create_group, name='create_group'),
    path('update/<int:id>/', update_group, name='update_group'),
    path('delete/<int:id>/', delete_group, name='delete_group'),
    path('delete_group_and_his_documents/<int:id>/', delete_group_and_his_documents, name='delete_group_and_his_documents'),

    path('delete_all_groups', delete_all_groups , name='delete_all_groups'),


    path('show/<int:id>/', show_group, name='show_group'), 
    path('result/<int:id>/', result_group, name='result_group'),
    path('result_group_exercise/<int:id>/', result_group_exercise, name='result_group_exercise'),
    path('result_group_skill/<int:id>/', result_group_skill, name='result_group_skill'),
    path('result_group_waiting/<int:id>/', result_group_waiting, name='result_group_waiting'),

    
    path('stats/<int:id>/', stat_group, name='stat_group'),
    path('print_statistiques/<int:group_id>/<int:student_id>/', print_statistiques, name='print_statistiques'),
    
    path('print_monthly_statistiques', print_monthly_statistiques, name='print_monthly_statistiques'),

    path('print_ids/<int:id>/', print_ids, name='print_ids'),
    path('print_list_ids/<int:id>/', print_list_ids, name='print_list_ids'),
    path('print_school_ids', print_school_ids, name='print_school_ids'),

    path('task_group/<int:id>/', task_group, name='task_group'),

    path('schedule_task_group/<int:id>/', schedule_task_group, name='schedule_task_group'),


    path('group_theme/<int:id>/<int:idt>/', result_group_theme, name='result_group_theme'),

    path('group_theme_exercise/<int:id>/<int:idt>/', result_group_theme_exercise, name='result_group_theme_exercise'),
    path('associate_exercise_by_parcours/<int:id>/<int:idt>/',  associate_exercise_by_parcours, name='associate_exercise_by_parcours'),

    path('ajax/student_select_to_school',  student_select_to_school, name='student_select_to_school'),
    path('ajax/student_remove_from_school',  student_remove_from_school, name='student_remove_from_school'),
    path('ajax/chargelisting', chargelisting, name='chargelisting'),
    path('ajax/chargelistgroup', chargelistgroup, name='chargelistgroup'),

    path('ajax_delete_student_profiles', ajax_delete_student_profiles, name='ajax_delete_student_profiles'),
    path('ajax_choose_parcours',  ajax_choose_parcours, name='ajax_choose_parcours'), 
    path('ajax/select_exercise_by_knowledge',  select_exercise_by_knowledge, name='select_exercise_by_knowledge'),

    path('aggregate_group',  aggregate_group, name='aggregate_group'), 

    path('export_skills',  export_skills, name='export_skills'), 
    path('envoieStatsEnMasse',envoieStatsEnMasse, name="envoieStatsEnMasse"),

    path('<slug:slug>', enroll , name='enroll'),

]
 