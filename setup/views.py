from django.conf import settings # récupération de variables globales du settings.py
from django.shortcuts import render,redirect
from django.forms import formset_factory
 
from django.contrib.auth import   logout , login, authenticate
from django.contrib.auth.forms import  UserCreationForm,  AuthenticationForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.forms import BaseFormSet
from django.utils import formats, timezone
from django.contrib import messages
 
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
from django.core.mail import send_mail, EmailMessage

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from django.db.models import Count, Q

from account.decorators import is_manager_of_this_school
from account.forms import  UserForm, TeacherForm, StudentForm , BaseUserFormSet , NewpasswordForm, DescriptionForm
from account.models import  User, Teacher, Student  , Parent , Adhesion , Facture
from association.models import Accounting , Detail , Rate , Abonnement , Holidaybook , Activeyear
from group.models import Group, Sharing_group
from group.views import student_dashboard
from qcm.models import Folder , Parcours, Exercise,Relationship,Studentanswer, Supportfile, Customexercise, Customanswerbystudent,Writtenanswerbystudent
from sendmail.models import Communication
from setup.forms import WebinaireForm , TweeterForm
from setup.models import Formule , Webinaire , Tweeter , Formuleprice
from school.models import Stage , School
from school.forms import  SchoolForm
from school.gar import *
from socle.models import Level, Subject
from lesson.models import ConnexionEleve
from tool.models import Quizz, Question, Choice , Positionnement
from bibliotex.models import Exotex
from datetime import date, datetime , timedelta

from itertools import chain
from general_fonctions import *
from payment_fonctions import *

import random
import pytz
import uuid
import time
import os
import fileinput 
import json

# le necessaire pour le module de paiement du CA
import hmac
# from Crypto.Signature import PKCS1_v1_5
# from Crypto.PublicKey import RSA
# from Crypto.Hash import SHA
from urllib.parse import unquote
import base64


##############   bibliothèques pour les impressions pdf    #########################
import os
from pdf2image import convert_from_path # convertit un pdf en autant d'images que de pages du pdf
from django.utils import formats, timezone
from io import BytesIO, StringIO
from django.http import  HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, inch, landscape , letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image , PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import yellow, red, black, white, blue
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.enums import TA_JUSTIFY,TA_LEFT,TA_CENTER,TA_RIGHT 
############## FIN bibliothèques pour les impressions pdf  #########################



def attribute_student_toindex() :
    folders = Folder.objects.filter(students=None)
    for folder in folders :
        level = folder.level
        student = Student.objects.filter(level = level , user__username__contains="_e-test_").first()
        folder.students.add(student)

    parcourses = Parcours.objects.filter(students=None)
    for parcours in parcourses :
        level = parcours.level
        student = Student.objects.filter(level = level , user__username__contains="_e-test_").first()
        parcours.students.add(student)



def end_of_contract() :

    data = {}
    date = datetime.now()

    if date.month < 6 :
        end = date.year
    else :
        end = int(date.year) + 1
    return end


def index(request):

    try :
        del request.session["answerpositionnement"]
        del request.session["student"]
        del request.session["positionnement_id"]
    except :
        pass

    if request.user.is_authenticated :
        index_tdb = True  # Permet l'affichage des tutos Youtube dans le dashboard
  
        today = time_zone_user(request.user)
        
        request.session["tdb"] = "Groups"
        if request.session.has_key("subtdb"): del request.session["subtdb"]

        ############################################################################################
        #### Mise à jour et affichage des publications  
        ############################################################################################  
        # relationships = Relationship.objects.filter(is_publish = 0,start__lte=today)
        # for r in relationships :
        #     Relationship.objects.filter(id=r.id).update(is_publish = 1)

        # parcourses = Parcours.objects.filter(start__lte=today).exclude(start = None)
        # for p in parcourses :
        #     Parcours.objects.filter(id=p.id).update(is_publish = 1)

        # customexercises = Customexercise.objects.filter(start__lte=today).exclude(start = None)
        # for c in customexercises :
        #     Customexercise.objects.filter(id=c.id).update(is_publish = 1)
        ############################################################################################
        #### Fin de Mise à jour et affichage des publications
        ############################################################################################
        timer = today.time()

        if request.user.last_login.date() != today.date() :
            request.user.last_login = today
            request.user.save()

        if request.user.is_teacher:

            teacher = request.user.teacher
            grps = teacher.groups.all() 
            shared_grps_id = Sharing_group.objects.filter(teacher=teacher).values_list("group_id", flat=True) 
            # sgps = []
            # for sg_id in shared_grps_id :
            #     grp = Group.objects.get(pk=sg_id)
            #     sgps.append(grp)

            sgps    = Group.objects.filter(pk__in=shared_grps_id)
            groupes =  grps | sgps
            groups  = groupes.order_by("level__ranking") 
            this_user = request.user
            nb_teacher_level = teacher.levels.count()
            relationships = Relationship.objects.filter(Q(is_publish = 1)|Q(start__lte=today), parcours__teacher=teacher, date_limit__gte=today).order_by("date_limit").order_by("parcours")
            folders_tab = teacher.teacher_folders.filter(students=None, is_favorite=1, is_archive=0 ,is_trash=0 ).exclude(teacher__user__username__contains="_e-test") ## Dossiers  favoris non affectés
            teacher_parcours = teacher.teacher_parcours
            parcours_tab = teacher_parcours.filter(students=None, is_favorite=1, is_archive=0 ,is_trash=0 ).exclude(teacher__user__username__contains="_e-test").order_by("is_evaluation") ## Parcours / évaluation favoris non affecté
            
            #Menu_right
            parcourses = teacher_parcours.filter(is_evaluation=0, is_favorite =1, is_archive=0,  is_trash=0 ).order_by("-is_publish")
            communications = Communication.objects.values('id', 'subject', 'texte', 'today').filter(active=1).order_by("-id")

            connexion_lessons = ConnexionEleve.objects.filter(event__user=this_user, is_done = 0)

            webinaire = Webinaire.objects.filter(date_time__gte=today,is_publish=1).first()
 
            template = 'dashboard.html'
            context = {'this_user': this_user, 'teacher': teacher, 'groups': groups,  'parcours': None, 'today' : today , 'timer' : timer , 'nb_teacher_level' : nb_teacher_level , 
                       'relationships': relationships, 'parcourses': parcourses, 'index_tdb' : index_tdb, 'folders_tab' : folders_tab , 'connexion_lessons' : connexion_lessons ,
                       'communications': communications, 'parcours_tab': parcours_tab, 'webinaire': webinaire}
        
        elif request.user.is_student :  ## student

            student = request.user.student
            this_today = datetime.now().date()
            prepevals  = student.prepevals.filter(date__gte = this_today)
            try :
                student_answer = student.answers.last()
                parcours       = student_answer.parcours
            except:
                parcours = None

            context  = { 'prepevals' : prepevals , 'parcours' : parcours }
            template = 'dashboard_student_init.html'


        elif request.user.is_parent :  ## parent
            if request.session.get('student_id',None) : # Sert pour la réservation de leçon
                del request.session['student_id']

            parent = request.user.parent
            students = parent.students.order_by("user__first_name")
            context = {'parent': parent, 'students': students, 'today' : today , 'index_tdb' : index_tdb, }
            template = 'dashboard.html'

        return render(request, template , context)
    
    else:  ## Anonymous
        #########
        ###################
        nb_exercises = Exercise.objects.filter(supportfile__is_title=0 ).count()
        nb_students  = Student.objects.count()
        formules = Formule.objects.filter(pk__lte=3)
        
        #delete_and_erase()     

        form = AuthenticationForm()
        np_form = NewpasswordForm()

        n_im = random.randint(1,7)
        image_accueil = 'img/accueil_students'+str(n_im)+'.png'


        levels = Level.objects.exclude(pk=13).exclude(pk=17).order_by("ranking")
        dataset = list()
        pk_ids = [6107, 1762,1651,1427,984,2489,2035,4842,8087,5802,1120,3891,3233]
        i = 0
        for level in levels :
            dico = {}
            dico["level"] = level
            if level.id == 4 : dico["exercise"] = Exercise.objects.filter(supportfile__code='73461082').first()
            elif level.id == 5 : dico["exercise"] = Exercise.objects.filter(supportfile__code='a2cb5280').first()
            elif level.id == 7 : dico["exercise"] = Exercise.objects.filter(supportfile__code='6ba5ee87').first()
            elif level.id == 8 : dico["exercise"] = Exercise.objects.filter(supportfile__code='e9b62f68').first()
            elif level.id == 9 : dico["exercise"] = Exercise.objects.filter(supportfile__code='b1c4c33b').first()
            elif level.id == 10 : dico["exercise"] = Exercise.objects.filter(supportfile__code='45807f5d').first()
            elif level.id == 11 : dico["exercise"] = Exercise.objects.filter(supportfile__code='9c02d47c').first()
            elif level.id == 12 : dico["exercise"] = Exercise.objects.filter(supportfile__code='58b1458d').first()
            else : dico["exercise"] = Exercise.objects.get(pk=pk_ids[i])
            dataset.append(dico)
            i+=1

        cookie_rgpd_accepted = request.COOKIES.get('cookie_rgpd_accepted',None)
        cookie_rgpd_accepted = not ( cookie_rgpd_accepted  == "True" )

        context = {  'cookie_rgpd_accepted' : cookie_rgpd_accepted ,  'nb_exercises' : nb_exercises , 'form' : form , 'np_form' : np_form , 'levels' : levels , 'nb_students' : nb_students , 'formules'  :  formules , 'image_accueil' : image_accueil , 'dataset' : dataset }
 
        response = render(request, 'home.html', context)
        return response



def dash_student(request):
    
    request.session["tdb"] = "training"
    
    if request.user.is_authenticated and request.user.is_student :
        today = time_zone_user(request.user)
        index_tdb = True  
  
        if request.user.closure and request.user.closure < today :
            messages.error(request,"Votre adhésion est terminée.")  
            return redirect("logout")

        template, context = student_dashboard(request, 0)

        return render(request, template , context)
    else :
        return redirect ('index')
 
 



