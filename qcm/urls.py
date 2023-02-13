#################################
#### Auteur : philipe Demaria 
#### pour SACADO
#################################
from django.urls import path, re_path
from .views import *
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [


    #################################################################
    # URL
    #################################################################

 

    path('fill_the_skills', fill_the_skills, name='fill_the_skills'),
    path('find_no_skill', find_no_skill, name='find_no_skill'),
    path('get_skill_to_support', get_skill_to_support, name='get_skill_to_support'),


    path('folders', list_folders, name='folders'),
    path('folders_archives', list_folders_archives, name='folders_archives'),
    #path('remove_parcours_folder', remove_parcours_folder, name='remove_parcours_folder'),
    #path('get_folder_to_folder', get_folder_to_folder, name='parcours'),

    path('parcours', list_parcours, name='parcours'),
    path('sequences', list_sequences, name='sequences'),
    path('evaluations', list_evaluations, name='evaluations'),
    path('archives', list_archives, name='archives'),
    path('evaluations_archives', list_evaluations_archives, name='evaluations_archives'),
    path('sequences_archives', list_sequences_archives, name='sequences_archives'),

    path('parcours_create/<int:idf>/', create_parcours, name='create_parcours'),
    path('parcours_create_evaluation/<int:idf>/', create_evaluation, name='create_evaluation'),
    path('parcours_evaluation_update/<int:id>/<int:idg>/', update_evaluation, name='update_evaluation'),
    path('parcours_evaluation_show/<int:id>/', show_evaluation, name='show_evaluation'), 

    path('parcours_create_sequence/<int:idf>/', create_sequence, name='create_sequence'),
    path('parcours_sequence_update/<int:id>/<int:idg>/', update_sequence, name='update_sequence'),
 

    path('parcours_update/<int:id>/<int:idg>/', update_parcours, name='update_parcours'),
    path('parcours_delete/<int:id>/<int:idg>/', delete_parcours, name='delete_parcours'), 
    path('parcours_dissociate/<int:id>/<int:idg>/', dissociate_parcours, name='dissociate_parcours'),

    path('parcours_archive/<int:id>/<int:idg>/', archive_parcours, name='archive_parcours'),
    path('parcours_unarchive/<int:id>/<int:idg>/', unarchive_parcours, name='unarchive_parcours'), 
    path('parcours_show/<int:idf>/<int:id>', show_parcours, name='show_parcours'), 

    path('parcours_folder/<int:idg>/', create_folder, name='create_folder'),
    path('parcours_folder_archive/<int:id>/<int:idg>/', folder_archive, name='folder_archive'),
    path('parcours_folder_unarchive/<int:id>/<int:idg>/', folder_unarchive, name='folder_unarchive'),
    path('parcours_update_folder/<int:id>/<int:idg>/', update_folder, name='update_folder'),
    path('parcours_delete_folder/<int:id>/<int:idg>/', delete_folder, name='delete_folder'),
    path('parcours_delete_folder_and_contents/<int:id>/<int:idg>/', delete_folder_and_contents, name='delete_folder_and_contents'),  
    path('parcours_delete_from_folder', parcours_delete_from_folder, name='parcours_delete_from_folder'), 

    path('ajax_charge_group_from_target', ajax_charge_group_from_target, name='ajax_charge_group_from_target'), 
    path('ajax_affectation_to_group', ajax_affectation_to_group, name='ajax_affectation_to_group'), 

    path('ajax_charge_folders', ajax_charge_folders, name='ajax_charge_folders'),
    path('ajax_course_charge_parcours', ajax_course_charge_parcours, name='ajax_course_charge_parcours'),
    path('ajax_built_diaporama', ajax_built_diaporama, name='ajax_built_diaporama'),

    path('this_parcours_to_sequences/<int:idp>', this_parcours_to_sequences, name='this_parcours_to_sequences'),


    path('parcours_tasks_and_publishes/<int:id>/', parcours_tasks_and_publishes, name='parcours_tasks_and_publishes'), # gestion des taches
    path('show_parcours_visual/<int:id>/', show_parcours_visual, name='show_parcours_visual'), 

    path('replace_exercise_into_parcours', replace_exercise_into_parcours, name='replace_exercise_into_parcours'), #Déplacer un execice de parcours

    path('actioner_pef', actioner_pef, name='actioner_pef'), #archiver ou supprimer une sélection

    path('actioner_course', actioner_course, name='actioner_course'), #archiver ou supprimer une sélection



    path('change_situations/<int:idf>/<int:idp>', change_situations_in_all_relationships , name='change_situations_in_all_relationships'),
    path('change_durations/<int:idf>/<int:idp>', change_durations_in_all_relationships , name='change_durations_in_all_relationships'),
    path('change_publications/<int:idf>/<int:idp>', change_publications_in_all_relationships , name='change_publications_in_all_relationships'),
    
    # Résultats d'un parcours
    path('parcours_result/<int:id>/<int:is_folder>', result_parcours, name='result_parcours'), 
    path('parcours_result_theme/<int:id>/<int:idt>/<int:is_folder>', result_parcours_theme, name='result_parcours_theme'),  # Je ne sais pas si cette route est utilisée ?????
    path('parcours_result_knowledge/<int:id>/<int:is_folder>', result_parcours_knowledge, name='result_parcours_knowledge'), 
    path('parcours_result_waiting/<int:id>/<int:is_folder>', result_parcours_waiting, name='result_parcours_waiting'), 

    path('parcours_progression/<int:id>/<int:idg>', parcours_progression, name='parcours_progression'),
    path('parcours_progression_student/<int:id>', parcours_progression_student, name='parcours_progression_student'),

    path('parcours_detail_task/<int:id>/<int:s>/<int:c>/', detail_task_parcours, name='detail_task_parcours'), #modif idp en id pour la sécurité
    path('parcours_exercises/<int:id>/', parcours_exercises, name='parcours_exercises'),  # student_list_exercises

    path('parcourses_all/<int:is_eval>/', all_parcourses, name='all_parcourses'),
    path('folders_all/0/', all_folders, name='all_folders'), 

    path('exercise_parcours_duplicate', exercise_parcours_duplicate, name='exercise_parcours_duplicate'), 
    path('duplicate_folder', duplicate_folder, name='duplicate_folder'), 


    
    path('parcours_clone/<int:id>/<int:course_on>', clone_parcours, name='clone_parcours'),
    path('parcours_clone_folder/<int:id>', clone_folder, name='clone_folder'),
    path('parcours_group/<int:id>/', list_parcours_group, name='list_parcours_group'), # parcours d'un groupe
    path('parcours_sub_parcours/<int:idg>/<int:idf>/', list_sub_parcours_group, name='list_sub_parcours_group'), # parcours d'un dossier
    path('list_sub_parcours_group_student/<int:idg>/<int:idf>/', list_sub_parcours_group_student, name='list_sub_parcours_group_student'), # parcours d'un parcours
    path('ajax_subparcours_check', ajax_subparcours_check, name='ajax_subparcours_check'), # parcours d'un parcours


    path('parcours_peuplate/<int:id>/', peuplate_parcours, name='peuplate_parcours'),
    path('parcours_individualise/<int:id>/', individualise_parcours, name='individualise_parcours'),#modif idp en id pour la sécurité
    path('ajax_populate', ajax_populate, name='ajax_populate'),
    path('ajax_individualise', ajax_individualise , name='ajax_individualise'),
    path('ajax_reset', ajax_reset , name='ajax_reset'),

    path('result_parcours_exercise_students/<int:id>/', result_parcours_exercise_students, name='result_parcours_exercise_students'),#modif idp en id pour la sécurité
    path('result_parcours_skill/<int:id>/', result_parcours_skill, name='result_parcours_skill'),#modif idp en id pour la sécurité
    path('result_parcours_exercises/<int:idf>/<int:id>/', result_parcours_exercises, name='result_parcours_exercises'),#modif idp en id pour la sécurité

    path('remove_students_from_parcours', remove_students_from_parcours, name='remove_students_from_parcours'),


    path('parcours_peuplate_evaluation/<int:id>/', peuplate_parcours_evaluation, name='peuplate_parcours_evaluation'),

    path('parcours_stat_evaluation/<int:id>/', stat_evaluation, name='stat_evaluation'), 
    path('stat_evaluation_group/<int:id>/<int:idg>', stat_evaluation_group, name='stat_evaluation_group'), 


    path('redo_evaluation', redo_evaluation, name='redo_evaluation'), 

    path('getter_parcours_exercice_custom', ajax_getter_parcours_exercice_custom, name='ajax_getter_parcours_exercice_custom'),

    path('parcours_get_exercise_custom', ajax_parcours_get_exercise_custom, name='ajax_parcours_get_exercise_custom'),
    path('parcours_clone_exercise_custom', parcours_clone_exercise_custom, name='parcours_clone_exercise_custom'),

    path('parcours_clone_course', ajax_parcours_clone_course, name='ajax_parcours_clone_course'),
    path('parcours_shower_course', ajax_parcours_shower_course, name='ajax_parcours_shower_course'),
    path('ajax_course_custom_for_this_parcours', ajax_course_custom_for_this_parcours, name='ajax_course_custom_for_this_parcours'),

    
    path('ajax/course_viewer', ajax_course_viewer, name='ajax_course_viewer'),
    path('parcours_get_course', ajax_parcours_get_course, name='ajax_parcours_get_course'),
    path('ajax_individualise_this_exercise', ajax_individualise_this_exercise, name='ajax_individualise_this_exercise'),
    path('ajax_individualise_this_document', ajax_individualise_this_document, name='ajax_individualise_this_document'),

    path('ajax_is_calculator', ajax_is_calculator, name='ajax_is_calculator'), 

    path('ajax_reset_this_exercise', ajax_reset_this_exercise, name='ajax_reset_this_exercise'),

    path('real_time/<int:id>', real_time, name='real_time'),
    path('ajax_real_time_live', ajax_real_time_live, name='ajax_real_time_live'),

    #####################################  Modifie les relations par parcours et exercices  ##############################################################  
    path('<int:idp>/<int:ide>/', execute_exercise, name='execute_exercise'),#modif idp en id pour la sécurité 
    ######################################################################################################################################################
    path('practice_group/<int:idf>/<int:idp>', practice_group, name='practice_group'), # Groupe de besoins
    path('recap_parcours/<int:idf>/<int:idp>', recap_parcours, name='recap_parcours'), # Listes de exercices donnés par élèves lors d'une individualisation ou d'un parcours IA
    path('print_practice_group', print_practice_group, name='print_practice_group'), # Impression des groupes de besoins


    path('print_kgroups/<int:idf>/<int:idp>/<slug:slug>', print_kgroups, name='print_kgroups'), # Impression des groupes de besoins
    path('delete_kgroups/<int:idf>/<int:idp>/<slug:slug>', delete_kgroups, name='delete_kgroups'), # Suppression des groupes de besoins
    ######################################################################################################################################################
    #################################       IA        ####################################################################################################
    ######################################################################################################################################################
    path('get_target_ia/<int:idp>', get_target_ia, name='get_target_ia'),
    path('create_test_ia/<int:idp>', create_test_ia, name='create_test_ia'),
    path('create_parcours_ia_assisted/<int:idf>/<int:idp>', create_parcours_ia_assisted, name='create_parcours_ia_assisted'),
    ######################################################################################################################################################
    ######################################################################################################################################################
    ######################################################################################################################################################


    path('associate_parcours/<int:id>/', associate_parcours, name='associate_parcours'),  # id est l'id du groupe auquel le parcours est associé
    path('parcours_aggregate',  aggregate_parcours, name='aggregate_parcours'), 
    path('ajax_parcoursinfo/', ajax_parcoursinfo, name='ajax_parcoursinfo'),    
    path('exercises', list_exercises, name='exercises'),
    path('ajax_list_exercises_by_level', ajax_list_exercises_by_level, name='ajax_list_exercises_by_level'),    
    path('ajax_list_exercises_by_level_and_theme', ajax_list_exercises_by_level_and_theme, name='ajax_list_exercises_by_level_and_theme'), 

    path('ajax/chargethemes', ajax_chargethemes, name='ajax_chargethemes'),
    path('ajax/chargeknowledges', ajax_chargeknowledges, name='ajax_chargeknowledges'),


    path('admin_supportfiles/<int:id>', admin_list_supportfiles, name='admin_supportfiles'),
    path('admin_associations/<int:id>', admin_list_associations, name='admin_associations'),
    path('admin_associations_ebep/<int:id>', admin_list_associations_ebep, name='admin_associations_ebep'),
    path('gestion_supportfiles', gestion_supportfiles, name='gestion_supportfiles'),

    path('ajax_update_association', ajax_update_association, name='ajax_update_association'),

    ######################################################################################################################################################
    #################################       Supportfile        ###########################################################################################
    ######################################################################################################################################################
    path('create_supportfile/<int:qtype>/<int:ids>', create_supportfile, name='create_supportfile'),
    path('admin/<int:id>', create_supportfile_knowledge, name='create_supportfile_knowledge'),
    path('update_supportfile/<int:id>/', update_supportfile, name='update_supportfile'),
    path('delete_supportfile/<int:id>/', delete_supportfile, name='delete_supportfile'), 

    path('supportfile_creator/<int:idq>', supportfile_creator, name='supportfile_creator'), 

    path('show_this_supportfile/<int:id>/', show_this_supportfile, name='show_this_supportfile'),  #from dashboard 
    path('create_exercise/<int:supportfile_id>/', create_exercise, name='create_exercise'), 

    path('my_own_exercises', my_own_exercises, name='my_own_exercises'), 
    path('ajax_assign_exercise_to_parcours', ajax_assign_exercise_to_parcours, name='ajax_assign_exercise_to_parcours'), 

    path('parcours_show_write_exercise/<int:id>/', show_write_exercise, name='show_write_exercise'), 
    #################################   Autre type de supportfile        
    path('ajax_knowledge_skills_subject_levels', ajax_knowledge_skills_subject_levels, name='ajax_knowledge_skills_subject_levels'),
    path('ajax_get_skills', ajax_get_skills, name='ajax_get_skills'),
    path('ajax_theme_exercice', ajax_theme_exercice, name='ajax_theme_exercice'),
    path('ajax_theme_subject_levels', ajax_theme_subject_levels, name='ajax_theme_subject_levels'),
    path('ajax_load_modal', ajax_load_modal, name='ajax_load_modal'), 

    #################################   Gestion des solutions par type d'exercice
    path('check_solution_vf'          , check_solution_vf          , name='check_solution_vf'),
    path('check_solution_answers'     , check_solution_answers     , name='check_solution_answers'),
    path('check_solution_qcm_numeric' , check_solution_qcm_numeric , name='check_solution_qcm_numeric'),
    path('check_solution_pairs'       , check_solution_pairs       , name='check_solution_pairs'),
    path('check_solution_regroup'     , check_solution_regroup       , name='check_solution_regroup'),
    path('check_anagram_answers'      , check_anagram_answers      , name='check_anagram_answers'),    
    path('check_sort_answers'         , check_sort_answers         , name='check_sort_answers'),    
    path('check_filltheblanks_answers', check_filltheblanks_answers, name='check_filltheblanks_answers'),

    path('check_grid_answers'         , check_grid_answers         , name='check_grid_answers'),
    path('check_secret_answers'       , check_secret_answers       , name='check_secret_answers'),
    path('ajax_secret_letter'         , ajax_secret_letter         , name='ajax_secret_letter'),
    path('check_memo_answers'         , check_memo_answers         , name='check_memo_answers'),
    path('check_image_answers'        , check_image_answers        , name='check_image_answers'),    
    path('check_axe_answers'          , check_axe_answers          , name='check_axe_answers'),
 

    #################################  Enregistrement des solutions par type d'exercice
    path('store_the_score_relation_ajax/', store_the_score_relation_ajax, name='store_the_score_relation_ajax'),
    ######################################################################################################################################################
    #################################           Autre          ###########################################################################################
    ######################################################################################################################################################

    path('ajax_customexercises_subjects_levels', ajax_customexercises_subjects_levels, name='ajax_customexercises_subjects_levels'),
    path('ajax_customexercises_skills', ajax_customexercises_skills, name='ajax_customexercises_skills'),
    path('ajax_customexercises_themes', ajax_customexercises_themes, name='ajax_customexercises_themes'),
    path('ajax_customexercises_knowledges', ajax_customexercises_knowledges, name='ajax_customexercises_knowledges'),

    path('change_knowledge', change_knowledge, name='change_knowledge'), 

    path('show_this_exercise/<int:id>/', show_this_exercise, name='show_this_exercise'),  #from dashboard 

    path('show_this_exercise_test/<int:id>/', show_this_exercise_test, name='show_this_exercise_test'),  #from dashboard 



    path('show_custom_sequence/<int:idc>/', show_custom_sequence, name='show_custom_sequence'),

    path('show_exercise/<int:id>/', show_exercise, name='show_exercise'),       #from index  
    path('exercises_level/<int:id>/', exercises_level , name='exercises_level'), 
    path('content_is_done/<int:id>/', content_is_done , name='content_is_done'), 
    path('relation_is_done/<int:id>/', relation_is_done , name='relation_is_done'), 

    path('show_all_type_exercise/<int:ids>/', show_all_type_exercise, name='show_all_type_exercise'),


    path('exercises_level_subject/<int:id>/<int:subject_id>', exercises_level_subject , name='exercises_level_subject'), 


    path('delete_relationship/<int:idr>/', delete_relationship, name='delete_relationship'),
    path('delete_relationship_by_individualise/<int:idr>/<int:id>/', delete_relationship_by_individualise, name='delete_relationship_by_individualise'),#modif idp en id pour la sécurité

    path('create_remediation/<int:idr>/', create_remediation, name='create_remediation'),
    path('update_remediation/<int:idr>/<int:id>/', update_remediation, name='update_remediation'),
    path('delete_remediation/<int:id>/', delete_remediation, name='delete_remediation'),  

    ####################################### Export Pronote #####################################################
    path('export_note_custom/<int:id>/<int:idp>', export_note_custom, name='export_note_custom'),   
    path('export_note/<int:idg>/<int:idp>/', export_note, name='export_note'),  


    path('detail_task/<int:id>/<int:s>/', detail_task, name='detail_task'), #modif idp en id pour la sécurité
    path('tasks', all_my_tasks, name='all_my_tasks'),
    path('all_tasks', these_all_my_tasks, name='these_all_my_tasks'),    
    path('group_tasks/<int:id>', group_tasks, name='group_tasks'), #taches en cours du groupe
    path('group_tasks_all/<int:id>', group_tasks_all, name='group_tasks_all'), #taches du groupe

    path('my_child_tasks/<int:id>', my_child_tasks, name='my_child_tasks'), #taches du groupe 
    #################################### Les cours dans les parcours ###########################################

    path('parcours_my_courses', list_courses, name='courses'),
    path('parcours_my_courses_archives', list_courses_archives, name='courses_archives'),
    path('parcours_create_course/<int:idc>/<int:id>', create_course, name='create_course'), # id = id du parcours, idc = id du cours
    path('parcours_update_course/<int:idc>/<int:id>', update_course, name='update_course'),
    path('parcours_delete_course/<int:idc>/<int:id>', delete_course, name='delete_course'),
    path('parcours_show_course/<int:idc>/<int:id>', show_course, name='show_course'),
    path('show_one_course/<int:idc>', show_one_course, name='show_one_course'),

    path('create_course_sequence/<int:id>', create_course_sequence, name='create_course_sequence'),
    path('create_custom_sequence/<int:id>', create_custom_sequence, name='create_custom_sequence'),

    path('clone_course_sequence/<int:idc>', clone_course_sequence, name='clone_course_sequence'),

    path('peuplate_course_parcours/<int:idp>', peuplate_course_parcours, name='peuplate_course_parcours'),
    path('ajax_find_peuplate_sequence', ajax_find_peuplate_sequence, name='ajax_find_peuplate_sequence'), 

    path('peuplate_custom_parcours/<int:idp>', peuplate_custom_parcours, name='peuplate_custom_parcours'),
    path('clone_custom_sequence/<int:idc>', clone_custom_sequence, name='clone_custom_sequence'),    

    path('parcours_show_course_student/<int:idc>/<int:id>', show_course_student, name='show_course_student'),
    path('show_course_sequence_student/<int:idc>/<int:id>', show_course_sequence_student, name='show_course_sequence_student'),


    path('parcours_show_courses_from_folder/<int:idf>/0', show_courses_from_folder, name='show_courses_from_folder'),  
    path('parcours_only_create_course/0', only_create_course, name='only_create_course'), 
    path('parcours_only_update_course/<int:idc>', only_update_course, name='only_update_course'), 

    path('get_course_in_this_parcours/<int:id>', get_course_in_this_parcours, name='get_course_in_this_parcours'), 
    path('get_this_course_for_this_parcours/<int:typ>/<int:id_target>/<int:idp>', get_this_course_for_this_parcours, name='get_this_course_for_this_parcours'), 


    path('ajax_show_hide_course', ajax_show_hide_course, name='ajax_show_hide_course'),
    
    ############################################################################################################  
    path('exercise_custom_show_shared', exercise_custom_show_shared, name='exercise_custom_show_shared'),  
    path('customexercise_shared_inside_parcours/<int:idp>', customexercise_shared_inside_parcours, name='customexercise_shared_inside_parcours'),  


    #################################### Mastering #############################################################

    path('parcours_create_mastering/<int:id>/', create_mastering, name='create_mastering'),
    path('parcours_mastering_delete/<int:id>/<int:idm>/', parcours_mastering_delete, name='parcours_mastering_delete'),
    path('ajax/sort_mastering', ajax_sort_mastering, name='ajax_sort_mastering'),

    path('parcours_mastering_student_show/<int:id>/', mastering_student_show, name='mastering_student_show'),
    path('ajax/mastering_modal_show', ajax_mastering_modal_show, name='ajax_mastering_modal_show'),    
    path('parcours_mastering_done', mastering_done, name='mastering_done'),    
    path('ajax_populate_mastering', ajax_populate_mastering, name='ajax_populate_mastering'),
    ############################################################################################################ 
    #################################### Mastering_custom ######################################################

    path('parcours_create_mastering_custom/<int:id>/<int:idp>', create_mastering_custom , name='create_mastering_custom'),
    path('parcours_mastering_custom_delete/<int:id>/<int:idm>/<int:idp>', parcours_mastering_custom_delete, name='parcours_mastering_custom_delete'),
    path('ajax/sort_mastering_custom', ajax_sort_mastering_custom, name='ajax_sort_mastering_custom'),

    path('parcours_mastering_student_show_custom/<int:id>/', mastering_custom_student_show, name='mastering_custom_student_show'),
    path('ajax/mastering_custom_modal_show', ajax_mastering_custom_modal_show, name='ajax_mastering_custom_modal_show'),    
    path('parcours_mastering_custom_done', mastering_custom_done, name='mastering_custom_done'),    
 

    path('ajax_locker_exercise', ajax_locker_exercise, name='ajax_locker_exercise'), 
 

    path('ajax_this_course_viewer', ajax_this_course_viewer, name='ajax_this_course_viewer'), 
    ############################################################################################################ 
    ############################################################################################################  

    path('show_canvas', show_canvas, name='show_canvas'), 
    path('get_values_canvas', get_values_canvas, name='get_values_canvas'), 

    ####################################     Les demandes d'exercice  ##########################################

    path('parcours_demands', list_demands, name='demands'),
    path('parcours_create_demand', create_demand, name='create_demand'),  
    path('parcours_update_demand/<int:id>', update_demand, name='update_demand'),
    path('parcours_delete_demand/<int:id>', delete_demand, name='delete_demand'),
    path('parcours_show_demand/<int:id>', show_demand, name='show_demand'),

    ############################################# IA  #########################################################  
    path('create_parcours_after_results/<int:idq>/<int:idp>', create_parcours_after_results , name='create_parcours_after_results'),
    #path('create_dataset/<int:idq>/<int:idp>', create_dataset , name='create_parcours_after_results'),



    ############################################################################################################  
 
    path('advises', advises, name='advises'),   

    path('exercise_error', exercise_error, name='exercise_error'),
    path('exercise_error_peda', exercise_peda, name='exercise_peda'),
    path('ajax_detail_parcours/', ajax_detail_parcours , name='ajax_detail_parcours'),
    path('add_exercice_in_a_parcours', add_exercice_in_a_parcours, name='add_exercice_in_a_parcours'),  
    path('show_remediation/<int:id>/', show_remediation, name='show_remediation'),       #from index   


    path('ajax/demand_done', ajax_demand_done, name='ajax_demand_done'),

    path('ajax/create_title_parcours', ajax_create_title_parcours, name='ajax_create_title_parcours'),
    path('ajax/erase_title', ajax_erase_title, name='ajax_erase_title'),

    path('ajax/parcours_default', ajax_parcours_default , name='ajax_parcours_default'),
    path('get_parcours_default/', get_parcours_default , name='get_parcours_default'),

    path('ajax_is_favorite', ajax_is_favorite, name='ajax_is_favorite'),
    path('ajax/course_sorter', ajax_course_sorter, name='ajax_course_sorter'),
    path('ajax/parcours_sorter', ajax_parcours_sorter, name='ajax_parcours_sorter'),
    path('ajax/folders_sorter', ajax_folders_sorter, name='ajax_folders_sorter'),

    path('ajax_is_active', ajax_is_active, name='ajax_is_active'),


    path('parcours_show_student/<int:id>', show_parcours_student, name='show_parcours_student'), 
    path('asking_parcours_sacado/<int:pk>', asking_parcours_sacado, name='asking_parcours_sacado'), # pk est la clé du group 


    path('ajax/sort_supportfile', ajax_sort_supportfile, name='ajax_sort_supportfile'),
    path('ajax_sort_exercise_from_admin', ajax_sort_exercise_from_admin, name='ajax_sort_exercise_from_admin'),

    path('ajax_search_exercise', ajax_search_exercise, name='ajax_search_exercise'),
    path('ajax_knowledge_exercise', ajax_knowledge_exercise, name='ajax_knowledge_exercise'),


    path('ajax_level_exercise', ajax_level_exercise, name='ajax_level_exercise'),
    path('ajax/sort_exercise', ajax_sort_exercise, name='ajax_sort_exercise'),
    path('ajax/sort_sequence', ajax_sort_sequence, name='ajax_sort_sequence'),
    path('ajax/publish', ajax_publish, name='ajax_publish'),  
    path('ajax/publish_parcours', ajax_publish_parcours, name='ajax_publish_parcours'),
    path('ajax_sharer_parcours', ajax_sharer_parcours, name='ajax_sharer_parcours'),

    path('ajax_publish_course', ajax_publish_course, name='ajax_publish_course'),
    path('ajax_sharer_course', ajax_sharer_course, name='ajax_sharer_course'),


    path('ajax/dates', ajax_dates, name='ajax_dates'), 
    path('ajax/skills', ajax_skills, name='ajax_skills'), 
    path('ajax/notes', ajax_notes, name='ajax_notes'), 
    path('ajax/maxexo', ajax_maxexo, name='ajax_maxexo'), 
    path('ajax/coefficient', ajax_coefficient, name='ajax_coefficient'), 
    path('ajax/delete_notes', ajax_delete_notes, name='ajax_delete_notes'), 
    path('ajax/remediation', ajax_remediation, name='ajax_remediation'),

    path('ajax/remediation_viewer', ajax_remediation_viewer , name='ajax_remediation_viewer'),
    path('json_create_remediation/<int:idr>/<int:idp>/<int:typ>', json_create_remediation, name='json_create_remediation'),  # création via la modal sans rechargement de la page
    path('json_delete_remediation/<int:id>/<int:idp>/<int:typ>', json_delete_remediation, name='json_delete_remediation'),   # suppression via la modal sans rechargement de la page    
    path('audio_remediation', audio_remediation, name='audio_remediation'),   


    path('audio_exercise', audio_exercise, name='audio_exercise'),  #Audio pour les EBEP  

    path('ajax/constraint_create', ajax_create_constraint, name='ajax_create_constraint'),
    path('ajax/constraint_delete', ajax_delete_constraint, name='ajax_delete_constraint'), 
    path('ajax/infoExo', ajax_infoExo, name='ajax_infoExo'),


    path('list_parcours_quizz_student/<int:idp>/', list_parcours_quizz_student, name='list_parcours_quizz_student'),
    path('list_parcours_bibliotex_student/<int:idp>/', list_parcours_bibliotex_student, name='list_parcours_bibliotex_student'),
    path('list_parcours_flashpack_student/<int:idp>/', list_parcours_flashpack_student, name='list_parcours_flashpack_student'),

    path('parcours_show_bibliotex_student/<int:idp>/<int:id>', parcours_show_bibliotex_student, name='parcours_show_bibliotex_student'),

    # page de création d'un exercice non auto-corrigé dans un parcours - l'id est celui du parcours.
    path('parcours_create_custom_exercise/<int:id>/<int:typ>', parcours_create_custom_exercise, name='parcours_create_custom_exercise'), 
    path('parcours_update_custom_exercise/<int:idcc>/<int:id>', parcours_update_custom_exercise, name='parcours_update_custom_exercise'), 
    path('parcours_delete_custom_exercise/<int:idcc>/<int:id>', parcours_delete_custom_exercise, name='parcours_delete_custom_exercise'), 
    path('parcours_show_custom_exercise/<int:id>/<int:idp>',  show_custom_exercise, name='show_custom_exercise'), # vue enseignant de l'exercice
 
 

 
    path('simulator', simulator, name='simulator'),
    #####################################################################################################################################
    ####################################### Testeurs 
    #####################################################################################################################################
    path('admin_testeur',  admin_testeur, name='admin_testeur'), 
    path('reporting',  reporting, name='reporting'), 
    path('reporting_list/<int:code>',  reporting_list, name='reporting_list'), 
    path('repaired_reporting/<int:pk>/<int:code>',  repaired_reporting, name='repaired_reporting'), 


    #####################################################################################################################################
    ####################################### Correction 
    #####################################################################################################################################

    path('correction_exercise/<int:id>/<int:idp>/<int:ids>', correction_exercise, name='correction_exercise'),  #from details_card 
    # Evaluation des exercices non auto corrigé
    path('ajax_choose_student', ajax_choose_student, name='ajax_choose_student'),
    path('ajax_exercise_evaluate', ajax_exercise_evaluate, name='ajax_exercise_evaluate'),
    path('ajax_comment_all_exercise', ajax_comment_all_exercise, name='ajax_comment_all_exercise'),
    path('ajax_audio_comment_all_exercise', ajax_audio_comment_all_exercise, name='ajax_audio_comment_all_exercise'),
    path('write_exercise/<int:id>', write_exercise, name='write_exercise'), # page dans laquelle l'élève repond à l'exercice non auto-corrigé - l'id est celui de la relation.


    path('ajax_save_annotation', ajax_save_annotation, name='ajax_save_annotation'),  #from details_card 
    path('ajax_remove_annotation', ajax_remove_annotation, name='ajax_remove_annotation'),  #from details_card 
    
    path('write_custom_exercise/<int:id>/<int:idp>', write_custom_exercise, name='write_custom_exercise'), 
    path('ajax_mark_evaluate', ajax_mark_evaluate, name='ajax_mark_evaluate'),

    path('ajax_create_or_update_appreciation', ajax_create_or_update_appreciation, name='ajax_create_or_update_appreciation'),
    path('ajax_remove_my_appreciation', ajax_remove_my_appreciation, name='ajax_remove_my_appreciation'),

    path('ajax_read_my_production', ajax_read_my_production, name='ajax_read_my_production'),

    path('ajax_annotate_exercise_no_made', ajax_annotate_exercise_no_made, name='ajax_annotate_exercise_no_made'),    
    path('ajax_delete_custom_answer_image', ajax_delete_custom_answer_image, name='ajax_delete_custom_answer_image'),

    path('export_notes_after_evaluation', export_notes_after_evaluation, name='export_notes_after_evaluation'),
    path('export_skills_after_evaluation', export_skills_after_evaluation, name='export_skills_after_evaluation'),
    path('export_results_after_evaluation', export_results_after_evaluation, name='export_results_after_evaluation'),
    path('export_knowledges_after_evaluation', export_knowledges_after_evaluation, name='export_knowledges_after_evaluation'),
    path('export_result_parcours_exercises', export_result_parcours_exercises, name='export_result_parcours_exercises'),

    path('ajax/chargethemes_parcours', ajax_chargethemes_parcours, name='ajax_chargethemes_parcours'),
    path('ajax/chargethemes_exercise', ajax_chargethemes_exercise, name='ajax_chargethemes_exercise'),

    path('ajax_all_parcourses', ajax_all_parcourses, name='ajax_all_parcourses'),  
    path('ajax_all_folders', ajax_all_folders, name='ajax_all_folders'),  
    path('ajax_course_custom_show_shared', ajax_course_custom_show_shared, name='ajax_course_custom_show_shared'), 


    path('all_courses', all_courses, name='all_courses'), 
     


    path('ajax_closer_exercise', ajax_closer_exercise, name='ajax_closer_exercise'),
    path('ajax_correction_viewer', ajax_correction_viewer, name='ajax_correction_viewer'),

    path('ajax_save_canvas', ajax_save_canvas, name='ajax_save_canvas'),
    
    #####################################################################################################################################
    #####################################################################################################################################
    ######################################################################################################################################################

    path('get_seconde_to_math_comp', get_seconde_to_math_comp, name='get_seconde_to_math_comp'),  # id est l'id du groupe auquel le parcours est associé


    path('ajax_add_criterion', ajax_add_criterion, name='ajax_add_criterion'),
    path('ajax_auto_evaluation', ajax_auto_evaluation, name='ajax_auto_evaluation'), 

 ]
