
from django.urls import path, re_path
from .views import *

urlpatterns = [

    re_path(r'^$', index, name='index'),

    re_path('dash_student', dash_student, name='dash_student'),

    re_path('get_cookie', get_cookie , name='get_cookie'),

    re_path('send_message', send_message, name='send_message'),
    path('rgpd', rgpd, name='rgpd'), 
    path('gar_rgpd', gar_rgpd, name='gar_rgpd'), 
    path('cgv', cgv, name='cgv'), 
    path('cgu', cgu, name='cgu'), 
    path('mentions', mentions, name='mentions'), 
    path('mentions_academy', mentions_academy, name='mentions_academy'), 

    path('admin_tdb', admin_tdb, name='admin_tdb'),

    path('exercises_shower/<int:idl>', exercises_shower, name='exercises_shower'),
    ############################################################################################
    #######  SACADO Académie
    ############################################################################################
    path('academy', academy, name='academy'), 
    path('student_to_association', student_to_association, name='student_to_association'),     
    path('choice_menu/<int:id>', choice_menu, name='choice_menu'), 
    path('details_of_adhesion', details_of_adhesion, name='details_of_adhesion'), 
    path('commit_adhesion', commit_adhesion, name='commit_adhesion'), 
    #path('save_adhesion', save_adhesion, name='save_adhesion'), 
    path('adhesions_academy', adhesions_academy, name='adhesions_academy'), 
    path('delete_adhesion', delete_adhesion, name='delete_adhesion'), 
    path('ajax_remboursement', ajax_remboursement, name='ajax_remboursement'),
    path('add_adhesion', add_adhesion, name='add_adhesion'),
    path('change_adhesion/<int:ids>', change_adhesion, name='change_adhesion'),  
    path('ajax_price_changement_formule', ajax_price_changement_formule, name='ajax_price_changement_formule'),

    path('save_renewal_adhesion', save_renewal_adhesion, name='save_renewal_adhesion'),
    path('accept_renewal_adhesion', accept_renewal_adhesion, name='accept_renewal_adhesion'),
    path('list_exercises_academy/<int:id>', list_exercises_academy, name='academy_level'),
    path('logout_academy', logout_academy , name='logout_academy'), 
    path('renewal_adhesion', renewal_adhesion, name='renewal_adhesion'),
    path('ajax_prices_formule', ajax_prices_formule, name='ajax_prices_formule'),
    path('ajax_tarifications_formule', ajax_tarifications_formule, name='ajax_tarifications_formule'),
    
    path('questionnaire', questionnaire, name='questionnaire'),
    ############################################################################################
    #######  Academy
    ############################################################################################
    path('acad_exercises', acad_exercises, name='acad_exercises'), 
    path('parents', parents, name='parents'),
    path('numeric', numeric, name='numeric'),
    path('contact', contact, name='contact'),
    path('advises_index', advises_index, name='advises_index'),
    path('faq', faq, name='faq'),
    path('who_is', who_is, name='who_is'),

    ############################################################################################
    #######  Paiement CA
    ############################################################################################
    path("paiement",paiement,name="paiement"),
    path("paiement_retour/<str:status>",paiement_retour,name="paiement_retour")

]


 