def exercises_shower(request,idl):
    
    request.session["tdb"] = "training"

    if idl == 1   : supportfile_ids = ['1432','1426','1470']
    elif idl == 2 : supportfile_ids = ['6022','1020','1493']
    elif idl == 3 : supportfile_ids = ['1036','1149','1427']
    elif idl == 4 : supportfile_ids = ['6118','1195','6334']
    elif idl == 5 : supportfile_ids = ['1887','1787','1560']
    elif idl == 6 : supportfile_ids = ['6118','106','4229']
    elif idl == 7 : supportfile_ids = ['3023','3448','4265']
    elif idl == 8 : supportfile_ids = ['4543','3420','424']
    elif idl == 9 : supportfile_ids = ['2814','354','194']
    elif idl == 10 : supportfile_ids = ['5641','935','51']
    elif idl == 11 : supportfile_ids = ['2543','669','642']
    elif idl == 12 : supportfile_ids = ['2126','2408','2035']
    elif idl == 14 : supportfile_ids = ['4817','4937','5039']

    exercises = Exercise.objects.filter(level_id= idl, supportfile_id__in=supportfile_ids).order_by("supportfile_id")
    level = Level.objects.get(pk=idl)
    nb = Exercise.objects.filter(supportfile__level_id = idl , supportfile__is_title=0).count()

    context = { 'exercises' : exercises , 'nb' : nb , 'level' : level  }

    return render(request, 'setup/exercises_shower.html', context)
 


 
# def ajax_reponse_to_rgpd(request) :

#     data     = {}
#     context  = {}
#     response = render(request, 'home.html', context)
#     if request.POST.get("response") == "yes" :
#         date = datetime.now()+timedelta(days=180)
#     else :
#         date = datetime.now()+timedelta(days=181)
    
#     response.set_cookie('bandeau_rgpd', date )
#     return JsonResponse(data)

 


def logout_view(request):
    try :
        is_gar_check = request.session.get("is_gar_check",None)
        # récupérer le nameId qui permet de récupérer l'IDO puis déconnecter avec l'IDO
    except :
        pass

    form = AuthenticationForm()
    u_form = UserForm()
    t_form = TeacherForm()
    s_form = StudentForm()
    logout(request)
    levels = Level.objects.all()
    context = {'form': form, 'u_form': u_form, 't_form': t_form, 's_form': s_form, 'levels': levels, 'cookie': False}
    return render(request, 'home.html', context)


def all_routes(request,adresse):
    return redirect("index")


def logout_academy(request):
    logout(request)
    return redirect("index")






def send_message(request):
    ''' traitement du formulaire de contact de la page d'accueil et du paiement de l'adhésion par virement bancaire '''
    name = request.POST.get("name")
    email = request.POST.get("email")
    subject = request.POST.get("subject",None)
    message = request.POST.get("message")
    token = request.POST.get("token", None)

    if token :
        if int(token) == 7 :
            if message:
                #### Si c'est un établissement qui fait une demande 
                school_datas = ""
                if not subject :
                    subject = "Adhésion SACADO - demande d'IBAN"
                    school_id = request.session.get("inscription_school_id",None)
                    if not school_id:
                        school_id = request.POST.get("inscription_school_id",None)
                    if school_id :
                        school = School.objects.get(pk = school_id)
                        school_datas = "\n"+school.name +"\n"+school.code_acad +  " - " + str(school.nbstudents) +  " élèves \n" + school.address +  "\n"+school.town+", "+school.country.name
                ############################################################  

                send_mail(subject,
                            message+" \n\n Ce mail est envoyé à partir de l'adresse : " + email + "\n\n" + school_datas,
                          settings.DEFAULT_FROM_EMAIL,
                          ["sacado.academie@gmail.com" ])
                messages.success(request,"Message envoyé..... Merci. L'équipe Sacado.")

        else :
            messages.error(request,"Erreur d'opération....")
    else :
        messages.error(request,"Oubli de token.")

    return redirect("index")



def school_adhesion(request):

    rates = Rate.objects.all() #tarifs en vigueur 
    school_year = rates.first().year #tarifs pour l'année scolaire
    form = SchoolForm(request.POST or None, request.FILES  or None)
    token = request.POST.get("token", None)
    today = time_zone_user(request.user)
    u_form = UserForm(request.POST or None)


    if request.method == "POST" :
        if  all((u_form.is_valid(), form.is_valid())):   
            if token :
                if int(token) == 7 :
                    school_commit = form.save(commit=False)
                    school_exists, created = School.objects.get_or_create(name = school_commit.name, town = school_commit.town , country = school_commit.country , 
                        code_acad = school_commit.code_acad , defaults={ 'nbstudents' : school_commit.nbstudents , 'logo' : school_commit.logo , 'address' : school_commit.address ,'complement' : school_commit.complement , 'gar' : school_commit.gar }  )

                    if not created :
                        # si l'établisseent est déjà créé, on la modifie et on récupère son utilisateur.
                        School.objects.filter(pk = school_exists.id).update(town = school_commit.town , country = school_commit.country , code_acad = school_commit.code_acad , 
                            nbstudents = school_commit.nbstudents , address = school_commit.address , complement = school_commit.complement, logo = school_commit.logo )
                        new_user_id = request.session.get("new_user_id", None)
                        if new_user_id :
                            user = User.objects.get(pk = new_user_id )
                        else :
                            user = u_form.save(commit=False)
                            user.user_type = User.TEACHER
                            user.school = school_exists # on attribue l'établissement à la personne qui devient référence
                            user.is_manager = 1 # on attribue l'établissement à la personne qui devient administratrice de sacado.
                            user.set_password(u_form.cleaned_data["password1"])
                            user.country = school_exists.country
                            user.save()
                            username = u_form.cleaned_data['username']
                            password = u_form.cleaned_data['password1']
                            teacher = Teacher.objects.create(user=user)
                            request.session["new_user_id"] = user.id    
                    else :
                        # si l'établissement vient d'être créé on crée aussi la personne qui l'enregistre.
                        user = u_form.save(commit=False)
                        user.user_type = User.TEACHER
                        user.school = school_exists # on attribue l'établissement à la personne qui devient référence
                        user.is_manager = 1 # on attribue l'établissement à la personne qui devient administratrice de sacado.
                        user.set_password(u_form.cleaned_data["password1"])
                        user.country = school_exists.country
                        user.save()
                        username = u_form.cleaned_data['username']
                        password = u_form.cleaned_data['password1']
                        teacher = Teacher.objects.create(user=user)
                        request.session["new_user_id"] = user.id 
                        ##########
                        ##########
                        # Si on vient de créer un établissement, on lui crée un abonnement.
                        ##########


                    is_active   = False # date d'effet, user, le paiement est payé non ici... doit passer par la vérification
                    observation = "Paiement en ligne"             
 
                    accounting_id = accounting_adhesion(school_exists, today , None, user, is_active , observation) # création de la facturation

                    ########################################################################################################################
                    #############  Abonnement
                    ########################################################################################################################
                    date_start, date_stop = date_abonnement(today)

                    abonnement, abo_created = Abonnement.objects.get_or_create( accounting_id = accounting_id  , defaults={'school' : school_exists, 'is_gar' : school_exists.gar, 'date_start' : date_start, 'date_stop' : date_stop,  'user' : user, 'is_active' : 0}  )
 
                    if school_exists.gar: # appel de la fonction qui valide le Web Service
                        create_abonnement_gar(today,school_exists,abonnement,request.user)
                    ########################################################################################################################
                    #############  FIN  Abonnement
                    ########################################################################################################################

                    school_datas =  school_exists.name +"\n"+school_exists.code_acad +  " - " + str(school_exists.nbstudents) +  " élèves \n" + school_exists.address +  "\n"+school_exists.town+", "+school_exists.country.name
                    send_mail("Demande d'adhésion à la version établissement",
                              "Bonjour l'équipe SACADO, \nl'établissement suivant demande la version établissement :\n"+ school_datas +"\n\nCotisation : "+str(school_exists.fee())+" €.\n\nEnregistrement de l'étalissement dans la base de données.\nEn attente de paiement. \nhttps://sacado-academie.fr . Ne pas répondre.",
                              settings.DEFAULT_FROM_EMAIL,
                              ['sacado.academie@gmail.com'])

                    send_mail("Demande d'adhésion à la version établissement",
                              "Bonjour "+user.first_name+" "+user.last_name +", \nVous avez demandé la version établissement pour :\n"+ school_datas +"\n\nCotisation : "+str(school_exists.fee())+" €. \nEn attente de paiement. \nL'équipe SACADO vous remercie de votre confiance. \nCeci est un mail automatique. Ne pas répondre. ",
                               settings.DEFAULT_FROM_EMAIL,
                               [user.email])


                    # Mise en session de l'ide de l'établissement et de l'id de la facture.
                    request.session["accounting_id"] = accounting_id
                    request.session["inscription_school_id"] = school_exists.pk  # inscription_school_id != school_id... On pourrait imaginer qu'un établissement en inscrive un autre sinon.
                    request.session["contact"] = user.first_name+" "+user.last_name 

                    return redirect('payment_school_adhesion')
        else :
            print(form.errors)
            print(u_form.errors)

    context = { 'form' : form , 'rates': rates, 'school_year': school_year, 'u_form' : u_form }
    return render(request, 'setup/school_adhesion.html', context)




def payment_school_adhesion(request):
 

    school_id     = request.session.get("inscription_school_id", None)
    accounting_id = request.session.get("accounting_id", None)
    contact       = request.session.get("contact", None)
    new_user_id   = request.session.get("new_user_id", None)

 
    if school_id and new_user_id :
        user = User.objects.get(pk = new_user_id )
        school     = School.objects.get(pk = school_id)
        accounting = Accounting.objects.get(pk=accounting_id) 

        context = { 'school' : school , 'contact' : contact ,   'accounting' : accounting ,   'user' : user , }

        return render(request, 'setup/payment_school_adhesion.html', context)

    else :
        return redirect('school_adhesion')     



def iban_asking(request,school_id,user_id):

    school = School.objects.get(pk = school_id)
    user = User.objects.get(pk = user_id)
    send_mail("Demande d'IBAN",
                "Bonjour l'équipe SACADO, \nJe souhaiterais recevoir un IBAN de votre compte pour procéder à un virement bancaire en faveur de mon établissement :\nIdentifiant : "+ str(school.id) +"\nUAI : "+ school.code_acad +"\n"+ school.name +"\n"+ school.town +","+ school.country.name +"\n\nNe pas répondre.",
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email,'sacado.academie@gmail.com'])

    messages.success(request,"Demande d'IBAN envoyée")
    return redirect('index')



