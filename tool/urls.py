from django.urls import path, re_path
from .views import *

urlpatterns = [

 

    path('list_tools', list_tools, name='list_tools'),
    path('new', create_tool, name='create_tool'),
    path('update/<int:id>', update_tool, name='update_tool'),
    path('delete/<int:id>', delete_tool, name='delete_tool'),
    path('show/<int:id>', show_tool, name='show_tool'), 

    path('list', list_quizzes, name='list_quizzes'),
    path('create_quizz/new', create_quizz, name='create_quizz'),
    path('update_quizz/<int:id>', update_quizz, name='update_quizz'),
    path('delete_quizz/<int:id>', delete_quizz, name='delete_quizz'),
    path('show_quizz/<int:id>', show_quizz, name='show_quizz'), 
 
    
    path('list', list_quizzes, name='list_quizzes'),
    path('create_quizz/new', create_quizz, name='create_quizz'),
    path('update_quizz/<int:id>', update_quizz, name='update_quizz'),
    path('delete_quizz/<int:id>', delete_quizz, name='delete_quizz'),
    path('show_quizz/<int:id>', show_quizz, name='show_quizz'), 
    path('print_answer_positionnement_to_pdf', print_answer_positionnement_to_pdf, name='print_answer_positionnement_to_pdf'),



    path('create_quizz_folder/<int:idf>', create_quizz_folder, name='create_quizz_folder'),
    path('create_quizz_parcours/<int:idp>', create_quizz_parcours, name='create_quizz_parcours'),

    path('peuplate_quizz_parcours/<int:idp>', peuplate_quizz_parcours, name='peuplate_quizz_parcours'),
    path('ajax_find_peuplate_sequence', ajax_find_peuplate_sequence, name='ajax_find_peuplate_sequence'), 

    path('print_quizz_to_pdf', print_quizz_to_pdf, name='print_quizz_to_pdf'), 
 
    path('create_quizz_sequence/<int:id>', create_quizz_sequence , name='create_quizz_sequence'),

    path('all_quizzes/search', all_quizzes, name='all_quizzes'), 
    path('ajax_shared_quizzes', ajax_shared_quizzes, name='ajax_shared_quizzes'), 
    path('clone_quizz/<int:id_quizz>', clone_quizz, name='clone_quizz'),
    path('ajax_chargethemes_quizz', ajax_chargethemes_quizz, name='ajax_chargethemes_quizz'),

    path('clone_quizz_sequence/<int:id_quizz>', clone_quizz_sequence, name='clone_quizz_sequence'),
    

    path('show_quizz_shared/<int:id>', show_quizz_shared, name='show_quizz_shared'), 

    path('tools_to_exercise/<int:id>', tools_to_exercise, name='tools_to_exercise'), 
    path('ajax_attribute_this_tool_to_exercise', ajax_attribute_this_tool_to_exercise, name='ajax_attribute_this_tool_to_exercise'), 


    path('ajax_affectation_to_group', ajax_affectation_to_group, name='ajax_affectation_to_group'), 



    path('create_question/<int:idq>/<int:qtype>', create_question, name='create_question'),
    path('update_question/<int:id>/<int:idq>', update_question, name='update_question'),   
    path('delete_question/<int:id>/<int:idq>', delete_question  , name='delete_question'),
    path('clone_question/<int:id>/<int:idq>/<int:qtype>', clone_question  , name='clone_question'),

    path('quizz_actioner', quizz_actioner  , name='quizz_actioner'),
    path('quizz_archived', all_quizzes_archived  , name='all_quizzes_archived'),

    path('list_diaporama', list_diaporama, name='list_diaporama'),
    path('all_diaporama_archived', all_diaporama_archived, name='all_diaporama_archived'),


    path('create_diaporama/new', create_diaporama, name='create_diaporama'),
    path('update_diaporama/<int:id>', update_diaporama, name='update_diaporama'),
    path('show_diaporama/<int:id>', show_diaporama, name='show_diaporama'),     
    path('delete_diaporama/<int:id>', delete_diaporama, name='delete_diaporama'),
    path('diaporama_actioner', diaporama_actioner, name='diaporama_actioner'),

    path('create_slide/<int:id>', create_slide, name='create_slide'),
    path('update_slide/<int:id>/<int:idp>', update_slide, name='update_slide'),
    path('delete_slide/<int:id>/<int:idp>', delete_slide, name='delete_slide'),

    path('show_quizz_group/<int:id>/<int:idg>', show_quizz_group, name='show_quizz_group'), 
    path('show_quizz_random_group/<int:id>/<int:idg>', show_quizz_random_group, name='show_quizz_random_group'), 
    path('create_quizz_code/<int:id>/<int:idg>', create_quizz_code, name='create_quizz_code'),

    path('show_quizz_parcours_student/<int:id>/<int:idp>', show_quizz_parcours_student, name='show_quizz_parcours_student'), 



    path('list_questions', list_questions, name='list_questions'),
 
    path('update_question/<int:id>/<int:idq>/<int:qtype>', update_question, name='update_question'),
 

    path('remove_question/<int:id>/<int:idq>', remove_question, name='remove_question'), # from a quizz
    path('show_question/<int:id>', show_question, name='show_question'), 


    ############## Ajax
    path('delete_my_tool', delete_my_tool, name='delete_my_tool'),

 
    path('ajax_chargeknowledges', ajax_chargeknowledges, name='ajax_chargeknowledges'),
    path('ajax_chargewaitings', ajax_chargewaitings, name='ajax_chargewaitings'),
    path('ajax_charge_groups', ajax_charge_groups, name='ajax_charge_groups'),
    path('ajax_charge_folders', ajax_charge_folders, name='ajax_charge_folders'),
    path('ajax_charge_parcours', ajax_charge_parcours, name='ajax_charge_parcours'),
    path('ajax_charge_parcours_without_folder', ajax_charge_parcours_without_folder, name='ajax_charge_parcours_without_folder'),
    path('ajax_charge_groups_level', ajax_charge_groups_level, name='ajax_charge_groups_level'),
 


    path('question_sorter', question_sorter, name='question_sorter'), 

    path('get_this_tool', get_this_tool, name='get_this_tool'),

    path('remove_slide/<int:id>/<int:idquizz>', remove_slide, name='remove_slide'), # from a quizz
 
    #path('send_slide', send_slide, name='send_slide'), 
    path('slide_sorter', slide_sorter, name='slide_sorter'),


    ############## Random_quizz
    path('create_quizz_random/<int:id>', create_quizz_random, name='create_quizz_random'),

    path('list_qrandom', list_qrandom, name='list_qrandom'),
    path('create_qrandom', create_qrandom, name='create_qrandom'),
    path('update_qrandom/<int:id>', update_qrandom, name='update_qrandom'),
    path('delete_qrandom/<int:id>', delete_qrandom, name='delete_qrandom'),

    path('admin_qrandom/<int:id_level>', admin_qrandom, name='admin_qrandom'),
    path('create_qrandom_admin/<int:id_knowledge>/new', create_qrandom_admin, name='create_qrandom_admin'),
    path('update_qrandom_admin/<int:id_knowledge>/<int:id>', update_qrandom_admin, name='update_qrandom_admin'),
    path('show_qrandom_admin/<int:id>', show_qrandom_admin, name='show_qrandom_admin'),
    path('show_quizz_random/<int:id>', show_quizz_random, name='show_quizz_random'), 


    path('ajax_show_generated', ajax_show_generated, name='ajax_show_generated'),
    path('result_quizz/<int:id>', result_quizz, name='result_quizz'), 

    path('delete_historic_quizz/<int:id>', delete_historic_quizz, name='delete_historic_quizz'), 

 

    ############## Play
    path('play_printing_teacher/<int:id>', play_printing_teacher, name='play_printing_teacher'), 
    path('play_quizz_teacher/<int:id>/<int:idg>', play_quizz_teacher, name='play_quizz_teacher'),

    path('launch_play_quizz', launch_play_quizz, name='launch_play_quizz'),
    path('ajax_quizz_show_result', ajax_quizz_show_result, name='ajax_quizz_show_result'),


    path('play_quizz_student', play_quizz_student, name='play_quizz_student'),
    path('ajax_display_question_to_student', ajax_display_question_to_student, name='ajax_display_question_to_student'),   
    path('ajax_display_question_for_student', ajax_display_question_for_student, name='ajax_display_question_for_student'),   
    path('store_student_answer', store_student_answer, name='store_student_answer'),

    path('list_quizz_student', list_quizz_student, name='list_quizz_student'),
    
    path('goto_quizz_numeric/<int:id>', goto_quizz_numeric, name='goto_quizz_numeric'),
    path('goto_quizz_student/<int:id>', goto_quizz_student, name='goto_quizz_student'),

 
    path('ajax_show_my_result', ajax_show_my_result, name='ajax_show_my_result'),


    path('ajax_find_question', ajax_find_question, name='ajax_find_question'),
    path('get_this_question/<int:id>/<int:idquizz>', get_this_question, name='get_this_question'),



    path('ajax_show_detail_question', ajax_show_detail_question, name='ajax_show_detail_question'),
 
    path('ajax_show_retroaction', ajax_show_retroaction, name='ajax_show_retroaction'),
 


    ############## Visiocopie
    path('list_visiocopie', list_visiocopie, name='list_visiocopie'),
    path('cv<int:code>', create_visiocopie, name='create_visiocopie'),   
    path('cv', create_visiocopie, name='create_visiocopie_vierge'),   
    
    path('delete_visiocopie/<int:id>', delete_visiocopie, name='delete_visiocopie'),



    path('show_quizz_student/<int:idgq>', show_quizz_student, name='show_quizz_student'), 
] 