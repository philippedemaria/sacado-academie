from django.urls import path, re_path
from .views import *

urlpatterns = [

    path('academy_index', academy_index , name='academy_index'),
    path('details_adhesion/<int:level_id>', details_adhesion , name='details_adhesion'),
    path('historic_adhesions/<int:level_id>', historic_adhesions , name='historic_adhesions'),
    path('delete_adhesion/<int:ida>', delete_adhesion , name='delete_adhesion'),

    path('delete_student_academy/<int:ids>/<int:level_id>', delete_student_academy , name='delete_student_academy'),

    path('autotests', autotests , name='autotests'),
    path('create_autotest', create_autotest , name='create_autotest'),
    path('delete_autotest/<int:test_id>', delete_autotest , name='delete_autotest'),


    path('synthese_parcours/<int:user_id>', synthese_parcours , name='synthese_parcours'),


    path('academy_list_adhesions', academy_list_adhesions , name='academy_list_adhesions'),
    path('academy_list_parents'  , academy_list_parents   , name='academy_list_parents'),
    path('academy_delete_parent/<int:user_id>' , academy_delete_parent  , name='academy_delete_parent'),


    path('contact_academy', contact_academy , name='contact_academy'),

    path('gestion_academy_dashboard', gestion_academy_dashboard , name='gestion_academy_dashboard'),
    path('delete_groups', delete_groups , name='delete_groups'), 
    path('delete_parcours', delete_parcours , name='delete_parcours'),
    path('delete_folders', delete_folders , name='delete_folders'),
    path('delete_courses', delete_courses , name='delete_courses'),
    path('delete_relations', delete_relations , name='delete_relations'),
    path('delete_teachers', delete_teachers , name='delete_teachers'),
    path('delete_users', delete_users , name='delete_users'),
    path('add_presentation/<int:idl>', add_presentation , name='add_presentation'),
    path('add_exo_presentation/<int:idl>', add_exo_presentation , name='add_exo_presentation'),
    path('list_parcours_sequence_academy/<int:isp>/<int:idl>', list_parcours_sequence_academy , name='list_parcours_sequence_academy'),

    path('create_academy/<int:idl>', create_academy , name='create_academy'), 


    path('associate_student_docs', associate_student_docs , name='associate_student_docs'),
    
]


 