def delete_school_adhesion(request):

    school_id = request.session.get("inscription_school_id")
    school = School.objects.get(pk = school_id)

    if school.users.count() == 0 :
        school.delete()
        messages.success(request,"Demande d'adhésion annulée")  

        try :
            send_mail("Suppression d'adhésion",
                    "Bonjour l'équipe SACADO, \nJe souhaite annuler la demande d'adhésion :\n\n"+ school.name +"\n"+ school.town +","+ school.country.name +"\n\nNe pas répondre.",
                        settings.DEFAULT_FROM_EMAIL,
                        ['sacado.academie@gmail.com'])
        except :
            pass

    elif school.users.count() == 1 :
        for u in school.users.all():
            u.teacher.delete()
            u.delete()

        school.delete()
        messages.success(request,"Demande d'adhésion annulée")  

        try :
            send_mail("Suppression d'adhésion",
                    "Bonjour l'équipe SACADO, \nJe souhaite annuler la demande d'adhésion :\n\n"+ school.name +"\n"+ school.town +","+ school.country.name +"\n\nNe pas répondre.",
                        settings.DEFAULT_FROM_EMAIL,
                        ['"sacado.academie@gmail.com"'])
        except :
            pass            

    else :  
        messages.error(request,"La demande d'annulation ne peut être validée. Des utilisateurs de votre établissement restent inscrits.")  

    return redirect('index')


 
def print_proformat_school(request):

    school_year = Rate.objects.get(pk=1).year
 

    new_user_id   = request.session.get("new_user_id", None)
    if new_user_id :
        user = User.objects.get(pk = new_user_id )
    else :
        user = request.user
 
    school_id = request.session.get("inscription_school_id", None)
    if school_id :
        school = School.objects.get(pk = school_id)
    else :
        school = request.user.school

    now = datetime.now().date()
    response = HttpResponse(content_type='application/pdf')

    response['Content-Disposition'] = 'attachment; filename="'+str(school.id)+"-"+str(datetime.now().strftime('%Y%m%d'))+".pdf"
    doc = SimpleDocTemplate(response,   pagesize=A4, 
                                        topMargin=0.3*inch,
                                        leftMargin=0.3*inch,
                                        rightMargin=0.3*inch,
                                        bottomMargin=0.3*inch     )

    sample_style_sheet = getSampleStyleSheet()

    sacado = ParagraphStyle('sacado', 
                            fontSize=20, 
                            leading=26,
                            borderPadding = 0,
                            alignment= TA_CENTER,
                            )

    elements = []                 
    title_black = ParagraphStyle('title', fontSize=20, )
    subtitle = ParagraphStyle('title', fontSize=16,  textColor=colors.HexColor("#00819f"),)
    normal = ParagraphStyle(name='Normal',fontSize=10,)
    normalr = ParagraphStyle(name='Normal',fontSize=12,alignment= TA_RIGHT)
 
    logo = Image('https://sacado-academie.fr/static/img/sacadoA1.png')  
    logo_tab = [[logo, "SAS SANSPB \n2B avenue de la pinède \n83400 La Capte Hyères \nFrance" ]]
    logo_tab_tab = Table(logo_tab, hAlign='LEFT', colWidths=[0.7*inch,5*inch])

    elements.append(logo_tab_tab)
    elements.append(Spacer(0, 0.2*inch))

    paragraph0 = Paragraph( "Adhésion Annuelle " + school_year  , sacado )
    elements.append(paragraph0)
    elements.append(Spacer(0, 0.5*inch))

    school_datas =  school.name +"\n"+school.code_acad +  " - " + str(school.nbstudents) +  " élèves \n" + school.address +  "\n"+school.town+", "+school.country.name
    demandeur =  school_datas+   "\n\nMontant de la cotisation : "+str(school.fee()+2)+"€ (frais de port inclus)" +"\n\nNom du demandeur : " + user.first_name + " "  + user.last_name + "\nCourriel : " + user.email  


    demandeur_tab = [[demandeur, "SAS SANSPB \n2B avenue de la pinède \n83400 La Capte Hyères \nFrance\n\n\n\n\n" ]]
    demandeur_tab_tab = Table(demandeur_tab, hAlign='LEFT', colWidths=[5*inch,2*inch])

    elements.append(demandeur_tab_tab)
    elements.append(Spacer(0, 0.2*inch))



    my_texte_ = "Sous réserve du bon fonctionnement de son hébergeur LWS, la SAS SANSPB met l'ensemble des fonctionnalités du site https://sacado-academie.fr à disposition des enseignants de l'établissement "+school.name+"."
    paragraph = Paragraph( my_texte_  , normal )
    elements.append(paragraph)
    elements.append(Spacer(0, 0.2*inch))

    sy = school_year.split("-")
    my_texte = "Le présent contrat est valide pour la période scolaire du 1 Septembre " + sy[0]+" jusqu'au 7 juillet "+sy[1]+" pour les établissements de rythme Nord. \nPour les établissements de rythme Sud, la validité de l'adhésion est valable sur l'année "+sy[1]+"."

    paragraph = Paragraph( my_texte  , normal )
    elements.append(paragraph)
    elements.append(Spacer(0, 0.2*inch))

    signature_tab = [[ 'Signature précédée de la mention "Lu et approuvé" \n\n...........................................................\n\n\n ...........................................................',"" ]]
    signature_tab_tab = Table(signature_tab, hAlign='LEFT', colWidths=[4*inch,3*inch])

    elements.append(signature_tab_tab)
    elements.append(Spacer(0, 0.4*inch))

    doc.build(elements)

    return response


def tutos_video_sacado(request):
    context = {}
    return render(request, 'setup/tutos_video_sacado.html', context)



def ajax_get_subject(request):
    subject_id =  request.POST.get("subject_id")
    data = {}
    level_ids = Exercise.objects.values_list("level__id", flat= True).filter(theme__subject_id = subject_id).distinct()
    levels =  Level.objects.filter(pk__in=level_ids).order_by("ranking")
    data['html'] = render_to_string('ajax_get_subject.html', { 'levels' : levels , 'subject_id' :  subject_id })

    return JsonResponse(data)


###############################################################################################################################################################################
###############################################################################################################################################################################
########  Interface Python
###############################################################################################################################################################################
###############################################################################################################################################################################

def python(request):
    context = {}
    return render(request, 'basthon/interface_python.html', context)


###############################################################################################################################################################################
###############################################################################################################################################################################
########  Inscription élève isolé
###############################################################################################################################################################################
###############################################################################################################################################################################

def acad_exercises(request):
    form = AuthenticationForm()
    np_form = NewpasswordForm()
    context = { 'form' : form  , 'np_form' : np_form }
    return render(request, 'setup/exercises.html', context)



def parents(request):
    form = AuthenticationForm()
    np_form = NewpasswordForm()
    context = { 'form' : form  , 'np_form' : np_form }
    return render(request, 'setup/parents.html', context)



def numeric(request):
    form = AuthenticationForm()
    np_form = NewpasswordForm()
    context = { 'form' : form  , 'np_form' : np_form }
    return render(request, 'setup/numeric.html', context)


def contact(request):
    form = AuthenticationForm()
    np_form = NewpasswordForm()
    context = { 'form' : form  , 'np_form' : np_form }
    return render(request, 'setup/contact.html', context)
 

def advises_index(request):
    form = AuthenticationForm()
    np_form = NewpasswordForm()
    delete_session_key(request, "answerpositionnement")
    delete_session_key(request, "positionnement_id")
    positionnements = Positionnement.objects.filter(is_publish=1).order_by("level__ranking")
    context = { 'form' : form  , 'np_form' : np_form , 'positionnements' : positionnements   }
    return render(request, 'setup/advises.html', context)



def faq(request):
    form = AuthenticationForm()
    np_form = NewpasswordForm()
    context = { 'form' : form  , 'np_form' : np_form }
    return render(request, 'setup/faq.html', context)


def who_is(request):
    form = AuthenticationForm()
    np_form = NewpasswordForm()
    context = { 'form' : form  , 'np_form' : np_form }
    return render(request, 'setup/who_is.html', context)


@is_manager_of_this_school
def admin_tdb(request):

    school = request.user.school
    schools = request.user.schools.all()
 
    schools_tab = [school]
    for s in schools :
        schools_tab.append(s)

    teachers = Teacher.objects.filter(user__school=school, user__user_type=2)

    nb_teachers = teachers.count()
    nb_students = User.objects.filter(school=school, user_type=0).exclude(username__contains="_e-test_").count()
    nb_groups   = Group.objects.filter(Q(teacher__user__school=school)|Q(teacher__user__schools=school)).count()
    
    is_lycee = False
    try :
        if not school.get_seconde_to_comp :
            for t in teachers :
                if t.groups.filter(level__gte=10).count() > 0 :
                    is_lycee = True
                    break
    except :
        pass

    try:
        stage = Stage.objects.get(school=school)
        if stage:
            eca, ac, dep = stage.medium - stage.low, stage.up - stage.medium, 100 - stage.up
        else:
            eca, ac, dep = 20, 15, 15

    except:
        stage = {"low": 50, "medium": 70, "up": 85}
        eca, ac, dep = 20, 15, 15
    
    if len(schools_tab) == 1 :
        school_id = request.user.school.id
        request.session["school_id"] = school_id
    else :
        if request.session.get("school_id",None) :
            school_id = int(request.session.get("school_id",None))
        else :
            school_id = 0

    rates       = Rate.objects.all() #tarifs en vigueur 
    school_year = rates.first().year #tarifs pour l'année scolaire


    renew_propose = renew(school)

 
    return render(request, 'dashboard_admin.html', {'nb_teachers': nb_teachers, 'nb_students': nb_students, 'school_id' : school_id , "school" : school ,  'renew_propose' : renew_propose ,
                                                    'nb_groups': nb_groups, 'schools_tab': schools_tab, 'stage': stage, 'is_lycee' : is_lycee , 'school_year' : school_year ,  'rates' : rates , 
                                                    'eca': eca, 'ac': ac, 'dep': dep , 'communications' : [],
                                                    })





def academy(request):

    nb_exercises = Exercise.objects.filter(supportfile__is_title=0 ).count()
    nb_students  = Student.objects.count()
    formules = Formule.objects.filter(pk__lte=3)
 

    form = AuthenticationForm()
    np_form = NewpasswordForm()

    levels = Level.objects.order_by("ranking")
    context = { 'nb_exercises' : nb_exercises , 'form' : form , 'np_form' : np_form , 'levels' : levels , 'nb_students' : nb_students , 'formules'  :  formules  }
    return render(request, 'setup/academy_index.html', context)



def inscription(request):
    context = {}
    return render(request, 'setup/register.html', context)


def test_display(request):
    context = {}
    return render(request, 'setup/test_display.html', context)


def student_to_association(request):

    frml = Formule.objects.get(pk=1)
    formule = Formule.objects.get(pk=4)
    context = { 'frml' : frml , 'formule' : formule }
    return render(request, 'setup/student_association.html', context)


