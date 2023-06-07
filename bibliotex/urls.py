#################################
#### Auteur : philipe Demaria 
#### pour SACADO
#################################
from django.urls import path, re_path
from .views import *
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [

    path('admin_exotexs/<int:idl>', admin_exotexs, name='admin_exotexs'),
    path('my_exotexs', my_exotexs, name='my_exotexs'),


    path('create_exotex_knowledge/<int:idk>', create_exotex_knowledge , name='create_exotex_knowledge'),
    path('exercise_exotex_update/<int:id>', update_exotex, name='update_exotex'),
    path('exercise_exotex_delete/<int:id>', delete_exotex, name='delete_exotex'), 
    path('set_exotex_in_bibliotex/<int:id>', set_exotex_in_bibliotex , name='set_exotex_in_bibliotex'), 

    path('bibliotexs', bibliotexs, name='bibliotexs'),
    path('my_bibliotexs', my_bibliotexs, name='my_bibliotexs'),
    path('actioner', actioner, name='actioner'),

    path('create_bibliotex_sequence/<int:id>', create_bibliotex_sequence, name='create_bibliotex_sequence'),

 
    path('my_bibliotex_archives', my_bibliotex_archives, name='my_bibliotex_archives'),

    path('exercise_bibliotex_create/<int:idf>', create_bibliotex , name='create_bibliotex'),
    path('exercise_bibliotex_update/<int:id>', update_bibliotex, name='update_bibliotex'),
    path('exercise_bibliotex_delete/<int:id>', delete_bibliotex, name='delete_bibliotex'), 
    path('exercise_bibliotex_peuplate/<int:id>', exercise_bibliotex_peuplate, name='exercise_bibliotex_peuplate'),
    path('exercise_bibliotex_show/<int:id>', show_bibliotex, name='show_bibliotex'),

    path('update_relationtex/<int:id>', update_relationtex , name='update_relationtex'),
    path('delete_relationtex/<int:id>', delete_relationtex , name='delete_relationtex'),

    path('create_bibliotex_from_parcours/<int:idp>', create_bibliotex_from_parcours , name='create_bibliotex_from_parcours'),
    path('peuplate_bibliotex_parcours/<int:idp>', peuplate_bibliotex_parcours , name='peuplate_bibliotex_parcours'), 
    path('clone_bibliotex_sequence/<int:idb>', clone_bibliotex_sequence, name='clone_bibliotex_sequence'),


    path('real_time_bibliotex/<int:id>', real_time_bibliotex, name='real_time_bibliotex'),  
    path('unset_exotex_in_bibliotex/<int:idr>', unset_exotex_in_bibliotex, name='unset_exotex_in_bibliotex'),  

    path('ajax_is_favorite', ajax_is_favorite, name='ajax_is_favorite'),


    path('print_exotex', print_exotex, name='print_exotex'),      
    path('print_bibliotex', print_bibliotex, name='print_bibliotex'), 

    path('print_bibliotex_by_student/<int:id>', print_bibliotex_by_student, name='print_bibliotex_by_student'), 
     

    path('ajax_publish_bibliotex', ajax_publish_bibliotex, name='ajax_publish_bibliotex'),  
    path('ajax_publish_list_bibliotex', ajax_publish_list_bibliotex, name='ajax_publish_list_bibliotex'),  


    path('exercise_bibliotex_individualise/<int:id>', exercise_bibliotex_individualise, name='exercise_bibliotex_individualise'), 
    path('exercise_bibliotex_results/<int:id>', exercise_bibliotex_results, name='exercise_bibliotex_results'),

    path('ajax_chargethemes', ajax_chargethemes, name='ajax_chargethemes'),
    path('ajax_level_exotex', ajax_level_exotex, name='ajax_level_exotex'),
    path('ajax_charge_folders', ajax_charge_folders, name='ajax_charge_folders'),
    path('ajax_charge_parcours', ajax_charge_parcours, name='ajax_charge_parcours'),

    path('ajax_my_bibliotexs', ajax_my_bibliotexs, name='ajax_my_bibliotexs'),
    path('ajax_set_exotex_in_bibliotex', ajax_set_exotex_in_bibliotex, name='ajax_set_exotex_in_bibliotex'),

    path('ajax_search_bibliotex', ajax_search_bibliotex, name='ajax_search_bibliotex'), 

    path('ajax_results_exotex', ajax_results_exotex, name='ajax_results_exotex'),
    path('ajax_print_exotex', ajax_print_exotex, name='ajax_print_exotex'),
    path('ajax_print_bibliotex', ajax_print_bibliotex, name='ajax_print_bibliotex'),
    path('ajax_individualise_exotex', ajax_individualise_exotex, name='ajax_individualise_exotex'),
    path('ajax_individualise', ajax_individualise, name='ajax_individualise'),

    #path('ajax_charge_group_from_target', ajax_charge_group_from_target, name='ajax_charge_group_from_target'), 
    path('ajax_affectation_to_group', ajax_affectation_to_group, name='ajax_affectation_to_group'), 
    path('ajax_sharer_parcours', ajax_sharer_parcours, name='ajax_sharer_parcours'), 
 
    path('ajax_sort_exotexs_in_bibliotex', ajax_sort_exotexs_in_bibliotex, name='ajax_sort_exotexs_in_bibliotex'), 
 
    path('ajax_find_peuplate_sequence', ajax_find_peuplate_sequence, name='ajax_find_peuplate_sequence'),
    path('clone_bibliotex_sequence/<int:idb>', clone_bibliotex_sequence, name='clone_bibliotex_sequence'),

    path('annales/<int:idl>', annales, name='annales'), 
    path('show_this_annale/<int:idb>', show_this_annale, name='show_this_annale'), 


 ]