def choice_menu(request,id):

    try :
        del request.session["answerpositionnement"]
        del request.session["student"]
        del request.session["positionnement_id"]
    except :
        pass

    form = AuthenticationForm()
    np_form = NewpasswordForm()

    formule  = Formule.objects.get(pk=id)
    end  = end_of_contract()
    context = { 'formule' : formule , 'end' : end , 'form' : form , 'np_form' : np_form   }
    return render(request, 'setup/menu.html', context)   


def details_of_adhesion(request) :

    nb_child   = request.POST.get("children")
    formule_id = request.POST.get("formule_id")

    data_post = request.POST
    levels    = Level.objects.exclude(pk=13).exclude(pk=17)
    formule   = Formule.objects.get(pk = formule_id)


    form = AuthenticationForm()
    np_form = NewpasswordForm()
  
    userFormset = formset_factory(UserForm, extra = int(nb_child) + 1, max_num= int(nb_child) + 2, formset=BaseUserFormSet)
    context     = {  'formule' : formule ,    'data_post' : data_post ,  'levels' : levels ,  'userFormset' : userFormset, "renewal" : False, "form" : form, "np_form" : np_form }
    template    = 'setup/detail_of_adhesion.html'

    return render(request, template , context)   



def renewal_adhesion(request) :

    levels = Level.objects.order_by("ranking")
    formules = Formule.objects.filter(is_sale=1)
    context = {    'formules'  : formules,  'levels'  : levels }
    return render(request, 'setup/renewal_adhesion.html', context)   


def ajax_prices_formule(request) :
 
    formule_id = request.POST.get("formule_id",None)
    student_id = request.POST.get("student_id",None)
    level_id   = request.POST.get("level_id",None)
    data = {}
    if formule_id :
        prices = Formule.objects.values("price","nb_month").filter(formule_id=int(formule_id)).order_by("-nb_month") 

    data["prices"] = list(prices)

    return JsonResponse(data) 

 
def get_price_by_formules(formule_id,duration,level_id):

    formule = Formule.objects.get(pk=formule_id)

    if formule.id > 1 and 5 < int(level_id) <10  :  price = formule.price + 10
    elif formule.id > 1 and 9 < int(level_id) <13:  price = formule.price +20 
    else : price = formule.price

    price_dico = { '1' : 5.00 , '3' : 14.00 , '6' : 26.00 , '12' : 50.00  }

    if formule.id == 1 :
        total_price = price_dico[str(duration)]
    else : total_price = int(duration)*price
    return total_price



 
def ajax_tarifications_formule(request) :
 
    formule_id = request.POST.get("formule_id",None)
    duration   = request.POST.get("duration",None)
    level_id   = request.POST.get("level_id",None)
    data = {}
    data['price'] = "{:.2f}".format(get_price_by_formules(formule_id,duration,level_id))

    return JsonResponse(data) 


def creation_facture(facture):
 
    ##################################################################################################################
    # Création de la facture de l'adhésion au format pdf
    ##################################################################################################################

    #filename = str(user.id)+str(datetime.now().strftime('%Y%m%d'))+".pdf"
    filename= facture.chrono+".pdf"
    now = datetime.now().date()

    #outfiledir = "D:/uwamp/www/sacadogit/sacado/static/uploads/factures/{}/".format(user.id) # local
    outfiledir = "uploads/factures/{}/".format(facture.user.id) # on a server
    if not os.path.exists(outfiledir):
        os.makedirs(outfiledir)

    store_path = os.path.join(outfiledir, filename)

    doc = SimpleDocTemplate(store_path,   pagesize=A4, 
                                        topMargin=0.3*inch,
                                        leftMargin=0.3*inch,
                                        rightMargin=0.3*inch,
                                        bottomMargin=0.3*inch     )

    sample_style_sheet = getSampleStyleSheet()

    sacado = ParagraphStyle('sacado', 
                            fontSize=26, 
                            leading=26,
                            borderPadding = 0,
                            alignment= TA_CENTER,
                            )

    elements = []                 
    title_black = ParagraphStyle('title', fontSize=20, )
    subtitle = ParagraphStyle('title', fontSize=16,  textColor=colors.HexColor("#00819f"),)
    normal = ParagraphStyle(name='Normal',fontSize=12,)
    normalr = ParagraphStyle(name='Normal',fontSize=12,alignment= TA_RIGHT)
     #### Mise en place du logo
    #logo = Image('D:/uwamp/www/sacadogit/sacado/static/img/sacadoA1.png') # local
    logo = Image('https://sacado-academie.fr/static/img/sacadoA1.png') # on a server
    logo_tab = [[logo, "SACADO" ]]
    logo_tab_tab = Table(logo_tab, hAlign='LEFT', colWidths=[0.7*inch,5*inch])
    logo_tab_tab.setStyle(TableStyle([ ('TEXTCOLOR', (0,0), (-1,0), colors.Color(0,0.5,0.62))]))
    
    elements.append(logo_tab_tab)
    elements.append(Spacer(0, 0.2*inch))

    paragraph0 = Paragraph( "Adhésion"   , sacado )
    elements.append(paragraph0)
    elements.append(Spacer(0, 1*inch))
    paragraph = Paragraph( "Réf : "+facture.chrono   , normal )
    elements.append(paragraph)
    elements.append(Spacer(0, 0.2*inch))

    paragraph = Paragraph( "Nom : "+facture.user.last_name   , normal )
    elements.append(paragraph)
    elements.append(Spacer(0, 0.1*inch))
    paragraph1 = Paragraph( "Prénom : "+facture.user.first_name   , normal )
    elements.append(paragraph1)
    elements.append(Spacer(0, 0.1*inch))
    paragraph2 = Paragraph( "Courriel : "+facture.user.email   , normal )
    elements.append(paragraph2)
    elements.append(Spacer(0, 0.3*inch))

 
    
    #para = Paragraph(  "Adhésion : "+formule.adhesion  , normal )
    #elements.append(para)
    #elements.append(Spacer(0, 0.1*inch))

    #para1 = Paragraph( "Menu : "+formule.name  , normal )
    #elements.append(para1)
    #elements.append(Spacer(0, 0.3*inch))
 
 
    total_price = 0     
    for adhesion in facture.adhesions.all() :

        delta    = adhesion.stop - adhesion.start
        duration = int(round(delta.days/30,0))

        paragraph_msg = Paragraph( "  -  {} {}, montant : {:.2f}€, durée : {:d} mois ".\
                  format(adhesion.student.user.first_name,adhesion.student.user.last_name,adhesion.amount,duration)  , normal )
        elements.append(paragraph_msg)
        elements.append(Spacer(0, 0.1*inch))
        total_price += adhesion.amount

    elements.append(Spacer(0, 0.5*inch))
    para3 = Paragraph( "Montant de l'adhésion : {:6.2f}€".format(total_price)  , normal )
    elements.append(para3)
    elements.append(Spacer(0, 0.1*inch))
 
        
    elements.append(Spacer(0, 2*inch))
    para3 = Paragraph( "Date de paiement : "+ facture.date.strftime('%d/%m/%Y') +" "  , normal )
    elements.append(para3)
    elements.append(Spacer(0, 0.1*inch))
 

    doc.build(elements)
    print("pdf facture ok")
    return store_path
  

def all_from_parent_user(user) :
    students = user.parent.students.all()
    u_parents = []
    for s in students :
        for  p in s.students_parent.all() : 
            if p not in u_parents :
                u_parents.append(p.user)
    return u_parents


def save_renewal_adhesion(request) :
    
    return render(request, 'setup/save_renewal_adhesion.html', context)  
  

@csrf_exempt
def accept_renewal_adhesion(request) :
    return HttpResponse("ok")


def attribute_all_documents_to_student_by_level(level,student) :

    teacher_ids = ["0" ,89513,89507,89508,89510, 89511, 46245  , 46242 , 46246  , 46247, 46222, 46243, 46244,"", 130243]
    teacher_id = teacher_ids[level.id]
    group = Group.objects.filter(level = level, school_id = 50, teacher_id=teacher_id).first()
    group.students.add(student)
    groups = [group]
    test = attribute_all_documents_of_groups_to_a_new_student(groups, student)
    success = True
    return success


def attribute_group_to_student_by_level(level,student,formule_id) :

    teacher_ids = ["0" ,89513,89507,89508,89510, 89511, 46245  , 46242 , 46246  , 46247, 46222, 46243, 46244,"", 130243] # "0" ET "" sont des offsets
    teacher_id = teacher_ids[level.id]
    if int(formule_id) > 2 : formule_id = 2
    group = Group.objects.filter(level = level, school_id = 50, teacher_id=teacher_id, formule_id=formule_id).first()
    group.students.add(student)
    groups = [group]
    test = attribute_all_documents_of_groups_to_a_new_student(groups, student)
    success = True
    return success


def cmd_abonnement(formule,facture_id):
    today = datetime.now().replace(tzinfo=timezone.utc)
    date="{}-{:02}-{:02}".format(today.year,today.month,today.day)
    return "Abonnement "+formule.name+"_" + date + "_"+ str(facture_id)



def add_adhesion(request) :
    
    request.session["tdb"] = 'adhesion'
    form =  UserForm(request.POST or None)
    formules = Formule.objects.filter(is_sale=1)
    levels = Level.objects.exclude(pk=13).order_by("ranking")
    today = time_zone_user(request.user)

    if request.method == "POST" :
        if form.is_valid():
            duration = int(request.POST.get("duration"))

            today = datetime.now()
            today = today.replace(tzinfo=timezone.utc)
            d,m,y = today.day , (today.month - 1 + duration)%12 + 1 , today.year + (today.month - 1 + duration)//12
            end = datetime(y,m,d).replace(tzinfo=timezone.utc)
            form_user = form.save(commit=False)
            form_user.closure = end
            form_user.school_id = 50
            form_user.cgu = 1
            form_user.country_id = 4
            form_user.user_type = 0
            form_user.save()
            level_id = request.POST.get("level")
            formule_id = request.POST.get("formule_id")
            level   = Level.objects.get(pk = level_id)            
            student = Student.objects.create(user=form_user, level = level)
            u_parents = all_from_parent_user(request.user)

            u_p_mails = ["sacado.academie@gmail.com"]
            for u_p in u_parents : 
                u_p.parent.students.add(student)
                u_p_mails.append(u_p.email)

            chrono = "BL_" +  request.user.last_name +"_"+str(today)

            if formule_id == 5 :
                data , amount , end_of_this_adhesion =  False , "5,00" ,  datetime(today.year + (today.month - 1 + duration)//12,9,1).replace(tzinfo=timezone.utc)
                if level_id == 10 :
                    sublevel = request.POST.get("sublevel",None)
                    if sublevel == "es":
                        group = Group.objects.get(pk=7323)
                    else :
                        group = Group.objects.get(pk=7324)
                    group.students.add(student)
                    success = attribute_all_documents_of_groups_to_a_new_student([group], student)
                else :
                    success = attribute_group_to_student_by_level(level,student,formule_id)
            else :
                data , amount , end_of_this_adhesion = get_price_and_end_adhesion(formule_id,  today, duration, student,level.id )
                success = attribute_group_to_student_by_level(level,student,formule_id)


            amount = float(amount.replace(",","."))
            adhesion = Adhesion.objects.create(start = today, stop = end_of_this_adhesion, student = student , level_id = level_id  , amount = amount  , formule_id = formule_id , is_active = 0 ) 
            facture  = Facture.objects.create(chrono = chrono, file = "" , user = request.user, is_lesson = 1   ) 
            facture.adhesions.add(adhesion)


            msg = "Bonjour,\n\nVous venez de souscrire à une adhésion à la SACADO ACADÉMIE. \n\n"
            msg += "Votre référence d'adhésion est "+facture.chrono+". Vous êtes en attente de paiement.\n\n"
            msg += "Vous avez inscrit : \n"
            msg += "- "+student.user.first_name+" "+student.user.last_name+", l'identifiant de connexion est : "+student.user.username +" \n"
            msg += "\nRetrouvez ces détails à partir de votre tableau de bord après votre connexion à https://sacado-academie.fr"
            msg += "\nPour accéder aux exercices, vous devez utiliser l'interface de votre enfant."
            msg += "\nL'équipe de SACADO ACADÉMIE vous remercie de votre confiance.\n\n"



            msg += "Voici quelques conseils pour votre enfant :\n\nConnecte-toi sur https://sacado-academie.fr\n"
            msg += "Indique ton Nom d’utilisateur et ton Mot de passe\n"
            msg += "Clique sur le bouton « connexion » \n"
            msg += "Indique ton identifiant et ton mot de passe \n" 
            msg += "-> Tu arrives ensuite sur ton tableau de bord avec tous les modules de ta formule. \n"   
            msg += "Tu peux y accéder aussi avec le menu à gauche :\n"
            msg += "Clique sur « entraînement » pour commencer les exercices classés par thème. \n\n" 
            msg += "Pense à t’entraîner au moins 10 minutes chaque jour pour fixer les notions, maîtriser les méthodes de base et construire des savoirs solides..\n"

    
            send_mail("Inscription SACADO ACADÉMIE", msg, settings.DEFAULT_FROM_EMAIL, u_p_mails )

            formule = Formule.objects.get(pk=formule_id)
            cmd =  cmd_abonnement(formule,facture.id)

            billing='<?xml version="1.0" encoding="utf-8" ?><Billing><Address><FirstName>{}</FirstName><LastName>{}</LastName><Address1>Sarlat</Address1><ZipCode>24200</ZipCode><City>Sarlat</City><CountryCode>250</CountryCode></Address></Billing>'.format("Académie","SACADO ACADÉMIE")


            champs_val=champs_briqueCA(amount,cmd,request.user.email,1,billing)
            context={ 'formule' : formule , 'level' : level , 'student' : student ,  'amount' : amount , 'end_day' : end , 'champs_val':champs_val}
            return render(request, 'setup/brique_credit_agricole.html', context)  




    context = {  "renewal" : True, "form" : form, "formules" : formules  ,   'levels' : levels , }
    return render(request, 'setup/add_adhesion.html', context)   
 
        
 

def insertion_into_database(parents,students):

    these_days = [31,31,29,31,30,31,30,31,31,30,31,30,31,31,29,31,30,31,30,31,31,30,31,30,31]
    today = datetime.now()
    today = today.replace(tzinfo=timezone.utc)
    adhesions_in , students_in = [] , set()
    
    students_to_session , parents_to_session , adhesion_in = [] , [] ,set()

    for s in students :

        duration_days = 0
        level = s['level']
        for i in range(s['duration']) :
            duration_days += these_days[i+today.month]
        date_end_dateformat = today + timedelta(days=duration_days)

        user, created = User.objects.update_or_create(username = s['username'], password = s['password'] , user_type = 0 , defaults = { "last_name" : s['last_name'] , "first_name" : s['first_name']  , "email" : s['email']  , "country_id" : 5 ,  "school_id" : 50 , "closure" : date_end_dateformat })
        student,created_s = Student.objects.update_or_create(user = user, defaults = { "task_post" : 1 , "level" : level })

        folders = Folder.objects.filter(level = level, teacher_id = 2480 , is_trash=0) # 2480 est SacAdoProf
        for f in folders :
            f.students.add(student)

        if created_s : 
            students_in.add(student) # pour associer les enfants aux parents 

        formule_id = s['formule'].id

        adhesion = Adhesion.objects.create( student = student , level = level , start = today , amount = s['price'] , stop = date_end_dateformat , formule_id  = formule_id , year  = today.year , is_active = 0)
        students_to_session.append({ 'student_id' :user.id , 'adhesion_id' : adhesion.id })
        adhesion_in.add(adhesion)
        success = attribute_group_to_student_by_level(level,student,formule_id)

    loop = 0
    for p in parents :
        user, created = User.objects.update_or_create(username = p['username'], password = p['password'] , user_type = 1 , defaults = { "last_name" : p['last_name'] , "first_name" : p['first_name']  , "email" : p['email'] , "country_id" : 5 ,  "school_id" : 50 ,  "closure" : None })
        parent,create = Parent.objects.update_or_create(user = user, defaults = { "task_post" : 1 })
        parent.students.set(students_in)

        if loop == 0 :
            facture = Facture.objects.create(chrono = "BL_" +  user.last_name +"_"+str(today) ,  user_id = user.id , file = "" ,  orderID = "" , is_lesson = 1  ) #orderID = Numéro de paiement donné par la banque"
            facture.adhesions.set(adhesion_in)
            parents_to_session.append({ 'parent_id' : user.id , 'password_no_crypted' : p['password_no_crypted'] , 'facture_id' : facture.id }) 

    return students_to_session , parents_to_session



def send_message_after_insertion(parents,students) :

    ##################################################################################################################
    # Envoi du courriel
    ##################################################################################################################
    nbc = ""
    if len(students) > 1 :
        nbc = "s"

    for p in parents :
        msg = "Bonjour "+p["first_name"]+" "+p["last_name"]+",\n\nVous venez de souscrire à un menu "+ p['formule'].name+" à la SACADO ACADÉMIE. \n\n"
        msg += "Votre adhésion est en attente de paiement.\n\n"     ##"+chrono+".\n\n"
        msg += "Votre identifiant est "+p["username"]+" et votre mot de passe est "+p["password_no_crypted"]+"\n"
        msg += "Vous avez inscrit : \n"
        for s in students :
            msg += "- "+s["first_name"]+" "+s["last_name"]+", son identifiant de connexion est : "+s["username"]+", son mot de passe est "+s["password_no_crypted"]+" \n"

        msg += "Leur accès est actuellement consultable mais leurs droits seront ouverts dès le paiement effectué. \n"

        if p['formule'].id > 1 :
            msg += "Un.e enseignant.e de la SACADO ACADÉMIE va vous contacter sous 24 heures par mail pour établir un plan de travail personnalisé.\n\n"
        #msg += "Pour établir des conseils personalisés, nous vous demandons à votre enfant de remplir un questionnaire à cette adresse : https://sacado-academie.fr/questionnaire\n\n"
        msg += "\n\nRetrouvez ces détails à partir de votre tableau de bord après votre connexion à https://sacado-academie.fr"
        msg += "\n\nPour accéder aux exercices, vous devez utiliser l'interface de votre enfant."
        msg += "\n\nL'équipe de SACADO ACADÉMIE vous remercie de votre confiance.\n\n"

        ###### Quelques recommandations pour les parents

        msg += "Voici quelques conseils pour votre enfant :\n\nConnecte-toi sur https://sacado-academie.fr\n"
        msg += "Indique ton Nom d’utilisateur et ton Mot de passe\n"
        msg += "Clique sur le bouton « connexion » \n"
        msg += "-> Tu arrives ensuite sur ton tableau de bord avec tous les modules de ta formule. \n"   
        msg += "Tu peux y accéder aussi avec le menu à gauche :\n"
        msg += "Clique sur « entraînement » pour commencer les exercices classés par thème. \n\n" 
        msg += "Pense à t’entraîner au moins 10 minutes chaque jour pour fixer les notions, maîtriser les méthodes de base et construire des savoirs solides..\n"

                

        send_mail("Inscription SACADO ACADÉMIE", msg, settings.DEFAULT_FROM_EMAIL, [p["email"],"sacado.academie@gmail.com"] )

    for s in students :
        srcv = ["sacado-academie@gmail.com"]        
        if s["email"] : 
            srcv.append(s["email"])
            smsg = "Bonjour "+s["first_name"]+" "+s["last_name"]+",\n\nTu viens d'être inscrit au menu "+ p['formule'].name +" de la SACADO ACADÉMIE. \n"
            if s['formule'].id > 1 :
                msg += "Un.e enseignant.e de la SACADO ACADÉMIE va vous contacter sous 24 heures par mail pour établir un plan de travail personnalisé.\n"
            smsg += "Ton identifiant est "+s["username"]+" et ton mot de passe est "+s["password_no_crypted"]+"\n"
            smsg += "Il est possible de retrouver ces détails à partir de ton tableau de bord après ta connexion à https://sacado-academie.fr\n"
            smsg += "\n\nL'équipe SACADO te remercie de ta confiance.... et en route vers la réussite \n"

            send_mail("Inscription SACADO ACADÉMIE", smsg, settings.DEFAULT_FROM_EMAIL, srcv)

    # Envoi à SACADO
    sacado_rcv = ["sacado.academie@gmail.com"]
    sacado_msg = "Une adhésion "+s['formule'].name +" SACADO ACADÉMIE vient d'être souscrite. \n\n"

    i,j = 1,1
    for p in parents :
        sacado_msg += "Parent "+str(i)+" : "+p["first_name"]+" "+p["last_name"]+" adresse de courriel : "+p["email"]+". \n\n"
        i+=1
    for s in students :
        if s["email"] :
            adr = ", adresse de courriel : "+s["email"]
        else :
            adr = "" 
        sacado_msg += "Enfant "+str(j)+" : "+s["first_name"]+" "+s["last_name"]+" Niveau :" +s["level"].name+adr+"\n\n"         
        j+=1

    send_mail("Inscription SACADO ACADÉMIE", sacado_msg, settings.DEFAULT_FROM_EMAIL, sacado_rcv)
    #########################################################
 

def champs_briqueCA(montant,cmd,email,nbr_articles,billing):
    """rend un tableau de  cles/valeurs nécessaires pour la brique du credit agricole ; 
    À passer au template appelant cette brique, ces différents champs entrent dans le formulaire
    caché"""
    # calcul ou copie des differents champs, et calcul de chaine à signer
    chaine=""
    champs_val=[]
    try :
        montant=str(int(float(montant)*100+0.5))
    except :
        with open("logs/debug.log","a") as f :
            print("fonction champs_briqueCA : je ne peux pas lire le montant : ",montant,file=f)
        return
    sc='<?xml version="1.0" encoding="utf-8" ?><shoppingcart><total><totalQuantity>{}</totalQuantity></total></shoppingcart>'.format(nbr_articles) 

    timestamp=datetime.now().astimezone().replace(microsecond=0).isoformat()
    cles=['SITE','RANG','IDENTIFIANT','ANNULE','REFUSE','ATTENTE','REPONDRE_A','SOURCE','TOTAL','DEVISE','CMD','PORTEUR','RETOUR','HASH','SHOPPINGCART','BILLING','TIME']
    valeurs=[None,None,None,None,None,None,None,"RWD", montant,"978",cmd,email,"Mt:M;Cmd:R;Auto:A;Erreur:E;idtrans:S;sig:K","SHA512",sc,billing,timestamp]
    
    for i,c in enumerate(cles):
       v=valeurs[i]
       if v==None : v=eval("settings.PBX_"+c)
       champs_val.append([c,v])
           
       chaine+='PBX_'+c+"="+v + ("&" if i<len(cles)-1 else "")
       
    # calcul de la signature
    HMAC=hmac.new(bytearray.fromhex(settings.PBX_CLE_HMAC),msg=chaine.encode("utf-8"),digestmod="sha512").hexdigest().upper()
    cles.append("HMAC")
    champs_val.append(["HMAC",HMAC])
    #htmlentities sur les champs shoppingcart et billing
    
    with open("logs/debug.log","a") as f :
        print("chaine a signer ",chaine,file=f)
        
    return champs_val




def commit_adhesion(request) :

    request.session["tdb"] = 'adhesion'

    data_post   = request.POST
    nb_child    = int( data_post.get("nb_child") )
    formule_id  = int(data_post.get("formule_id"))    
    levels      = data_post.getlist("level")
    userFormset = formset_factory(UserForm, extra = nb_child + 1, max_num = nb_child + 2 , formset=BaseUserFormSet)
    formset     = userFormset(data_post)

    formule = Formule.objects.get(pk = formule_id)


    today = datetime.now()
    today = today.replace(tzinfo=timezone.utc)
    timestamp=datetime.today().isoformat()

    amount = 0
    parents , students = [], []

    if formset.is_valid():
        i = 0
        for form in formset :

            last_name  = form.cleaned_data["last_name"]
            first_name = form.cleaned_data["first_name"]
            username   = form.cleaned_data["username"]
            password_no_crypted = form.cleaned_data["password1"] 
            password  =  make_password(form.cleaned_data["password1"])
            email     =  form.cleaned_data["email"]  

            if 1<= i <= nb_child : 
                level  = Level.objects.get(pk = int(levels[i]))
                duration = int(data_post.get("duration"+str(i)))
                price = get_price_by_formules( int(formule_id), int(duration), level.id )
                amount += price
                students.append({ "last_name" : last_name , "first_name" : first_name  , "email" : email , "level" : level , "username" : username , "password" : password , "password_no_crypted" : password_no_crypted  , "duration" : duration , "price" : price  , "formule" : formule  })
            else :
                if i == 0 :
                    family_name ,family_fname , family_email = last_name , first_name , email
                parents.append({ "last_name" : last_name , "first_name" : first_name  , "email" : email ,  "username" : username, "password" : password , "password_no_crypted" : password_no_crypted  , "formule" : formule })
            i += 1

        students_to_session , parents_to_session = insertion_into_database(parents,students)
        send_message_after_insertion(parents,students)

        request.session["students_to_session"] = students_to_session
        request.session["parents_to_session"]  = parents_to_session


    else :
        error_str = ""
        for error in formset.errors :
            print(request,error)
            error_str += str(error)+" - "

        messages.error(request,"Erreur d'inscription : " + error_str)
        return redirect('index')
    
    cmd=cmd_abonnement(formule,parents_to_session[0]['facture_id'])
    billing='<?xml version="1.0" encoding="utf-8" ?><Billing><Address><FirstName>{}</FirstName><LastName>{}</LastName><Address1>Sarlat</Address1><ZipCode>24200</ZipCode><City>Sarlat</City><CountryCode>250</CountryCode></Address></Billing>'.format("Académie","SACADO ACADÉMIE")
    champs_val=champs_briqueCA(amount,cmd,family_email,nb_child,billing)
    context={'formule':formule,'data_post':data_post,'parents':parents,'students':students,'champs_val':champs_val , 'amount' : amount}

    return render(request, 'setup/commit_adhesion.html', context)   





def paiement_change_adhesion(request) :  
    """page de paiement 
    request.POST contient une liste student_ids, une liste level, et des
    listes "engagement"+student_ids"""
    #----- on met les informations concernant le paiment dans session
    #------------- extraction des infos pour les passer au template
    student_id = request.POST.get('student_id')
    amount     = request.POST.get('amount')
    start      = request.POST.get('start')
    stop       = request.POST.get('stop')
    level_id   = request.POST.get('level_id')
    formule_id = request.POST.get('formule')

    today = datetime.now().replace(tzinfo=timezone.utc)
    this_year = today.year
    user = request.user
    amount = float(amount.replace(",","."))
    facture = Facture.objects.create(chrono = "BL_" +  user.last_name +"_"+str(today) ,  user_id = user.id , file = "" ,  orderID = "" , is_lesson = 1 ) #orderID = Numéro de paiement donné par la banque"
    adhesion = Adhesion.objects.create(amount = amount , student_id = student_id , formule_id = formule_id , start = start , stop = stop , level_id = level_id , year = this_year , is_active = 0 )
    facture.adhesions.add(adhesion)


    student = Student.objects.get(pk=student_id)
    level   = Level.objects.get(pk=level_id)
    formule = Formule.objects.get(pk=formule_id)
    cmd     = cmd_abonnement(formule,facture.id)

    email= user.email
    billing='<?xml version="1.0" encoding="utf-8" ?><Billing><Address><FirstName>{}</FirstName><LastName>{}</LastName><Address1>Sarlat</Address1><ZipCode>24200</ZipCode><City>Sarlat</City><CountryCode>250</CountryCode></Address></Billing>'.format("Académie","SACADO ACADÉMIE")
    try : y,m,d = stop.split("T")[0].split("-")
    except : y,m,d = stop.split("-")
    end_day = d+"-"+m+"-"+y
    champs_val=champs_briqueCA(amount,cmd,email,1,billing)
    
    context={ 'formule' : formule , 'level' : level , 'student' : student ,  'amount' : amount , 'end_day' : end_day , 'champs_val':champs_val}
    return render(request, 'setup/brique_credit_agricole.html', context)  




def paiement(request) :  
    """page de paiement 
    request.POST contient une liste student_ids, une liste level, et des
    listes "engagement"+student_ids"""
    #----- on met les informations concernant le paiment dans session
    #------------- extraction des infos pour les passer au template
    student_id = request.POST.get('student_id')
    amount     = request.POST.get('amount')
    start      = request.POST.get('start')
    stop       = request.POST.get('stop')
    level_id   = request.POST.get('level_id')
    formule_id = request.POST.get('formule')
    today = datetime.now().replace(tzinfo=timezone.utc)

    student = Student.objects.get(pk=student_id)
    level   = Level.objects.get(pk=level_id)
    formule = Formule.objects.get(pk=formule_id)
    user = request.user
    this_year = today.year

 
    adhesion = Adhesion.objects.filter(amount = amount , student_id = student_id , formule_id = formule_id, level_id =  level_id , is_active = 0 ).last()
    facture = adhesion.factures.first()
    cmd     = cmd_abonnement(formule,facture.id)
 
    request.session["details_of_student"] = {'student_id' : student_id , 'level_id' : level_id ,  'formule_id' : formule_id , 'amount' : amount , 'today' : start , 'end_day' : stop }

    email=  request.user.email
    billing='<?xml version="1.0" encoding="utf-8" ?><Billing><Address><FirstName>{}</FirstName><LastName>{}</LastName><Address1>Sarlat</Address1><ZipCode>24200</ZipCode><City>Sarlat</City><CountryCode>250</CountryCode></Address></Billing>'.format("Académie","SACADO ACADÉMIE")
    try : y,m,d = stop.split("T")[0].split("-")
    except : y,m,d = stop.split("-")
    end_day = d+"-"+m+"-"+y
    champs_val=champs_briqueCA(amount,cmd,email,1,billing)
    
    context={ 'formule' : formule , 'level' : level , 'student' : student ,  'amount' : amount , 'end_day' : end_day , 'champs_val':champs_val}
    return render(request, 'setup/brique_credit_agricole.html', context)  



def find_facture_and_send_mail(facture_id, autorisation ):

    chrono  = create_chrono(Facture,"F")
    facture = Facture.objects.get(pk=facture_id)
    facture.chrono  = chrono
    facture.orderID = autorisation
    facture.save()
    
    for adhesion in facture.adhesions.all() :
        adhesion.is_active=1
        adhesion.save()

    try :
        sacado_msg = "Bonjour {} {},\n\nVotre paiement vient d'être reçu. \n\nL'équipe de l'ACADÉMIE SACADO vous remercie et vous souhaite une bonne utilisation.\nCordialement.\n\nCeci est  un mail automatique. Ne pas répondre.".format(facture.user.first_name,facture.user.last_name)
        send_mail("Inscription SACADO ACADÉMIE", sacado_msg, settings.DEFAULT_FROM_EMAIL, [facture.user.email,"sacado.academie@gmail.com"])
    
        msg_interne="Paiement reçu : de la part de {} {}, chrono = {}, autorisation={}".format(facture.user.first_name,facture.user.last_name,chrono,autorisation)
        send_mail("Paiement reçu", msg_interne, settings.DEFAULT_FROM_EMAIL, ["sacado.academie@gmail.com", "stephan.ceroi@gmail.com"])
        
    except:
        f=open("logs/debug.log","a")
        print("Erreur d'envoi du mail",file=f)



def paiement_retour(request,status):
    # la banque appelle cette page lorsque la transaction est terminée
    # status = 
    context={}
    erreur=request.GET.get('Erreur',None)
    autorisation=request.GET.get("Auto",None)
    cmd = request.GET.get("Cmd",None)
    f=open("logs/debug.log","a")
      

    if status=="repondre_a" : # envoyé directement par le CA, c'est le seul retour fiable
        ip=request.META.get('HTTP_X_FORWARDED_FOR')
        if ip!="194.2.160.85" and ip!="194.2.122.190" :
            print("ip emetteur : ",ip,"n'est pas dans la liste des ip autorisées",file=f)
            return
        montant=request.GET.get("Mt")
        if erreur!="00000" :
            print("transaction a echoué, code erreur=",erreur, file=f)
        # verifier le montant
 
        signature=request.GET.get("sig")
        facture_id = cmd.split("_")[2]
        find_facture_and_send_mail(facture_id, autorisation )
        msg=request.get_full_path()  #l'url complete avec les données get
        print("================ PAIEMENT REPONDRE_A ================",file=f)
        print(facture_id,file=f)
        print(msg,file=f)
        deb=msg.find("?")
        fin=msg.find("&sig=")
        if deb==-1 or fin==-1 :
            print("Impossible d'extraire la signature à partir de l'url", file=f)
            f.close()
            return render(request,"setup/paiement_retour_vide.html",{})
        signature=msg[fin+5:]
        msg=msg[deb+1:fin]
 
        return render(request,"setup/paiement_retour_vide.html",{})

    elif status=="annule":
        pass
    elif status=="refuse":
        pass
    elif status=="attente":
        pass
    else :
        print("(retour_paiement) : je ne comprends pas le status de la réponse venant de la banque", file=f)

    context['statut']=status
    return render(request,"setup/paiement_retour.html",context)
        
############## FIN CA  #########################



def change_adhesion(request,ids):
    """ liste des adhésions """
    request.session["tdb"] = 'adhesion'
    user     = request.user
    formules = Formule.objects.filter(is_sale=1)
    student  = Student.objects.get(user_id=ids)
    adhesion = student.adhesions.last()    
    today    = time_zone_user(student.user)
    if today.month < 7 : this_year = today.year 
    else : this_year = today.year + 1
 
    context = {    "student" : student , "adhesion" : adhesion   , "formules" : formules   , "this_year" : this_year  }

    return render(request, 'setup/change_adhesion.html', context)


def get_price_and_end_adhesion(formule_id, today, duration, student,level_id ):
    data = {}
    formule = Formule.objects.get(pk=formule_id)
    price_a_month = formule.price

    if student : adhesions = student.adhesions.filter( start__lte=today+ timedelta(days=1), stop__gte=today,is_active=1)
    else : adhesions = None
    if adhesions :
        adhesion = adhesions.last()
        today    = adhesion.stop
    else : 
        adhesion = None

    if today.month < 7 : this_year = today.year 
    else : this_year = today.year + 1

    if(this_year%4==0 and this_year%100!=0 or this_year%400==0) : days_list = [31,29,31,30,31,30,31,31,30,31,30,31,31,29,31,30,31,30,31,31,30,31,30,31]
    else   : days_list = [31,28,31,30,31,30,31,31,30,31,30,31,31,28,31,30,31,30,31,31,30,31,30,31]

    nb_days = 0
    for i in range(int(duration)) :
        nb_days += days_list[today.month+i-1]


    end_of_this_adhesion = today + timedelta(days=nb_days+1)


    if adhesion :
        data["no_end"] = True
        try    : 
            start_str = str(adhesion.stop).split(" ")[0]
            data["date"] = start_str.split("-")[2] +"-"+start_str.split("-")[1]+"-"+start_str.split("-")[0]
        except : data["date"] = str(adhesion.stop)

    else :
        data["no_end"] = False
        data["date"] = str(end_of_this_adhesion)
    if student : price = get_price_by_formules( int(formule_id), int(duration), student.level.id )
    else :  price = get_price_by_formules( int(formule_id), int(duration), level_id )
    
    return data , str(int(price))+",00" , end_of_this_adhesion



def ajax_price_changement_formule(request) :

    student_id = request.POST.get("student_id",None)
    formule_id = request.POST.get("formule_id",None)
    duration   = request.POST.get("duration",None)
    level_id   = request.POST.get("level_id",None)
    today   = time_zone_user(request.user)

 
    if student_id : student = Student.objects.get(user_id=student_id)   
    else : student = None
    
    dataset , price,end_of_this_adhesion = get_price_and_end_adhesion(formule_id, today,duration,student,level_id )
    amount = float(price.replace(",","."))

    try    : adhesion = student.adhesions.last()
    except : adhesion = None


    if today.month < 7 : this_year = today.year
    else :  this_year = today.year + 1
    data = {}
    data["end_of_this_adhesion"] = str(end_of_this_adhesion.day) +"-" + str(end_of_this_adhesion.month) +"-" + str(end_of_this_adhesion.year)
    data["result"]   = str(price) 
    data["amount"]   = amount
    data["start"]    = today
    data["stop"]     = end_of_this_adhesion
    if adhesion:
        data["year"]     = adhesion.year
        data["level_id"] = adhesion.level.id
    else :
        data["year"]     = this_year
        data["level_id"] = level_id

    return JsonResponse(data)


def adhesions_academy(request):
    """ liste des adhésions """
    request.session["tdb"] = 'adhesion'
    user = request.user
    u_parents = all_from_parent_user(user)
    factures =  Facture.objects.filter(user__in=u_parents,is_lesson=1) 
    today = time_zone_user(request.user)
    last_week = today + timedelta(days = 7)
    context = { "factures" : factures,  "last_week" : last_week    }

    return render(request, 'setup/list_adhesions.html', context)



def calcul_remboursement(adhesion) :

    today = time_zone_user(adhesion.user)
    delta = adhesion.date_end - adhesion.date_start
    nb_days = delta.days 

    delta1 = today - adhesion.date_start
    nb_day1s = delta1.days

    ratio = 1 - round(nb_day1s/nb_days,2)

    formule = Formule.objects.get(pk= adhesion.menu)
    adhesion_tab = adhesion.amount.split(",")
    price = float(adhesion_tab[0]+"."+adhesion_tab[1])

    pluri = ""
    if nb_day1s > 1 :
        pluri =  "s"

    nd = str(nb_day1s)+" jour"+pluri

    return round(ratio*price - 5.99,2) , nd



def delete_adhesion(request):

    pk = int(request.POST.get("adh_id"))
    adhesion = Adhesion.objects.get(pk=pk)

    remb  = calcul_remboursement(adhesion)[0]

    msg = "Une demande d'annulation vient d'être formulée de la part de "+adhesion.user+". \n"
    msg += "La référence d'adhésion est "+adhesion.code+" et son id est "+adhesion.id+".\n\n"
    msg += "Le montant du remboursement est de "+remb+"€ au pro-rata des jours adhérés." 

    send_mail("Demande d'annulation d'adhésion SACADO", msg, settings.DEFAULT_FROM_EMAIL, ["sacado.academie@gmail.com"])

    return redirect("adhesions")


 

def csrf_failure(request, reason=""):
    ctx = {'message': 'some custom messages'}
    return render(request,"csrf_failure.html", ctx) 




def list_exercises_academy(request , id):

    level = Level.objects.get(pk=id)    
    exercises = Exercise.objects.filter(level=level,supportfile__is_title=0,theme__subject_id=1).order_by("theme","knowledge__waiting","knowledge","ranking")

    pk_ids = [0,1762,1651,1427,984,2489,2035,4842,8087,5802,1120,3891,3233,0,6107]

    exercise = Exercise.objects.get(pk=pk_ids[id])

    return render(request, 'setup/list_exercises_academy.html', {'exercises': exercises, 'level':level, 'exercise':exercise  })




def envoie_rapport(fichiers,destinataires):
    """envoie les rapports à une seule famille.
    Fichiers contient une liste de noms de fichiers pdf à envoyer
    destinataires : une liste de chaines contenant les destinataires"""
    #------------
    if destinataires==[] :
        return "aucun destinataire"
    
    msg=MIMEMultipart()
    msg['From'] = settings.DEFAULT_FROM_EMAIL
    msg['To'] = destinataires[0]
    for i in range(1,len(destinataires)):
        msg['to']+=","+destinataires[i]
        
    liste_eleves=[]  #liste des eleves dont on joint les rapports

    for fichier in fichiers :
        try :
            pdf=open(fichier,'rb')
            fpdf = MIMEBase('application','octet-stream')
            fpdf.set_payload(pdf.read())
            pdf.close()
            encoders.encode_base64(fpdf)
            fpdf.add_header('content-disposition', 'attachment; filename ='+ fichier)
            msg.attach(fpdf)
            liste_eleves.append("eleve"+fichier)
        except :
            print("""fonction envoie_pdf de setup : 
le fichier {} qui doit être envoyé à {} est introuvable""".format(fichier,msg['To']))
    npdf=len(liste_eleves)  #nombre de fichiers à envoyer
    if npdf==0 :
        print("""fonction envoie_pdf de setup : 
aucun fichier pdf à envoyer""")
        return "aucun fichier pdf à envoyer"

    # preparation du joli texte du corps du message
    eleves=liste_eleves[0]
    if npdf==1 :
        pluriel=""
    else :
        pluriel="s"
        for i in range(1,npdf-1) :
            eleves+=", "+liste_eleves[i]
        eleves+=" et "+liste_eleves[-1]
    #-------------------------------
    msg['Subject'] = "Rapport{} d'activité de ".format(pluriel)+eleves
    
    msg.attach(MIMEText("""Bonjour,
veuillez trouver en pièce jointe le{} rapport{} d'activité{} de {}.

Très cordialement,

L'équipe Sacado Académie""".format(pluriel,pluriel,pluriel,eleves),'plain'))

    server = smtplib.SMTP(settings.EMAIL_HOST,settings.EMAIL_PORT)
    server.set_debuglevel(False) # show communication with the server
    try:
       server.ehlo()
       if server.has_extn('STARTTLS'):
          server.starttls()
          server.ehlo() 
       server.login(settings.DEFAULT_FROM_EMAIL, settings.EMAIL_HOST_PASSWORD)
       server.sendmail(settings.DEFAULT_FROM_EMAIL, destinataires,msg.as_string() )
    finally:
        server.quit()
    return "mails envoyés avec succès"



    
def send_reports(request) :
    """envoie tous les rapports à toutes les familles"""
    fichiers=["toto1.pdf","toto2.pdf", "toto1.pdf"]
    destinataires=["stephan.ceroi@mailo.com","stephan.ceroi@gmail.com"]
    r=envoie_rapport(fichiers, destinataires)
    return HttpResponse(r)








@is_manager_of_this_school
def admin_tdb(request):

    school = request.user.school
    schools = request.user.schools.all()
 
    schools_tab = [school]
    for s in schools :
        schools_tab.append(s)

    teachers = Teacher.objects.filter(user__school=school, user__user_type=2)

    nb_teachers = teachers.count()
    nb_students = User.objects.filter(school=school, user_type=0).exclude(username__contains="_e-test_").count()
    nb_groups   = Group.objects.filter(Q(teacher__user__school=school)|Q(teacher__user__schools=school)).count()
    
    is_lycee = False
    try :
        if not school.get_seconde_to_comp :
            for t in teachers :
                if t.groups.filter(level__gte=10).count() > 0 :
                    is_lycee = True
                    break
    except :
        pass

    try:
        stage = Stage.objects.get(school=school)
        if stage:
            eca, ac, dep = stage.medium - stage.low, stage.up - stage.medium, 100 - stage.up
        else:
            eca, ac, dep = 20, 15, 15

    except:
        stage = {"low": 50, "medium": 70, "up": 85}
        eca, ac, dep = 20, 15, 15
    
    if len(schools_tab) == 1 :
        school_id = request.user.school.id
        request.session["school_id"] = school_id
    else :
        if request.session.get("school_id",None) :
            school_id = int(request.session.get("school_id",None))
        else :
            school_id = 0

    rates       = Rate.objects.all() #tarifs en vigueur 
    school_year = Activeyear.objects.get(is_active=1).year  

    renew_propose = False
    last_accounting = school.accountings.filter(date_payment=None)
    if last_accounting :
        renew_propose = True

 
    return render(request, 'dashboard_admin.html', {'nb_teachers': nb_teachers, 'nb_students': nb_students, 'school_id' : school_id , "school" : school ,  'renew_propose' : renew_propose ,
                                                    'nb_groups': nb_groups, 'schools_tab': schools_tab, 'stage': stage, 'is_lycee' : is_lycee , 'school_year' : school_year ,  'rates' : rates , 
                                                    'eca': eca, 'ac': ac, 'dep': dep , 'communications' : [],
                                                    })


def gestion_files(request):
    levels = Level.objects.all()
    if request.method == "POST":

        level_id = request.POST.get("level")
        level = Level.objects.get(pk=level_id)
        supportfiles = Supportfile.objects.filter(level_id=level_id, is_title=0)
    else:
        level, level_id = None, 0
        supportfiles = []

    context = {'levels': levels, 'level': level, 'level_id': level_id, 'level_id': level_id,
               'supportfiles': supportfiles}

    return render(request, 'setup/gestion_files.html', context )


def get_cookie(request):
    request.session["cookie"] = "accept"
    return redirect('index')




@login_required
def questionnaire(request) :
    """questionnaire après adhesion"""
    student = request.user.student

    form = DescriptionForm(request.POST or None )
 
    context = {    "form" : form   ,  "student" : student   }

    return render(request, 'setup/questionnaire.html', context)







##################################################################################################################
##################################################################################################################
#########################################  play_quizz  ###########################################################
##################################################################################################################
################################################################################################################## 


def play_quizz(request):

    context = {}
    return render(request, 'tool/play_quizz.html', context)

 
def play_quizz_login(request):


    code = request.POST.get("code")
 
    if Quizz.objects.filter(code = code).count() == 1:

        quizz = Quizz.objects.get(code = code)
        groups = quizz.groups.all()
        student_set = set()
        for group in groups :
            student_set.update(group.students.all())
        students = list(student_set)
        random.shuffle(students)
 

        context = { "quizz" : quizz , "students" : students , }
        return render(request, 'tool/play_quizz_login.html', context)
    else :
        context = { 'error' : True}
        return render(request, 'tool/play_quizz.html', context)
 

def play_quizz_start(request):

    student_id = request.POST.get("student_id")
    student = Student.objects.get(pk = student_id)

    quizz_id = request.POST.get("quizz_id")
    quizz = Quizz.objects.get(pk = quizz_id)
    
    n = request.POST.get("n",0)

    quizz.students.add(student)
   
    questions = list(quizz.questions.order_by("ranking"))
    question = questions[n]    
    n +=1
    context = {  "quizz" : quizz , "question" : question , "n" : n}
    return render(request, 'tool/play_quizz_start.html', context)

##################################################################################################################
##################################################################################################################
##############################################  AJAX  ############################################################
##################################################################################################################
################################################################################################################## 

def ajax_get_price(request):

    nbr_students = request.POST.get("nbr_students",None)
    data = {}
    price = ""
    if nbr_students :
        if int(nbr_students) < 1500 : 
            adhesion = Rate.objects.filter(quantity__gte=int(nbr_students)).first()
            
            today = datetime.now()

            seuil = datetime(2021, 7, 1)

            if today < seuil :
                price = adhesion.discount
            else :
                price = adhesion.amount

    data["price"] = price

    return JsonResponse(data)



def ajax_remboursement(request):
    data_id = int(request.POST.get("data_id"))
    adhesion = Adhesion.objects.get(pk=data_id)
    data ={}
    data["remb"] , data["jour"] = calcul_remboursement(adhesion)
    return JsonResponse(data)


 
def ajax_changecoloraccount(request):
    """
    Appel Ajax pour afficher la liste des élèves du groupe sélectionné
    """
    if request.user.is_authenticated:
        code = request.POST.get('code')

    color = request.user.color
    filename1 = "static/css/navbar-fixed-left.min.css"
    filename2 = "static/css/AdminLTEperso.css"

    User.objects.filter(pk=request.user.id).update(color=code)

    change_color(filename1, color, code)
    change_color(filename2, color, code)

    return redirect("index")


def change_color(filename, color, code):
    # Read in the file
    with open(filename, 'r') as file:
        filedata = file.read()
    # Replace the target string
    filedata = filedata.replace(color, code)
    # Write the file out again
    with open(filename, 'w') as file:
        file.write(filedata)



############################################################################################
#######  WEBINAIRE
############################################################################################


def webinaire_register(request):

    today = time_zone_user(request.user) 
    webinaire = Webinaire.objects.filter(date_time__gte=today,is_publish=1).first()
    nb_places = 20 - webinaire.users.count()
    return render(request, 'setup/form_webinaire_register.html', {'webinaire': webinaire , 'nb_places' : nb_places })


def webinaire_registrar(request,id,key):

    if request.user.is_superuser :
        webinaire = Webinaire.objects.get(id=id)
        if key == 1:
            webinaire.users.add(request.user)
        else :
            webinaire.users.remove(request.user)

    return redirect('index') 



def webinaire_show(request,id):
    if request.user.is_superuser :
        webinaire = Webinaire.objects.get(id=id)
        return render(request, 'setup/show_webinaire.html', {'webinaire': webinaire })
    else :
        return redirect('index') 



def webinaire_list(request):
    if request.user.is_superuser :
        webinaires = Webinaire.objects.all()
        return render(request, 'setup/list_webinaires.html', {'webinaires': webinaires })
    else :
        return redirect('index') 



def webinaire_create(request):

    if request.user.is_superuser :
        form = WebinaireForm(request.POST or None ,  request.FILES or None  )
        if form.is_valid():
            form.save()
            messages.success(request, 'Le webinaire a été créé avec succès !')
            return redirect('webinaires')
        else:
            print(form.errors)
        context = {'form': form, 'communications' : [] , 'webinaire': None  }

        return render(request, 'setup/form_webinaire.html', context)
    else :
        return redirect('index') 



def webinaire_update(request, id):

    if request.user.is_superuser :
        webinaire = Webinaire.objects.get(id=id)
        form = WebinaireForm(request.POST or None, request.FILES or None, instance=webinaire )
        if request.method == "POST" :
            if form.is_valid():
                form.save()
                messages.success(request, 'Le webinaire a été modifié avec succès !')
                return redirect('webinaires')
            else:
                print(theme_form.errors)

        context = {'form': form,  'webinaire': webinaire,   }

        return render(request, 'setup/form_webinaire.html', context )
    else :
        return redirect('index')  


def webinaire_delete(request, id):
    if request.user.is_superuser :
        webinaire = Webinaire.objects.get(id=id)
        webinaire.delete()

        return redirect('webinaires')
    else :
        return redirect('index') 

############################################################################################
#######  SET UP
############################################################################################


def rgpd(request):
    context = {  }
    return render(request, 'setup/rgpd_gar.html', context)  

def gar_rgpd(request):
    context = {  }
    return render(request, 'setup/rgpd_gar.html', context)  


def cgu(request):
    context = {  }
    return render(request, 'setup/cgu.html', context)  


def cgv(request):
    context = {  }
    return render(request, 'setup/cgv.html', context)  


def mentions(request):
    context = {  }
    return render(request, 'setup/mentions.html', context)  

def mentions_academy(request):
    context = {  }
    return render(request, 'setup/mentions_academy.html', context)  


def tweeters(request):
    if request.user.is_superuser :
        tweeters = Tweeter.objects.all().order_by("-date_created")
        return render(request, 'setup/tweeters.html', {'tweeters': tweeters })
    else :
        return redirect('index') 


def tweeters_public(request):
    tweeters = Tweeter.objects.all().order_by("-date_created")
    return render(request, 'setup/tweeters_public.html', {'tweeters': tweeters })
 
def tweeter_create(request):

    if request.user.is_superuser :
        form = TweeterForm(request.POST or None  )
        if form.is_valid():
            form.save()
            messages.success(request, 'Le tweet a été créé avec succès !')
            return redirect('tweeters')
        else:
            print(form.errors)
        context = {'form': form, 'tweeter': None  }

        return render(request, 'setup/form_tweeter.html', context)
    else :
        return redirect('index') 

def tweeter_update(request, id):

    if request.user.is_superuser :
        tweeter = Tweeter.objects.get(id=id)
        form = TweeterForm(request.POST or None,  instance=tweeter )
        if request.method == "POST" :
            if form.is_valid():
                form.save()
                messages.success(request, 'Le tweet a été modifié avec succès !')
                return redirect('tweeters')
            else:
                print(form.errors)

        context = {'form': form,  'tweeter': tweeter,   }

        return render(request, 'setup/form_tweeter.html', context )
    else :
        return redirect('index')  


def tweeter_delete(request, id):
    if request.user.is_superuser :
        tweeter = Tweeter.objects.get(id=id)
        tweeter.delete()

        return redirect('tweeters')
    else :
        return redirect('index') 
