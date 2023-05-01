#################################
#### Auteur : philipe Demaria 
#### pour SACADO
#################################

from django.conf import settings # récupération de variables globales du settings.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import  AuthenticationForm
from django.forms.models import modelformset_factory
from django.forms import inlineformset_factory
from django.contrib.auth.decorators import  permission_required,user_passes_test, login_required
from django.db.models import Q , Sum , Avg
from django.core.mail import send_mail
from django.http import JsonResponse 
from django.core import serializers
from django.core.files.storage import FileSystemStorage
from django.template.loader import render_to_string
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from account.decorators import user_can_create, user_is_superuser, user_is_creator , user_is_testeur
from account.models import  Student, Teacher, User,Resultknowledge, Resultskill, Resultlastskill
from account.forms import StudentForm, TeacherForm, UserForm
from bibliotex.models import Bibliotex
from flashcard.models import Flashpack
from group.decorators import user_is_group_teacher 
from group.forms import GroupForm 
from group.models import Group , Sharing_group
from qcm.decorators import user_is_parcours_teacher, user_can_modify_this_course, student_can_show_this_course , user_is_relationship_teacher, user_is_customexercice_teacher , parcours_exists , folder_exists
from qcm.models import *
from qcm.forms import * 
from qcm.grid_letters_creator import * 
from school.models import Stage, School
from sendmail.forms import  EmailForm
from socle.models import  Theme, Knowledge , Level , Skill , Waiting , Subject
from tool.consumers import *
from tool.models import Quizz , Answerplayer , Qtype
from tool.forms import QuizzForm

import uuid
import time
import math
import json
import random
from datetime import datetime , timedelta

##############bibliothèques pour les impressions pdf  #########################
from pdf2image import convert_from_path # convertit un pdf en autant d'images que de pages du pdf
from django.utils import formats, timezone
from io import BytesIO, StringIO
from django.http import  HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, inch, landscape , letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image , PageBreak , PageTemplate, Frame , FrameBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import yellow, red, black, white, blue
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.enums import TA_JUSTIFY,TA_LEFT,TA_CENTER,TA_RIGHT
from html import escape
from operator import attrgetter
from itertools import chain
cm = 2.54
import re
import pytz
import csv
import html
from general_fonctions import *
import xlwt 

 
# def duration_all_relationship():

#     exercises = Exercise.objects.all()
#     for exercise in exercises :
#         seconde_avg = exercise.ggbfile_studentanswer.aggregate(average=Avg("secondes"))
#         if seconde_avg['average'] :
#             for relationship in exercise.exercise_relationship.all() :
#                 relationship.duration = int(seconde_avg['average'] // 60) + 2
#                 relationship.save()




def is_sacado_asso(this_user, today):
    is_sacado = False
    is_active = False
    try :
        abonnement = this_user.school.abonnement.last()
        if today < abonnement.date_stop and abonnement.is_active :
            is_sacado = True
            is_active = True
    except :
        pass
    return is_sacado, is_active


#################################################################
# Transformation de parcours en séquences
#################################################################
def all_parcours_to_sequences(request):

    parcourses = Parcours.objects.filter(teacher_id=2480,is_trash=0,is_sequence = 0)
    for parcours in parcourses :
        students = parcours.students.all()

    customexercises  = parcours.parcours_customexercises.all()
    for c  in customexercises : 
        relationc = Relationship.objects.create(parcours = parcours , exercise_id = None , document_id = c.id  , type_id = 2 , ranking =  200 , is_publish= c.is_publish  , start= None , date_limit= None, duration= c.duration, situation= 0 ) 
        relationc.students.set(students)


        courses    = parcours.course.all()
        for course in courses : 
            relation = Relationship.objects.create(parcours = parcours , exercise_id = None , document_id = course.id  , type_id = 2 , ranking =  200 , is_publish= course.is_publish  , start= None , date_limit= None, duration= course.duration, situation= 0 ) 
            relation.students.set(students)
        
        quizzes    = parcours.quizz.all()
        for quizz in quizzes : 
            relationq = Relationship.objects.create(parcours = parcours , exercise_id = None , document_id = quizz.id  , type_id = 3 , ranking =  200 , is_publish= quizz.is_publish , start= None , date_limit= None, duration= 10, situation= 0 ) 
            relationq.students.set(students)

        flashpacks  = parcours.flashpacks.all()
        for flashpack in flashpacks : 
            relationf = Relationship.objects.create(parcours = parcours , exercise_id = None , document_id = flashpack.id  , type_id = 4 , ranking =  200 , is_publish= flashpack.is_publish  , start= None , date_limit= None, duration= 10, situation= 0 ) 
            relationf.students.set(students)

        bibliotexs = parcours.bibliotexs.all()
        for bibliotex in bibliotexs : 
            relationb = Relationship.objects.create(parcours = parcours , exercise_id = None , document_id = bibliotex.id  , type_id = 5 , ranking =  200 , is_publish= bibliotex.is_publish  , start= None , date_limit= None, duration= 10, situation= 0 ) 
            relationb.students.set(students)


        Parcours.objects.filter(pk=parcours.id).update(is_sequence=1)


    context = { 'parcourses' : parcourses ,   }
    return render(request, 'qcm/all_parcours_to_sequences.html', context ) 



def this_parcours_to_sequences(request,idp):

    parcours = Parcours.objects.get(pk=idp)
    students = parcours.students.all()

    customexercises    = parcours.parcours_customexercises.all()
    for c  in customexercises : 
        relationc = Relationship.objects.create(parcours = parcours , exercise_id = None , document_id = c.id  , type_id = 2 , ranking =  200 , is_publish= c.is_publish  , start= None , date_limit= None, duration= c.duration, situation= 0 ) 
        relationc.students.set(students)

    courses    = parcours.course.all()    

    for course in courses : 
        relation = Relationship.objects.create(parcours = parcours , exercise_id = None , document_id = course.id  , type_id = 2 , ranking =  200 , is_publish= course.is_publish  , start= None , date_limit= None, duration= course.duration, situation= 0 ) 
        relation.students.set(students)
    
    quizzes    = parcours.quizz.all()
    for quizz in quizzes : 
        relationq = Relationship.objects.create(parcours = parcours , exercise_id = None , document_id = quizz.id  , type_id = 3 , ranking =  200 , is_publish= quizz.is_publish , start= None , date_limit= None, duration= 10, situation= 0 ) 
        relationq.students.set(students)

    flashpacks  = parcours.flashpacks.all()
    for flashpack in flashpacks : 
        relationf = Relationship.objects.create(parcours = parcours , exercise_id = None , document_id = flashpack.id  , type_id = 4 , ranking =  200 , is_publish= flashpack.is_publish  , start= None , date_limit= None, duration= 10, situation= 0 ) 
        relationf.students.set(students)

    bibliotexs = parcours.bibliotexs.all()
    for bibliotex in bibliotexs : 
        relationb = Relationship.objects.create(parcours = parcours , exercise_id = None , document_id = bibliotex.id  , type_id = 5 , ranking =  200 , is_publish= bibliotex.is_publish  , start= None , date_limit= None, duration= 10, situation= 0 ) 
        relationb.students.set(students)


    Parcours.objects.filter(pk=idp).update(is_sequence=1)


    return redirect('show_parcours' , 0 , idp  ) 


#################################################################
#  
#################################################################

def fill_the_skills(request):

    rs = Relationship.objects.filter(skills=None,exercise__supportfile__is_title=0)
    nb = rs.count() 
    relations = rs[:1000]
    for r in relations:
        rse = r.exercise.supportfile.skills.all()
        r.skills.set( rse )
    context = { 'nb' : nb ,   }
    return render(request, 'qcm/fill_the_skills_page.html', context )

#################################################################
# Duplication des folder
#################################################################
 
def find_no_skill(request):

    skills   = Skill.objects.filter(subject_id=1)
    supports = Supportfile.objects.filter(skills=None, is_title=0)
    context  = {'supports': supports,  'skills': skills,  }

    return render(request, 'qcm/find_no_skill.html', context )



def get_skill_to_support(request) :
    no_skills = request.POST.getlist("no_skills")
 
    for ns in no_skills :
        tab = ns.split("==")
 
        support = Supportfile.objects.get(pk=tab[0])
 
        skill   = Skill.objects.get(pk=tab[1])
        support.skills.add(skill)
 
    return redirect("find_no_skill")

# def remove_parcours_folder(request):

#     old_folders = Parcours.objects.filter(is_folder=1) 

#     for old_folder in old_folders :
#         old_folder.groups.clear()
#         old_folder.students.clear()
#         old_folder.coteachers.clear()
#         Parcours.objects.filter(pk=old_folder.id).update(is_trash=1)


#     return redirect('index' )

def get_accordion(c,q,b,f):
    accordion = True
    if c : nb_accordion = c.count() + q.count() + b.count() + f.count() 
    else : nb_accordion = q.count() + b.count() + f.count()
    if nb_accordion == 0:
        accordion = False
    return accordion


#################################################################
#Récupération du parcours Seconde to Maths complémentaires
#################################################################

def folders_contains_evaluation(folds, is_eval,is_sequence) :
    folders = []
    if is_eval :
        for folder in folds :
            for p in folder.parcours.filter(is_trash=0) :
                if p.is_evaluation and folder not in folders :
                    folders.append(folder)
    else :
        for folder in folds :
            for p in folder.parcours.filter(is_sequence = is_sequence,is_trash=0) :
                if not p.is_evaluation and folder not in folders :
                    folders.append(folder)
    return folders



def get_teacher_id_by_subject_id(subject_id):

    if subject_id == 1 or subject_id == "1" :
        teacher_id = 2480

    elif  subject_id == 2 or subject_id == "2" :
        teacher_id = 35487

    elif subject_id == 3 or subject_id == "3"  :
        teacher_id = 37053

    else :
        teacher_id = 2480

    return teacher_id


def get_images_for_parcours_or_folder(group):
    try :
        sacadoprof_id = get_teacher_id_by_subject_id(group.subject.id)
        images = set()
        imags = Folder.objects.values_list("vignette", flat = True).filter(Q(teacher_id= sacadoprof_id)|Q(teacher= group.teacher),level_id=group.level.id, subject_id=group.subject.id).exclude(vignette=" ").distinct()
        images.update(imags)
        imgs = Parcours.objects.values_list("vignette", flat = True).filter(Q(teacher_id= sacadoprof_id)|Q(teacher= group.teacher), level_id=group.level.id, subject_id=group.subject.id).exclude(vignette=" ").distinct()
        images.update(imgs)
    except :
        images = []
    return images



def get_seconde_to_math_comp(request):

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')
 
    group = Group.objects.get(id=1921)#groupe fixe sur le serveur 1921

    parcourses = group.group_parcours.all()

    cod = "_e-test_"+ str(uuid.uuid4())[:4]  
    user = User.objects.create(last_name=teacher.user.last_name, first_name =teacher.user.first_name+cod , email="", user_type=0,
                                                      school=request.user.school, time_zone=request.user.time_zone,
                                                      is_manager=0, username = teacher.user.username+ cod  ,  password ="sacado2020",
                                                      is_extra = 0 )
    student = Student.objects.create(user=user, level=group.level, task_post=1)

    group.pk = None
    group.teacher = teacher
    group.code = str(uuid.uuid4())[:8]  
    group.lock = 0
    group.save()

    group.students.add(student)

    all_new_parcours_folders , all_new_parcours_leaves  = [],[]

    for parcours in parcourses :

        relationships = parcours.parcours_relationship.all() 
        courses = parcours.course.all()
        #################################################
        # clone le parcours
        #################################################
        parcours.pk = None
        parcours.teacher = teacher
        parcours.is_publish = 1
        parcours.is_archive = 0
        parcours.is_share = 0
        parcours.is_favorite = 1
        parcours.target_id = None
        parcours.code = str(uuid.uuid4())[:8]  
        parcours.save()
        if parcours.is_folder :
            all_new_parcours_folders.append(parcours)
        else :
            all_new_parcours_leaves.append(parcours)
        parcours.groups.add(group)
        parcours.students.add(student)
        #################################################
        # clone les exercices attachés à un cours 
        #################################################
        former_relationship_ids = []

        for course in courses :

            old_relationships = course.relationships.all()
            # clone le cours associé au parcours
            course.pk = None
            course.parcours = parcours
            course.save()



            for relationship in old_relationships :
                # clone l'exercice rattaché au cours du parcours 
                if not relationship.id in former_relationship_ids :
                    relationship.pk = None
                    relationship.parcours = parcours
                    relationship.save()


                course.relationships.add(relationship)
                former_relationship_ids.append(relationship.id)

        #################################################
        # clone tous les exercices rattachés au parcours 
        #################################################
        for relationship in relationships :
            try :
                relationship.pk = None
                relationship.parcours = parcours
                relationship.save()       
                relationship.students.add(student)
            except :
                pass
        try :
            for prcr in all_new_parcours_folders :
                prcr.set(all_new_parcours_leaves)
        except :
            pass

    School.objects.filter(pk = request.user.school.id).update(get_seconde_to_comp=1)

    messages.success(request,"Tous les parcours du groupe PREPA Maths Complémentaires ont été placés dans tous les dossiers. Vous devez manuellement les sélectionner pour personnaliser vos dossiers.")

    return redirect('admin_tdb' )



def set_students(nf,stus) :
    try:
        if len(stus) > 0 :
            nf.students.set(stus)
        var = True
    except :
        var = False
    return var

def set_groups(nf,gps) :
    try:
        if len(gps) > 0 :
            nf.groups.set(gps)   
        var = True
    except :
        var = False
    return var


def clear_realtime(parcours_tab , today,  timer ):
    """  efface le realtime de plus de timer secondes sur un ensemble de parcours parcours_tab """
    today_delta = today.now() - timedelta(seconds = timer)
    Tracker.objects.filter(parcours__in = parcours_tab, date_created__lte= today_delta).delete()

##################################################################################################################################
##################################################################################################################################
##################################################################################################################################

def new_content_type(s):
    names = ['Pages', 'Questionnaires', 'Activités', 'Tâches',  'Fichiers', 'Urls externes', 'Discussions' , 'Notes',  'Acquis', 'Participants', 'Suivis' ]                
    slugs = ['page', 'test',  'activity', 'task', 'file', 'url', 'discussion', 'mark', 'acquis', 'user', 'suivi' ]   
    verbose_names = ['Toutes les pages', 'Tous les questionnaires', 'Toutes les activités', 'Toutes les tâches',  'Tous les fichiers', 'Toutes les urls externes', 'Toutes les discussions', 'Notes', 'Acquis', 'Tous les participants', 'Les suivis des activités' ] 

    for i in range(len(names)) :
        verbose_button = verbose_names[i]
        slug = slugs[i]
        name = names[i]
        image = "img/"+slugs[i]+".png"
        Content_type.objects.create(name = name, image = image , slug = slug ,verbose_button = verbose_button, display = 1 ,section = s)

def get_time(s,e):
    start_time = s.split(",")[0]
    end_time = e.split(".")[0]
    full_time = int(end_time) - int(start_time)
    return  full_time


def convert_seconds_in_time(secondes):
    if secondes < 60:
        return "{}s".format(secondes)
    elif secondes < 3600:
        minutes = secondes // 60
        sec = secondes % 60
        if sec < 10:
            sec = f'0{sec}'
        return "{}:{}".format(minutes, sec)
    else:
        hours = secondes // 3600
        minutes = (secondes % 3600) // 60
        sec = (secondes % 3600) % 60
        if sec < 10:
            sec = f'0{sec}'
        if minutes < 10:
            minutes = f'0{minutes}'
        return "{}:{}:{}".format(hours, minutes, sec)



def sending_to_teachers(teacher , level,subject,topic) : # envoie d'une notification au enseignant du niveau coché lorsqu'un exercice est posté
    try :
        users = teacher.user.school.users.filter(user_type=2)
        for u in users :
            if u.teacher.exercise_post :
                if u.email : 
                    msg =  str(topic) + " vient d'être publié sur SacAdo sur le niveau "+str(level.name)+" en "+str(subject.name)+"\n\nSi vous ne souhaitez plus recevoir ces notifications, décochez dans votre profil cette option (notification 2)."
                    sending_mail(str(topic) +" SacAdo",  msg , settings.DEFAULT_FROM_EMAIL , u.email)
    except :
        pass

    

def students_from_p_or_g(request,parcours) :
    """
    Si un groupe est en session, renvoie la liste des élèves du groupe et du parcours
    Sinon les élèves du parcours
    Classés par ordre alphabétique
    """
    try :
        group_id = request.session["group_id"]
        group = Group.objects.get(id = group_id) 
        students_group = group.students.order_by("user__last_name")
        students_parcours = parcours.students.order_by("user__last_name")
        students = [student for student in students_parcours if student   in students_group] # Intersection des listes
    except :
        students = list(parcours.students.order_by("user__last_name"))
    return students

def get_complement(request, teacher, parcours_or_group):

    try :
        group_id = request.session.get("group_id",None)
        if group_id :
            group = Group.objects.get(pk = group_id)
        else :
            try :
                group = parcours_or_group.groups.first()
            except :
                group = None 

        if Sharing_group.objects.filter(group_id= group_id , teacher = teacher).exists() :
            sh_group = Sharing_group.objects.get(group_id=group_id, teacher = teacher)
            role = sh_group.role
            access = True
        else :
            role = False
            access = False
    except :
        group_id = None
        role = False
        group = None
        access = False

    if parcours_or_group.teacher == teacher or teacher.user.is_superuser :
        role = True
        access = True

    return role, group , group_id , access


def get_stage(user):

    try :
        if user.school :
            school = user.school
            stg = Stage.objects.get(school = school)
            stage = { "low" : stg.low ,  "medium" : stg.medium  ,  "up" : stg.up  }
        else : 
            stage = { "low" : 50 ,  "medium" : 70 ,  "up" : 85  }
    except :
        stage = { "low" : 50 ,  "medium" : 70 ,  "up" : 85  }  
    return stage


def group_has_parcourses(group,is_evaluation ,is_archive ):
    pses_tab = []

    for s in group.students.all() :
        pses = s.students_to_parcours.filter(is_evaluation=is_evaluation,is_archive=is_archive)
        for p in pses :
            if p not in  pses_tab :
                pses_tab.append(p)
    return pses_tab



def teacher_has_parcourses(teacher,is_evaluation ,is_archive ):
    """
    Renvoie les parcours dont le prof est propriétaire et donc les parcours lui sont partagés
    """
    parcours      =  teacher.teacher_parcours.filter(is_evaluation=is_evaluation,is_archive=is_archive,is_trash=0)
    parcourses_co = teacher.coteacher_parcours.filter(is_evaluation=is_evaluation,is_archive=is_archive,is_trash=0 )
    parcourses    = parcours | parcours_co 
    prcs          = parcourses.order_by("subject","level")
    return prcs


def teacher_has_folders(teacher ,is_archive ):
    """ 
    Renvoie les parcours dont le prof est propriétaire et donc les parcours lui sont partagés
    """
    folders    = teacher.teacher_folders.filter( is_archive=is_archive,is_trash=0)
    folders_co = teacher.coteacher_folders.filter( is_archive=is_archive,is_trash=0 )
    fold       = folders | folders_co
    folds      = fold.order_by("subject","level")
    return folds



def teacher_has_own_parcourses_and_folder(teacher,is_evaluation,is_archive,is_sequence ):
    """
    Renvoie les parcours et les dossiers dont le prof est propriétaire
    """
    parcourses =  teacher.teacher_parcours.filter( is_evaluation=is_evaluation,is_archive=is_archive,is_trash=0,is_sequence = is_sequence ).order_by("subject","level")

    return parcourses



def teacher_has_parcourses(teacher,is_evaluation ,is_archive ):
    """
    Renvoie les parcours dont le prof est propriétaire et donc les parcours lui sont partagés
    """
    sharing_groups = teacher.teacher_sharingteacher.all()
    parcourses =  teacher.teacher_parcours.filter(is_evaluation=is_evaluation,is_archive=is_archive,is_trash=0).order_by("subject","level") 

    coteacher_parcours = teacher.coteacher_parcours.filter(is_evaluation=is_evaluation,is_archive=is_archive,is_trash=0).order_by("subject","level")

    prcs = list(parcourses | coteacher_parcours)
    # for sg in sharing_groups :
    #     pcs = group_has_parcourses(sg.group,is_evaluation ,is_archive )
    #     for p in pcs :
    #         if p not in parcourses:
    #             parcourses.append(p) 
    return parcourses

def teacher_has_permisson_to_share_inverse_parcourses(request,teacher,parcours):
    """
    Quand un enseignant partage son groupe, il doit aussi voir les parcours que son co animateur propose.
    """
    test_has_permisson = False
    for student in parcours.students.all() :
        for group in teacher.groups.all() :
            if student in group.students.all()  :
                test_has_permisson = True
                break
    #if parcours.is_share == 1 : test_has_permisson = True
    return test_has_permisson

def teacher_has_permisson_to_parcourses(request,teacher,parcours):


    test_has_permisson = teacher_has_permisson_to_share_inverse_parcourses(request,teacher,parcours)

    if test_has_permisson or parcours in teacher_has_parcourses(teacher,0,0) or parcours in teacher_has_parcourses(teacher,0,1) or parcours in teacher_has_parcourses(teacher,1,0) or parcours in teacher_has_parcourses(teacher,1,1):
        has_permisson = True
    elif request.user.is_superuser or request.user.is_creator or request.user.is_testeur :
        has_permisson = True
    else :
        messages.error(request, "  !!!  Redirection automatique  !!! Violation d'accès. Contacter SACADO...")
        has_permisson = False
    return has_permisson 


def teacher_has_permisson_to_folder(request,teacher,folder):

    has_permisson = False
    if teacher in folder.coteachers.all() or folder.teacher == teacher :
        has_permisson = True

    return has_permisson 




def skills_in_parcours(request,parcours):

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')


    relationships = Relationship.objects.filter(parcours=parcours)
    skillsInParcours = set()
    for r in relationships:
        skillsInParcours.update(r.skills.all()) # skill des exo sacado

    customexercises = Customexercise.objects.filter(parcourses=parcours)
    for c in customexercises :
        skillsInParcours.update(c.skills.all()) # skill des exo perso

    skills = Skill.objects.filter(subject__in = request.user.teacher.subjects.all())

    union_skills = []
    for s in skills :
        if s in skillsInParcours :
            union_skills.append(s)

    return union_skills

# def skills_in_parcours(parcours):
#     """
#     version moins rapide sans request
#     """
#     skills = []
#     for exercise in parcours.exercises.all():
#         relationships = exercise.exercise_relationship.filter(parcours=parcours)
#         for r in relationships :
#             for sk in r.skills.all() :
#                 if sk not in skills :
#                     skills.append(sk)
#     for ce in parcours.parcours_customexercises.all():
#         for sk in ce.skills.all() :
#             if sk not in skills :
#                 skills.append(sk)   
#     return skills


def knowledges_in_parcours(parcours):

    knowledges = []
    for exercise in parcours.exercises.filter(supportfile__is_title=0):
        relationships = exercise.exercise_relationship.filter(parcours=parcours,is_publish=1)
        for r in relationships :
            sr = r.exercise.knowledge
            if sr not in knowledges :
                    knowledges.append(sr)
    for ce in parcours.parcours_customexercises.all():
        for sk in ce.knowledges.all() :
            if sk not in knowledges :
                knowledges.append(sk)
    return knowledges


def total_by_skill_by_student(skill,relationships, parcours,student) : # résultat d'un élève par compétence sur un parcours donné
    total_skill = 0            
    scs = student.student_correctionskill.filter(skill = skill, parcours = parcours)
    nbs = scs.count()
 
    for sc in scs :
        total_skill += int(sc.point)

    # Ajout éventuel de résultat sur la compétence sur un exo SACADO
    exercise_ids = relationships.values_list("exercise_id").filter(skills = skill  )

    result_sacado_skills = student.answers.filter(parcours= parcours , exercise_id__in = exercise_ids   ) 
    #student.student_resultggbskills.filter(skill= skill, relationship__in = relationships)
    for rss in result_sacado_skills :
        total_skill += rss.point
        nbs += 1

    ################################################################

    if nbs != 0 :
        tot_s = total_skill//nbs
    else :
        tot_s = -10

    return tot_s


def total_by_knowledge_by_student(knowledge,relationships, parcours,student) : # résultat d'un élève par knowledge sur un parcours donné
    total_knowledge = 0            
    sks = student.student_correctionknowledge.filter(knowledge = knowledge, parcours = parcours)
    nbk = sks.count()

    for sk in sks :
        total_knowledge += int(sk.point)

    # Ajout éventuel de résultat sur la compétence sur un exo SACADO
    result_sacado_knowledges = student.answers.filter(parcours= parcours , exercise__knowledge = knowledge) 
    for rsk in result_sacado_knowledges :
        total_knowledge += rsk.point
        nbk += 1

    ################################################################
    if nbk !=0  :
        tot_k = total_knowledge//nbk
    else :
        tot_k  = -10
    return tot_k



################################################################
##  Trace les élève lors l'exécution d'exercice : Real time
################################################################


def tracker_execute_exercise(track_untrack ,  user , idp=0 , ide=None , custom=0) :
    """ trace l'utilisateur. Utile pour le real time """
    if track_untrack :
        try :
            Tracker.objects.get_or_create( user = user , parcours_id = idp , exercise_id = ide , is_custom= custom)
        except :
            pass
    else :
        try :
            tracker, created = Tracker.objects.get_or_create( user= user , parcours_id = idp , exercise_id = ide , is_custom= custom)
            tracker.delete()
        except :
            pass


#######################################################################################################################################################################
#######################################################################################################################################################################
#################   parcours par defaut
#######################################################################################################################################################################
#######################################################################################################################################################################
@login_required(login_url= 'index')
def advises(request):

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    return render(request, 'advises.html', {'teacher': teacher})


@login_required(login_url= 'index')
def associate_parcours(request,id):
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    group = Group.objects.get(pk = id)
    theme_theme_ids = request.POST.getlist("themes")
    for theme_id in theme_theme_ids :
        theme = Theme.objects.get(pk = int(theme_id))
        parcours, created = Parcours.objects.get_or_create(title=theme.name, color=group.color, author=teacher, teacher=teacher, level=group.level, subject = group.subject, is_favorite = 1,  is_share = 0, linked = 1)
        exercises = Exercise.objects.filter(level= group.level,theme = theme, theme__subject = group.subject , supportfile__is_title=0)
        parcours.students.set(group.students.all())
        parcours.groups.add(group)
        i  = 0
        for e in exercises:
            relationship, created = Relationship.objects.get_or_create(parcours = parcours, exercise=e, ranking = i)
            relationship.students.set(group.students.all())
            if created :
                relationship.skills.set(e.supportfile.skills.all()) 
            i+=1

    if len(parcours.students.all())>0 :
        return redirect("list_parcours_group" , group.id )
    else :
        return redirect("index") 

@csrf_exempt
def ajax_parcours_default(request):
    data = {}
    level_id =  request.POST.get("level_selected_id")    
    level =  Level.objects.get(pk = level_id)
    context = {  'level': level,   }
    data['html'] = render_to_string('qcm/parcours_default_popup.html', context)
 
    return JsonResponse(data)

@login_required(login_url= 'index')
def get_parcours_default(request):
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')
    level_id = request.POST.get("level_selected_id")
    theme_ids = request.POST.getlist("themes")
    n = 0
    for theme_id in theme_ids :
        theme = Theme.objects.get(pk = int(theme_id))
        parcours, created = Parcours.objects.get_or_create(title=theme.name, color="#5d4391", author=teacher, teacher=teacher, level_id=level_id,  is_favorite = 1,  is_share = 0, linked = 0)
        exercises = Exercise.objects.filter(level_id=level_id,theme = theme, supportfile__is_title=0)
        i  = 0
        for e in exercises:
            relationship, created = Relationship.objects.get_or_create(parcours = parcours, exercise=e, ranking = i)
            if created :
                relationship.skills.set(e.supportfile.skills.all()) 
            i+=1
        n +=1
    if n > 1 :
        messages.info(request, "Les parcours sont créés avec succès. Penser à leur attribuer des élèves et à les publier.")
    else :
        messages.info(request, "Le parcours est créé avec succès. Penser à lui attribuer des élèves et à le publier.")
    return redirect("index") 

#######################################################################################################################################################################
#######################################################################################################################################################################
#################   parcours
#######################################################################################################################################################################
#######################################################################################################################################################################

@csrf_exempt
def ajax_chargethemes(request):
    ids_level =  request.POST.get("id_level")
    id_subject =  request.POST.get("id_subject")
    
    data = {}
    level =  Level.objects.get(pk = ids_level)

    thms = level.themes.values_list('id', 'name').filter(subject_id=id_subject).order_by("name")
    data['themes'] = list(thms)

    # gère les propositions d'image d'accueil
    data['imagefiles'] = None
    imagefiles = level.level_parcours.values_list("vignette", flat = True).filter(subject_id=id_subject).exclude(vignette=" ").distinct()
    if imagefiles.count() > 0 :
        data['imagefiles'] = list(imagefiles)


    return JsonResponse(data)


@csrf_exempt  # PublieDépublie un exercice depuis organize_parcours
def ajax_populate(request):  

    exercise_id = int(request.POST.get("exercise_id"))
    parcours_id = int(request.POST.get("parcours_id"))
    parcours = Parcours.objects.get(pk = parcours_id)
    exercise = Exercise.objects.get(pk = exercise_id)
    statut = request.POST.get("statut") 
    data = {}    

    teacher = Teacher.objects.get(user= request.user)  

    if statut=="true" or statut == "True":

        r = Relationship.objects.get(parcours=parcours, exercise = exercise)  
        students = parcours.students.all()
        for student in students :
            r.students.remove(student)

        r.delete()         
        statut = 0
        data["statut"] = "False"
        data["class"] = "btn btn-danger"
        data["noclass"] = "btn btn-success"
        data["html"] = "<i class='fa fa-times'></i>"
        data["no_store"] = False

    else:
        statut = 1
        if Relationship.objects.filter(parcours_id=parcours_id , exercise__supportfile = exercise.supportfile ).count() == 0 :
            try :
                relation = Relationship.objects.create(parcours_id=parcours_id, exercise_id = exercise_id, ranking = 100, maxexo = parcours.maxexo, is_calculator = exercise.supportfile.calculator ,
                                                                                situation = exercise.supportfile.situation , duration = exercise.supportfile.duration) 
                relation.skills.set(exercise.supportfile.skills.all())
                students = parcours.students.all()
                relation.students.set(students)
            except :
                pass
            data["statut"] = "True"
            data["class"] = "btn btn-success"
            data["noclass"] = "btn btn-danger"
            data["html"] = "<i class='fa fa-check-circle fa-2x'></i>"
            data["no_store"] = False
        else :
            data["statut"] = "False"
            data["class"] = "btn btn-danger"
            data["noclass"] = "btn btn-success"
            data["html"] = "<i class='fa fa-times'></i>"
            data["no_store"] = True

    #Relationship.objects.filter(parcours_id=parcours_id , exercise__supportfile = exercise.supportfile ).count() == 0            
    data["nb"] = parcours.exercises.count()

    return JsonResponse(data) 




def peuplate_parcours(request,id):
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')
    levels =  teacher.levels.order_by("ranking")
    parcours = Parcours.objects.get(id=id)

    role, group , group_id , access = get_complement(request, teacher, parcours)


    if not authorizing_access(teacher,parcours, access ):
        messages.error(request, "  !!!  Redirection automatique  !!! Violation d'accès. Contacter SACADO...")
        return redirect('index')

    form = ParcoursForm(request.POST or None , instance=parcours, teacher = parcours.teacher , folder = None ,   group = group)
    relationships = Relationship.objects.filter(parcours=parcours).prefetch_related('exercise__supportfile').order_by("ranking")
    """ affiche le parcours existant avant la modif en ajax""" 
    exercises = parcours.exercises.filter(supportfile__is_title=0).order_by("theme","knowledge__waiting","knowledge","ranking")
    """ fin """
    themes_tab = []
    for level in levels :
        for theme in level.themes.all():
            if not theme in themes_tab:
                themes_tab.append(theme)
    
    if request.method == 'POST' :
        level = request.POST.get("level") 
        # modifie les exercices sélectionnés
        exercises_all = parcours.exercises.filter(supportfile__is_title=0,level=level).order_by("theme","knowledge__waiting","knowledge","ranking")
        exercises_posted_ids = request.POST.getlist('exercises')

        new_list = []
        for e_id in exercises_posted_ids :
            try : 
                exercise  = Exercise.objects.get(id=e_id)
                new_list.append(exercise)
            except :
                pass


        intersection_list = [value for value in exercises_all if value not in new_list]

        for exercise in intersection_list :
            try :
                rel = Relationship.objects.get(parcours = parcours , exercise = exercise).delete() # efface les existants sur le niveau sélectionné
            except :
                pass
        i = 0 # réattribue les exercices choisis

        for exercise in exercises_posted_ids :
            try :
                if Relationship.objects.filter(parcours = nf , exercise__supportfile = exercise.supportfile ).count() == 0 :
                    r = Relationship.objects.create(parcours = nf , exercise = exercise , ranking =  i, is_calculator = exercise.supportfile.calculator, situation = exercise.supportfile.situation , duration = exercise.supportfile.duration )  
                    r.skills.set(exercise.supportfile.skills.all()) 
                    i+=1
                else :
                    pass
            except :
                pass


        # fin ---- modifie les exercices sélectionnés
    context = {'form': form, 'parcours': parcours, 'communications':[], 'group' : group , 'role' : role , 'teacher': teacher, 'exercises': exercises , 'levels': levels , 'themes' : themes_tab , 'user': request.user , 'group_id' : group_id , 'relationships' :relationships  }

    return render(request, 'qcm/form_peuplate_parcours.html', context)


@login_required(login_url= 'index')
def peuplate_parcours_evaluation(request,id):
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')
    levels =  teacher.levels.order_by("ranking")
 
    parcours = Parcours.objects.get(id=id)

    role, group , group_id , access = get_complement(request, teacher, parcours)

    if not authorizing_access(teacher,parcours, access ):
        messages.error(request, "  !!!  Redirection automatique  !!! Violation d'accès. Contacter SACADO...")
        return redirect('index')



    form = ParcoursForm(request.POST or None , instance=parcours, teacher = teacher , folder = None,   group = None )
    relationships = Relationship.objects.filter(parcours=parcours).prefetch_related('exercise__supportfile').order_by("ranking")
    """ affiche le parcours existant avant la modif en ajax""" 
    exercises = parcours.exercises.filter(supportfile__is_title=0).order_by("theme","knowledge__waiting","knowledge","ranking")
    """ fin """
    themes_tab = []
    for level in levels :
        for theme in level.themes.all():
            if not theme in themes_tab:
                themes_tab.append(theme)
    
    if request.method == 'POST' :
        level = request.POST.get("level") 
        # modifie les exercices sélectionnés
        exercises_all = parcours.exercises.filter(supportfile__is_title=0,level=level)
        exercises_posted_ids = request.POST.getlist('exercises')

        new_list = []
        for e_id in exercises_posted_ids :
            try : 
                exercise  = Exercise.objects.get(id=e_id)
                new_list.append(exercise)
            except :
                pass


        intersection_list = [value for value in exercises_all if value not in new_list]

        for exercise in intersection_list :
            try :
                rel = Relationship.objects.get(parcours = parcours , exercise = exercise).delete() # efface les existants sur le niveau sélectionné
            except :
                pass
        i = 0 # réattribue les exercices choisis

        for exercise in exercises_posted_ids :
            try :
                if Relationship.objects.filter(parcours = nf , exercise__supportfile = exercise.supportfile ).count() == 0 :
                    r = Relationship.objects.create(parcours = nf , exercise = exercise , ranking =  i, is_calculator = exercise.supportfile.calculator, situation = exercise.supportfile.situation , duration = exercise.supportfile.duration )  
                    r.skills.set(exercise.supportfile.skills.all()) 
                    i+=1
                else :
                    pass
            except :
                pass
 
        # fin ---- modifie les exercices sélectionnés
    context = {'form': form, 'parcours': parcours, 'communications':[], 'group' : group , 'role' : role , 'teacher': teacher, 'exercises': exercises , 'levels': levels , 'themes' : themes_tab , 'user': request.user , 'group_id' : group_id , 'relationships' :relationships  }

    return render(request, 'qcm/form_peuplate_parcours.html', context)


@login_required(login_url= 'index')
def individualise_parcours(request,id):

    folder_id = request.session.get("folder_id",None)
    folder = None
    if folder_id :
        folder = Folder.objects.get(pk = folder_id)

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')
    parcours = Parcours.objects.get(pk = id)
    relationships = parcours.parcours_relationship.order_by("ranking")
    customexercises = Customexercise.objects.filter(parcourses = parcours).order_by("ranking") 

    nb_rc = relationships.count() + customexercises.count()

    role, group , group_id , access = get_complement(request, teacher, parcours)

    if not authorizing_access(teacher,parcours, access ):
        messages.error(request, "  !!!  Redirection automatique  !!! Violation d'accès. Contacter SACADO...")
        return redirect('index')
 
    relationships_customexercises , nb_exo_only, nb_exo_visible  = ordering_number(parcours) 

    context = {'relationships': relationships, 'parcours': parcours,     'communications':[],  'form': None,  
                'teacher': teacher, 'customexercises' : customexercises , 'nb_rc' : nb_rc ,
                'exercises': None , 'folder' : folder , 'relationships_customexercises' : relationships_customexercises , 
                 'levels': None , 
                'themes' : None ,
                'user': request.user , 
                'group_id' : group_id , 'group' : group , 'role' : role }

    return render(request, 'qcm/form_individualise_parcours.html', context )




def update_parcourscreator_ia(knowledge , parcours, student, exercise_id , action):

    eid = str(exercise_id)
    ex = Exercise.objects.get(pk=exercise_id)  
    if action == 1 :
        pcrses = Parcourscreator.objects.filter(knowledge_id = knowledge.id ,  parcours_id = parcours.id )

        for p in pcrses :
            if eid in p.exercises :
                idx = p.index( eid)
                if idx > len(parcours):
                    p = p[:idx]+"##"+eid
                else :  
                    p = p[:idx]+eid+"##"+p[idx:]
                p.save()
                print(p.id)
                break
    else :
        if Parcourscreator.objects.filter(knowledge_id = knowledge.id ,  student_id = student.user.id ,  parcours_id = parcours.id ).count() == 1 :
            pcrs = Parcourscreator.objects.get(knowledge_id = knowledge.id ,  student_id = student.user.id ,  parcours_id = parcours.id )
        else :
            pcrs = Parcourscreator.objects.filter(knowledge_id = knowledge.id ,  student_id = student.user.id ,  parcours_id = parcours.id ).first()
        if pcrs and eid in pcrs.exercises :
            pcrs.exercises.replace("#"+eid+"#","")
            pcrs.save()
        elif pcrs :
            print(pcrs.id)
        else :
            print("pcrs.exercises")



@csrf_exempt # PublieDépublie un exercice depuis organize_parcours
def ajax_individualise(request):  

    exercise_id = int(request.POST.get("exercise_id"))
    parcours_id = int(request.POST.get("parcours_id"))
    student_id = int(request.POST.get("student_id"))
    data = {}
    teacher = Teacher.objects.get(user= request.user)
    parcours = Parcours.objects.get(pk = parcours_id)
    statut = request.POST.get("statut")

    is_checked = request.POST.get("is_checked")


    if not authorizing_access(teacher,parcours , True ):
        messages.error(request, "  !!!  Redirection automatique  !!! Violation d'accès. Contacter SACADO...")
        return redirect('index')

    custom = int(request.POST.get("custom") )

    if is_checked == "true" :

        if custom :

            for customexercise in parcours.parcours_customexercises.filter(is_publish=1 ):
                if student_id == 0 : # affecte à tous les élèves 

                    if statut=="true" or statut == "True" :
                        try :
                            som = 0
                            for s in parcours.students.all() :
                                if Customanswerbystudent.objects.filter(student = s , customexercise = customexercise).count() == 0 :
                                    customexercise.students.remove(s)
                                    som +=1
                                Blacklist.objects.get_or_create(customexercise=customexercise, student = s ,relationship = None   )
                        except :
                            pass

          
                        data["statut"] = "False"
                        data["class"] = "btn btn-default"
                        data["noclass"] = "btn btn-success"
                        if som == 0 :
                            data["alert"] = True
                        else :
                            data["alert"] = False 
                    else : 
                        try :
                            customexercise.students.set(parcours.students.all())
                            for s in parcours.students.all():
                                if Blacklist.objects.filter(customexercise=customexercise, student = s ).count()  > 0:
                                    Blacklist.objects.get(customexercise=customexercise, student = s ).delete()
                        except :
                            pass
          
                        data["statut"] = "True"
                        data["class"] = "btn btn-success"
                        data["noclass"] = "btn btn-default"
                        data["alert"] = False  
                else :
                    student = Student.objects.get(pk = student_id) 
                    if statut=="true" or statut == "True":
                        try :
                            if Customanswerbystudent.objects.filter(student = student , customexercise = customexercise).count() == 0 :
                                customexercise.students.remove(student)
                                Blacklist.objects.get_or_create(customexercise=customexercise, student = student , relationship = None   )
                                data["alert"] = False
                            else :
                                data["alert"] = True                        
                        except :
                            pass
 
                        data["statut"] = "False"
                        data["class"] = "btn btn-default"
                        data["noclass"] = "btn btn-success" 
                    else:
 
                        try :
                            customexercise.students.add(student)
                            if Blacklist.objects.filter(customexercise=customexercise, student = student , relationship = None   ).count()  > 0 :
                                Blacklist.objects.get(customexercise=customexercise, student = student , relationship = None   ).delete() 
                        except :
                            pass
                        data["statut"] = "True"
                        data["class"] = "btn btn-success"
                        data["noclass"] = "btn btn-default"
                        data["alert"] = False
                            
        else :

            for relationship in parcours.parcours_relationship.filter(is_publish=1 ) : 
                if student_id ==  0  :
                    if statut=="true" or statut == "True" :
                        somme = 0
                        try :
                            for s in parcours.students.all() :
                                exercise = Exercise.objects.get(pk = exercise_id )
                                if Studentanswer.objects.filter(student = s , exercise = exercise, parcours = relationship.parcours).count() == 0 :
                                    relationship.students.remove(s)
                                    somme +=1
                                Blacklist.objects.get_or_create(customexercise=None, student = s ,relationship = relationship   )
                        except :
                            pass
       
                        data["statut"] = "False"
                        data["class"] = "btn btn-default"
                        data["noclass"] = "btn btn-success"
                        if somme == 0 :
                            data["alert"] = True
                        else :
                            data["alert"] = False

                    else : 
                        relationship.students.set(parcours.students.all())
                        for s in parcours.students.all():
                            if Blacklist.objects.filter(relationship=relationship, student = s ).count() > 0 :
                                Blacklist.objects.get(relationship=relationship, student = s ).delete()   
                        data["statut"] = "True"
                        data["class"] = "btn btn-success"
                        data["noclass"] = "btn btn-default"
                        data["alert"] = False

                else :
                    student = Student.objects.get(pk = student_id)  
  
                    if statut=="true" or statut == "True":

                        if Studentanswer.objects.filter(student = student , parcours = relationship.parcours).count() == 0 :
                            relationship.students.remove(student)
                            Blacklist.objects.get_or_create(relationship=relationship, student = student , customexercise = None   )
                            data["statut"] = "False"
                            data["class"] = "btn btn-default"
                            data["noclass"] = "btn btn-success"
                            data["alert"] = False

                        else :
                            data["statut"] = "True"
                            data["class"] = "btn btn-success"
                            data["noclass"] = "btn btn-default"
                            data["alert"] = True

                        update_parcourscreator_ia(relationship.exercise.knowledge , parcours, student, relationship.exercise.id , 0)

                    else:
                        relationship.students.add(student)
                        if Blacklist.objects.filter(relationship=relationship, student = student , customexercise = None   ).count()  > 0 :
                            Blacklist.objects.get(relationship=relationship, student = student , customexercise = None   ).delete()
                        data["statut"] = "True"
                        data["class"] = "btn btn-success"
                        data["noclass"] = "btn btn-default"
                        data["alert"] = False

                        update_parcourscreator_ia(relationship.exercise.knowledge , parcours, relationship.exercise.id , student, 1)

            if relationship.students.count() != relationship.parcours.students.count() :
                data["indiv_nb"]   = relationship.students.count()
                data["indiv_hide"] = True
            else :
                data["indiv_hide"] = False
                data["indiv_nb"]   = relationship.students.count()
    else :
        if custom :
            customexercise = Customexercise.objects.get(pk = exercise_id )
            if student_id == 0 : # affecte à tous les élèves 
                if statut=="true" or statut == "True" :
                    try :
                        som = 0
                        for s in parcours.students.all() :
                            if Customanswerbystudent.objects.filter(student = s , customexercise = customexercise).count() == 0 :
                                customexercise.students.remove(s)
                                som +=1
                            Blacklist.objects.get_or_create(customexercise=customexercise, student = s ,relationship = None   )    
                    except :
                        pass

                    statut = 0
                    data["statut"] = "False"
                    data["class"] = "btn btn-default"
                    data["noclass"] = "btn btn-success"
                    if som == 0 :
                        data["alert"] = True
                    else :
                        data["alert"] = False 
                else : 
                    try :
                        customexercise.students.set(parcours.students.all())
                        for s in parcours.students.all() :
                            if Blacklist.objects.filter(customexercise=customexercise, student = s ,relationship = None   ).count() > 0 :
                                Blacklist.objects.get(customexercise=customexercise, student = s ,relationship = None   ).delete()
                    except :
                        pass
                    statut = 1    
                    data["statut"] = "True"
                    data["class"] = "btn btn-success"
                    data["noclass"] = "btn btn-default"
                    data["alert"] = False   
            else :
                student = Student.objects.get(pk = student_id)
                if statut=="true" or statut == "True":
                    if Customanswerbystudent.objects.filter(student = student , customexercise = customexercise).count() == 0 :
                        customexercise.students.remove(student)
                        Blacklist.objects.get_or_create(customexercise=customexercise, student = student ,relationship = None   )
                        data["alert"] = False
                    else :
                        data["alert"] = True                        

                    data["statut"] = "False"
                    data["class"] = "btn btn-default"
                    data["noclass"] = "btn btn-success" 
                else:
                    try :
                        customexercise.students.add(student)
                        if Blacklist.objects.filter(customexercise=customexercise, student = student ,relationship = None   ).count()  > 0 :
                            Blacklist.objects.get(customexercise=customexercise, student = student ,relationship = None   ).delete()
                    except :
                        pass
                    data["statut"] = "True"
                    data["class"] = "btn btn-success"
                    data["noclass"] = "btn btn-default"
                    data["alert"] = False   
        
        else :

            exercise = Exercise.objects.get(pk = exercise_id)
            relationship = Relationship.objects.get(parcours=parcours,exercise=exercise) 
            if student_id == 0 :  

                if statut=="true" or statut == "True" :
                    somme = 0
                    for s in parcours.students.all() :
                        if Studentanswer.objects.filter(student = s , exercise = exercise, parcours = relationship.parcours).count() == 0 :
                            relationship.students.remove(s)
                            somme +=1
                        Blacklist.objects.get_or_create(relationship=relationship, student = s ,customexercise = None   )

                    data["statut"] = "False"
                    data["class"] = "btn btn-default"
                    data["noclass"] = "btn btn-success"
                    if somme == 0 :
                        data["alert"] = True
                    else :
                        data["alert"] = False

                else : 
                    relationship.students.set(parcours.students.all())
                    for s in parcours.students.all() :
                        Blacklist.objects.get_or_create(relationship=relationship, student = s ,customexercise = None   )
                    data["statut"] = "True"
                    data["class"] = "btn btn-success"
                    data["noclass"] = "btn btn-default"
                    data["alert"] = False
            else :
                student = Student.objects.get(pk = student_id)  

                if statut=="true" or statut == "True":

                    if Studentanswer.objects.filter(student = student , exercise = exercise, parcours = relationship.parcours).count() == 0 :
                        relationship.students.remove(student)
                        Blacklist.objects.get_or_create(relationship=relationship, student = student ,customexercise = None   )
                        data["statut"] = "False"
                        data["class"] = "btn btn-default"
                        data["noclass"] = "btn btn-success"
                        data["alert"] = False

                    else :
                        data["statut"] = "True"
                        data["class"] = "btn btn-success"
                        data["noclass"] = "btn btn-default"
                        data["alert"] = True


                    update_parcourscreator_ia(relationship.exercise.knowledge , parcours, student, relationship.exercise.id , 0)

                else:
                    relationship.students.add(student) 
                    if Blacklist.objects.filter(relationship=relationship, student = student ,customexercise = None ).count() > 0 :
                        Blacklist.objects.get(relationship=relationship, student = student ,customexercise = None ).delete()
                    
                    data["statut"] = "True"
                    data["class"] = "btn btn-success"
                    data["noclass"] = "btn btn-default"
                    data["alert"] = False
                    update_parcourscreator_ia(relationship.exercise.knowledge , parcours, student, relationship.exercise.id , 1)


            if relationship.students.count() != relationship.parcours.students.count() :
                data["indiv_nb"]   = relationship.students.count()
                data["indiv_hide"] = True
            else :
                data["indiv_hide"] = False
                data["indiv_nb"]   = relationship.students.count()

    return JsonResponse(data) 




def ajax_individualise_this_exercise(request):

    relationship_id = int(request.POST.get("relationship_id"))
    custom          = int(request.POST.get("custom"))
    group_id        = request.POST.get("group_id",None) 

    if custom :
        rc = Customexercise.objects.get(pk=relationship_id)
        try :
            parcours = rc.parcourses.first()
        except :
            parcours = None
    else :
        rc = Relationship.objects.get(pk=relationship_id)
        parcours = rc.parcours 

    if group_id :
        group    = Group.objects.get(pk=group_id)
        students = group.students.exclude(user__username__contains="_e-test").order_by("user__last_name")
    else :
        students = rc.students.exclude(user__username__contains="_e-test").order_by("user__last_name") 


    data = {}
    data['html'] = render_to_string('qcm/ajax_individualise_this_exercise.html', {'rc' : rc, 'parcours' : parcours, 'students' : students, })

    return JsonResponse(data)




def ajax_individualise_this_document(request):

    relationship_id = int(request.POST.get("relationship_id"))
    group_id        = request.POST.get("group_id",None) 

    rc = Relationship.objects.get(pk=relationship_id)
    parcours = rc.parcours 

    if group_id :
        group    = Group.objects.get(pk=group_id)
        students = group.students.exclude(user__username__contains="_e-test").order_by("user__last_name")
    else :
        students = rc.students.exclude(user__username__contains="_e-test").order_by("user__last_name") 


    data = {}
    data['html'] = render_to_string('qcm/ajax_individualise_this_document.html', {'rc' : rc, 'parcours' : parcours, 'students' : students, })

    return JsonResponse(data)



def ajax_reset_this_exercise(request):

    relationship_id = int(request.POST.get("relationship_id"))
    group_id        = request.POST.get("group_id",None) 

    rc = Relationship.objects.get(pk=relationship_id)
    parcours = rc.parcours 

    if group_id :
        group    = Group.objects.get(pk=group_id)
        students = group.students.exclude(user__username__contains="_e-test").order_by("user__last_name")
    else :
        students = rc.students.exclude(user__username__contains="_e-test").order_by("user__last_name") 

    data = {}
    data['html'] = render_to_string('qcm/ajax_reset_this_exercise.html', {'rc' : rc, 'parcours' : parcours, 'students' : students, })

    return JsonResponse(data)
 


@csrf_exempt   
def ajax_reset(request):  

    exercise_id = int(request.POST.get("exercise_id"))
    parcours_id = int(request.POST.get("parcours_id"))
    student_id  = int(request.POST.get("student_id"))
    teacher     = Teacher.objects.get(user= request.user)
    parcours    = Parcours.objects.get(pk = parcours_id)

    if not authorizing_access(teacher,parcours , True ):
        messages.error(request, "  !!!  Redirection automatique  !!! Violation d'accès. Contacter SACADO...")
        return redirect('index')

    data = {}
    if student_id != 0 :
        Studentanswer.objects.filter( parcours_id = parcours_id , exercise_id = exercise_id , student_id = student_id ).delete()
    else :
        Studentanswer.objects.filter( parcours_id = parcours_id , exercise_id = exercise_id ).delete()

    return JsonResponse(data) 




def ajax_affectation_to_group(request):
    group_id    = request.POST.get('group_id') 
    status      = request.POST.get('status')
    target_id   = request.POST.get('target_id')
    checked     = request.POST.get('checked')

    group       = Group.objects.get(pk=group_id)
    data        = {}
    html        = ""
    change_link = "no"


    if status == "parcours" :
        parcours = Parcours.objects.get(pk=target_id)        
        if checked == "false" :
            parcours.groups.remove(group)
        else :
            parcours.groups.add(group)
            groups = (group,)
            attribute_all_documents_of_groups_to_all_new_students(groups)
        for g in parcours.groups.all():
            html += "<small>"+g.name +" (<small>"+ str(g.just_students_count())+"</small>)</small> "

    else :
        folder   = Folder.objects.get(pk=target_id)
        if checked == "false" :
            folder.groups.remove(group)
        else :
            folder.groups.add(group)
            groups = (group,)
            attribute_all_documents_of_groups_to_all_new_students(groups)
        for g in folder.groups.all():
            html += "<small>"+g.name +" (<small>"+ str(g.just_students_count())+"</small>)</small> "
        change_link = "change"

    data['html']        = html
    data['change_link'] = change_link
    return JsonResponse(data)





def ajax_charge_group_from_target(request):
 
    status    = request.POST.get('status')
    target_id = request.POST.get('target_id')

    if status == "parcours" :
        parcours = Parcours.objects.get(pk=target_id)        
        groups   = parcours.groups.all()
        title    = parcours.title
    else :
        folder   = Folder.objects.get(pk=target_id)
        groups   = folder.groups.all()
        title    = folder.title 

    data = {}
    data['html_modal_group_name'] = title
    data['html_list_students'] = render_to_string('qcm/listingOfStudents.html', {  'groups':groups,    })
    return JsonResponse(data)
 

def ajax_built_diaporama(request):

    data = {}
    parcours_id = request.POST.get('parcours_id',None)
    if parcours_id :
        parcours = Parcours.objects.get(pk = parcours_id )
        courses = parcours.course.filter(is_publish=1)
        data['html'] = render_to_string('qcm/course/ajax_built_diaporama.html', {  'courses':courses,    })
        
    return JsonResponse(data)




############################################################################################################################################
############################################################################################################################################
##################     Listes dossiers parcours évaluation archives  #######################################################################
############################################################################################################################################
############################################################################################################################################



def delete_exo():
    Relationship.objects.filter(exercise__supportfile__code="f0600d3c").delete()



@login_required(login_url= 'index')
def list_folders(request):

    delete_exo()

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')
    today   = time_zone_user(teacher.user)

    folders   = teacher_has_folders(teacher, 0  ) #  is_archive
    nb_base =  len( folders  )   
    nb_archive =  len( teacher_has_folders(teacher, 1  )  ) 
 
    request.session["tdb"] = "Documents" # permet l'activation du surlignage de l'icone dans le menu gauche
    request.session["subtdb"] = "Folders"
 
    groups = teacher.has_groups()


    if request.session.has_key("group_id"):
        del request.session["group_id"]
    if request.session.has_key("folder_id"):
        del request.session["folder_id"]

    return render(request, 'qcm/list_folders.html', { 'folders' : folders ,    'groups' : groups , 'nb_base' : nb_base , 
                    'parcours' : None , 'group' : None , 'today' : today ,  'teacher' : teacher , 'nb_archive' : nb_archive })


@login_required(login_url= 'index')
def list_folders_archives(request):

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    today   = time_zone_user(teacher.user)

    folders   = teacher_has_folders(teacher, 1  ) #  is_archive
    nb_base =  len( folders  )   
 
 
    request.session["tdb"] = "Documents" # permet l'activation du surlignage de l'icone dans le menu gauche
    request.session["subtdb"] = "Folders"
 
    groups = teacher.has_groups()

    if request.session.has_key("group_id"):
        del request.session["group_id"]
    if request.session.has_key("folder_id"):
        del request.session["folder_id"]

    return render(request, 'qcm/list_folders_archives.html', { 'folders' : folders ,    'groups' : groups , 'nb_base' : nb_base , 
                    'parcours' : None , 'group' : None , 'today' : today ,  'teacher' : teacher ,  })



@login_required(login_url= 'index')
def list_parcours(request):

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')
    today   = time_zone_user(teacher.user)

    folds   = teacher_has_folders(teacher, 0  ) #  is_archive
    folders = folders_contains_evaluation(folds, False,0)

    parcourses = Parcours.objects.filter(Q(teacher=teacher)|Q(coteachers=teacher),folders=None,is_evaluation=0,is_sequence=0, is_archive=0,is_trash=0)

    nb_archive =  len(  teacher_has_own_parcourses_and_folder(teacher,0,1,0 )   )   
    nb_base = len( folders ) + parcourses.count()

    request.session["tdb"] = "Documents" # permet l'activation du surlignage de l'icone dans le menu gauche
    request.session["subtdb"] = "Parcours"

    groups = teacher.has_groups()

    if request.session.has_key("group_id"):
        del request.session["group_id"]
    if request.session.has_key("folder_id"):
        del request.session["folder_id"]

    return render(request, 'qcm/list_parcours.html', { 'folders' : folders , 'parcourses' : parcourses , 'nb_base' : nb_base ,  'groups' : groups ,
                    'parcours' : None , 'group' : None , 'today' : today ,  'teacher' : teacher , 'nb_archive' : nb_archive })



@login_required(login_url= 'index')
def list_archives(request):

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')
    today = time_zone_user(teacher.user)

    folders = teacher_has_folders(teacher, 1  ) #  is_archive
    parcourses = Parcours.objects.filter(Q(teacher=teacher)|Q(coteachers=teacher),folders=None,is_archive=1,is_sequence=0,is_trash=0)
    nb_archive =  len(  teacher_has_own_parcourses_and_folder(teacher,0,1,0 )   )   
 
 
    request.session["tdb"] = "Documents" # permet l'activation du surlignage de l'icone dans le menu gauche
    request.session["subtdb"] = "Parcours"

    return render(request, 'qcm/list_archives.html', { 'folders' : folders , 'parcourses' : parcourses ,  'is_sequence': False ,
                                                        'today' : today ,  'teacher' : teacher , 'nb_base' : nb_archive   })



@login_required(login_url= 'index')
def list_sequences(request):

    #duration_all_relationship()

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')
    today   = time_zone_user(teacher.user)

    folds   = teacher_has_folders(teacher, 0  ) #  is_archive
    folders = folders_contains_evaluation(folds, False,1)

    parcourses = Parcours.objects.filter(Q(teacher=teacher)|Q(coteachers=teacher),folders=None,is_evaluation=0, is_archive=0,is_sequence=1,is_trash=0)

    nb_archive =  len(  teacher_has_own_parcourses_and_folder(teacher,0,1,1)   )   
    nb_base = len( folders ) + parcourses.count()
    
    request.session["tdb"] = "Documents"  
    request.session["subtdb"] = "Sequences"

    groups = teacher.has_groups()

    if request.session.has_key("group_id"): del request.session["group_id"]
    if request.session.has_key("folder_id"): del request.session["folder_id"]

    return render(request, 'qcm/list_sequences.html', { 'folders' : folders , 'parcourses' : parcourses , 'nb_base' : nb_base ,  'groups' : groups ,
                    'parcours' : None , 'group' : None , 'today' : today ,  'teacher' : teacher , 'nb_archive' : nb_archive })



@login_required(login_url= 'index')
def list_sequences_archives(request):

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')
    today = time_zone_user(teacher.user)

    folders = teacher_has_folders(teacher, 1  ) #  is_archive
    parcourses = Parcours.objects.filter(Q(teacher=teacher)|Q(coteachers=teacher),folders=None,is_archive=1,is_sequence=1,is_trash=0)
    nb_archive =  len(  teacher_has_own_parcourses_and_folder(teacher,0,1,1 )   )   
 
 
    request.session["tdb"] = "Documents" # permet l'activation du surlignage de l'icone dans le menu gauche
    request.session["subtdb"] = "Sequences"

    return render(request, 'qcm/list_archives.html', { 'folders' : folders , 'parcourses' : parcourses ,  'is_sequence': True,
                                                        'today' : today ,  'teacher' : teacher , 'nb_base' : nb_archive   })




@login_required(login_url= 'index')
def list_evaluations(request):

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')
    today = time_zone_user(teacher.user)

    folds = teacher_has_folders(teacher, 0  ) #  is_archive
    folders = folders_contains_evaluation(folds, True,0)

    parcourses = Parcours.objects.filter(Q(teacher=teacher)|Q(coteachers=teacher),folders=None,is_evaluation=1,is_archive=0,is_trash=0,is_sequence=0)
    nb_archive =  len(  teacher_has_own_parcourses_and_folder(teacher,1,1,0 )   )   
    nb_base = len( folders ) + parcourses.count()
    
    request.session["tdb"] = "Documents" # permet l'activation du surlignage de l'icone dans le menu gauche
    request.session["subtdb"] = "Evaluations"

    groups = teacher.has_groups()

    delete_session_key(request, "group_id") 
    delete_session_key(request, "folder_id") 
 
    return render(request, 'qcm/list_evaluations.html', { 'folders' : folders , 'parcourses' : parcourses , 'nb_base' : nb_base ,  'groups' : groups ,
                    'parcours' : None , 'group' : None , 'today' : today ,  'teacher' : teacher , 'nb_archive' : nb_archive })


 

@login_required(login_url= 'index')
def list_evaluations_archives(request):
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    request.session["tdb"] = "Documents" # permet l'activation du surlignage de l'icone dans le menu gauche
    request.session["subtdb"] = "Evaluations"

    parcourses = teacher_has_parcourses(teacher,1 ,1 ) #  is_evaluation ,is_archive 
    nb_base = len( parcourses )  
    today = time_zone_user(teacher.user)
    delete_session_key(request, "group_id")

    return render(request, 'qcm/list_evaluations_archives.html', { 'parcourses' : parcourses, 'parcours' : None , 'teacher' : teacher , 'communications' : [] ,  'today' : today ,  'nb_base' : nb_base   })





@login_required(login_url= 'index')
def list_parcours_group(request,id):

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    today = time_zone_user(request.user)
    group = Group.objects.get(pk = id) 

    request.session["tdb"] = "Documents" # permet l'activation du surlignage de l'icone dans le menu gauche
    if request.session.has_key("subtdb"): del request.session["subtdb"]


    #On entre dans un groupe donc on garde sa clé dans la session
    request.session["group_id"] = id

    role, group , group_id , access = get_complement(request, teacher, group)

    group = Group.objects.get(pk = id) 

    if not authorizing_access(teacher,group, access ):
        messages.error(request, "  !!!  Redirection automatique  !!! Violation d'accès. Contacter SACADO...")
        return redirect('index')

    #On sort du dossier donc on enlève sa clé de la session
    request.session.pop('folder_id', None)

    folders     = group.group_folders.filter(Q(teacher=teacher)|Q(author=teacher)|Q(coteachers = teacher), subject = group.subject, level = group.level , is_favorite=1, is_archive=0, is_trash=0 ).distinct().order_by("ranking")

    bases       = group.group_parcours.filter(Q(teacher=teacher)|Q(author=teacher)|Q(coteachers = teacher), subject = group.subject, level = group.level , is_favorite=1, folders = None, is_trash=0).distinct()


    evaluations = bases.filter( is_evaluation=1, is_sequence=0).order_by("ranking")
    parcourses  = bases.filter( is_evaluation=0, is_sequence=0).order_by("ranking")
    sequences   = bases.filter( is_sequence=1).order_by("ranking")

    parcours_tab = evaluations | parcourses

    ###efface le realtime de plus de 30min
    clear_realtime(parcours_tab , today.now() ,  1800 )
    nb_bases = bases.count() + folders.count()

    bibliotexs = group.bibliotexs.filter(folders=None)
    quizzes    = group.quizz.filter(folders=None)
    flashpacks = group.flashpacks.filter(folders=None)




    context =  { 'folders': folders , 'teacher' : teacher , 'group': group,  'parcours' : None ,  'role' : role , 'today' : today , 'bibliotexs' : bibliotexs,  'quizzes' : quizzes,  'flashpacks' : flashpacks, 
                 'parcourses': parcourses , 'sequences' : sequences ,  'evaluations' : evaluations , 'nb_bases' : nb_bases }

    return render(request, 'qcm/list_parcours_group.html', context )


@login_required(login_url= 'index')
def list_sub_parcours_group(request,idg,idf):

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')
    today   = time_zone_user(teacher.user)
    folder  = Folder.objects.get(pk = idf)

    role, groupe , group_id , access = get_complement(request, teacher, folder )
    request.session["folder_id"] = folder.id
    request.session["group_id"] = group_id
    delete_session_key(request, "quizz_id")

    try :
        group   = Group.objects.get(pk = idg)
    except :
        group = groupe
 
    parcours_tab = folder.parcours.filter(is_archive=0 , is_sequence=0 , is_trash=0).order_by("is_evaluation", "ranking")
    sequences    = folder.parcours.filter(is_archive=0 , is_sequence=1 , is_trash=0).order_by("ranking")
    quizzes      = folder.quizz.filter(teacher=teacher,is_archive=0,parcours=None)
    bibliotexs   = folder.bibliotexs.filter(Q(teacher=teacher)|Q(author=teacher)|Q(coteachers = teacher),is_archive=0,parcours=None)
    flashpacks   = folder.flashpacks.filter(Q(teacher=teacher),is_archive=0,parcours=None)

    accordion    = get_accordion(None, quizzes, bibliotexs, flashpacks)

    ###efface le realtime de plus de 2 h
    clear_realtime(parcours_tab , today.now() ,  1800 )


    context = { 'parcours_tab': parcours_tab , 'teacher' : teacher , 'group' : group ,  'folder' : folder, 'sequences' : sequences ,  'quizzes' : quizzes ,  
                'bibliotexs' : bibliotexs,   'flashpacks' : flashpacks,    'role' : role , 'today' : today , 'accordion' : accordion  }

    return render(request, 'qcm/list_sub_parcours_group.html', context )



@login_required(login_url= 'index')
def list_sub_parcours_group_student(request,idg,idf):

    student = request.user.student
    today   = time_zone_user(request.user)
    folder  = Folder.objects.get(pk = idf) 
    group   = Group.objects.get(pk = idg)
    request.session["folder_id"] = folder.id 
    delete_session_key(request, "quizz_id")

    bases = folder.parcours.filter(Q(is_publish=1) | Q(start__lte=today, stop__gte=today), students = student , is_archive=0 , is_trash=0).order_by("is_evaluation", "ranking") 

    parcourses = bases.filter( is_evaluation=0).order_by("ranking")
    evaluations = bases.filter( is_evaluation=1).order_by("ranking")

    quizzes    = folder.quizz.filter(Q(is_publish=1) | Q(start__lte=today, stop__gte=today), students = student , is_archive=0  ) 
    flashpacks = folder.flashpacks.filter(Q(is_publish=1) | Q(start__lte=today, stop__gte=today), students = student , is_archive=0  )  
    bibliotexs = folder.bibliotexs.filter(Q(is_publish=1) | Q(start__lte=today, stop__gte=today), students = student , is_archive=0 ) 


    context = {'parcourses': parcourses , 'evaluations': evaluations , 'quizzes': quizzes , 'flashpacks': flashpacks , 'bibliotexs': bibliotexs , 'student' : student , 'group' : group ,  'folder' : folder,    'today' : today }

    return render(request, 'qcm/list_sub_parcours_group_student.html', context )
    



@login_required(login_url= 'index')
def change_situations_in_all_relationships(request,idf,idp):

    parcours      = Parcours.objects.get(id=idp)
    relationships = parcours.parcours_relationship.filter(exercise__supportfile__is_title=0)

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    role, group , group_id , access = get_complement(request, teacher, parcours)

    if request.method == "POST" :
        global_situation = request.POST.get('global', None)

        for r in relationships :
            Relationship.objects.filter(pk=r.id).update(situation = global_situation)

        return redirect('show_parcours' , idf , idp )



    context = { 'parcours': parcours, 'relationships': relationships , 'role' : role , 'teacher': teacher   }

    return render(request, 'qcm/change_situations.html', context)




@login_required(login_url= 'index')
def change_durations_in_all_relationships(request,idf,idp):

    parcours      = Parcours.objects.get(id=idp)
    relationships = parcours.parcours_relationship.filter(exercise__supportfile__is_title=0)
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')
    role, group , group_id , access = get_complement(request, teacher, parcours)

    if request.method == "POST" :
        global_duration = request.POST.get('global', None)

        for r in relationships :
            Relationship.objects.filter(pk=r.id).update(duration = global_duration)

        return redirect('show_parcours' , idf , idp )



    context = { 'parcours': parcours, 'relationships': relationships , 'role' : role , 'teacher': teacher   }

    return render(request, 'qcm/change_durations.html', context)



@login_required(login_url= 'index')
def change_publications_in_all_relationships(request,idf,idp):

    parcours      = Parcours.objects.get(id=idp)
    relationships = parcours.parcours_relationship.filter(exercise__supportfile__is_title=0)
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')
    role, group , group_id , access = get_complement(request, teacher, parcours)

    if request.method == "POST" :
        global_publication = request.POST.get('global', 0)

        for r in relationships :
            Relationship.objects.filter(pk=r.id).update(is_publish = global_publication)

        parcours_publication = request.POST.get('parcours', 0)
        # si tous les exercices sont dépubliés, on dépublie le parcours et si vous publiez tous 
        Parcours.objects.filter(pk=idp).update(is_publish = parcours_publication)



        return redirect('show_parcours' , idf , idp )



    context = { 'parcours': parcours, 'relationships': relationships , 'role' : role , 'teacher': teacher   }

    return render(request, 'qcm/change_publications.html', context)

############################################################################################################################################
############################################################################################################################################
##################   Fin des listes dossiers parcours évaluation archives  #################################################################
############################################################################################################################################
############################################################################################################################################

@login_required(login_url= 'index')
def parcours_progression(request,id,idg):

    parcours = Parcours.objects.get(id=id)
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')
    role, group , group_id , access = get_complement(request, teacher, parcours)
 

    if not authorizing_access(teacher,parcours, True ):
        messages.error(request, "  !!!  Redirection automatique  !!! Violation d'accès. Contacter SACADO...")
        return redirect('index')
    if idg :
        group = Group.objects.get(id = idg) 
        students_group = group.students.all()
        students_parcours = parcours.students.order_by("user__last_name")
        students = [student for student in students_parcours if student   in students_group] # Intersection des listes
        group_id = idg
    else :
        students = parcours.students.order_by("user__last_name")

    context = {'students': students, 'parcours': parcours, 'communications':[], 'group' : group , 'role' : role , 'teacher': teacher, 'group_id' : group_id   }

    return render(request, 'qcm/progression_group.html', context)



@login_required(login_url= 'index')
def parcours_progression_student(request,id):

    parcours = Parcours.objects.get(id=id)

    try :
        student = request.user.student
    except :
        messages.error(request,"Vous n'êtes pas élève ou pas connecté.")
        return redirect('index')

    if parcours.is_achievement : 
 
        students = parcours.students.order_by("user__last_name")
        context = {'students': students, 'parcours': parcours, 'student':student,  }
        return render(request, 'qcm/progression_group_student.html', context)
    else :
        messages.error(request,"accès interdit")
        return redirect('index')



@login_required(login_url= 'index')
def all_parcourses(request,is_eval):
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')
    #parcours_ids = Parcours.objects.values_list("id",flat=True).filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=2480),is_evaluation = is_eval, is_share = 1,level__in = teacher.levels.all()).exclude(teacher=teacher).order_by('level').distinct()
    parcours_ids = []  

    parcourses , tab_id = [] , [] 
    for p_id in parcours_ids :
        if not p_id in tab_id :
            p =  Parcours.objects.get(pk = p_id)
            if p.exercises.count() > 0 :
                parcourses.append(p)
                tab_id.append(p_id)
 
    try :
        group_id = request.session.get("group_id",None)
        if group_id :
            group = Group.objects.get(pk = group_id)
            same_level_groups = teacher.groups.filter(level=group.level,subject=group.subject)
        else :
            group = None
            same_level_groups = teacher.groups.all()   
    except :
        group = None
        same_level_groups = teacher.groups.all()

    try :
        parcours_id = request.session.get("parcours_id",None)
        if parcours_id :
            parcours = Parcours.objects.get(pk = parcours_id)
        else :
            parcours = None   
    except :
        parcours = None


    if request.user.school != None :
        inside = True
    else :
        inside = False

    levels = teacher.levels.order_by("ranking")

    return render(request, 'qcm/list_parcours_shared.html', { 'is_eval' : is_eval ,  'teacher' : teacher , "levels" : levels ,   'parcourses': parcourses , 'inside' : inside ,   'parcours' : parcours , 'group' : group , 'same_level_groups' : same_level_groups  })

 
def ajax_all_parcourses(request):

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')
    data = {}
    is_eval    = int(request.POST.get('is_eval',0))
    level_id   = request.POST.get('level_id',None)
    subject_id = request.POST.get('subject_id',None)
    keywords   = request.POST.get('keywords',None)
    theme_ids = request.POST.getlist('theme_id',[])
    teacher_id = get_teacher_id_by_subject_id(subject_id)

    if is_eval == 2 :
        base = Parcours.objects.filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id)| Q(teacher_id=teacher_id),  is_share = 1, is_sequence = 1 ).exclude( teacher=teacher).exclude(exercises = None) 
    else :   
        base = Parcours.objects.filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id)| Q(teacher_id=teacher_id),  is_share = 1, is_evaluation = is_eval).exclude(teacher=teacher).exclude(exercises = None) 

    if subject_id : 
        subject = Subject.objects.get(pk=subject_id)
        base = base.filter(subject = subject)

    if  keywords :
        base = base.filter(  Q(title__icontains = keywords) | Q(teacher__user__first_name__icontains = keywords) |Q(teacher__user__last_name__icontains = keywords))


    if level_id and int(level_id) > 0:
        base = base.filter( level_id = level_id )

    base = base.order_by('teacher').distinct() 

    if len(theme_ids) > 0 and theme_ids[0] != '' :
        nbase = set()
        for p in base :
            if str(p.get_theme().id) in theme_ids :
                nbase.add(p)
        base = nbase 

 

    data['html'] = render_to_string('qcm/ajax_list_parcours.html', {'parcourses' : base, 'teacher' : teacher ,  })
 


    return JsonResponse(data)


@login_required(login_url= 'index')
def all_folders(request):
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')
    #parcours_ids = Parcours.objects.values_list("id",flat=True).filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=2480),is_evaluation = is_eval, is_share = 1,level__in = teacher.levels.all()).exclude(teacher=teacher).order_by('level').distinct()
    parcours_ids = []  

    parcourses , tab_id = [] , [] 
    for p_id in parcours_ids :
        if not p_id in tab_id :
            p =  Parcours.objects.get(pk = p_id)
            if p.exercises.count() > 0 :
                parcourses.append(p)
                tab_id.append(p_id)
 
    try :
        group_id = request.session.get("group_id",None)
        if group_id :
            group = Group.objects.get(pk = group_id)
            same_level_groups = teacher.groups.filter(level=group.level,subject=group.subject)
        else :
            group = None
            same_level_groups = teacher.groups.all()  
    except :
        group = None
        same_level_groups = teacher.groups.all()


    if request.user.school != None :
        inside = True
    else :
        inside = False

    return render(request, 'qcm/list_folders_shared.html', {  'teacher' : teacher ,   'parcourses': parcourses , 'inside' : inside ,  'group' : group , 'same_level_groups' : same_level_groups  })



 
def ajax_all_folders(request):

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')
    data = {}
    level_id = request.POST.get('level_id',0)
    subject_id = request.POST.get('subject_id',None)
    listing = request.POST.get('listing',None)

    teacher_id = get_teacher_id_by_subject_id(subject_id)
    keywords = request.POST.get('keywords',None)

    base = Folder.objects.filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id), is_share = 1 , subject_id = subject_id ).exclude(teacher=teacher)

    if int(level_id) > 0 :
        base = base.filter( level_id = level_id )

    if keywords:
        parcours_key = Parcours.objects.filter(Q(exercises__supportfile__title__icontains = keywords)|Q(exercises__supportfile__annoncement__icontains = keywords)|Q(teacher__user__first_name__icontains = keywords) |Q(teacher__user__last_name__icontains = keywords)   )
        base = base.objects.filter( Q( title__icontains = keywords )|Q(parcours__in=parcours_key) )

    folders = base.order_by("author") 


    if listing == "yes" :
        data['html'] = render_to_string('qcm/ajax_list_folders_listing.html', {'folders' : folders, 'teacher' : teacher ,  }) 
    else :
        data['html'] = render_to_string('qcm/ajax_list_folders.html', {'folders' : folders, 'teacher' : teacher ,  })
 
    return JsonResponse(data)


@login_required(login_url= 'index')
def clone_folder(request, id ):
    """ cloner un dossier """

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    folder = Folder.objects.get(pk = id)
    prcs   = folder.parcours.all()
 
    #################################################
    # clone le dossier
    #################################################
    folder.pk = None
    folder.teacher = teacher
    folder.is_publish = 0
    folder.is_archive = 0
    folder.is_share = 0
    folder.is_favorite = 1
    folder.save()

    #################################################
    # clone les exercices attachés à un cours 
    #################################################
    former_relationship_ids = []
    new_folder_id_tab , folder_id_tab = [] , []
    # ajoute le group au parcours si group    

    group_id = request.session.get("group_id",None)
    if group_id :
        group = Group.objects.get(pk = group_id)
        folder.groups.add(group)
        students = group.students.all()
        folder.students.set(students)

    i = 0
    for p in prcs :
        courses = p.course.all()
        p.pk = None
        p.code = str(uuid.uuid4())[:8] 
        p.teacher = teacher
        if group_id :
            p.subject = group.subject
            p.level = group.level
        p.is_publish = 0
        p.is_archive = 0
        p.is_share = 0
        p.is_favorite = 1
        p.save()
        if group_id :
            p.students.set(students)
        new_folder_id_tab.append(p.id)
        folder.parcours.add(p)

        for course in courses :
            old_relationships = course.relationships.all()
            # clone le cours associé au parcours
            course.pk = None
            course.parcours_id = new_folder_id_tab[i]
            course.save()
            if group_id :
                course.students.set(students)
            # clone l'exercice rattaché au cours du parcours
            try :
                for relationship in old_relationships : 
                    if not relationship.id in former_relationship_ids :
                        relationship.pk = None
                        relationship.parcours_id = new_folder_id_tab[i]
                        relationship.save()
                    course.relationships.add(relationship)
                    former_relationship_ids.append(relationship.id)
            except :
                pass
        #################################################
        # clone tous les exercices rattachés au parcours 
        #################################################
        for relationship in p.parcours_relationship.all()  :
            skills = relationship.skills.all()
            try :
                relationship.pk = None
                relationship.parcours_id = new_folder_id_tab[i]
                relationship.save()
                relationship.skills.set(skills)    
                if group_id :
                    relationship.students.set(students)
            except :
                pass
        i += 1

    messages.success(request, "Duplication réalisée avec succès. Bonne utilisation.")
    if group_id :
        return redirect('list_parcours_group',  group_id)
    else :
        return redirect('all_folders')



@login_required(login_url= 'index')
def duplicate_folder(request):
    """ cloner un dossier """

    folder_id  = request.POST.get("this_document_id",None)
    groups       = request.POST.getlist("groups",[])
    teacher = request.user.teacher
    data = {}

    students = set()
    for grp_id in groups :
        group = Group.objects.get(pk=grp_id)
        students.update( group.students.all() )

    if folder_id :
        folder = Folder.objects.get(pk = folder_id)
        prcs   = folder.parcours.all()
        #################################################
        # clone le dossier
        #################################################
        folder.pk = None
        folder.teacher = teacher
        folder.is_publish = 0
        folder.is_archive = 0
        folder.is_share = 0
        folder.is_favorite = 1
        folder.save()
        folder.students.set(students)
        folder.groups.set(groups)
        folder.parcours.set(prcs)
        for g in groups :
            Folder.objects.filter(pk=folder.pk).update(level = group.level)
            Folder.objects.filter(pk=folder.pk).update(subject = group.subject)
        #################################################
        # clone les exercices attachés à un cours 
        #################################################
        former_relationship_ids = []
        new_folder_id_tab , folder_id_tab = [] , []
        # ajoute le group au parcours si group    
        i = 0
        for p in prcs :
            courses = p.course.all()
            p.pk = None
            p.code = str(uuid.uuid4())[:8] 
            p.teacher = teacher
            for g in groups :
                group     = Group.objects.get(pk=g)
                p.subject = group.subject
                p.level   = group.level
                Folder.objects.filter(pk=folder.pk).update(level = group.level)
                Folder.objects.filter(pk=folder.pk).update(subject = group.subject)
            p.is_publish = 0
            p.is_archive = 0
            p.is_share = 0
            p.is_favorite = 1
            p.save()
            p.students.set(students)
            new_folder_id_tab.append(p)
            for course in courses :
                old_relationships = course.relationships.all()
                # clone le cours associé au parcours
                course.pk = None
                course.parcours = new_folder_id_tab[i]
                course.save()
                course.students.set(students)
                # clone l'exercice rattaché au cours du parcours
                try :
                    for relationship in old_relationships : 
                        if not relationship.id in former_relationship_ids :
                            relationship.pk = None
                            relationship.parcours = new_folder_id_tab[i]
                            relationship.save()
                        course.relationships.add(relationship)
                        former_relationship_ids.append(relationship.id)
                except :
                    pass
            #################################################
            # clone tous les exercices rattachés au parcours 
            #################################################
            for relationship in p.parcours_relationship.all()  :
                skills = relationship.skills.all()
                try :
                    relationship.pk = None
                    relationship.parcours_id = new_folder_id_tab[i]
                    relationship.save()
                    relationship.skills.set(skills)    
                    relationship.students.set(students) 
                except :
                    pass
            i += 1

        data["validation"] = "Duplication réussie. Retrouvez-le depuis le menu Groupes."
    else :
        data["validation"] = "Duplication abandonnée." 

    return JsonResponse(data)









@csrf_exempt
def ajax_chargethemes_parcours(request):
    level_id =  request.POST.get("id_level")
    id_subject =  request.POST.get("id_subject")
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    teacher_id = get_teacher_id_by_subject_id(id_subject)

    data = {}
    level =  Level.objects.get(pk = level_id)

    thms = level.themes.values_list('id', 'name').filter(subject_id=id_subject).order_by("name")
    data['themes'] = list(thms)
    parcourses = Parcours.objects.filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id),is_share = 1, exercises__level_id = level_id ,is_trash=0).exclude(teacher=teacher).order_by('author').distinct()

    data['html'] = render_to_string('qcm/ajax_list_parcours.html', {'parcourses' : parcourses, })


    # gère les propositions d'image d'accueil
    data['imagefiles'] = None
    imagefiles = level.level_parcours.values_list("vignette", flat = True).filter(subject_id=id_subject).exclude(vignette=" ").distinct()
    if imagefiles.count() > 0 :
        data['imagefiles'] = list(imagefiles)

    return JsonResponse(data)


@csrf_exempt
def ajax_chargethemes_exercise(request):
    level_id =  request.POST.get("id_level")
    id_subject =  request.POST.get("id_subject")
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    data = {}
    level =  Level.objects.get(pk = level_id)

    thms = level.themes.values_list('id', 'name').filter(subject_id=id_subject).order_by("name")
    data['themes'] = list(thms)
    exercises = Exercise.objects.filter(level_id = level_id , theme__subject_id = id_subject ,  supportfile__is_title=0 ).order_by("theme","knowledge__waiting","knowledge","supportfile__ranking")

    #data['html'] = render_to_string('qcm/ajax_list_exercises_by_level.html', { 'exercises': exercises  , "teacher" : teacher , "level_id" : level_id })
    data['html'] = "<div class='alert alert-info'>Choisir un thème</div>"

    # gère les propositions d'image d'accueil
    data['imagefiles'] = None
    imagefiles = level.level_parcours.values_list("vignette", flat = True).filter(subject_id=id_subject).exclude(vignette=" ").distinct()
    if imagefiles.count() > 0 :
        data['imagefiles'] = list(imagefiles)


    return JsonResponse(data)
 
 

def lock_all_exercises_for_this_student(parcours,student):

    dateur = parcours.stop
    for exercise in  parcours.exercises.all() :
        relationship = Relationship.objects.get(parcours=parcours, exercise = exercise) 
        if dateur :
            if Exerciselocker.objects.filter(student = student , relationship = relationship, custom = 0 ) :
                Exerciselocker.objects.filter(student = student , relationship = relationship, custom = 0 ).delete()
            result, created = Exerciselocker.objects.get_or_create(student = student , relationship = relationship, custom = 0, defaults={"lock" : dateur})
            if not created :
                Exerciselocker.objects.filter(student = student , relationship = relationship, custom = 0).update(lock = dateur)
        else :
            for res in Exerciselocker.objects.filter (student = student , relationship = relationship, custom = 0) :
                res.delete() 

    for ce in Customexercise.objects.filter(parcourses = parcours) :
        if dateur :
            if Exerciselocker.objects.filter(student = student , customexercise = ce, custom = 1 ) :
                Exerciselocker.objects.filter(student = student , customexercise = ce, custom = 1 ).delete()
            result, created = Exerciselocker.objects.get_or_create(student = student , customexercise = ce, custom = 1, defaults={"lock" : dateur})
            if not created :
                Exerciselocker.objects.filter(student = student , customexercise = ce, custom = 1).update(lock = dateur)
        else :
            if Exerciselocker.objects.filter(student = student , customexercise = ce, custom = 1).exists():
                res = Exerciselocker.objects.get(student = student ,  customexercise = ce, custom = 1)
                res.delete() 




def lock_all_exercises_for_student(dateur,parcours):

    for student in parcours.students.all() :
        lock_all_exercises_for_this_student(parcours,student)



def set_coanimation_teachers(nf, group_ids,teacher):
    test = False
    try :
        historic_teachers = []
        if len(group_ids) > 0 : # récupération de la vignette précréée et insertion dans l'instance du parcours.
            for group_id in group_ids :
                g = Group.objects.get(pk=group_id)
                if teacher != g.teacher :
                    if not g.teacher in historic_teachers :
                        historic_teachers.append(g.teacher)
                        nf.coteachers.add(g.teacher)
                        test = True
    except :
        test = False
    return test



def change_coanimation_teachers(nf, target , group_ids , teacher): # target = parcours, eval , folder

    target.coteachers.clear()
    test = set_coanimation_teachers(nf, group_ids ,teacher)

    return test



def all_attributions_for_this_nf(group_ids,nf) :

    all_students = set()
    groups = list()
    for gid in group_ids :
        group = Group.objects.get(pk=gid)
        all_students.update(group.students.all())
        groups.append(group)
    attribute_all_documents_of_groups_to_all_new_students(groups)
    nf.students.set(all_students)
 

##########################################################################################################################
##########################################################################################################################
####################      CREATION des évaluations et des parcours     ###################################################
##########################################################################################################################
##########################################################################################################################
def get_form(request, parcours, teacher ,  group_id, folder_id):

    if parcours :
        if folder_id and group_id :
            folder = Folder.objects.get(pk=folder_id)
            group  = Group.objects.get(pk=group_id)
            form   = ParcoursForm(request.POST or None, request.FILES or None, instance=parcours, teacher=teacher , folder = folder,   group = group  , initial= {   'folders':  [folder],  'groups':  [group], 'subject': folder.subject , 'level': folder.level }  )
        elif group_id :
            group = Group.objects.get(pk=group_id)
            level = group.level.name
            form = ParcoursForm(request.POST or None, request.FILES or None, instance=parcours, teacher=teacher , folder = None,   group = group , initial= { 'groups': [group],  'subject': group.subject , 'level': group.level } )
        elif folder_id :
            folder = Folder.objects.get(pk=folder_id)
            form = ParcoursForm(request.POST or None, request.FILES or None, instance=parcours, teacher=teacher , folder = folder,   group = None  , initial= { 'folders':  [folder],  'subject': folder.subject , 'level': folder.level }  )
        else :
            form = ParcoursForm(request.POST or None, request.FILES or None, instance=parcours, teacher=teacher , folder = None,   group = None   )

    else :
        if folder_id and group_id :
            folder = Folder.objects.get(pk=folder_id)
            group  = Group.objects.get(pk=group_id)
            form   = ParcoursForm(request.POST or None, request.FILES or None,  teacher=teacher , folder = folder,   group = group , initial= {   'folders':  [folder],  'groups':  [group], 'subject': folder.subject , 'level': folder.level } )
        elif group_id :
            group = Group.objects.get(pk=group_id)
            level = group.level.name
            form = ParcoursForm(request.POST or None, request.FILES or None,  teacher=teacher , folder = None,   group = group , initial= { 'groups': [group],  'subject': group.subject , 'level': group.level } )
        elif folder_id :
            folder = Folder.objects.get(pk=folder_id)
            form = ParcoursForm(request.POST or None, request.FILES or None,  teacher=teacher , folder = folder,   group = None , initial= { 'folders':  [folder],  'subject': folder.subject , 'level': folder.level } )
        else :            
            form = ParcoursForm(request.POST or None, request.FILES or None,  teacher=teacher , folder = None,   group = None  )

    return form



def affectation_students_to_contents_parcours_or_evaluation(parcours_ids,all_students ):
   
    for parcours_id in parcours_ids :

        parcours = Parcours.objects.get(pk=parcours_id)
        parcours.students.set(all_students) 

        for r in parcours.parcours_relationship.all():
            blacklisted_student_ids = Blacklist.objects.values_list("student").filter(relationship=r).exclude(student__user__username__contains="_e-test")
            students_no_blacklisted = all_students.difference(blacklisted_student_ids)
            r.students.set(students_no_blacklisted)

        for c in  parcours.parcours_customexercises.all() :
            blacklisted_student_customexercises_ids = Blacklist.objects.values_list("student").filter(customexercise=c).exclude(student__user__username__contains="_e-test")
            students_customexercises_no_blacklisted = all_students.difference(blacklisted_student_customexercises_ids)
            c.students.set(students_customexercises_no_blacklisted)

        courses = parcours.course.all()
        for course in courses:
            course.students.set(all_students)

        flashpacks = parcours.flashpacks.all()
        for flashpack in flashpacks:
            flashpack.students.set(all_students)

        bibliotexs = parcours.bibliotexs.all()
        for bibliotex in bibliotexs:
            bibliotex.students.set(all_students)

        quizz = parcours.quizz.all()
        for quiz in quizz:
            quiz.students.set(all_students)



def create_parcours_or_evaluation(request,create_or_update,is_eval, idf,is_sequence):
    """ 'parcours_is_folder' : False pour les vignettes et différencier si folder ou pas """
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    levels          = teacher.levels.order_by("ranking")
    ############################################################################################## 
    ################# ############## On regarde s'il existe un groupe  ###########################
    images = [] 
    group_id = request.session.get("group_id", None)
    if group_id :
        group  = Group.objects.get(pk=group_id)
        images = get_images_for_parcours_or_folder(group)
    else :
        group    = None
        group_id = None

    request.session["group_id"]  = group_id
    ############################################################################################## 
    ######## On regarde s'il existe un dossier ou un groupe et on assigne le formulaire  #########
    folder_id = request.session.get("folder_id",idf)
    if folder_id :
        folder = Folder.objects.get(pk=folder_id)
    else :
        folder = None

    form = get_form(request, create_or_update , teacher, group_id, folder_id)
    ##############################################################################################
    ##############################################################################################
    if request.method == "POST" :
        if form.is_valid():
            nf = form.save(commit=False)
            nf.author = teacher
            nf.teacher = teacher
            nf.is_evaluation = is_eval
            nf.is_sequence   = is_sequence
            if nf.is_share :
                if is_eval :
                    texte = "Une nouvelle évaluation"
                else :
                    texte = "Un nouveau parcours"
                sending_to_teachers(teacher , nf.level , nf.subject,texte)

            if nf.is_ia :
                nf.is_publish=0

            if request.POST.get("this_image_selected",None) : # récupération de la vignette précréée et insertion dans l'instance du parcours.
                nf.vignette = request.POST.get("this_image_selected",None)

            nf.save()
            form.save_m2m()

            if folder_id :
                folder.parcours.add(nf) 
     
            parcours_ids = request.POST.getlist("parcours",[])
            group_ids = request.POST.getlist("groups",[])

            groups_students = set()
            for gid in group_ids :
                group = Group.objects.get(pk = gid)
                groups_students.update( group.students.all() )

     
            nf.students.set(groups_students)
            attribute_all_documents_to_students([nf],groups_students)
            ################################################            
            #Gestion de la coanimation
            coanim = set_coanimation_teachers(nf,  group_ids,teacher) 
            ################################################
            lock_all_exercises_for_student(nf.stop,nf)


            if nf.is_ia :
                return redirect('get_target_ia', nf.id)
            elif is_sequence :
                return redirect('show_parcours', 0 , nf.id)
            elif request.POST.get("save_and_choose") :
                return redirect('peuplate_parcours', nf.id)
            elif group_id and idf == 0 :
                return redirect('list_parcours_group' , group_id)                
            elif group_id and idf > 0 :
                    return redirect('list_sub_parcours_group' , group_id, idf ) 
            else:
                return redirect('parcours')
        else:
            messages.error(request,str(form.errors)+". Si le niveau est absent, renseigner le niveau du groupe.")
 
    context = {'form': form,  'folder' : False,   'teacher': teacher, 'idg': 0,  'folder':  folder ,  'group_id': group_id , 'parcours': None, 
               'exercises': [], 'levels': levels, 'communications' : [],  'group': group , 'role' : True ,  'images' : images }

    if is_eval :
        return render(request, 'qcm/form_evaluation.html', context)
    elif is_sequence :
        return render(request, 'qcm/form_sequence.html', context) 
    else :
        return render(request, 'qcm/form_parcours.html', context) 


@login_required(login_url= 'index')
def create_parcours(request,idf=0):
    """ 'parcours_is_folder' : False pour les vignettes et différencier si folder ou pas """
    return create_parcours_or_evaluation(request, False , False,idf , 0 )

    
@login_required(login_url= 'index')
def create_evaluation(request,idf=0):
    """ 'parcours_is_folder' : False pour les vignettes et différencier si folder ou pas """
    return create_parcours_or_evaluation(request, False , True, idf , 0 )


@login_required(login_url= 'index')
def create_sequence(request,idf=0):
    """ 'parcours_is_folder' : False pour les vignettes et différencier si folder ou pas """
    return create_parcours_or_evaluation(request, False , False, idf , 1 )




def convert_into_str(knowledge_ids):
    knowledges_str = ""
    i=1 
    for knowledge_id in knowledge_ids :
        if i == len(knowledge_ids) : sep = ""
        else : sep = "##"
        knowledges_str += str(knowledge_id) + sep
        i+=1
    return knowledges_str
 


def create_parcours_after_results(request,idq,idp):

    quizz    = Quizz.objects.get(id=idq)
    students = quizz.students.all()
    parcours = Parcours.objects.get(id=idp)

    knowledge_ids = quizz.questions.values_list("knowledge_id",flat=True).distinct()
    dataset = list()

    exercises = Exercise.objects.filter(knowledge__in= knowledge_ids)

    for knowledge_id in knowledge_ids :
        knowledge = Knowledge.objects.get(pk=knowledge_id)
        data = {}
        datas_list = list()
        data['knowledge'] = knowledge
        datas_list = list()
        for student in students :
            datas = {}
            datas['student'] =  student.user.first_name.lower().capitalize()+" "+student.user.last_name.lower().capitalize()
            datar_list = list()
            for answerplayer in quizz.answerplayer.filter(student=student, question__knowledge = knowledge) :
                adatas = dict()      
                adatas['timer']        = answerplayer.timer
                adatas['is_correct']   = answerplayer.is_correct
                datar_list.append(adatas)     
            datas['results']   = datar_list
            datas['exercises'] = exercises


            datas_list.append(datas)
        data['features'] = datas_list   
        dataset.append(data)
 
    context = {'dataset': dataset,   'quizz': quizz, 'parcours': parcours, 'exercises' : exercises  }
 
    return render(request, 'qcm/previsual_parcours.html', context) 



def practice_group(request,idf,idp): 
    '''Créer les groupes de besoins'''
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    stage = get_stage(request.user)
    is_heterogene = None
    parcours = Parcours.objects.get(pk=idp)
    if idf > 0 :
        folder = Folder.objects.get(id=idf)
    else :
        folder = None

    role, group , group_id , access = get_complement(request, teacher, parcours)

    sfs = list()
    for sf in parcours.exercises.values_list("knowledge_id",flat=True).distinct() :
        sfs.append(Knowledge.objects.get(pk=sf))

    groups, printable_groups = list() , ""
    number , print_knowledges , nature = None , "" , ""
    post_knowledges = list()
    if request.method =="POST" :
        students   = parcours.students.all()
        nature     = request.POST.get('nature',None)
        number     = request.POST.get('number',None)
        if number : number = int(number)
        knowledges = request.POST.getlist('knowledges')

        print_knowledges = ""
        for k in knowledges:
            post_knowledges.append(int(k))
            print_knowledges += k+ "##"
        
        all_students, printable_all_students = list() , list()
        for student in students :
            student_avg = dict()
            stu_ans = Studentanswer.objects.filter(exercise__knowledge_id__in = knowledges, student = student).aggregate(average_score=Avg('point'))  
            student_avg['student'] = student
            if stu_ans['average_score'] : student_avg['avg'] = int(stu_ans['average_score'])
            else : student_avg['avg'] = 0 
            style = 'color:white;border-radius:2px;font-size:12px;padding:3px;'
            if student_avg['avg'] < stage['low'] : student_avg['style'] = style + 'background-color: #b5322b'
            elif student_avg['avg'] < stage['medium'] : student_avg['style'] = style + 'background-color: #b5a32b'
            elif student_avg['avg'] < stage['up'] : student_avg['style'] = style + 'background-color: #62d85a'
            else : student_avg['style'] = style +'background-color: #1d6718'

            all_students.append(student_avg)
            printable_all_students.append(student.user.id) 

        if not number : number = len(all_students)
        
        all_students = sorted(all_students, key=lambda k: k["avg"])
        

        i = 0
        while i < len(all_students):
            if i%int(number)==0 : group, group_printable = list() , ""
            if nature == "hetero" :
                is_heterogene = 1
                if i%2==0:k=i
                else :k=len(all_students)-1-i
            else :
                is_heterogene = 0
                k=i
            group.append(all_students[k])
            group_printable += str(printable_all_students[k]) + "##"
            if len(group) == number or i+1 == len(all_students): 
                gr_dict = dict()
                gr_dict['students'] = group
                groups.append(gr_dict)
                printable_groups+= group_printable +"##"
            i +=1

    stamps = Knowledgegroup.objects.filter(parcours=parcours).values_list('stamp', flat=True).distinct()

    kgroups_stamp = list()
    for stamp in stamps :
        stamp_dict = dict()
        kgroups = Knowledgegroup.objects.filter(stamp=stamp)
        stamp_dict['nb']            = kgroups.count()
        stamp_dict['id']            = stamp
        stamp_dict['is_heterogene'] = kgroups.first().is_heterogene
        stamp_dict['date']          = kgroups.first().datetime
        stamp_dict['stamp']         = stamp
        try : 
            knowledges_tab = kgroups.first().knowledges.split("##")
            stamp_dict['nb_knowledges'] = len( knowledges_tab )
            k_list = list()
            for kid in knowledges_tab :
                k_dict = dict()
                knowledge = Knowledge.objects.get(pk=kid)
                k_dict['name'] = knowledge.name
                k_list.append(k_dict)
            stamp_dict['k_list'] = k_list

            k_group_list = list()
            for kgroup in kgroups :
                k_group = dict()
                k_group['name'] = kgroup.title
                students_tab = kgroup.students.split("##")
                student_list = list()
                for student in students_tab :
                    student_dict = dict()
                    student_dict['name'] = student
                    if student != "" :
                        student_list.append(student_dict)
                k_group['students'] = student_list
                k_group_list.append(k_group)
            stamp_dict['k_group_list'] = k_group_list

        except : stamp_dict['nb_knowledges'] = 0

        kgroups_stamp.append(stamp_dict)

    relationships_customexercises , nb_exo_only, nb_exo_visible  = ordering_number(parcours)

    context = { 'parcours': parcours,  'sfs' : sfs , 'groups' : groups , 'post' : request.POST , 'post_knowledges' : post_knowledges , 'number' : number , 'role' : role ,  'relationships_customexercises' : relationships_customexercises,
                'printable_groups' : printable_groups, 'print_knowledges' : print_knowledges, 'is_heterogene' : is_heterogene , 'kgroups_stamp' : kgroups_stamp }
 
    return render(request, 'qcm/practice_group.html', context) 





def print_practice_group(request): 

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=groupes_de_besoins.pdf'

    doc = SimpleDocTemplate(response,   pagesize=A4, 
                                        topMargin=0.3*inch,
                                        leftMargin=0.3*inch,
                                        rightMargin=0.3*inch,
                                        bottomMargin=0.3*inch     )

    groupe = ParagraphStyle('groupe',  fontSize=13, textColor=colors.HexColor("#000000"),) 
    title = ParagraphStyle('title',  fontSize=11, textColor=colors.HexColor("#000000"),)                   
    today = datetime.now().strftime("%d-%m-%Y")


    is_heterogene    = request.POST.get('is_heterogene',None)
    parcours_id      = request.POST.get('parcours_id',None)
    these_knowledges = request.POST.get('these_knowledges',None)
    printable        = request.POST.get('printable',None)
    printable_tab    = printable.split("####")

    parcours = Parcours.objects.get(pk=parcours_id)


    #logo = Image('D:/uwamp/www/sacado/static/img/sacadoA1.png')
    logo = Image('https://sacado.xyz/static/img/sacadoA1.png')
    logo_tab = [[logo, parcours.title+"\nGroupes créés le "+str(today)+"\nDocument généré par SACADO"  ]]
    logo_tab_tab = Table(logo_tab, hAlign='LEFT', colWidths=[0.7*inch,5*inch])
    logo_tab_tab.setStyle(TableStyle([ ('TEXTCOLOR', (0,0), (-1,0), colors.Color(0,0.5,0.62))]))
    
    elements = list()
    elements.append(logo_tab_tab)
    elements.append(Spacer(0, 0.2*inch))

    #title page frames
    framesFirstPage = []
    titleFrame = Frame(doc.leftMargin, doc.height-2*inch, doc.width , 2*inch  )
    framesFirstPage.append(titleFrame)



    elements.append(Paragraph( "Savoir faire" , groupe ))
    elements.append(Spacer(0, 0.1*inch))
    for knowledge_id in these_knowledges.split("##") :
        if knowledge_id !="" : 
            kname = Knowledge.objects.get(pk=knowledge_id).name
            elements.append(Paragraph( "- " + kname , title ))
    elements.append(Spacer(0, 0.1*inch))



    elements.append(FrameBreak())
    frame1 = Frame(doc.leftMargin, doc.bottomMargin, doc.width/2-6, doc.height-2.5*inch)
    frame2 = Frame(doc.leftMargin+doc.width/2+6, doc.bottomMargin, doc.width/2-6, doc.height-2.5*inch)    

    doc.addPageTemplates([PageTemplate(frames=[titleFrame, frame1,frame2]), ])

    i = 1
    stamp =  str(uuid.uuid4())[:8]
    for i in range(len(printable_tab))  :
        ##########################################################################
        #### Parcours
        ##########################################################################
        if i==6: elements.append(FrameBreak())
        titlegroup = 'Groupe '+str(i+1)
        paragraph = Paragraph( titlegroup , groupe )
        elements.append(paragraph)
        elements.append(Spacer(0, 0.1*inch))
        if printable_tab[i] != "" :
            sid_tab = printable_tab[i].split("##")
            stu_str , stu_str_p = "" , ""
            j = 1
            for sid in sid_tab :

                student = Student.objects.get(user_id=sid)
                stu_str += student.user.first_name.capitalize().strip()+ " "+student.user.last_name.capitalize().strip()+"<br/>"
                stu_str_p += student.user.first_name.capitalize().strip()+ " "+student.user.last_name.capitalize().strip()+"##"
                if j == len(sid_tab) : stu_str +="<br/>"
                j +=1

            if printable and these_knowledges and parcours_id :
                kgroup , create = Knowledgegroup.objects.update_or_create(title = titlegroup , parcours_id = parcours_id, is_heterogene = is_heterogene , stamp = stamp,
                                                                          knowledges=these_knowledges[:-2] , defaults = { 'students' : stu_str_p })
            elements.append(  Paragraph( stu_str , title )  )
        i+=1
    doc.build(elements)
    return response


def print_kgroups(request,idf,idp,slug):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=groupes_de_besoins.pdf'

    doc = SimpleDocTemplate(response,   pagesize=A4, 
                                        topMargin=0.3*inch,
                                        leftMargin=0.3*inch,
                                        rightMargin=0.3*inch,
                                        bottomMargin=0.3*inch     )

    groupe = ParagraphStyle('groupe',  fontSize=13, textColor=colors.HexColor("#000000"),) 
    title = ParagraphStyle('title',  fontSize=11, textColor=colors.HexColor("#000000"),)                   

    #logo = Image('D:/uwamp/www/sacado/static/img/sacadoA1.png')
    logo = Image('https://sacado.xyz/static/img/sacadoA1.png')
    logo_tab = [[logo, "SACADO \nSuivi des acquisitions de savoir faire" ]]
    logo_tab_tab = Table(logo_tab, hAlign='LEFT', colWidths=[0.7*inch,5*inch])
    logo_tab_tab.setStyle(TableStyle([ ('TEXTCOLOR', (0,0), (-1,0), colors.Color(0,0.5,0.62))]))
    
    elements = list()
    elements.append(logo_tab_tab)
    elements.append(Spacer(0, 0.1*inch))

    kgroups = Knowledgegroup.objects.filter(stamp = slug, parcours_id=idp)

    frame1 = Frame(doc.leftMargin, doc.bottomMargin, doc.width/2-6, doc.height, id='col1')
    frame2 = Frame(doc.leftMargin+doc.width/2+6, doc.bottomMargin, doc.width/2-6, doc.height, id='col2')    

    doc.addPageTemplates([PageTemplate(id='TwoCol',frames=[frame1,frame2]), ])

    for kgroup in kgroups  :
        ##########################################################################
        #### Parcours
        ##########################################################################
        paragraph = Paragraph( kgroup.title , groupe )
        elements.append(paragraph)
        elements.append(Spacer(0, 0.1*inch))
        stu_str = ""
        j=1
        sid_tab = kgroup.students.split('##')
        for student in sid_tab :
            stu_str += student.strip()+"<br/>"
            if j == len(sid_tab) : stu_str +="<br/>"
            j +=1

        elements.append(  Paragraph( stu_str , title )  )

    doc.build(elements)
    return response

 



def delete_kgroups(request,idf,idp,slug):
    Knowledgegroup.objects.filter(stamp = slug, parcours_id=idp).delete()
    return redirect('practice_group', idf,idp)




def recap_parcours(request,idf,idp):

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    parcours      = Parcours.objects.get(pk=idp)
    if idf > 0 :
        folder = Folder.objects.get(id=idf)
    else :
        folder = None

    role, group , group_id , access = get_complement(request, teacher, parcours)
    relationships_customexercises , nb_exo_only, nb_exo_visible  = ordering_number(parcours)

    students = parcours.students.order_by("user__last_name")
    dataset = list()
    for student in students :
        stu = dict()
        stu['student'] = student
        relations = Relationship.objects.filter(parcours=parcours, students=student)
        stu['relationships'] = relations.order_by("ranking")
        stu['length'] = relations.count()
        dataset.append(stu)

    context = {'dataset': dataset,  'parcours': parcours, 'role' : role , 'relationships_customexercises' : relationships_customexercises }
 
    return render(request, 'qcm/list_recap_parcours.html', context) 


########################################################################################################################################################################
########################################################################################################################################################################
##          IA
########################################################################################################################################################################
########################################################################################################################################################################


@login_required(login_url= 'index')
def get_target_ia(request,idp):
    """ Envoie la liste des exercice pour un seul niveau """
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')
    
    parcours  = Parcours.objects.get(pk=idp)   
    level     = parcours.level
    subject   = parcours.subject
    exercises = Exercise.objects.filter(level  = level  , theme__subject = subject , supportfile__is_title=0).order_by("theme","knowledge__waiting","knowledge")

    group_id = request.session.get("group_id", None)
    if group_id :
        group  = Group.objects.get(pk=group_id)
    else :
        group    = None

    if request.method == "POST":
        knowledge_ids = request.POST.getlist('knowledge_id')
        knowledges_str = convert_into_str(knowledge_ids)

        Testtraining.objects.update_or_create(parcours = parcours , defaults = {'requires': "", 'targets' :  knowledges_str,   'questions_proposed' : "", 'questions_effective' : "" } )

        return redirect('create_test_ia', idp )


    context =  { 'exercises': exercises  , "teacher" : teacher , "level" : level , "group" : group  , "parcours" : parcours ,'get_target' : True  }
 
    return render(request, 'qcm/list_knowledges_by_level.html', context) 




# @login_required(login_url= 'index')
# def create_test_ia(request,idp):
#     """ Envoie la liste des exercice pour un seul niveau """
#     try :
#         teacher = request.user.teacher
#     except :
#         messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
#         return redirect('index')

#     parcours = Parcours.objects.get(pk=idp)
#     if parcours.level.id < 13 : level_id = parcours.level.id - 1
#     elif parcours.level.id == 17 : level_id = 12
#     elif parcours.level.id == 14 : level_id = 14
#     level = Level.objects.get(pk=level_id)

#     subject  = parcours.subject
#     exercises = Exercise.objects.filter(level  = level  , theme__subject = subject , supportfile__is_title=0).order_by("theme","knowledge__waiting","knowledge")
    
#     group_id = request.session.get("group_id", None)
#     if group_id :
#         group  = Group.objects.get(pk=group_id)
#     else :
#         group    = None

#     if request.method == "POST":
#         knowledge_ids = request.POST.getlist('knowledge_id')
#         # knowledges_str = convert_into_str(knowledge_ids)

#         # questions , titles = set() , list()
#         # for knowledge_id in knowledge_ids :
#         #     knowledge = Knowledge.objects.get(pk=knowledge_id)
#         #     for q in knowledge.question.all():
#         #         if q.title not in titles :
#         #             questions.add(q)
#         #             titles.append( q.title )

#         # nbq = len(questions)

#         # if nbq > 40:
#         #     ratio =  40/nbq 
#         #     questions , titles = set() , list()
#         #     for knowledge_id in knowledge_ids :
#         #         knowledge = Knowledge.objects.get(pk=knowledge_id)
#         #         nb_this_question = int( knowledge.question.count()*ratio )
#         #         ks = knowledge.question.all()[:nb_this_question]
#         #         for q in ks :
#         #             if q.title not in titles :
#         #                 questions.add(q)
#         #                 titles.append( q.title )

#         # if Quizz.objects.filter(title = "Test Positionnement IA", parcours=parcours) :
#         #     created = False
#         # else :
#         #     quizz = Quizz.objects.create(title = "Test Positionnement IA", teacher=teacher, color= parcours.color , subject =subject, is_numeric = 1, is_mark=1,is_ranking= 1 , is_shuffle= 1,is_publish=0 )
#         #     created = True

#         # if created :
#         #     quizz.parcours.add( parcours ) 
#         #     quizz.levels.add( level )

#         #     if len( parcours.get_themes() ):
#         #         quizz.themes.set( parcours.get_themes() )
        
#         # if len( parcours.groups.all() ):
#         #     quizz.groups.set( parcours.groups.all() ) 

#         # if parcours.folders.count() :  
#         #     quizz.folders.set( parcours.folders.all() )

#         # quizz.students.set( parcours.students.all() ) 
#         # quizz.questions.set( questions ) 


#         questions_str  = ""
#         i=1 
#         for question in questions :
#             if i == len(questions) : sep = ""
#             else : sep = "##"
#             questions_str += str(question.id) + sep
#             i+=1

#         testtraining                = Testtraining.objects.get(parcours = parcours)
#         testtraining.requires       = knowledges_str
#         testtraining.quizz_proposed = questions_str
#         testtraining.save()

#         return redirect('show_quizz_numeric',quizz.id , idp )

#     context =  { 'exercises': exercises  , "teacher" : teacher , "level" : level , "group" : group  , "parcours" : parcours ,'get_target' : False  }
 
#     return render(request, 'qcm/list_knowledges_by_level.html', context) 


def max_number_exercises(n, init_exercises , knowledge_ids):  
    """ Nombre maximal d'exercices pour le test ,  n est le nombre maximal """
    nbq = len(init_exercises)
    if nbq > n :
        ratio =  n/nbq 
        eid_for_rs = set()
        for knowledge_id in knowledge_ids :
            knowledge = Knowledge.objects.get(pk=knowledge_id)
            exo_k = knowledge.exercises.values_list("id",flat=True) 
            init , nb_exercises = 0, int( exo_k.count()*ratio )
            while init < nb_exercises :
                index = random.randint(0, len(exo_k)-1)
                eid_for_rs.add( exo_k[index] )  
                init += 1
    else :
        eid_for_rs = init_exercises
    return eid_for_rs



@login_required(login_url= 'index')
def create_test_ia(request,idp):
    """ Envoie la liste des exercice pour un seul niveau """
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    parcours = Parcours.objects.get(pk=idp)
    if parcours.level.id < 13 : level_id = parcours.level.id - 1
    elif parcours.level.id == 17 : level_id = 12
    elif parcours.level.id == 14 : level_id = 14
    level = Level.objects.get(pk=level_id)

    subject  = parcours.subject
    exercises = Exercise.objects.filter(level  = level  , theme__subject = subject , supportfile__is_title=0).order_by("theme","knowledge__waiting","knowledge")
    
    group_id = request.session.get("group_id", None)
    if group_id :
        group  = Group.objects.get(pk=group_id)
    else :
        group    = None


    sfs = list()
    for sf in Testtraining.objects.get(parcours_id = idp).targets.split('##') :
        sfs.append(Knowledge.objects.get(pk=sf))

    if request.method == "POST":

        ########### Parcours cible
        title    = parcours.title
        p_id     = parcours.id
        groups   = parcours.groups.all()
        students = parcours.students.all()
        ######################################################################################
        # Création du parcours Test de positionnement
        ######################################################################################
        parcours.pk     = None
        parcours.title = "TPo "+title
        parcours.is_publish = 0        
        parcours.code = str(uuid.uuid4())[:8] 
        parcours.maxexo = 1
        parcours.target_id = p_id
        if Parcours.objects.filter(target_id = p_id).count()==0 :
            parcours.save()
        else :
            messages.error(request,"Le test de positionnement ne peut pas être créé, il existe déjà un test de positionnement pour ce parcours.")
            return redirect('show_parcours', 0 , idp )

        parcours.groups.set(groups)
        parcours.students.set(students)
        knowledge_ids = request.POST.getlist('knowledge_id')
        init_exercises = Exercise.objects.values_list("id",flat=True).filter(knowledge_id__in=knowledge_ids)

        eid_for_rs = max_number_exercises(30, init_exercises , knowledge_ids) # on choisit délibérément 30 exercices pour le test.
  
        e_str  = ""
        i=1 
        for eid in eid_for_rs :
            ######## Mise en place des exercices (relationships) #################################           
            exercise = Exercise.objects.get(pk=eid)
            relationship = Relationship.objects.create(exercise = exercise, parcours=parcours, maxexo=1, situation=2, duration=2, is_calculator = exercise.supportfile.calculator )
            relationship.students.set(parcours.students.all())
            relationship.skills.set(exercise.supportfile.skills.all())

            if i == len(eid_for_rs) : sep = ""
            else : sep = "##"
            e_str += str(eid) + sep
            i+=1

        knowledges_str = convert_into_str(knowledge_ids)

        testtraining                    = Testtraining.objects.get(parcours_id = idp)
        testtraining.requires           = knowledges_str
        testtraining.questions_proposed = e_str
        testtraining.save()

        return redirect('show_parcours', 0 , parcours.id )

    context =  { 'exercises': exercises  , "teacher" : teacher , "level" : level , "group" : group  , "parcours" : parcours ,'get_target' : False , 'sfs' : sfs  }
 
    return render(request, 'qcm/list_knowledges_by_level.html', context) 

##############################################################################################################################################################################
# Lorsque le test de positionnement est dépublié avec le scrit 'ajax_publish_parcours', le modèle Testtraining récupère les questions du test que les enseignants ont choisi
##############################################################################################################################################################################
# Permet de peupler les studentanswer pour faire des tests
def peuplate_parcours_ia(idp) :

    parcours = Parcours.objects.get(pk=idp)
    students = parcours.students.all()
    relationships = Relationship.objects.filter(parcours=parcours)
    
    for relationship in relationships :
        point = 0 
        
        for student in students :        
            if point>100 : point = 100
            secondes = random.randint(45,180)
            point += 5            
            Studentanswer.objects.create(exercise = relationship.exercise, parcours=parcours, student=student, point=point, secondes = secondes )
            Resultexercise.objects.get_or_create(exercise = relationship.exercise,  student=student, defaults = { 'point' : point} )




def create_relationships(rt,parcours,exercises,student,label):  

    label_score_list = list()
    n=0
    for e in exercises :
        sc_label = dict()
        if rt =='r' :
            score_label = student.answers.filter(exercise = e ).aggregate(avg = Avg('point'))
        else :
            score_label = Studentanswer.objects.filter(exercise = e ).aggregate(avg = Avg('point'))
        if score_label['avg'] : #  Si des exercices ne sont jamais faits, ils ne sont pas pris.
            sc_label['e_id'] = e.id
            sc_label['avg']  = score_label['avg']
            label_score_list.append(sc_label)
    sorted_list = sorted(label_score_list, key=lambda k: k["avg"])

    if rt == 'r' :
        if  label == 0 : maxi = 90
        elif label == 1 :  maxi = 75
        elif label == 2 :  maxi = 60
        get_sorted_list = [ dico for dico in sorted_list if dico['avg'] < maxi ]
        ranking = 0 # Permet de classer les pré requis avant.
    else :
        ranking = 100 # Permet de classer les pré requis avant.
        l = len(sorted_list)
        if  label == 0 : # les meilleurs
            if l > 15:
                n = l  - 15
                get_sorted_list = sorted_list[n:]
            else :
                get_sorted_list = sorted_list

        elif label == 1 : # la majorité (espérons)
            if l > 15:            
                n = l - 15
                get_sorted_list = sorted_list[n//2:l-n//2] 
            else :
                get_sorted_list = sorted_list

        elif label == 2 : # les  + faibles
            if l > 15:            
                n = l - 15
                get_sorted_list = sorted_list[:l-n] 
            else :
                get_sorted_list = sorted_list


    exercises_str = ""
    j = 0
    for exercise_dict in get_sorted_list :
        exercise = Exercise.objects.get(pk=exercise_dict['e_id'])
        relationship,create = Relationship.objects.get_or_create(exercise  = exercise , parcours=parcours, defaults={ 'situation' : 5, 'ranking' : ranking , 'duration' : exercise.supportfile.duration, 'is_calculator' : exercise.supportfile.calculator} )
        ranking +=1
        if create :
            relationship.skills.set(exercise.supportfile.skills.all())
        relationship.students.add(student)

        if j == len(get_sorted_list)-1 : sep = ""
        else : sep = "##"
        exercises_str += str(exercise.id) + sep
        j+=1


    return exercises_str



def parcours_ia_creator(knowledge_id , student ,  parcours ,  exercises, requires, global_duration, duration, average_score, nb_k_required):

    if duration < global_duration and int(average_score) >= 90 :  # les meilleurs
        requires_str  =  create_relationships('r',parcours,requires,student,0)
        exercises_str = create_relationships('t',parcours,exercises,student,0)
    elif duration > global_duration and int(average_score) < 50 :    # les plus faibles
        requires_str  =  create_relationships('r',parcours,requires,student,2)
        exercises_str = create_relationships('t',parcours,exercises,student,2)
    else :  
        requires_str  =  create_relationships('r',parcours,requires,student,1)
        exercises_str = create_relationships('t',parcours,exercises,student,1)

    if nb_k_required : all_str = requires_str + '##' + exercises_str
    else : all_str = exercises_str  

    Parcourscreator.objects.create(knowledge_id = knowledge_id ,  student_id = student.user.id ,  parcours_id = parcours.id , duration = duration, score = average_score, exercises = all_str ) 


def create_parcours_ia_assisted(request,idf,idp):
    '''Choix des exercices en fonction des résultats des élèves et des target du Testtraining'''

    parcours      = Parcours.objects.get(pk=idp)
    parcours_test = Parcours.objects.get(target_id=idp)
    testtraining  = Testtraining.objects.get(parcours=parcours)
    tab_target    = testtraining.targets.split("##")# liste des knowledges ciblés
    tab_requires  = testtraining.requires.split("##")# liste des knowledges ciblés

    if len(tab_requires) == 1 : nb_k_required = 1
    else : nb_k_required = None

    timer = Relationship.objects.filter(parcours=parcours_test).aggregate(duration=Sum('duration'))
    global_duration = timer['duration']*60 # Conversion en secondes

    students = parcours.students.all()
    dataset = list()
    i = 1
    for knowledge_id in tab_target :
        for student in students :
            requires       = Exercise.objects.filter(knowledge_id__in = tab_requires)
            exercises      = Exercise.objects.filter(knowledge_id=knowledge_id)
            studentanswers = student.answers.filter(parcours=parcours_test, exercise__knowledge__id__in = tab_requires ).aggregate(duration=Sum('secondes'), average_score=Avg('point'))
            if  studentanswers['duration'] and studentanswers['average_score'] :
                parcours_ia_creator(knowledge_id ,student ,  parcours , exercises, requires , global_duration, studentanswers['duration'], studentanswers['average_score'] , nb_k_required )
            else :
                if i == 1 : # Pour n'afficher le message qu'une seule fois par élève
                    messages.error(request,"L'élève "+str(student)+" n'a pas fait le test de positionnement")
        i+=1 

    return redirect('show_parcours', idf , idp )


#######################################################################################################################
###################  Modification
#######################################################################################################################

def update_parcours_or_evaluation(request, is_eval, id, is_sequence, idg=0 ): 
    """ 'parcours_is_folder' : False pour les vignettes et différencier si folder ou pas """
    teacher  = Teacher.objects.get(user_id=request.user.id)
    levels   = teacher.levels.order_by("ranking")
    parcours = Parcours.objects.get(id=id)

    images = [] 
    group_id = request.session.get("group_id", idg)
    if group_id : 
        group    = Group.objects.get(pk=group_id)
        images   = get_images_for_parcours_or_folder(group)
        request.session["group_id"] = group_id
    else : 
        group = None
        request.session["group_id"] = None
        role = False

    try :
        if Sharing_group.objects.filter(group_id=group_id, teacher = teacher).exists() :
            sh_group = Sharing_group.objects.get(group_id=group_id, teacher = teacher)
            role = sh_group.role 
        elif group.teacher == teacher :
            role = True
        else :
            role = False
    except :
        role = False

    ############################################################################################## 
    ######## On regarde s'il existe un dossier ou un groupe et on assigne le formulaire  #########
    folder_id = request.session.get("folder_id",None)

    if folder_id :
        folder = Folder.objects.get(pk=folder_id)
    else :
        folder = None
 
    form = get_form(request, parcours, teacher, group_id, folder_id)
    ##############################################################################################
    ##############################################################################################
    share_groups = Sharing_group.objects.filter(teacher  = teacher, role=1).order_by("group__level")
    sharing = len(share_groups) > 0
 
    if not authorizing_access(teacher, parcours, sharing ):
        messages.error(request, "  !!!  Redirection automatique  !!! Violation d'accès. Contacter SACADO...")
        return redirect('index')

    if request.method == "POST":
        if form.is_valid():
            nf = form.save(commit=False)
            nf.is_evaluation = is_eval
            nf.is_sequence   = is_sequence
            if request.POST.get("this_image_selected",None) : # récupération de la vignette précréée et insertion dans l'instance du parcours.
                nf.vignette = request.POST.get("this_image_selected",None)
            nf.save()
            form.save_m2m()

            group_ids = request.POST.getlist("groups",[])
            group_students = set()
            for gid in group_ids :
                group = Group.objects.get(pk = gid)
                group_students.update( group.students.all() )

            affectation_students_to_contents_parcours_or_evaluation( [nf.id] , group_students )
            nf.students.set(group_students)
            try :
                folder_ids = request.POST.getlist("folders",[]) 
                nf.folders.set(folder_ids)
            except :
                pass

            #Gestion de la coanimation
            change_coanimation_teachers(nf, parcours , group_ids , teacher)


            if "stop" in form.changed_data :
                lock_all_exercises_for_student(nf.stop,parcours)

            if nf.is_ia :
                return redirect('get_target_ia', nf.id)
            elif request.POST.get("save_and_choose") :
                return redirect('peuplate_parcours', nf.id)
            elif request.POST.get("to_index"):
                return redirect('index') 
            elif idg == 99999999999:
                return redirect('index')
            elif request.session.get("folder_id",None) :
                return redirect('list_sub_parcours_group' , idg , folder_id )
            elif idg > 0:
                return redirect('list_parcours_group', idg)     
            else:
                return redirect('parcours')


        else :
            print(form.errors)


    if parcours.teacher == teacher :
        role = True
 

    context = {'form': form,   'idg': idg, 'teacher': teacher, 'group_id': idg ,  'group': group ,  'folder': folder ,  'is_folder' : False,   'role' : role , 'images' : images ,  'parcours': parcours }
 
    return render(request, 'qcm/form_parcours.html', context) 

@login_required(login_url= 'index')
@parcours_exists
def update_parcours(request, id, idg=0 ): 
    return  update_parcours_or_evaluation(request, False, id,0, idg)

@login_required(login_url= 'index')
@parcours_exists
def update_evaluation(request, id,idg=0): 
    return  update_parcours_or_evaluation(request, True, id,0, idg )

@login_required(login_url= 'index')
@parcours_exists
def update_sequence(request, id, idg=0 ): 
    return  update_parcours_or_evaluation(request, False, id,1, idg )

##########################################################################################################################
##########################################################################################################################
##########################################################################################################################
##########################################################################################################################
##########################################################################################################################


@login_required(login_url= 'index')
def archive_parcours(request, id, idg=0):

    parcours = Parcours.objects.filter(id=id).update(is_archive=1,is_favorite=0,is_publish=0)
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    if idg == 99999999999:
        return redirect('index')
    elif idg == 0 :
        return redirect('parcours')
    else :
        return redirect('list_parcours_group', idg)

@login_required(login_url= 'index')
@parcours_exists
def unarchive_parcours(request, id, idg=0):

    parcours = Parcours.objects.filter(id=id).update(is_archive=0,is_favorite=0,is_publish=0)
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    if idg == 99999999999:
        return redirect('index')
    elif idg == 0 :
        return redirect('parcours')
    else :
        return redirect('list_parcours_group', idg)


@login_required(login_url= 'index')
@parcours_exists
def delete_parcours(request, id, idg=0):

    parcours = Parcours.objects.get(id=id)
    parcours_is_evaluation = parcours.is_evaluation

    if parcours.teacher.user.id == 2480 :
        messages.error(request, "  !!!  Redirection automatique  !!! Suppression interdite.")
        return redirect('index')

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    if not authorizing_access(teacher, parcours, False ):
        messages.error(request, "  !!!  Redirection automatique  !!! Violation d'accès. Contacter SACADO...")
        return redirect('index')


    studentanswers = Studentanswer.objects.filter(parcours = parcours)
    for s in studentanswers :
        s.delete()
 
    parcours.is_trash=1
    parcours.save()

    if idg == 99999999999:
        return redirect('index')
    elif idg == 0 and parcours_is_evaluation :
        return redirect('evaluations')
    elif idg == 0 :
        return redirect('parcours')
    else :
        return redirect('list_parcours_group', idg)




@login_required(login_url= 'index')
@parcours_exists
def dissociate_parcours(request, id, idg=0):

    parcours = Parcours.objects.get(id=id)
    parcours_is_evaluation = parcours.is_evaluation
    parcours.folders.clear()



    if idg == 99999999999:
        return redirect('index')
    elif idg == 0 and parcours_is_evaluation :
        return redirect('evaluations')
    elif idg == 0 :
        return redirect('parcours')
    else :
        return redirect('list_parcours_group', idg)




def ordering_number(parcours):

    listing_ordered = set() 
    relationships = parcours.parcours_relationship.prefetch_related('exercise__supportfile').order_by("ranking")
    listing_ordered.update(relationships)


    if not parcours.is_sequence :
        customexercises = Customexercise.objects.filter(parcourses=parcours).order_by("ranking") 
        listing_ordered.update(customexercises)
    listing_order = sorted(listing_ordered, key=attrgetter('ranking')) #set trié par ranking

    ################################################################
    #IA
    ################################################################

    # if parcours.is_ia :       
    #     get_parcourses_to_parcours(parcours.id)

    nb_exo_only, nb_exo_visible  = [] , []   
    i , j = 0, 0

    for item in listing_order :

        try :
            if not item.exercise.supportfile.is_title and not item.exercise.supportfile.is_subtitle:
                i += 1
            nb_exo_only.append(i)
            if not item.exercise.supportfile.is_title and not item.exercise.supportfile.is_subtitle and item.is_publish != 0:
                j += 1
            nb_exo_visible.append(j)
        except :
            i += 1
            nb_exo_only.append(i)
            if item.is_publish :
                j += 1
            nb_exo_visible.append(j)

    return listing_order , nb_exo_only, nb_exo_visible  




def rcs_for_realtime(parcours):

    listing_ordered = set() 
    relationships = Relationship.objects.filter(is_publish=1,parcours=parcours,exercise__supportfile__is_title=0).prefetch_related('exercise__supportfile').order_by("ranking")
    customexercises = Customexercise.objects.filter(is_publish=1,parcourses=parcours).order_by("ranking") 
    listing_ordered.update(relationships)
    listing_ordered.update(customexercises)

    listing_order = sorted(listing_ordered, key=attrgetter('ranking')) #set trié par ranking

    return listing_order


@login_required(login_url= 'index')
def show_parcours(request, idf = 0, id=0):
    """ show parcours coté prof """
    #peuplate_parcours_ia(id)
    
    if idf > 0 :
        folder = Folder.objects.get(id=idf)
    else :
        folder = None

    parcours = Parcours.objects.get(id=id)
    rq_user = request.user

    try :
        teacher = rq_user.teacher
    except :
        return redirect ('index')

    today = time_zone_user(rq_user)
    delete_session_key(request, "quizz_id")

    role, group , group_id , access = get_complement(request, teacher, parcours)

    if not teacher_has_permisson_to_parcourses(request,teacher,parcours) :
        return redirect('index')
 
    relationships_customexercises , nb_exo_only, nb_exo_visible  = ordering_number(parcours)

    nb_point , nb_time = 0 , 0
    nb_point_display = False
    for rc in relationships_customexercises :
        try : 
            nb_point += rc.mark
        except : pass
        try : 
            nb_time += rc.duration
        except : pass

    if nb_point > 0 :
        nb_point = str(nb_point) + " points"
        nb_point_display = True

    accordion = get_accordion(parcours.course, parcours.quizz, parcours.bibliotexs, parcours.flashpacks)

    skills = Skill.objects.all()

    parcours_folder_id = request.session.get("folder_id",None)
    request.session["parcours_id"] = parcours.id
 
    form_reporting = DocumentReportForm(request.POST or None )

    form = QuizzForm(request.POST or None, request.FILES or None ,teacher = teacher, folder = folder , group = group ,  initial={'parcours': parcours ,   'subject': parcours.subject , 'levels': parcours.level , 'groups': group })
 
    context = { 'parcours': parcours, 'teacher': teacher,  'communications' : [] ,  'today' : today , 'skills': skills,  'form_reporting': form_reporting, 'user' : rq_user , 'form' : form , 
                  'nb_exo_visible': nb_exo_visible ,   'relationships_customexercises': relationships_customexercises,
               'nb_exo_only': nb_exo_only,'group_id': group_id, 'group': group, 'role' : role,  'folder' : folder,  'accordion' : accordion,  'nb_time' : nb_time,  'nb_point' : nb_point,  'nb_point_display' : nb_point_display      }

    return render(request, 'qcm/show_parcours.html', context) 




@login_required(login_url= 'index')
def result_parcours_exercises(request, idf = 0, id=0):

    parcours = Parcours.objects.get(id=id)
    try :
        teacher = request.user.teacher
    except :
        return redirect ('index')

    stage = get_stage(request.user)
    
    if idf > 0 :
        folder = Folder.objects.get(id=idf)
        role, group , group_id , access = get_complement(request, teacher, folder)
        students = folder.only_students_folder() # liste des élèves d'un parcours donné
    else :
        folder = None
        role, group , group_id , access = get_complement(request, teacher, parcours)
        students =  parcours.only_students(group)

    relationships = Relationship.objects.filter(parcours=parcours, exercise__supportfile__is_title=0).prefetch_related('exercise').order_by("ranking")
    customexercises = parcours.parcours_customexercises.all() 

    listing = []
    nb_time = 0
    global_time = 0
    for student in students :
        datastudent = {}
        datastudent["student"] = student
        listing_r = []
        nb_time = 0
        global_time = 0
        base_studentanswer = Studentanswer.objects.filter(parcours=parcours,student=student)
        for relationship in relationships :
            nb_time += relationship.duration
            data_r = dict()
            studentanswer = base_studentanswer.filter(exercise=relationship.exercise).last()
            if studentanswer :
                global_time += int(studentanswer.secondes)
                data_r["point"]    = studentanswer.point
                data_r["secondes"] = studentanswer.secondes
                if int(studentanswer.point) < stage['low'] :     css = 'red' 
                elif int(studentanswer.point) < stage['medium']  :css = 'orange' 
                elif int(studentanswer.point) < stage['up']  :    css = 'green'
                else :                                         css = 'darkgreen'
                data_r["css"] = css
            else :
                data_r["point"]    = "Non not."
                data_r["secondes"] = ""
                data_r["css"] = ""
            listing_r.append(data_r)
        datastudent["listing_r"] = listing_r
        datastudent["global_time"] = global_time
        listing.append(datastudent)


    context= { 'role' : role, 'listing' : listing , 'nb_time':nb_time, 'parcours' : parcours, 'folder' : folder,'relationships':relationships, 'customexercises' : customexercises }

    return render(request, 'qcm/result_parcours_exercises.html', context) 




def ordering_number_for_student(parcours,student):
    """ créer une seule liste des exercices personnalisés et des exercices sacado coté eleve """

    listing_ordered = set()

    if parcours.is_sequence : 
        listing_order = Relationship.objects.filter(parcours=parcours, students=student, is_publish=1).order_by("ranking")
    else :
        relationships = Relationship.objects.filter(parcours=parcours, students=student, is_publish=1).prefetch_related('exercise__supportfile').order_by("ranking")
        customexercises = Customexercise.objects.filter(parcourses=parcours, students=student, is_publish=1).order_by("ranking")
        listing_ordered.update(relationships)
        listing_ordered.update(customexercises)
        listing_order = sorted(listing_ordered, key=attrgetter('ranking')) #set trié par ranking



    nb_exo_only, nb_exo_visible  = [] , []   
    i , j = 0, 0

    for item in listing_order :
        try :
            if not item.exercise.supportfile.is_title and not item.exercise.supportfile.is_subtitle:
                i += 1
            nb_exo_only.append(i)
            if not item.exercise.supportfile.is_title and not item.exercise.supportfile.is_subtitle and item.is_publish != 0:
                j += 1
            nb_exo_visible.append(j)
        except :
            i += 1
            nb_exo_only.append(i)
            if item.is_publish :
                j += 1
            nb_exo_visible.append(j)

    return listing_order , nb_exo_only, nb_exo_visible

@login_required(login_url= 'index')
def show_parcours_student(request, id):

    folder = None
    try :
        folder_id = request.session.get('folder_id', None)
        if folder_id :
            folder = Folder.objects.get(id=folder_id)
    except :
        pass

    request.session["prepeval_id"] = None

    parcours = Parcours.objects.get(id=id)

    stage = get_stage(parcours.teacher.user)

    try :
        student = request.user.student
    except :
        messages.error(request,"Vous n'êtes pas élève ou pas connecté.")
        return redirect('index')


    if parcours.stop :
        lock_all_exercises_for_this_student(parcours,student)

    user = request.user
    today = time_zone_user(user)
 
    tracker_execute_exercise(True ,  user , id , None , 0)

    relationships_customexercises , nb_exo_only, nb_exo_visible  = ordering_number_for_student(parcours,student)
    nb_exercises = len(relationships_customexercises)

    nb_courses = parcours.course.filter(Q(is_publish=1)|Q(publish_start__lte=today,publish_end__gte=today)).count()
    nb_quizzes = parcours.quizz.filter(Q(is_publish=1)|Q(start__lte=today,stop__gte=today)).count()

    context = { 'stage' : stage , 'relationships_customexercises': relationships_customexercises, 'folder': folder, 'nb_courses' : nb_courses , 
                'parcours': parcours, 'student': student, 'nb_exercises': nb_exercises,'nb_exo_only': nb_exo_only,  'nb_quizzes' : nb_quizzes ,
                'today': today ,    }

    return render(request, 'qcm/show_parcours_student.html', context)
 



@login_required(login_url= 'index')
def show_folder_student(request, id):

    folder = Folder.objects.get(id=id)
 

    user = request.user
    student = user.student
    today = time_zone_user(user)
    stage = get_stage(user)

    parcourses = folder.parcours.filter(Q(is_publish=1)|Q(start__lte=today,stop__gte=today)).order_by("ranking")
    nb_parcourses = parcourses.count()
    context = {'parcourses': parcourses , 'nb_parcourses': nb_parcourses ,   'parcours': parcours ,   'stage' : stage , 'today' : today ,  }

    return render(request, 'qcm/show_parcours_folder_student.html', context)

 


@login_required(login_url= 'index')
def list_parcours_quizz_student(request, idp):

    parcours = Parcours.objects.get(id=idp)
    user = request.user
    today = time_zone_user(user)
    quizzes = parcours.quizz.filter(Q(is_publish=1)|Q(start__lte=today,stop__gte=today)).order_by("-date_modified")

    context = { 'quizzes': quizzes ,   'parcours': parcours , 'today' : today ,  }

    return render(request, 'qcm/list_parcours_quizz_student.html', context)




@login_required(login_url= 'index')
def list_parcours_bibliotex_student(request, idp):

    parcours = Parcours.objects.get(id=idp)
    user = request.user
    today = time_zone_user(user)
    bibliotexs = parcours.bibliotexs.filter(Q(is_publish=1)|Q(start__lte=today,stop__gte=today)).order_by("-date_modified")

    context = { 'bibliotexs': bibliotexs ,   'parcours': parcours , 'today' : today ,  }

    return render(request, 'qcm/list_parcours_bibliotex_student.html', context)


@login_required(login_url= 'index')
def parcours_show_bibliotex_student(request, idp,id):

    try :
        parcours = Parcours.objects.get(id=idp)
    except : 
        parcours = None

    bibliotex = Bibliotex.objects.get(id=id)
    relationtexs = bibliotex.relationtexs.order_by("ranking")

    context = { 'bibliotex': bibliotex, 'relationtexs': relationtexs, 'parcours': parcours, }

    return render(request, 'bibliotex/show_bibliotex.html', context )




@login_required(login_url= 'index')
def list_parcours_flashpack_student(request, idp):

    parcours = Parcours.objects.get(id=idp)
    user = request.user
    today = time_zone_user(user)
    flashpacks = parcours.flashpacks.filter(Q(is_publish=1)|Q(start__lte=today,stop__gte=today)|Q(stop__gte=today),students=user.student) 

    context = { 'flashpacks': flashpacks , 'parcours': parcours , 'parcours': parcours , 'student' : user.student ,  'today' : today  }

    return render(request, 'qcm/list_parcours_flashpack_student.html', context)





@login_required(login_url= 'index')
@parcours_exists
def show_parcours_visual(request, id):

    parcours = Parcours.objects.get(id=id)
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    role, group , group_id , access = get_complement(request, teacher, parcours)


    relationships = Relationship.objects.filter(parcours=parcours,  is_publish=1 ).order_by("ranking")
    nb_exo_only = [] 
    i=0
    for r in relationships :
        if r.exercise.supportfile.is_title or r.exercise.supportfile.is_subtitle:
            i=0
        else :
            i+=1
        nb_exo_only.append(i)
    nb_exercises = parcours.exercises.filter(supportfile__is_title=0).count()
    context = {'relationships': relationships,  'parcours': parcours,   'nb_exo_only': nb_exo_only, 'nb_exercises': nb_exercises,  'group' : group ,  }
 
    return render(request, 'qcm/show_parcours_visual.html', context)



def replace_exercise_into_parcours(request):

    exercise_id = request.POST.get("change_parcours_exercise_id")
    parcours_id = request.POST.get("change_parcours_parcours_id")
    custom = request.POST.get("change_parcours_custom")

    parcourses_id = request.POST.getlist("change_into_parcours")
    parcours = Parcours.objects.get(pk = parcours_id)

    if request.method == "POST" :

        if custom == "0" :
            relationship = Relationship.objects.get(pk = exercise_id)
            
            for p_id in parcourses_id :
                prcrs = Parcours.objects.get(pk = p_id)                
                Relationship.objects.filter(pk = int(exercise_id)).update(parcours = prcrs)
                try :
                    Studentanswer.objects.filter(exercise = relationship.exercise, parcours = parcours).update(parcours = prcrs)
                except :
                    pass

        else :
            customexercise = Customexercise.objects.get(pk = exercise_id)
            parcours = Parcours.objects.get(pk = parcours_id)
            customexercise.parcourses.remove(prcrs)
            for p_id in parcourses_id :
                prcrs = Parcours.objects.get(pk = p_id)
                customexercise.parcourses.add(prcrs)
                try :
                    Customanswerbystudent.objects.filter(customexercise = customexercise, parcours = parcours).update(parcours =  prcrs)
                    Correctionskillcustomexercise.objects.filter(customexercise = customexercise, parcours = parcours).update(parcours =  prcrs)
                    Correctionknowledgecustomexercise.objects.filter(customexercise = customexercise, parcours = parcours).update(parcours =  prcrs)
                except :
                    pass

    return redirect('show_parcours' , 0, parcours_id)

 
@login_required(login_url= 'index')
def result_parcours(request, id, is_folder):

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    if  is_folder == 1 :
        folder = Folder.objects.get(id=id)
        role, group , group_id , access = get_complement(request, teacher, folder)
        students = folder.only_students_folder() # liste des élèves d'un parcours donné 
        relationships = Relationship.objects.filter(parcours__in=folder.parcours.all(),exercise__supportfile__is_title=0).prefetch_related('exercise').order_by("ranking")

        custom_set = set()
        for p in folder.parcours.all():
            cstm = p.parcours_customexercises.all() 
            custom_set.update(set(cstm))
        customexercises = list(custom_set)

        target = folder

    else :
        parcours = Parcours.objects.get(id=id)
        role, group , group_id , access = get_complement(request, teacher, parcours)
        students =  parcours.only_students(group)
        relationships = Relationship.objects.filter(parcours=parcours, exercise__supportfile__is_title=0).prefetch_related('exercise').order_by("ranking")
        customexercises = parcours.parcours_customexercises.all() 

        target = parcours

    themes_tab, historic = [],  []
    for relationship in relationships:
        theme = {}
        # on devrait mettre la condition dans la requète 
        # mais le relationships ci-dessus doit être envoyé dans le template
        # alors on enlève les titres du supportfile
        if not relationship.exercise.supportfile.is_title :
            thm = relationship.exercise.theme
            if not thm  in historic :
                historic.append(thm)
                theme["id"] = thm.id
                theme["name"]= thm.name
                themes_tab.append(theme)



    form = EmailForm(request.POST or None )

    stage = get_stage(teacher.user)

    context = {  'customexercises': customexercises, 'relationships': relationships, 'parcours': target, 'students': students, 'themes': themes_tab, 'form': form,  'group_id' : group_id  , 'stage' : stage, 'communications' : [] , 'role' : role }

    return render(request, 'qcm/result_parcours.html', context )




@login_required(login_url= 'index') 
def result_parcours_theme(request, id, idt, is_folder):

    teacher = Teacher.objects.get(user=request.user)

    parcours = Parcours.objects.get(id=id)
    students = students_from_p_or_g(request,parcours)

    role, group , group_id , access = get_complement(request, teacher, parcours)

    if not teacher_has_permisson_to_parcourses(request,teacher,parcours) :
        return redirect('index')

    theme = Theme.objects.get(id=idt)
    exercises = Exercise.objects.filter(knowledge__theme = theme, supportfile__is_title=0).order_by("id")
    


    if  is_folder == 1 :
        relationships = Relationship.objects.filter(parcours = parcours ,exercise__in=exercises, exercise__supportfile__is_title=0).order_by("ranking")

        customexercises = parcours.parcours_customexercises.all() 
 
    else :
        relationships = Relationship.objects.filter(parcours= parcours,exercise__in=exercises, exercise__supportfile__is_title=0 ).order_by("ranking")
        customexercises = parcours.parcours_customexercises.all() 


    themes_tab, historic = [],  []
    for relationship in relationships:
        theme = {}
        thm = relationship.exercise.theme
        if not thm  in historic :
            historic.append(thm)
            theme["id"] = thm.id
            theme["name"]= thm.name
            themes_tab.append(theme)

    stage = get_stage(teacher.user)
    form = EmailForm(request.POST or None)

    context = {  'relationships': relationships, 'customexercises': customexercises,'parcours': parcours, 'students': students,  'themes': themes_tab,'form': form, 'group_id' : group_id , 'stage' : stage, 'communications' : [], 'role' : role  }

    return render(request, 'qcm/result_parcours.html', context )



def get_items_from_parcours(parcours, is_folder) :
    """
    Permet de déterminer les compétences dans l'ordre d'apparition du BO dans un parcours
    """
    if is_folder :
        relationships = Relationship.objects.filter(parcours =parcours , exercise__supportfile__is_title=0).prefetch_related('exercise__supportfile').order_by("ranking")
        customexercises = parcours.parcours_customexercises.all() 

    else :
        relationships = Relationship.objects.filter(parcours= parcours, exercise__supportfile__is_title=0).prefetch_related('exercise__supportfile').order_by("ranking")
        customexercises = parcours.parcours_customexercises.all() 

    skill_set = set()
    for relationship in relationships :
        skill_set.update(set(relationship.skills.all()))


    for ce in  customexercises :
        skill_set.update(set(ce.skills.all()))

    skill_tab = []
    for s in Skill.objects.filter(subject__in = parcours.teacher.subjects.all()):
        if s in skill_set :
            skill_tab.append(s)

    return relationships , skill_tab 


@parcours_exists
def result_parcours_skill(request, id ):

    teacher = Teacher.objects.get(user=request.user)
    parcours = Parcours.objects.get(id=id)
    students = students_from_p_or_g(request,parcours)

    role, group , group_id , access = get_complement(request, teacher, parcours)

    if not teacher_has_permisson_to_parcourses(request,teacher,parcours) :
        return redirect('index')
    form = EmailForm(request.POST or None)

 
    relationships = get_items_from_parcours(parcours, False)[0]
    skill_tab =  get_items_from_parcours(parcours, False)[1]

 
    stage = get_stage(teacher.user)
    context = {  'relationships': relationships,  'students': students, 'parcours': parcours,  'form': form, 'skill_tab' : skill_tab, 'group' : group, 'group_id' : group_id, 'stage' : stage , 'communications' : [] , 'role' : role  }

    return render(request, 'qcm/result_parcours_skill.html', context )




@parcours_exists
def result_parcours_knowledge(request, id, is_folder):

    teacher = Teacher.objects.get(user=request.user)
    parcours = Parcours.objects.get(id=id)


    form = EmailForm(request.POST or None)
 

    if  is_folder == 1 :
    
        folder = Folder.objects.get(id=id)
        students = students_from_p_or_g(request,folder)
        parcourses = folder.parcours.all()
        relationships = Relationship.objects.filter(parcours__in=parcourses, exercise__supportfile__is_title=0).prefetch_related('exercise__supportfile').order_by("ranking")

        custom_set = set()
        knowledge_set = set()
        for p in parcourses:
            cstm = p.parcours_customexercises.all() 
            custom_set.update(set(cstm))

            knw = p.exercises.values_list("knowledge",flat=True).filter(supportfile__is_title=0).order_by("knowledge").distinct()
            knowledge_set.update(set(knw))

        customexercises = list(custom_set)
        knwldgs = list(knowledge_set)        

    else :
        parcours = Parcours.objects.get(id=id)
        students = students_from_p_or_g(request,parcours)
        relationships = Relationship.objects.filter(parcours=parcours, exercise__supportfile__is_title=0).prefetch_related('exercise__supportfile').order_by("ranking")
        customexercises = parcours.parcours_customexercises.all() 
        knwldgs = parcours.exercises.values_list("knowledge_id",flat=True).filter(supportfile__is_title=0).order_by("knowledge").distinct()



    knowledges,knowledge_ids = [], []
         
    role, group , group_id , access = get_complement(request, teacher, parcours)
 

    if not teacher_has_permisson_to_parcourses(request,teacher,parcours) :
        return redirect('index')


    for ce in  customexercises :
        for knowledge in ce.knowledges.all() :
            knowledges.append(knowledge)

    for k_id in knwldgs :
        if k_id not in knowledge_ids :
            k = Knowledge.objects.get(pk = k_id)
            knowledge_ids.append(k_id)
            knowledges.append(k)

    stage = get_stage(teacher.user)
    context = {  'relationships': relationships,  'students': students, 'parcours': parcours,  'form': form, 'exercise_knowledges' : knowledges, 'group_id' : group_id, 'stage' : stage , 'communications' : [] , 'role' : role  }

    return render(request, 'qcm/result_parcours_knowledge.html', context )
 


@parcours_exists
def result_parcours_waiting(request, id, is_folder):

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')
    parcours = Parcours.objects.get(id=id)
    students = students_from_p_or_g(request,parcours)

    form = EmailForm(request.POST or None)
 

    if  is_folder == 1:
        folder = Folder.objects.get(id=id)
        students = students_from_p_or_g(request,folder)
        parcourses = folder.parcours.all()
        relationships = Relationship.objects.filter(parcours__in=parcourses, exercise__supportfile__is_title=0).prefetch_related('exercise__supportfile').order_by("ranking")

        custom_set = set()
        knowledge_set = set()        
        for p in parcourses:
            cstm = p.parcours_customexercises.all() 
            custom_set.update(set(cstm))
            knw = p.exercises.values_list("knowledge",flat=True).filter(supportfile__is_title=0).order_by("knowledge").distinct()
            knowledge_set.update(set(knw))
        knwldgs = list(knowledge_set)  
        customexercises = list(custom_set)    

    else :
        parcours = Parcours.objects.get(id=id)
        students = students_from_p_or_g(request,parcours)
        relationships = Relationship.objects.filter(parcours=parcours, exercise__supportfile__is_title=0).prefetch_related('exercise__supportfile').order_by("ranking")
        customexercises = parcours.parcours_customexercises.all() 
        knwldgs = parcours.exercises.values_list("knowledge_id",flat=True).filter(supportfile__is_title=0).order_by("knowledge").distinct()


    waitings,waiting_ids , wtngs = [], [] , []
 

    role, group , group_id , access = get_complement(request, teacher, parcours)


    if not teacher_has_permisson_to_parcourses(request,teacher,parcours) :
        return redirect('index')

    for ce in  customexercises :
        for knowledge in ce.knowledges.all() :
            waitings.append(knowledge.waiting)

    for k_id in knwldgs :
        k = Knowledge.objects.get(pk = k_id)
        try :
            if k.waiting.name not in waiting_ids :
                waiting_ids.append(k.waiting.name)
                waitings.append(k.waiting)
        except :
            print(k)


    stage = get_stage(teacher.user)
    context = {  'relationships': relationships,  'students': students, 'parcours': parcours,  'form': form, 'exercise_waitings' : waitings, 'group_id' : group_id, 'stage' : stage , 'communications' : [] , 'role' : role  }

    return render(request, 'qcm/result_parcours_waiting.html', context )





def check_level_by_point(student, point):
    point = int(point)
    try :
        school = student.user.school
        stage = Stage.objects.get(school = school)

        if point > stage.up :
            level = "darkgreen"
        elif point > stage.medium :
            level = "green"
        elif point > stage.low :
            level = "warning"
        elif point > -1 :
            level = "danger"
        else :
            level = "default"
    except : 
        stage = { "low" : 50 ,  "medium" : 70 ,  "up" : 85  }

        if point > stage["up"]  :
            level = "darkgreen"
        elif point > stage["medium"]  :
            level = "green"
        elif point > stage["low"]  :
            level = "warning"
        elif point > -1 :
            level = "warning"
        else :
            level = "default"

    rep = "<i class='fa fa-square text-"+level+" pull-right'></i>"
 
    return rep
 



def get_student_result_from_eval(s, parcours, exercises,relationships,skills, knowledges,parcours_duration) : 

    customexercises = parcours.parcours_customexercises.filter(students=s).order_by("ranking")

    student = {"percent" : "" , "total_numexo" : "" , "good_answer" : "" , "test_duration" : False ,  "duration" : "" , "average_score" : "" ,"last_connexion" : "" ,"median" : "" ,"score" : "" ,"score_tab" : "" }
    student.update({"total_note":"", "details_note":"" ,  "detail_skill":"" ,  "detail_knowledge":"" , "ajust":"" , "tab_title_exo":"" , })
    student["name"] = s

    exercise_ids =  set(Studentanswer.objects.values_list("exercise",flat=True).filter(student=s, parcours=parcours).order_by("-point"))
    studentanswer_ids = set()
    for exercise_id  in exercise_ids :
        studentanswer_ids.add( Studentanswer.objects.values_list("id",flat=True).filter(student=s, parcours=parcours, exercise_id = exercise_id).order_by("-point").first() ) 

    #studentanswer_ids =  Studentanswer.objects.values_list("id",flat=True).filter(student=s, parcours=parcours).order_by("-date") [obsolète]
    #studentanswer_ids est la liste des studentanswers dont le nombre de points est maximal.

    #nb_exo_w = s.student_written_answer.filter(relationship__exercise__in = studentanswer_tab, relationship__parcours = parcours, relationship__is_publish = 1 ).count()
    nb_exo_ce = s.student_custom_answer.filter(parcours = parcours, customexercise__is_publish = 1 ).count()
    #nb_exo  = len(studentanswer_tab) + nb_exo_w + nb_exo_ce
    nb_exo  = len(studentanswer_ids)  +  nb_exo_ce
    student["nb_exo"] = nb_exo
    duration, score, total_numexo, good_answer = 0, 0, 0, 0
    tab, tab_date  , tab_title_exo , student_tab  = [], [], [] , []
    student["legal_duration"] = parcours.duration
    total_nb_exo = len(relationships)
    student["total_nb_exo"] = total_nb_exo       
    score_coeff = 0
    total_coeff = 0

    rtcoeff          =  Relationship.objects.filter(parcours=parcours).exclude(exercise__supportfile__is_title=1).aggregate(Sum('coefficient'))
    real_total_coeff = rtcoeff['coefficient__sum']

    for studentanswer_id in  studentanswer_ids : 
        studentanswer = Studentanswer.objects.get(pk=studentanswer_id)
        coefficient = Relationship.objects.get(exercise = studentanswer.exercise , parcours = studentanswer.parcours  ).coefficient
        duration += int(studentanswer.secondes)
        score += int(studentanswer.point)
        score_coeff += int(studentanswer.point)*coefficient
        total_numexo += int(studentanswer.numexo)
        good_answer += int(studentanswer.numexo*studentanswer.point/100)
        tab.append(studentanswer.point)
        tab_date.append(studentanswer.date)
        tab_title_exo.append(studentanswer.exercise.supportfile.title)
        student_tab.append(studentanswer)
        total_coeff += coefficient

    try :
        student["tab_title_exo"] = tab_title_exo        
        student["good_answer"] = int(good_answer)
        student["total_numexo"] = int(total_numexo)
        student["last_connexion"] = studentanswer.date
        student["score"] = int(score)
        student["score_coeff"] = math.ceil(int(score_coeff)/int(total_coeff))
        student["score_real_coeff"] = math.ceil(int(score_coeff)/int(real_total_coeff))
        student["score_tab"] = student_tab
        percent = math.ceil(int(good_answer)/int(total_numexo) * 100)
        if percent > 100 :
            percent = 100
        student["percent"] = percent
        ajust = math.ceil( (nb_exo / total_nb_exo ) * int(good_answer)/int(total_numexo) * 100  ) 
        if ajust > 100 :
            ajust=100
        student["ajust"] = ajust

        if duration > parcours_duration : 
            student["test_duration"] = True
        else :
            student["test_duration"] = False 

        if duration > 0 :
            student["duration"] = convert_seconds_in_time(duration)
        else :
            student["duration"] = ""

        if len(student_tab)>1 :
            tab.sort()
            if len(tab)%2 == 0 :
                med = (tab[len(tab)//2-1]+tab[(len(tab))//2])/2 ### len(tab)-1 , ce -1 est causé par le rang 0 du tableau
            else:
                med = tab[(len(tab)-1)//2]
            student["median"] = int(med)
  
        else :
            student["median"] = int(score)   

        student["score_real_coeff_display"] = False
        if real_total_coeff != len(studentanswer_ids): ### Si la somme des coeff est différente de la longueur alors il y a des coeff différents sur les exos. 
            student["score_real_coeff_display"] = True  
    except :
        pass

    details_c , score_custom , cen , score_total = "" , 0 , [] , 0
    total_knowledge, total_skill, detail_skill, detail_knowledge = 0,0, "",""

    for ce in customexercises :
        score_total += float(ce.mark)
        if ce.is_mark :
            try:
                cstm = ce.customexercise_custom_answer.get( student=s, parcours = parcours)
                if cstm.point :
                    score_custom +=  float(cstm.point)
                cen.append(cstm)
            except :
                pass


  
    student["score_custom"] = score_custom
    student["tab_custom"]   = cen
    student["score_total"]  = int(score_total)

    for skill in  skills:

        tot_s = total_by_skill_by_student(skill,relationships,parcours,s)
       
        detail_skill += skill.name + " " +check_level_by_point(s,tot_s) + "<br>" 

    student["detail_skill"] = detail_skill

    for knowledge in  knowledges :

        tot_k = total_by_knowledge_by_student(knowledge,relationships,parcours,s)

        detail_knowledge += knowledge.name + " "  +check_level_by_point(s,tot_k) + "<br>" 

    student["detail_knowledge"] = detail_knowledge 

    return student


@parcours_exists
def stat_evaluation(request, id):

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    stage = get_stage(teacher.user)
    parcours = Parcours.objects.get(id=id)
    skills = skills_in_parcours(request,parcours)
    knowledges = knowledges_in_parcours(parcours)
    #exercises = parcours.exercises.all()
    relationships = Relationship.objects.filter(parcours=parcours,is_publish = 1,exercise__supportfile__is_title=0).order_by("ranking")
    parcours_duration = parcours.duration #durée prévue pour le téléchargement
    exercises = []
    for r in relationships :
        parcours_duration += r.duration
        exercises.append(r.exercise)

    form = EmailForm(request.POST or None )
    stats = []
 
    role, group , group_id , access = get_complement(request, teacher, parcours)


    if not authorizing_access(teacher, parcours,access):
        messages.error(request, "  !!!  Redirection automatique  !!! Violation d'accès. Contacter SACADO...")
        return redirect('index')

    try : 
        students = parcours.only_students(group)
    except:
        students = students_from_p_or_g(request,parcours) 

    for s in students :
        student = get_student_result_from_eval(s, parcours, exercises,relationships,skills, knowledges,parcours_duration) 
        stats.append(student)

    context = { 'parcours': parcours, 'form': form, 'stats':stats , 'group_id': group_id , 'group': group , 'relationships' : relationships , 'stage' : stage , 'role' : role  }

    return render(request, 'qcm/stat_parcours.html', context )



@parcours_exists
def stat_evaluation_group(request, id, idg):
    request.session["group_id"] = idg
    return redirect('stat_evaluation', id)





 
def redo_evaluation(request):

    data = {}     
    parcours_id = request.POST.get("parcours_id", None)
    student_id  = request.POST.get("student_id", None)
    student     = Student.objects.get(pk=int(student_id) )
    parcours    = Parcours.objects.get(pk=int(parcours_id) )

    student.answers.filter(parcours=parcours).delete() # toutes les répones de cet élève à ce parcours/évaluation
    student.student_correctionskill.filter(parcours= parcours).delete()
    student.student_resultggbskills.filter(relationship__parcours = parcours).delete()  
    student.student_exerciselocker.filter( relationship__parcours = parcours, custom = 0).delete()     
    student.student_correctionknowledge.filter(parcours = parcours).delete()

    skills = skills_in_parcours(request,parcours)
    knowledges = knowledges_in_parcours(parcours)

    detail_knowledge = ""
    detail_skill     = ""

    for knowledge in  knowledges :
        detail_knowledge += knowledge.name + "<i class='fa fa-square text-default pull-right'></i> <br>" 

    for skill in  skills :
        detail_skill += knowledge.name + "<i class='fa fa-square text-default pull-right'></i> <br>" 

    data["skills"]    = detail_skill 
    data["knowledges"] = detail_knowledge  

    return JsonResponse(data)




def add_exercice_in_a_parcours(request):

    e = request.POST.get('exercise',None)
    if e :
        exercise = Exercise.objects.get(id=int(e))

        exercises_parcours = request.POST.get('exercises_parcours') 
        p_tab_ids = []
        for p in exercises_parcours.split("-"):
            if p != "" :
                p_tab_ids.append(int(p))

        for p_id in p_tab_ids :
            parcours = Parcours.objects.get(pk=p_id)
            try :
                rel = Relationship.objects.get(parcours = parcours , exercise = exercise).delete() 
            except :
                pass    

        ps= request.POST.getlist('parcours') 
        orders = request.POST.getlist('orders') 
        i=0
        for p in ps :
            parcours = Parcours.objects.get(id=int(p))
            try:
                r = int(orders[i])
            except :
                r = 0

            relation = Relationship.objects.create(parcours = parcours , exercise = exercise , ranking=  r, is_publish= 1 , start= None , date_limit= None, is_calculator = exercise.supportfile.calculator, duration= exercise.supportfile.duration, situation= exercise.supportfile.situation ) 
            relation.skills.set(exercise.supportfile.skills.all())   
            i +=1

    return redirect('exercises')


@parcours_exists
def clone_parcours(request, id, course_on ):
    """ cloner un parcours """

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')
    parcours = Parcours.objects.get(pk=id) # parcours à cloner
    relationships = parcours.parcours_relationship.all() 
    courses = parcours.course.filter(is_share = 1)
    # clone le parcours
    parcours.pk = None
    parcours.title = parcours.title+"-2"
    parcours.teacher = teacher
    parcours.is_publish = 0
    parcours.is_archive = 0
    parcours.is_share = 0
    parcours.is_favorite = 1
    parcours.target_id = None
    parcours.code = str(uuid.uuid4())[:8]  
    parcours.save()

    # ajoute le group au parcours si group    
    try :
        group_id = request.session.get("group_id",None)
        if group_id :
            group = Group.objects.get(pk = group_id)
            parcours.groups.add(group)
            Parcours.objects.filter(pk = parcours.id).update(subject = group.subject)
            Parcours.objects.filter(pk = parcours.id).update(level = group.level)
        else :
            group = None   
    except :
        group = None



    former_relationship_ids = []

    if course_on == 1 : 
        for course in courses :

            old_relationships = course.relationships.all()
            # clone le cours associé au parcours
            course.pk = None
            course.parcours = parcours
            course.teacher = teacher
            course.save()


            for relationship in old_relationships :
                # clone l'exercice rattaché au cours du parcours 
                if not relationship.id in former_relationship_ids :
                    relationship.pk = None
                    relationship.parcours = parcours
                    relationship.save() 
                course.relationships.add(relationship)

                former_relationship_ids.append(relationship.id)

    # clone tous les exercices rattachés au parcours 
    for relationship in relationships :
        skills = relationship.skills.all()
        try :
            relationship.pk = None
            relationship.parcours = parcours
            relationship.save() 
            relationship.skills.set(skills) 
        except :
            pass

    messages.success(request, "Duplication réalisée avec succès. Bonne utilisation. Vous pouvez placer le parcours dans le dossier en cliquant sur la config. du parcours")


    if group_id :
        return redirect('list_parcours_group', group_id)
    else :
        if parcours.is_evaluation :
            return redirect('all_parcourses' , 1 )
        elif parcours.is_sequence :
            return redirect('all_parcourses' , 2 )   
        else :
            return redirect('all_parcourses', 0 )



def exercise_parcours_duplicate(request):

    parcours_id  = request.POST.get("this_document_id",None)
    folders      = request.POST.getlist("folders",[])
    groups       = request.POST.getlist("groups",[])
    teacher = request.user.teacher
    data = {}

    if parcours_id : 

        parcours = Parcours.objects.get(pk=parcours_id) # parcours à cloner
        relationships = parcours.parcours_relationship.all() 
        courses = parcours.course.filter(is_share = 1)
        # clone le parcours
        parcours.pk = None
        parcours.title = parcours.title+"-2"
        parcours.teacher = teacher
        parcours.is_publish = 0
        parcours.is_archive = 0
        parcours.is_share = 0
        parcours.is_favorite = 1
        parcours.target_id = None
        parcours.code = str(uuid.uuid4())[:8]  
        parcours.save()

        parcours.folders.set(folders)    
        parcours.groups.set(groups)

        students = set()
        for fldr_id in folders :
            folder = Folder.objects.get(pk=fldr_id)
            students.update( folder.students.all() )
        for grp_id in groups :
            group = Group.objects.get(pk=grp_id)
            parcours.level = group.level
            parcours.subject = group.subject
            parcours.save()
            students.update( group.students.all() )

        parcours.students.set(students)

        former_relationship_ids = []


        for course in courses :
            old_relationships = course.relationships.all()
            course.pk = None
            course.parcours = parcours
            course.teacher = teacher
            course.save()

            for relationship in old_relationships :
                # clone l'exercice rattaché au cours du parcours 
                try : 
                    if not relationship.id in former_relationship_ids :
                        relationship.pk = None
                        relationship.parcours = parcours
                        relationship.save() 
                        
                    course.relationships.add(relationship)

                    former_relationship_ids.append(relationship.id)
                except : pass
        # clone tous les exercices rattachés au parcours 
        for relationship in relationships :
            skills = relationship.skills.all()
            try :
                relationship.pk = None
                relationship.parcours = parcours
                relationship.save() 
                relationship.skills.set(skills) 
            except :
                pass

        data["validation"] = "Duplication réussie. Retrouvez-le depuis le menu Groupes."
    else :
        data["validation"] = "Duplication abandonnée." 

    return JsonResponse(data)





 
def ajax_parcours_get_exercise_custom(request):

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')
    exercise_id =  int(request.POST.get("exercise_id"))
    customexercise = Customexercise.objects.get(pk=exercise_id)
    parcourses =  teacher.teacher_parcours.all()    

    context = {  'customexercise': customexercise , 'parcourses': parcourses , 'teacher' : teacher  }
    data = {}
    data['html'] = render_to_string('qcm/ajax_parcours_get_exercise_custom.html', context)
 
    return JsonResponse(data)
 
def parcours_clone_exercise_custom(request):

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    exercise_id =  int(request.POST.get("exercise_id"))
    customexercise = Customexercise.objects.get(pk=exercise_id)

    skills     = customexercise.skills.all()
    knowledges = customexercise.knowledges.all()

    checkbox_value = request.POST.get("checkbox_value")
    customexercise.pk = None
    customexercise.teacher = teacher
    customexercise.code = str(uuid.uuid4())[:8]  
    customexercise.save()

    customexercise.skills.set(knowledges) 
    customexercise.knowledges.set(knowledges)  

    if checkbox_value != "" :
        checkbox_ids = checkbox_value.split("-")
        for checkbox_id in checkbox_ids :
            try :
                parcours = Parcours.objects.get(pk = checkbox_id)
                customexercise.parcourses.add(parcours)
            except :
                pass 

    data = {}  
    return JsonResponse(data)

 
 
 
def ajax_getter_parcours_exercice_custom(request):

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    exercise_id    = int(request.POST.get("exercise_id"))
    customexercise = Customexercise.objects.get(pk=exercise_id)
    parcours_id    = int(request.POST.get("parcours_id"))
    parcours       = Parcours.objects.get(pk=parcours_id)

    data = {}
    customexercise.parcourses.add(parcours)
 
    return JsonResponse(data)
 




def  exercise_error(request):

    message     = request.POST.get("message")  
    exercise_id = request.POST.get("exercise_id",None)
    if exercise_id :
        exercise = Exercise.objects.get(id = int(exercise_id))
    else :
        messages.error(request, "L'exercice n'est pas reconnu.")
        redirect('index')        
    parcours_id = request.POST.get("parcours_id",None)

    if request.user :
        usr = request.user
        email = " "
        if usr.email :
            email = usr.email
        msg = "Message envoyé par l'utilisateur #"+str(usr.id)+", "+usr.last_name+", "+email+" :\n\nL'exercice dont l'id est -- "+str(exercise_id)+" --  décrit ci-dessous : \n Savoir faire visé : "+exercise.knowledge.name+ " \n Niveau : "+exercise.level.name+  "  \n Thème : "+exercise.theme.name +" comporte un problème. \n  S'il est identifié par l'utilisateur, voici la description :  \n" + message   
        response = "\n\n Pour répondre, utiliser ces liens en remplaçant le - par un slash :  sacado.xyz-account-response_from_mail-"+str(usr.id)+"\n\n Pour voir l'exercice en question, utiliser ce lien en remplaçant le - par un slash :   sacado.xyz-qcm-show_this_exercise-"+str(exercise_id)+"-"

    else :
        usr = "non connecté"
        msg = "Message envoyé par l'utilisateur #Non connecté :\n\nL'exercice dont l'id est -- "+str(exercise_id)+" --  décrit ci-dessous : \n Savoir faire visé : "+exercise.knowledge.name+ " \n Niveau : "+exercise.level.name+  "  \n Thème : "+exercise.theme.name +" comporte un problème. \n  S'il est identifié par l'utilisateur, voici la description :  \n" + message   
        response = "\n\n Pour voir l'exercice en question, utiliser ce lien en remplaçant le - par un slash :   sacado.xyz-qcm-show_this_exercise-"+str(exercise_id)+"-"

    sending_mail("Avertissement SacAdo Exercice "+str(exercise_id),  msg + response , settings.DEFAULT_FROM_EMAIL , ["sacado.asso@gmail.com"])
 
    if request.user.is_teacher :
        
        return redirect( 'show_this_exercise', exercise_id) 
    else :
        return redirect( 'show_parcours_student', parcours_id) 





def  exercise_peda(request):

    message = request.POST.get("message_peda")  
    exercise_id = request.POST.get("exercise_id")
    parcours_id = request.POST.get("parcours_id")
    exercise = Exercise.objects.get(id = int(exercise_id))

    parcours = Parcours.objects.get(pk=parcours_id)
 
    usr = request.user
    email = " "
    if usr.email :
        email = usr.email
    msg = "Message envoyé par l'utilisateur #"+str(usr.id)+", "+usr.last_name+", "+email+" :\n\nExercice Id : "+str(exercise_id)+" décrit ci-dessous : \n Savoir faire visé : "+exercise.knowledge.name+ " \n Niveau : "+exercise.level.name+  "  \n Thème : "+exercise.theme.name +" \n\n" + message   
    sending_mail("Aide pédagogique SacAdo Exercice "+str(exercise_id),  msg  , settings.DEFAULT_FROM_EMAIL , [parcours.teacher.user.email])

 
    return redirect(  'show_parcours_student', parcours_id)




@parcours_exists
def parcours_tasks_and_publishes(request, id):

    today = time_zone_user(request.user)
    parcours = Parcours.objects.get(id=id)
    teacher = Teacher.objects.get(user=request.user)

    role, group , group_id , access = get_complement(request, teacher, parcours) 
 

    relationships_customexercises , nb_exo_only, nb_exo_visible  = ordering_number(parcours)


    if not teacher_has_permisson_to_parcourses(request,teacher,parcours) :
        return redirect('index')

    form = AttachForm(request.POST or None, request.FILES or None)

 


    context = {'relationships_customexercises': relationships_customexercises,  'parcours': parcours, 'teacher': teacher  , 'today' : today , 'group' : group , 'group_id' : group_id , 'communications' : [] , 'form' : form , 'role' : role , }
    return render(request, 'qcm/parcours_tasks_and_publishes.html', context)





@parcours_exists
def result_parcours_exercise_students(request,id):

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    parcours = Parcours.objects.get(pk = id)
 
    if not teacher_has_permisson_to_parcourses(request,teacher,parcours) :
        return redirect('index')

    role, group , group_id , access = get_complement(request, teacher, parcours)


    relationships = Relationship.objects.filter(parcours = parcours, is_publish = 1) 
    customexercises = parcours.parcours_customexercises.filter( is_publish = 1).order_by("ranking")
    stage = get_stage(teacher.user)

    return render(request, 'qcm/result_parcours_exercise_students.html', {'customexercises': customexercises , 'stage':stage ,   'relationships': relationships ,  'parcours': parcours , 'group_id': group_id ,  'group' : group , 'role' : role , })


@csrf_exempt # PublieDépublie un exercice depuis organize_parcours
def ajax_is_favorite(request):  

    target_id = int(request.POST.get("target_id",None))
    statut = int(request.POST.get("statut"))
    status = request.POST.get("status") 
    data = {}
    if status == "parcours" :
        if statut :
            Parcours.objects.filter(pk = target_id).update(is_favorite = 0)
            data["statut"] = "<i class='fa fa-star text-default' ></i>"  
            data["fav"] = 0
        else :
            Parcours.objects.filter(pk = target_id).update(is_favorite = 1)  
            data["statut"] = "<i class='fa fa-star text-is_favorite' ></i>"
            data["fav"] = 1
    else :
        if statut :
            Folder.objects.filter(pk = target_id).update(is_favorite = 0)
            data["statut"] = "<i class='fa fa-star text-default' ></i>"
            data["fav"] = 0
        else :
            Folder.objects.filter(pk = target_id).update(is_favorite = 1)  
            data["statut"] = "<i class='fa fa-star   text-is_favorite' ></i>"
            data["fav"] = 1     

    return JsonResponse(data) 




@csrf_exempt # PublieDépublie un exercice depuis organize_parcours
def ajax_is_active(request):  

    target_id = int(request.POST.get("target_id",None))
    data = {}
    parcours = Parcours.objects.get(pk = target_id)
    if parcours.is_active :
        parcours.is_active = 0
        data["html"] = "<i class='fa fa-thumbs-up text-default' ></i>"
    else :
        parcours.is_active = 1
        data["html"] = "<i class='fa fa-thumbs-up text-is_favorite' ></i>"
    parcours.save()   

    return JsonResponse(data) 



@csrf_exempt # Autorise ou pas la calculatrice dans une relationship
def ajax_is_calculator(request):  

    rc_id = int(request.POST.get("rc_id",None))
    data = {}
    relationship = Relationship.objects.get(pk = rc_id)
    if relationship.is_calculator :
        relationship.is_calculator = 0
        data["html"] = '<img src="https://sacado.xyz/static/img/no_calculator.png" class="pull-right" width="35px" loading="lazy" title="Autoriser la calculatrice" />'
    else :
        relationship.is_calculator = 1
        data["html"] = '<img src="https://sacado.xyz/static/img/calculator.png" class="pull-right" width="35px" loading="lazy" title="Interdire la calculatrice" />'
    relationship.save()   

    return JsonResponse(data) 


@csrf_exempt # PublieDépublie un exercice depuis organize_parcours
def ajax_course_sorter(request):  
    try :
        course_ids = request.POST.get("valeurs")
        course_tab = course_ids.split("-") 
        parcours_id = int(request.POST.get("parcours_id"))

        for i in range(len(course_tab)-1):
            Course.objects.filter(parcours_id = parcours_id , pk = course_tab[i]).update(ranking = i)
    except :
        pass

    data = {}
    return JsonResponse(data) 


@csrf_exempt # PublieDépublie un exercice depuis organize_parcours
def ajax_parcours_sorter(request):  

    try :
        course_ids = request.POST.get("valeurs")
        course_tab = course_ids.split("-") 
        for i in range(len(course_tab)-1):
            Parcours.objects.filter( pk = course_tab[i]).update(ranking = i)
    except :
        pass
    data = {}
    return JsonResponse(data)



@csrf_exempt # PublieDépublie un exercice depuis organize_parcours
def ajax_folders_sorter(request):  

    try :
        folder_ids = request.POST.get("valeurs")
        folder_tab = folder_ids.split("-") 
        for i in range(len(folder_tab)-1):
            Folder.objects.filter( pk = folder_tab[i]).update(ranking = i)
    except :
        pass
    data = {}
    return JsonResponse(data)



@csrf_exempt
def ajax_sort_exercise(request):
    """ tri des exercices""" 
    try :
        parcours = request.POST.get("parcours")

        exercise_ids = request.POST.get("valeurs")
        exercise_tab = exercise_ids.split("-") 

        customizes = request.POST.get("customizes")
        customize_tab = customizes.split("-") 

        for i in range(len(exercise_tab)-1):
            if int(customize_tab[i]) == 1 :
                Customexercise.objects.filter(pk = exercise_tab[i]).update(ranking = i)
            else :
                Relationship.objects.filter(parcours = parcours , exercise_id = exercise_tab[i]).update(ranking = i)
    except :
        pass
    data = {}
    return JsonResponse(data) 




@csrf_exempt
def ajax_sort_sequence(request):
    """ tri des exercices""" 
    try :
        parcours = request.POST.get("parcours")

        exercise_ids = request.POST.get("valeurs")
        exercise_tab = exercise_ids.split("-") 

        print(exercise_tab)

        for i in range(len(exercise_tab)-1):
            Relationship.objects.filter(pk = exercise_tab[i]).update(ranking = i)
    except :
        pass
    data = {}
    return JsonResponse(data) 


@csrf_exempt # PublieDépublie un exercice depuis organize_parcours
def ajax_publish(request):  

    statut = request.POST.get("statut")
    custom = request.POST.get("custom")

    data = {}
 
    if statut=="true" or statut == "True":
        statut = 0
        data["statut"] = "false"
        data["publish"] = "Dépublié"
        data["class"] = "legend-btn-danger"
        data["noclass"] = "legend-btn-success"
        data["removeclass"] = "btn-success"

    else:
        statut = 1
        data["statut"] = "true"
        data["publish"] = "Publié"
        data["class"] = "legend-btn-success"
        data["noclass"] = "legend-btn-danger"
        data["removeclass"] = "btn-danger"

    if custom == "0" :
        relationship_id = request.POST.get("relationship_id")        
        Relationship.objects.filter(pk = int(relationship_id)).update(is_publish = statut)
    else :
        customexercise_id = request.POST.get("relationship_id")        
        Customexercise.objects.filter(pk = int(customexercise_id)).update(is_publish = statut)    
    return JsonResponse(data) 



@csrf_exempt   # PublieDépublie un parcours depuis form_group et show_group
def ajax_publish_parcours(request):  

    parcours_id = request.POST.get("parcours_id")
    statut = request.POST.get("statut")
    data = {}
    if statut=="true" or statut == "True":
        statut = 0
        data["statut"] = "false"
        if request.POST.get("from") == "1" :
            data["publish"] = "Parcours non publié"
        elif request.POST.get("from") == "2" :
            data["publish"] = "Non publié"
        else :
            data["publish"] = "Dépublier"
        data["style"] = "#dd4b39"
        data["class"] = "legend-btn-danger"
        data["noclass"] = "legend-btn-success"
        data["label"] = "Non publié"
        data["is_publish_label"] = "<span class='text-danger'>non publié <i class='fa fa-circle'></i>"
    else:
        statut = 1
        data["statut"] = "true"
        if request.POST.get("from") == "1" :
            data["publish"] = "Parcours publié"
        elif request.POST.get("from") == "2" :
            data["publish"] = "Publié" 
        else :
            data["publish"] = "Dépublier"
        data["style"] = "#00a65a"
        data["class"] = "legend-btn-success"
        data["noclass"] = "legend-btn-danger"
        data["label"] = "Publié"
        data["is_publish_label"] = "publié <i class='fa fa-circle text-success'></i>"

    is_folder = request.POST.get("is_folder",None)
    is_quizz = request.POST.get("is_quizz",None)

    if is_quizz == "yes" :
        Quizz.objects.filter(pk = int(parcours_id)).update(is_publish = statut)
    elif is_folder == "no" :
        if statut == 1 :
            pcs = Parcours.objects.get(pk = int(parcours_id))
            exercise_ids = Relationship.objects.values_list("exercise_id",flat=True).filter(parcours=pcs, is_publish=1)
            # if pcs.is_testpos : # Training pour le test de positionnement
            #     pcs_str = convert_into_str(exercise_ids)
            #     Testtraining.objects.filter(parcours = pcs.target_id).update(questions_effective = pcs_str)
            # elif pcs.is_ia and not pcs.is_testpos : # Training pour le parcours IA
            students  = pcs.students.all()
            knowledge_ids = Parcourscreator.objects.filter(parcours_id = pcs.id).values_list('knowledge_id',flat=True).distinct()
            for kid in knowledge_ids :
                for student in students :
                    exercise_ids_std = Relationship.objects.values_list("exercise_id",flat=True).filter(parcours=pcs, is_publish=1,students=student)
                    exercise_ids_std_str = convert_into_str(exercise_ids_std)
                    Parcourscreator.objects.filter(parcours_id = pcs.id , knowledge_id = kid , student_id = student.user.id).update(effective = "")
                    Parcourscreator.objects.filter(parcours_id = pcs.id , knowledge_id = kid , student_id = student.user.id).update(effective = exercise_ids_std_str)

        Parcours.objects.filter(pk = int(parcours_id)).update(is_publish = statut)
    else :
        Folder.objects.filter(pk = int(parcours_id)).update(is_publish = statut)

    return JsonResponse(data) 

 
 



@csrf_exempt   # PublieDépublie un parcours depuis form_group et show_group
def ajax_sharer_parcours(request):  

    parcours_id = request.POST.get("parcours_id")
    statut = request.POST.get("statut")
    is_folder = request.POST.get("is_folder")
 
    data = {}
    if statut=="true" or statut == "True":
        statut = 0
        data["statut"]  = "false"
        data["share"]   = "Privé"
        data["style"]   = "#dd4b39"
        data["class"]   = "legend-btn-danger"
        data["noclass"] = "legend-btn-success"
        data["label"]   = "Privé"
    else:
        statut = 1
        data["statut"]  = "true"
        data["share"]   = "Mutualisé"
        data["style"]   = "#00a65a"
        data["class"]   = "legend-btn-success"
        data["noclass"] = "legend-btn-danger"
        data["label"]   = "Mutualisé"

    is_folder = request.POST.get("is_folder")
 
    if is_folder == "no" :
        Parcours.objects.filter(pk = int(parcours_id)).update(is_share = statut)
    else :
        Folder.objects.filter(pk = int(parcours_id)).update(is_share = statut)

    return JsonResponse(data) 


@csrf_exempt
def ajax_dates(request):  # On conserve relationship_id par commodité mais c'est relationship_id et non customexercise_id dans tout le script
    data = {}
    relationship_id = request.POST.get("relationship_id")
    duration =  request.POST.get("duration") 
    custom =  request.POST.get("custom") 
    try :
        typp =  request.POST.get("type")
        if typp : 
            typ = int(typp)
        if typ == 0 : # Date de publication
            date = request.POST.get("dateur") 
            if date :
                if custom == "0" :
                    Relationship.objects.filter(pk = int(relationship_id)).update(start = date)
                else :
                    Customexercise.objects.filter(pk = int(relationship_id)).update(start = date)
                data["class"] = "btn-success"
                data["noclass"] = "btn-default"
            else :
                if custom == "0" :
                    Relationship.objects.filter(pk = int(relationship_id)).update(start = None)
                else :
                    Customexercise.objects.filter(pk = int(relationship_id)).update(start = None)
                data["class"] = "btn-default"
                data["noclass"] = "btn-success"
            data["dateur"] = date 

        elif typ == 1 :  # Date de rendu de tache
            date = request.POST.get("dateur") 
            if date :
                if custom == "0" : 
                    Relationship.objects.filter(pk = int(relationship_id)).update(date_limit = date)

                    r = Relationship.objects.get(pk = int(relationship_id))
                    data["class"] = "btn-success"
                    data["noclass"] = "btn-default"
                    msg = "Pour le "+str(date)+": \n Un exercice vous est assigné. Rejoindre sacado.xyz. \n. Si vous ne souhaitez plus recevoir les notifications, désactiver la notification dans votre compte."
                    data["dateur"] = date 
                    students = r.students.all()
                    rec = []
                else :
                    Customexercise.objects.filter(pk = int(relationship_id)).update(date_limit = date)
                    ce = Customexercise.objects.get(pk = int(relationship_id))
                    data["class"] = "btn-success"
                    data["noclass"] = "btn-default"
                    msg = "Pour le "+str(date)+": \n Un exercice vous est assigné. Rejoindre sacado.xyz. Si vous ne souhaitez plus recevoir les notifications, désactiver la notification dans votre compte."
                    data["dateur"] = date 
                    students = ce.students.all()
                    rec = []


                for s in students :
                    if s.task_post : 
                        if  s.user.email :                  
                            rec.append(s.user.email)

                sending_mail("SacAdo Tâche à effectuer avant le "+str(date),  msg , settings.DEFAULT_FROM_EMAIL , rec ) 
                sending_mail("SacAdo Tâche à effectuer avant le "+str(date),  msg , settings.DEFAULT_FROM_EMAIL , [r.parcours.teacher.user.email] )   

            else :
                if custom == "0" : 
                    Relationship.objects.filter(pk = int(relationship_id)).update(date_limit = None)

                    r = Relationship.objects.get(pk = int(relationship_id))
                    data["class"] = "btn-default"
                    data["noclass"] = "btn-success"
                    msg = "L'exercice https://sacado.xyz/qcm/show_this_exercise/"+str(r.exercise.id)+" : "+str(r.exercise)+" n'est plus une tâche \n. Si vous ne souhaitez plus recevoir les notifications, désactiver la notification dans votre compte."
                    date = "Tâche ?"  
                    data["dateur"] = date 
                    students = r.students.all()
                else :
                    Customexercise.objects.filter(pk = int(relationship_id)).update(date_limit = None)
                    ce = Customexercise.objects.get(pk = int(relationship_id))
                    data["class"] = "btn-success"
                    data["noclass"] = "btn-default"
                    msg = "L'exercice https://sacado.xyz/qcm/show_this_exercise/"+str(ce.id)+" : n'est plus une tâche \n Si vous ne souhaitez plus recevoir les notifications, désactiver la notification dans votre compte."
                    data["dateur"] = date 
                    students = ce.students.all()
          
                rec = []
                for s in students :
                    if s.task_post : 
                        if  s.user.email :                  
                            rec.append(s.user.email)
                sending_mail("SacAdo. Annulation de tâche à effectuer",  msg , settings.DEFAULT_FROM_EMAIL , rec ) 
                sending_mail("SacAdo. Annulation de tâche à effectuer",  msg , settings.DEFAULT_FROM_EMAIL , [r.parcours.teacher.user.email] ) 

        else :            
            if custom == "0" :
                Relationship.objects.filter(pk = int(relationship_id)).update(start = date)
                r = Relationship.objects.get(pk = int(relationship_id))
                msg = "Pour le "+str(date)+": \n Faire l'exercice : https://sacado.xyz/qcm/show_this_exercise/"+str(r.exercise.id)+" : " +str(r.exercise)+" \n. Si vous ne souhaitez plus recevoir les notifications, désactiver la notification dans votre compte. Ceci est un mail automatique. Ne pas répondre."
                students = r.students.all()
            else :
                Customexercise.objects.filter(pk = int(relationship_id)).update(start = date)
                Customexercise.objects.filter(pk = int(relationship_id)).update(date_limit = None)
                ce = Customexercise.objects.get(pk = int(relationship_id))
                msg = "Pour le "+str(date)+": \n Faire l'exercice : https://sacado.xyz/qcm/show_this_exercise/"+str(ce.id)+"\n Si vous ne souhaitez plus recevoir les notifications, désactiver la notification dans votre compte. Ceci est un mail automatique. Ne pas répondre."
                students = ce.students.all()

            data["class"] = "btn-success"
            data["noclass"] = "btn-default"
 
            rec = []
            for s in students :
                if s.task_post : 
                    if  s.user.email :                  
                        rec.append(s.user.email)

            sending_mail("SacAdo Tâche à effectuer avant le "+str(date),  msg , settings.DEFAULT_FROM_EMAIL , rec ) 
            sending_mail("SacAdo Tâche à effectuer avant le "+str(date),  msg , settings.DEFAULT_FROM_EMAIL , [r.parcours.teacher.user.email] ) 

            data["dateur"] = date  

    except :        
        
        try :
 
            duration =  request.POST.get("duration") 
            if custom == "0" :
                Relationship.objects.filter(pk = int(relationship_id)).update(duration = duration)
            else :
                Customexercise.objects.filter(pk = int(relationship_id)).update(duration = duration)
            data["clock"] = "<i class='fa fa-clock-o'></i> "+str(duration)+"  min."          
            try :
                situation =  request.POST.get("situation")
                rel = Relationship.objects.get(pk = int(relationship_id))
                Relationship.objects.filter(pk = int(relationship_id)).update(situation = situation)
                data["save"] = "<i class='fa fa-save'></i> "+str(situation)
                data["situation"] = "<i class='fa fa-save'></i> "+str(situation)
                data["annonce"] = ""
                data["annoncement"]   = False

            except : 
                pass

        except :
            try :
                situation =  request.POST.get("situation") 
                rel = Relationship.objects.get(pk = int(relationship_id))
                Relationship.objects.filter(pk = int(relationship_id)).update(situation = situation)
                data["save"] = "<i class='fa fa-save'></i> "+str(situation) 
                data["annonce"] = "" 
                data["annoncement"]   = False                                 
                try :
                    duration =  request.POST.get("duration") 
                    if custom == "0" :
                        Relationship.objects.filter(pk = int(relationship_id)).update(duration = duration)
                    else :
                        Customexercise.objects.filter(pk = int(relationship_id)).update(duration = duration)
                    data["clock"] = "<i class='fa fa-clock-o'></i> "+str(duration)+"  min."                            
                    data["duration"] = duration
                except : 
                    pass
            except :
                pass

    return JsonResponse(data) 



@csrf_exempt
def ajax_notes(request):  
    data = {}
    relationship_id = request.POST.get("relationship_id")
    mark =  request.POST.get("mark")
    relationship  = Relationship.objects.filter(pk = relationship_id ).update(is_mark = 1, mark = mark)
    return JsonResponse(data) 


@csrf_exempt
def ajax_maxexo(request):  
    data = {}
    relationship_id = request.POST.get("relationship_id")
    maxexo =  request.POST.get("maxexo")
    Relationship.objects.filter(pk = relationship_id ).update(maxexo = maxexo)
    return JsonResponse(data) 


@csrf_exempt
def ajax_coefficient(request):  
    data = {}
    relationship_id = request.POST.get("relationship_id")
    coefficient =  request.POST.get("coefficient")
    Relationship.objects.filter(pk = relationship_id ).update(coefficient = coefficient)
    data['html'] = coefficient
    return JsonResponse(data) 



@csrf_exempt
def ajax_delete_notes(request):  
    data = {}
    relationship_id = request.POST.get("relationship_id")
    relationship  = Relationship.objects.filter(pk = relationship_id ).update(is_mark = 0, mark = "")
    return JsonResponse(data) 


@csrf_exempt
def ajax_skills(request):  
    data = {}
    relationship_id = request.POST.get("relationship_id")
    skill_id =  int(request.POST.get("skill_id") )
    relationship  = Relationship.objects.get(pk = relationship_id )
    skill = Skill.objects.get(pk = skill_id ) 

    if Relationship.objects.filter(pk = relationship_id, skills = skill).count()>0 :
        relationship.skills.remove(skill)    
    else :
        relationship.skills.add(skill)   

    return JsonResponse(data) 

def aggregate_parcours(request):

    code = request.POST.get("parcours")
    student = Student.objects.get(user=request.user)

    if Parcours.objects.exclude(students = student).filter(code = code).exists()  :
        parcours = Parcours.objects.get(code = code)
        parcours.students.add(student)

    return redirect("index") 

def ajax_parcoursinfo(request):

    code =  request.POST.get("code")
    data = {}    
    try : 
        nb_group = Parcours.objects.filter(code = code).count()
 
        if  nb_group == 1 :

            data['htmlg'] = "<br><i class='fa fa-check text-success'></i>" 
 
        else :
            data['htmlg'] = "<br><i class='fa fa-times text-danger'></i> Parcours inconnu."
 
    except :
            data['htmlg'] = "<br><i class='fa fa-times text-danger'></i> Parcours inconnu."
 

 
    return JsonResponse(data)

def ajax_detail_parcours(request):

    custom =  int(request.POST.get("custom"))    
    parcours_id =  int(request.POST.get("parcours_id"))
    exercise_id =  int(request.POST.get("exercise_id"))
    num_exo =  int(request.POST.get("num_exo"))    
    parcours = Parcours.objects.get(id = parcours_id)

    today = time_zone_user(request.user)

    students = students_from_p_or_g(request,parcours)

    try :
        relationship = Relationship.objects.get(exercise_id = exercise_id, parcours = parcours)
    except :
        relationship = None
    
    data = {}
    if custom == 0 :
        exercise = Exercise.objects.get(id = exercise_id) 
        stats = []
        for s in students :
            student = {}
            student["name"] = s 

            studentanswers = Studentanswer.objects.filter(student=s, exercise = exercise ,  parcours = parcours)
            duration, score = 0, 0
            tab, tab_date = [], []
            for studentanswer in  studentanswers : 
                duration += int(studentanswer.secondes)
                score += int(studentanswer.point)
                tab.append(studentanswer.point)
                tab_date.append(studentanswer.date)
            tab_date.sort()
            try :
                if len(studentanswers)>1 :
                    average_score = int(score/len(studentanswers))
                    student["duration"] = convert_seconds_in_time(duration)
                    student["average_score"] = int(average_score)
                    student["heure_max"] = tab_date[len(tab_date)-1]
                    student["heure_min"] = tab_date[0]
                    tab.sort()
                    if len(tab)%2 == 0 :
                        med = (tab[(len(tab)-1)//2]+tab[(len(tab)-1)//2+1])/2 ### len(tab)-1 , ce -1 est causÃ© par le rang 0 du tableau
                    else:
                        med = tab[(len(tab)-1)//2+1]
                    student["median"] = int(med)
                    student["nb"] = int(len(tab))                
                else :
                    average_score = int(score)
                    student["duration"] = convert_seconds_in_time(duration)
                    student["average_score"] = int(score)
                    student["heure_max"] = tab_date[0]
                    student["heure_min"] = tab_date[0]
                    student["median"] = int(score)
                    student["nb"] = 0  
            except :
                student["duration"] = ""
                student["average_score"] = ""
                student["heure_max"] = ""
                student["heure_min"] = ""
                student["median"] = ""
                student["nb"] = 0  
            stats.append(student)

 
        context = { 'parcours': parcours, 'exercise':exercise ,  'stats': stats ,  'today' : today ,  'num_exo':num_exo , 'relationship':relationship, 'communications' : [] , }

        data['html'] = render_to_string('qcm/ajax_detail_parcours.html', context)

    else :
        customexercise = Customexercise.objects.get(pk = exercise_id, parcourses = parcours) 
        students = customexercise.students.order_by("user__last_name")  
        duration, score = 0, 0
        tab = []
        cas =  customexercise.customexercise_custom_answer.filter(parcours=parcours)
        
        for ca in cas  : 
            try :
                score += int(ca.point)
                tab.append(ca.point)
            except:
                pass
        tab.sort()

        try :
            if len(tab)%2 == 0 :
                med = (tab[(len(tab)-1)//2]+tab[(len(tab)-1)//2+1])/2 ### len(tab)-1 , ce -1 est cause par le rang 0 du tableau
            else:
                med = tab[(len(tab)-1)//2+1]
        except :
            med = 0     
 
        try :
            average = int(score / len(cas))
        except :
            average = "" 


        context = {  'parcours': parcours,  'customexercise':customexercise ,'average':average ,  'today': today ,   'students' : students , 'relationship':[], 'num_exo' : num_exo, 'communications' : [] , 'median' : med , 'communications' : [] , }

        data['html'] = render_to_string('qcm/ajax_detail_parcours_customexercise.html', context)


    return JsonResponse(data)




def delete_relationship(request,idr):

    relation = Relationship.objects.get(pk = idr)
    link =  relation.parcours.id
    if relation.parcours.teacher.user == request.user  :
        relation.delete()

    return redirect("show_parcours" , 0 , link ) 


    
def delete_relationship_by_individualise(request,idr, id):

    relation = Relationship.objects.get(pk = idr)
    link =  relation.parcours.id
    if relation.parcours.teacher.user == request.user  :
        relation.delete()

    return redirect("individualise_parcours" , link   ) 



def remove_students_from_parcours(request):

    parcours_id = request.POST.get("parcours_id")
    parcours = Parcours.objects.get(pk = parcours_id)
    students_id = request.POST.getlist("students")
    for student_id in students_id:
        student = Student.objects.get(user = student_id)
        relationships = Relationship.objects.filter(parcours = parcours, students = student)
        for r in relationships :
            r.students.remove(student)
        parcours.students.remove(student)
 
    return redirect("parcours" ) 



def ajax_locker_exercise(request):

    custom =  int(request.POST.get("custom"))
    student_id =  request.POST.get("student_id")
    exercise_id =  request.POST.get("exercise_id")

    today = time_zone_user(request.user).now()

    data = {}    
    
    if custom == 1 :
        if Exerciselocker.objects.filter(student_id = student_id, customexercise_id = exercise_id, custom = 1).exists() :
            result =  Exerciselocker.objects.get(student_id = student_id, customexercise_id = exercise_id, custom = 1 )
            result.delete()
            lock_result = '<i class="fa fa-unlock text-default"></i>'
        else :
            Exerciselocker.objects.create(student_id = student_id, customexercise_id = exercise_id, custom = 1, relationship = None, lock = today )
            lock_result = '<i class="fa fa-lock text-danger"></i>'
    else :
        if Exerciselocker.objects.filter(student_id = student_id, relationship_id = exercise_id, custom = 0).exists() :
            result =  Exerciselocker.objects.get(student_id = student_id, relationship_id = exercise_id, custom = 0)
            result.delete()
            lock_result = '<i class="fa fa-unlock text-default"></i>'
        else :
            Exerciselocker.objects.create(student_id = student_id, relationship_id = exercise_id, custom = 0,customexercise = None,lock = today )
            lock_result = '<i class="fa fa-lock text-danger"></i>'
 
    data["html"] = lock_result

    return JsonResponse(data)
 



def real_time(request,id):
    """ module de real time"""
    parcours = Parcours.objects.get(pk = id)
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    today = time_zone_user(request.user).now()

    role, group , group_id , access = get_complement(request, teacher, parcours)
    connected_student_ids =  Tracker.objects.values_list("user_id",flat = True).filter(parcours = parcours ).distinct()

    relationships_customexercises , nb_exo_only, nb_exo_visible  = ordering_number(parcours)


    if not teacher_has_permisson_to_parcourses(request,teacher,parcours) :
        return redirect('index')

    students = parcours.students.order_by("user__last_name").exclude(user__username__contains="_e-test")
    rcs      = rcs_for_realtime(parcours)

    context = { 'teacher': teacher , 'parcours': parcours, 'rcs': rcs, 'students': students , 'group': group , 'role': role , 'access': access  , 'relationships_customexercises': relationships_customexercises  }

    return render(request, 'qcm/real_time.html', context )



def time_done(arg):
    """
    convertit 1 entier donné  (en secondes) en durée h:m:s
    """
    if arg == "":
        return arg
    else:
        arg = int(arg)
        s = arg % 60
        m = arg // 60 % 60
        h = arg // 3600
        
        if arg < 60:
            return f"{s}s"
        if arg < 3600:
            return f"{m}min.{s}s"
        else:
            return f"{h}h.{m}min.{s}s"




def ajax_real_time_live(request):
    """ Envoie la liste des exercices d'un parcours """
    data = {} # envoie vers JSON
    parcours_id = request.POST.get("parcours_id")
    parcours = Parcours.objects.get(pk=int(parcours_id))
    today = time_zone_user(request.user).now()
    trackers =  Tracker.objects.filter(parcours = parcours )

    i , line, cell, result =  0 , "", "", ""
    for tracker in trackers :
        tui = tracker.user.id
        tr = "tr_student_"+str(tui)
        exo_id = "rc_"+parcours_id+"_"+str(tracker.exercise_id)+"_"+tr

        if tracker.is_custom :
            trck = "en_compo"
        else :

            if tracker.parcours.answers.filter(student=tracker.user.student, exercise_id = tracker.exercise_id) :
                ans = tracker.parcours.answers.filter(student=tracker.user.student, exercise_id = tracker.exercise_id).last()
                trck = str(ans.numexo)+" > "+str(ans.point)+"% "+str(time_done(ans.secondes))
            else :
                trck = "en composition"
            
        if i == trackers.count()-1:
            line +=  tr 
            cell +=  exo_id 
            result +=  trck
        else :
            line +=  tr + "====="
            cell +=  exo_id  + "====="
            result +=  trck  + "====="
        i+=1
      
    data["line"] = line
    data["cell"] = cell
    data["result"] = result

    return JsonResponse(data)

 
def get_values_canvas(request):
    """ Récupère la réponse élève en temps réel """
    data = {} # envoie vers JSON
    parcours_id = request.POST.get("parcours_id")
    customexercise_id = request.POST.get("customexercise_id")
    student_id = request.POST.get("student_id")
 
    ce = Customanswerbystudent.objects.get(customexercise_id = customexercise_id, parcours_id = parcours_id, student_id = student_id )
    values = ce.answer

    data["values"] = values
 

    return JsonResponse(data)

#######################################################################################################################################################################
#######################################################################################################################################################################
#################   Exercise
#######################################################################################################################################################################
#######################################################################################################################################################################


@csrf_exempt  
def audio_exercise(request):

    data = {}
    ide =  int(request.POST.get("id_exercise"))
    exercise = Exercise.objects.get(pk=ide) 
    form = AudioForm(request.POST or None, request.FILES or None , instance=exercise )

    if form.is_valid():
        print(request.FILES.get("id_audiofile"))
        nf =  form.save(commit = False)
        nf.audiofile = request.FILES.get("id_audiofile")
        nf.save()
    else:
        print(form.errors)
    return JsonResponse(data)  


def all_levels(user, status):
    teacher = Teacher.objects.get(user=user)
    datas = []
    levels_tab,knowledges_tab, exercises_tab    =   [],  [],  []

    if status == 0 : 
        levels = teacher.levels.order_by("ranking")
    elif status == 1 : 
        levels = Level.objects.order_by("ranking")

    for level in levels :
        levels_dict = {}
        levels_dict["name"]=level 

        datas.append(levels_dict)
    return datas



def list_exercises(request):

    request.session["tdb"] = "Documents"  
    request.session["subtdb"] = "Consulting"

    
    user = request.user
    if user.is_authenticated :
        if user.is_teacher:  # teacher
            teacher = Teacher.objects.get(user=user)
            datas = all_levels(user, 0)

            customexercises = teacher.teacher_customexercises.all()
            return render(request, 'qcm/list_exercises.html', {'datas': datas, 'teacher': teacher , 'customexercises':customexercises, 'parcours': None, 'relationships' : [] ,  'communications': [] , })
        
        elif user.is_student: # student
            student = Student.objects.get(user=user)
            parcourses = student.students_to_parcours.all()

            nb_exercises = Relationship.objects.filter(parcours__in=parcourses,is_publish=1,exercise__supportfile__is_title=0).count()
            relationships = Relationship.objects.filter(parcours__in=parcourses,is_publish=1,exercise__supportfile__is_title=0).order_by("exercise__theme")

            return render(request, 'qcm/student_list_exercises.html',
                          {'relationships': relationships, 'nb_exercises': nb_exercises ,     })

        else: # non utilisé
            parent = Parent.objects.get(user=user)
            students = parent.students.all()
            parcourses = []
            for student in students :
                for parcours in student.students_to_parcours.all() :
                    if parcours not in parcourses :
                        parcourses.append(parcours)  

            nb_exercises = Relationship.objects.filter(parcours__in=parcourses,is_publish=1,exercise__supportfile__is_title=0).count()
            relationships = Relationship.objects.filter(parcours__in=parcourses,is_publish=1,exercise__supportfile__is_title=0).order_by("exercise__theme")

            return render(request, 'qcm/student_list_exercises.html',
                          {'relationships': relationships, 'nb_exercises': nb_exercises ,     })
        
    return redirect('index')



def ajax_list_exercises_by_level(request):
    """ Envoie la liste des exercice pour un seul niveau """
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    level_id =  int(request.POST.get("level_id"))  
 
    level = Level.objects.get(pk=level_id)
    exercises = Exercise.objects.filter(level_id = level_id , supportfile__is_title=0).order_by("theme","knowledge__waiting","knowledge","supportfile__ranking")
 
    data = {}
    data['html'] = render_to_string('qcm/ajax_list_exercises_by_level.html', { 'exercises': exercises  , "teacher" : teacher , "level_id" : level_id })
 
    return JsonResponse(data)





def ajax_list_exercises_by_level_and_theme(request):
    """ Envoie la liste des exercice pour un seul niveau """
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    level_id =  int(request.POST.get("level_id",0))  
    theme_ids =  request.POST.getlist("theme_id")

    subject_id =  request.POST.get("subject_id",None)
    level = Level.objects.get(pk=level_id)

    try : 
        test  = theme_ids[0]
        exercises = Exercise.objects.filter(level_id = level_id , theme_id__in= theme_ids ,  supportfile__is_title=0).order_by("theme","knowledge__waiting","knowledge","supportfile__ranking")
    except :
        if subject_id :
            exercises = Exercise.objects.filter(level_id = level_id , theme__subject_id = subject_id,  supportfile__is_title=0).order_by("theme","knowledge__waiting","knowledge","supportfile__ranking")
        else :
            exercises = Exercise.objects.filter(level_id = level_id , supportfile__is_title=0).order_by("theme","knowledge__waiting","knowledge","supportfile__ranking")
 
    data= {}
    data['html'] = render_to_string('qcm/ajax_list_exercises_by_level.html', { 'exercises': exercises  , "teacher" : teacher , "level_id" : level_id })
 
    return JsonResponse(data)





@user_passes_test(user_is_superuser)
def admin_list_associations(request,id):
    level = Level.objects.get(pk = id)
    user = request.user

    teacher  = Teacher.objects.get(user=user)
    subjects = teacher.subjects.all()
    exercises = level.exercises.filter(theme__subject__in=subjects,supportfile__is_title=0).order_by("theme","knowledge__waiting","knowledge","ranking")

    return render(request, 'qcm/list_associations.html', {'exercises': exercises, 'teacher': teacher , 'parcours': None ,   'level' : level   })
 



@user_passes_test(user_is_superuser)
def admin_list_associations_ebep(request,id):
    level = Level.objects.get(pk = id)
    user = request.user

    teacher  = Teacher.objects.get(user=user)
    subjects = teacher.subjects.all()
    exercises = level.exercises.filter(theme__subject__in=subjects,supportfile__is_title=0).order_by("theme","knowledge__waiting","knowledge","ranking")

    return render(request, 'qcm/list_associations_ebep.html', {'exercises': exercises, 'teacher': teacher , 'parcours': None,   'level' : level  })
 



@user_passes_test(user_is_superuser)
def gestion_supportfiles(request):
  
    lvls = []
    q_levels = Level.objects.all()
    for level in q_levels :
        query_lk = level.knowledges.all()

        nbk = query_lk.count() # nombre de savoir faire listés sur le niveau
        nbe = level.exercises.filter(supportfile__is_title=0).count() # nombre d'exercices sur le niveau
        m = level.exercises.filter(knowledge__in = query_lk).count()
        nb = nbk - m
        lvls.append({ 'name' : level.name , 'nbknowlegde': nbk , 'exotot' : nbe , 'notexo' : nb }) 

    return render(request, 'qcm/gestion_supportfiles.html', {'lvls': lvls, 'parcours': None, 'relationships' : [] , 'communications' : [] })



@user_passes_test(user_is_superuser)
def ajax_update_association(request):
    data = {} 
    code = request.POST.get('code')
    exercise_id = int(request.POST.get('exercise_id'))
    action = request.POST.get('action')


    if action == "create" :
        supportfile = Supportfile.objects.get(code=code)
        try :
            knowledge = Knowledge.objects.get(pk=exercise_id)
            exercise = Exercise.objects.create(knowledge= knowledge, level= knowledge.level,theme= knowledge.theme,supportfile_id= supportfile.id)
            data['error'] = ""
        except :
            data['error'] = "Code incorrect"
        data['html'] = render_to_string('qcm/ajax_create_association.html', {  'exercise' : exercise ,  })

    elif action == "update" : 
        try :
            supportfile = Supportfile.objects.get(code=code)
            exercise_id = int(request.POST.get('exercise_id'))
            exercise = Exercise.objects.get(pk=exercise_id)

            Exercise.objects.filter(pk=exercise_id).update(supportfile= supportfile)
            data['error'] = ""
        except :
            data['error'] = "Code incorrect"
        data['html'] = render_to_string('qcm/ajax_association.html', {  'exercise' : exercise ,  })

    elif action == "delete" :
        exercise = Exercise.objects.get(pk=exercise_id) 
        exercise.delete()
    return JsonResponse(data)


@user_passes_test(user_is_creator)
def admin_list_supportfiles(request,id):
    user = request.user
    teacher = Teacher.objects.get(user=user)
    if user.is_superuser or user.is_extra :  # admin and more

        teacher = Teacher.objects.get(user=user)
        level = Level.objects.get(pk=id)

        waitings = level.waitings.filter(theme__subject__in= teacher.subjects.all()).order_by("theme__subject" , "theme")
 
    return render(request, 'qcm/list_supportfiles.html', { 'waitings': waitings, 'teacher':teacher , 'level':level , 'relationships' : [] , 'communications' : [] , 'parcours' :  None })


@parcours_exists
def parcours_exercises(request,id):
    user = request.user
    parcours = Parcours.objects.get(pk=id)
    student = Student.objects.get(user=user)

    relationships = Relationship.objects.filter(parcours=parcours,is_publish=1).order_by("exercise__theme")

    return render(request, 'qcm/student_list_exercises.html', {'parcours': parcours  , 'relationships': relationships, })


def exercises_level(request, id):
    teacher = request.user.teacher
    level = Level.objects.get(pk=id)    
    exercises = Exercise.objects.filter(level=level,supportfile__is_title=0).order_by("theme","knowledge__waiting","knowledge","ranking")
    themes =  level.themes.all()
    form = AuthenticationForm() 
    u_form = UserForm()
    t_form = TeacherForm()
    s_form = StudentForm()
    return render(request, 'list_exercises.html', {'exercises': exercises, 'level':level , 'themes':themes , 'teacher' : teacher , 'form':form , 'u_form':u_form , 's_form': s_form , 't_form': t_form , 'levels' : [] })


def exercises_level_subject(request, id, subject_id):

    exercises = Exercise.objects.filter(level_id=id,supportfile__is_title=0,theme__subject_id = subject_id).order_by("theme","knowledge__waiting","knowledge","ranking")
    level = Level.objects.get(pk=id)
    themes =  level.themes.all()
    form = AuthenticationForm() 
    u_form = UserForm()
    t_form = TeacherForm()
    s_form = StudentForm()
    return render(request, 'list_exercises.html', {'exercises': exercises, 'level':level , 'themes':themes ,  'form':form , 'u_form':u_form , 's_form': s_form , 't_form': t_form , 'levels' : [] })

############################################################################################################################################################################
########################## Début de gestion des supportfiles 
############################################################################################################################################################################

def supportfile_creator(request,idq=0) :
    if request.user.is_superuser :
        qtypes = Qtype.objects.filter(is_online=1).order_by("ranking")
    else :
        qtypes = Qtype.objects.filter(is_online=1).exclude(pk=100).order_by("ranking")
    context = {  'qtypes': qtypes,  }

    return render(request, 'qcm/supportfile_creator.html', context)


@user_passes_test(user_is_creator)
def create_supportfile_knowledge(request,id):
    knowledge = Knowledge.objects.get(id = id)
    request.session['exo_knowledge_id'] = knowledge.id
    qtypes = Qtype.objects.filter(is_online=1).order_by("ranking")
    context = {  'qtypes': qtypes, 'knowledge': knowledge, }
    return render(request, 'qcm/supportfile_creator.html', context)



def insert_form(looper,fa,dico):

    subfields = ('answer','imageanswer','label','is_correct','retroaction')
    nd={}
    liste = list()
    for loop in range(int(dico['subloop'+str(looper)][0])) :
        d={key:value for key,value in dico.items() if "supportsubchoices-"+str(looper)+"_"+str(loop) in key}
         


def create_supportfile(request,qtype,ids):
    """ Création d'un supportfile"""
    code = str(uuid.uuid4())[:8]
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    if request.user.is_superuser :
        qtypes = Qtype.objects.filter(is_online=1).order_by("ranking")
    else :
        qtypes = Qtype.objects.filter(is_online=1).exclude(pk=100).order_by("ranking")

    qt = Qtype.objects.get(pk=qtype)
    extra = qt.extra

    knowledge_id = request.session.get('exo_knowledge_id',None)
    knowledge = None
    if knowledge_id :
        knowledge = Knowledge.objects.get(pk=knowledge_id)    

    form       = SupportfileForm(request.POST or None,request.FILES or None,teacher = teacher)
    form_c     = CriterionOnlyForm(teacher = teacher) 
    subjects   = teacher.subjects.all()
    formSetvar = inlineformset_factory( Supportfile , Supportvariable , fields=('name','is_integer','is_notnull','minimum','maximum', 'words') , extra=0  )

    today      = time_zone_user(request.user)
    sacado_asso, sacado_is_active = is_sacado_asso(teacher.user,today)

    if qt.is_sub == 0 : 
        formSet  = inlineformset_factory( Supportfile , Supportchoice , fields=('answer','imageanswer','answerbis','imageanswerbis','is_correct','retroaction')  , extra =  extra)
    else :
        formSet = formSetNested()

    if request.method == "POST" : 
        if form.is_valid() :
            nf = form.save(commit=False)
            nf.teacher = teacher
            if nf.qtype == 9    : nf.nb_pseudo  = 1
            elif nf.qtype == 19 : nf.is_python  = True
            elif nf.qtype == 100: nf.is_ggbfile = True
            elif nf.is_scratch  : nf.is_image   = True
            nf.code = code
            nf.is_share = 0
            if teacher.user.is_superuser : nf.is_share = 1
            nf.author = teacher
            if nf.imagefile != "" :  
                nf.imagefile = 'qtype_img/underlayer.png'
            if nf.is_ggbfile :
                nf.annoncement = unescape_html(cleanhtml(nf.annoncement)) 

            try :
                sending_to_teachers(teacher , nf.level,nf.theme.subject,"Un nouvel exercice")   
            except :
                pass   
                          
            nf.save()
            form.save_m2m()
            Exercise.objects.create(supportfile = nf, knowledge = nf.knowledge, level = nf.level, theme = nf.theme )

            if qt.is_alea :
                form_var = formSetvar(request.POST or None,  instance = nf) 
                for form_v in form_var :
                    if form_v.is_valid():
                        var = form_v.save()
                    else :
                        print(form_v.errors)

            if qtype < 19 :
                if qt.is_sub == 0  :
                    form_ans = formSet(request.POST or None,  request.FILES or None, instance = nf)
                    for form_answer in form_ans :
                        if form_answer.is_valid():
                            form_answer.save()
 
                else :
                    formset = formSetNested(request.POST or None,  request.FILES or None, instance=nf)
                    if formset.is_valid():
                        formset.save()
                    else :
                        print( formset.errors )


            try :
                msg = "Bonjour l'équipe,\n\n Un exercice vient d'être posté.\n\nPour le visualiser : https://sacado.xyz/qcm/show_all_type_exercise/"+nf.id+"/ .\n\nCet exercice n'est pas encore mutualisé.\n\nCeci est un mail automatique. Merci de ne pas répondre."
                if user.email :
                    send_mail('SACADO : Exercice Perso', msg ,settings.DEFAULT_FROM_EMAIL,['sacado.asso@gmail.com', ])
            except :
                pass
            return redirect('my_own_exercises' )
        else :
            print(form.errors)


    template = "qcm/qtype/"+qt.custom+".html"
    context = { 'form_c' : form_c, 'sacado_asso' : sacado_asso , 'form_var' : formSetvar ,  'form_ans' : formSet
     ,  'qt' : qt , 'qtype' : qtype , 'form': form, 'subjects' : subjects , 
                'teacher': teacher,  'knowledge': knowledge,  'supportfile': None,  'form_template' : False ,  'parcours': None, 'qtypes': qtypes,  }
    
    if qt.is_sub > 0 :
        form_sub_ans = formSubSet()
        context.update(  { 'form_sub_ans' : form_sub_ans,  } )


    return render(request, template , context)




@user_passes_test(user_is_creator)
def update_supportfile(request, id, redirection=0):

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    subjects = teacher.subjects.all()
    supportfile   = Supportfile.objects.get(id=id)
    form_template = "qcm/qtype/"+Qtype.objects.get(pk=supportfile.qtype).custom+".html"

    knowledge = supportfile.knowledge
    supportfile_form = UpdateSupportfileForm(request.POST or None, request.FILES or None, instance=supportfile, knowledge = knowledge)
    levels = Level.objects.all()
    supportfiles = Supportfile.objects.filter(is_title=0).order_by("level","theme","knowledge__waiting","knowledge","ranking")
    knowledges = Knowledge.objects.all().order_by("level")


    form_c     = CriterionOnlyForm(request.POST or None, request.FILES or None , teacher = teacher,instance = supportfile) 
    formSetvar = inlineformset_factory( Supportfile , Supportvariable , fields=('name','is_integer','is_notnull','minimum','maximum', 'words') , extra=0 )
    form_var   = formSetvar(request.POST or None,  instance = supportfile) 
    qtype      = supportfile.qtype

    qto        = Qtype.objects.get(pk=qtype)

    if qto.is_sub == 0 : 
        formSet  = inlineformset_factory( Supportfile , Supportchoice , fields=('answer','imageanswer','answerbis','imageanswerbis','is_correct','retroaction')  , extra =  0)
        form_ans = formSet(request.POST or None, request.FILES or None , instance = supportfile)
    else :
        form_ans = formSetUpdateNested(instance = supportfile)
    

    if request.method == "POST" :

        if supportfile_form.is_valid() :
            nf = supportfile_form.save(commit=False)
            nf.code = supportfile.code
            if nf.is_ggbfile :
                nf.annoncement = unescape_html(cleanhtml(nf.annoncement)) 
            nf.teacher = teacher
            if nf.qtype == 9     : nf.nb_pseudo   = 1
            elif nf.qtype == 19  : nf.is_python  = True            
            elif nf.qtype == 100 : nf.is_ggbfile = True
            elif nf.is_scratch   : nf.is_image   = True

            nf.save()
            supportfile_form.save_m2m()  
                       
            qtype  = nf.qtype
             
            is_sub = qto.is_sub
            extra  = qto.extra
            if qto.is_alea :
                for form_v in form_var :
                    if form_v.is_valid():
                        var = form_v.save()
                    else :
                        print(form_v.errors)

            formSet  = inlineformset_factory( Supportfile , Supportchoice , fields=('answer','imageanswer','answerbis','imageanswerbis','is_correct','retroaction')  , extra=extra)
            form_ans = formSet(request.POST or None,  request.FILES or None, instance = nf)

            if qtype < 19 :
                if qto.is_sub == 0  :
                    form_ans = formSet(request.POST or None,  request.FILES or None, instance = nf)
                    for form_answer in form_ans :
                        if form_answer.is_valid():
                            form_answer.save()

                else :
                    formset = formSetNested(request.POST or None,  request.FILES or None, instance=nf)
                    if formset.is_valid():
                        formset.save()
            try :
                msg = "Bonjour l'équipe,\n\n Un exercice vient d'être modifié.\n\nPour le visualiser : https://sacado.xyz/qcm/show_this_supportfile/"+nf.id+"/ .\n\nCeci est un mail automatique. Merci de ne pas répondre."
                if user.email :
                    send_mail('SACADO : Exercice Perso', msg ,settings.DEFAULT_FROM_EMAIL,['sacado.asso@gmail.com', ])
            except :
                pass

            messages.success(request, "L'exercice a été modifié avec succès !")
            if request.session.get('my_own_exercises') :
                return redirect('my_own_exercises')
            else :
                return redirect('admin_supportfiles', supportfile.level.id)

 
    context = {'form': supportfile_form,  'form_ans' : form_ans, 'form_c' : form_c,  'form_var' : form_var , 'qtype' : qtype  , 'teacher': teacher, 'supportfile': supportfile, 
                'knowledges': knowledges,  'subjects' : subjects , 'qt' : qto ,
               'supportfiles': supportfiles, 'levels': levels,   'communications' : [] , 'knowledge' : knowledge ,    }


    return render(request, form_template , context)



@user_passes_test(user_is_superuser)
def delete_supportfile(request, id):
    supportfile = Supportfile.objects.get(id=id)
    level_id = supportfile.level.id

    if request.user.is_superuser or supportfile.author.user.id == request.user.id :
        
        if Relationship.objects.filter(exercise__supportfile=supportfile).count() == 0:
            supportfile.delete()
            messages.success(request, "Le support a été supprimé avec succès !")
        else:
            messages.error(request, " Des parcours utilisent cet exercice. Il n'est pas possible de le supprimer.")

    my_own_exercises = request.session.get('my_own_exercises', None)

    if request.user.is_superuser and not my_own_exercises:
        return redirect('admin_supportfiles', level_id ) 
    else :
        return redirect('my_own_exercises') 


@user_passes_test(user_is_testeur)
def show_this_supportfile(request, id):


    if request.user.is_teacher:
        teacher = Teacher.objects.get(user=request.user)
        parcours = Parcours.objects.filter(teacher=teacher,is_trash=0)
    else :
        parcours = None


    user = request.user    
    form_reporting = DocumentReportForm(request.POST or None )
 
    supportfile = Supportfile.objects.get(id=id)
    request.session['level_id'] = supportfile.level.id
    start_time = time.time()
    context = {'supportfile': supportfile, 'start_time': start_time, 'communications' : [] ,  'parcours': parcours , "user" :  user , "form_reporting" :  form_reporting , }

    if supportfile.is_ggbfile :
        url = "qcm/show_supportfile.html" 
    elif supportfile.is_python :
        url = "basthon/index_supportfile.html"
    else :
        wForm = WrittenanswerbystudentForm(request.POST or None, request.FILES or None )
        context = {'exercise': exercise, 'start_time': start_time, 'parcours': parcours , 'communications' : [] , 'relationships' : [] , 'today' : today , 'wForm' : wForm }
        url = "qcm/show_teacher_writing.html"  

    return render(request, url , context)



@login_required(login_url= 'index') 
def my_own_exercises(request): # Modification d'un exercice non autocorrigé dans un parcours

    request.session["tdb"] = "Documents"  
    request.session["subtdb"] = "Exercises"

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    exercises = Exercise.objects.filter(supportfile__author=teacher,supportfile__qtype__lt=100).order_by('-id')[:15]

    subjects = teacher.subjects.all()
    levels   = teacher.levels.all()

    request.session['my_own_exercises'] = True
    try :
        del request.session['exo_knowledge_id']
    except :
        pass

    if request.user.is_superuser :
        qtypes = Qtype.objects.order_by("ranking")
    else :
        qtypes = Qtype.objects.filter(is_online=1).exclude(pk=100).order_by("ranking")


    context = { 'qtypes': qtypes, 'exercises' : exercises, 'subjects' : subjects, 'levels' : levels , 'is_mathJax' : False ,  'teacher' : teacher ,  }
    return render(request, 'qcm/list_my_own_exercises.html', context)



@csrf_exempt
def ajax_sort_supportfile(request):
    """ tri des supportfiles""" 
    exercise_ids = request.POST.get("valeurs")
    exercise_tab = exercise_ids.split("-") 
    for i in range(len(exercise_tab)-1):
        Supportfile.objects.filter( pk = exercise_tab[i]).update(ranking = i)
    data = {}
    return JsonResponse(data) 
############################################################################################################################################################################
########################## Def des custom files amener à disparaitre 
############################################################################################################################################################################
@login_required(login_url= 'index') 
def parcours_create_custom_exercise(request,id,typ): #Création d'un exercice non autocorrigé dans un parcours

    parcours = Parcours.objects.get(pk=id)
    teacher = Teacher.objects.get(user= request.user)
    stage = get_stage(teacher.user)


    if not teacher_has_permisson_to_parcourses(request,teacher,parcours) :
        return redirect('index')

    ceForm = CustomexerciseForm(request.POST or None, request.FILES or None , teacher = teacher , parcours = parcours) 
    form_c = CriterionForm(request.POST or None, request.FILES or None , teacher = teacher , parcours = parcours) 

    if request.method == "POST" :
        if ceForm.is_valid() :
            nf = ceForm.save(commit=False)
            nf.teacher = teacher
            if nf.is_scratch :
                nf.is_image = True
            nf.save()
            ceForm.save_m2m()
            nf.parcourses.add(parcours)  
            nf.students.set( parcours.students.all() )     
        else :
            print(ceForm.errors)
        return redirect('show_parcours', 0 , parcours.id  )
 
    context = {'parcours': parcours,  'teacher': teacher, 'stage' : stage ,  'communications' : [] , 'form' : ceForm , 'form_c':form_c , 'customexercise' : False }

    return render(request, 'qcm/form_exercise_custom.html', context)






@login_required(login_url= 'index') 
def parcours_update_custom_exercise(request,idcc,id): # Modification d'un exercice non autocorrigé dans un parcours

    custom = Customexercise.objects.get(pk=idcc)

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    stage   = get_stage(request.user)

    if id == 0 :

        if not authorizing_access(teacher, custom ,True):
            messages.error(request, "  !!!  Redirection automatique  !!! Violation d'accès. Contacter SACADO...")
            return redirect('index')

        ceForm = CustomexerciseNPForm(request.POST or None, request.FILES or None , teacher = teacher ,  custom = custom, instance = custom ) 
        form_c = CriterionOnlyForm(request.POST or None, request.FILES or None , teacher = teacher )

        if request.method == "POST" :
            if ceForm.is_valid() :
                nf = ceForm.save(commit=False)
                nf.teacher = teacher
                if nf.is_scratch :
                    nf.is_image = True
                nf.save()
                ceForm.save_m2m()
            else :
                print(ceForm.errors)
            return redirect('my_own_exercises' )
     
        context = {  'teacher': teacher, 'stage' : stage ,  'communications' : [] , 'form' : ceForm , 'form_c':form_c , 'customexercise' : custom ,'parcours': None, }

    else :
 
        parcours = Parcours.objects.get(pk=id)
        if not teacher_has_permisson_to_parcourses(request,teacher,parcours) :
            messages.error(request, "  !!!  Redirection automatique  !!! Violation d'accès.")
            return redirect('index')

        ceForm = CustomexerciseForm(request.POST or None, request.FILES or None , teacher = teacher , parcours = parcours, instance = custom ) 

        if request.method == "POST" :
            if ceForm.is_valid() :
                nf = ceForm.save(commit=False)
                nf.teacher = teacher
                if nf.is_scratch :
                    nf.is_image = True
                nf.save()
                ceForm.save_m2m()
                nf.parcourses.add(parcours)
                nf.students.set( parcours.students.all() )  
            else :
                print(ceForm.errors)
            return redirect('show_parcours', 0, parcours.id )
     
        context = {'parcours': parcours,  'teacher': teacher, 'stage' : stage ,  'communications' : [] , 'form' : ceForm , 'customexercise' : custom }

    return render(request, 'qcm/form_exercise_custom.html', context)




@login_required(login_url= 'index') 
def exercise_custom_show_shared(request): # Modification d'un exercice non autocorrigé dans un parcours
    
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    customexercises = set()
    subjects = teacher.subjects.all()    
    levels   = teacher.levels.all()
    for subject in subjects :
        for level in levels :
            customexercises.update(subject.customexercises.filter(is_share=1,levels=level))

    context = { 'customexercises' : customexercises, 'subjects' : subjects, 'levels' : levels , 'is_mine' : False } 

    return render(request, 'qcm/list_my_custom_exercises.html', context)




# def exercise_custom_show_shared(request):
    
#     user = request.user
#     if user.is_teacher:  # teacher
#         teacher = Teacher.objects.get(user=user) 
#         customexercises = Customexercise.objects.filter(is_share = 1).exclude(teacher = teacher)
#         return render(request, 'qcm/list_custom_exercises.html', {  'teacher': teacher , 'customexercises':customexercises, 'parcours': None, })
#     else :
#         return redirect('index')   
 

def customexercise_shared_inside_parcours(request,idp):
    parcours = Parcours.objects.get(pk=idp)
    user = request.user
    if user.is_teacher:  # teacher
        teacher = Teacher.objects.get(user=user) 
        customexercises = Customexercise.objects.filter(is_share = 1).exclude(parcourses = parcours)
        return render(request, 'qcm/list_custom_exercises.html', {  'teacher': teacher , 'customexercises':customexercises, 'parcours': parcours,   })
    else :
        return redirect('index')   



############################################################################################################################################################################
########################## Fin de gestion des supportfiles 
############################################################################################################################################################################
@user_passes_test(user_is_creator)
def create_exercise(request, supportfile_id):
 
    knowledges = Knowledge.objects.all().select_related('level').order_by("level")
    supportfile = Supportfile.objects.get(id=supportfile_id)

    if request.user.is_superuser or user_is_creator : 
        if request.method == "POST":
            knowledges_id = request.POST.getlist("choice_knowledges")
            knowledges_id_tab = []
            for k_id in knowledges_id:
                knowledges_id_tab.append(int(k_id))

            # les exercices déjà référencés sur le même support par leur knowledge
            exercises = Exercise.objects.filter(supportfile=supportfile)
            exercises_Kno_tab = []
            for exercise in exercises:
                if exercise.knowledge.id not in exercises_Kno_tab:
                    exercises_Kno_tab.append(int(exercise.knowledge.id))

            delete_list = [value for value in exercises_Kno_tab if value not in knowledges_id_tab]

            for knowledge_id in knowledges_id_tab:
                knowledge = Knowledge.objects.get(pk=knowledge_id)
                exercise, result = Exercise.objects.get_or_create(supportfile=supportfile, knowledge=knowledge,
                                                                  level=knowledge.level, theme=knowledge.theme)

            for kn_id in delete_list:
                knowledge = Knowledge.objects.get(pk=kn_id)
                exercise = Exercise.objects.get(supportfile=supportfile, knowledge=knowledge)

                if Relationship.objects.filter(exercise=exercise).count() == 0:
                    exercise.delete()  # efface les existants sur le niveau sélectionné

            return redirect('admin_supportfiles' , supportfile.level.id )

    context = {  'knowledges': knowledges, 'supportfile': supportfile , 'parcours': None, 'communications' : [] , 'communications' : [] , 'relationships' : []  }

    return render(request, 'qcm/form_exercise.html', context)



@user_passes_test(user_is_creator)
def ajax_load_modal(request):
    """ crée la modale pour changer les savoir faire"""

    exercise_id  = request.POST.get('exercise_id', None)
    exercise = Exercise.objects.get(pk = exercise_id)
    waitings = exercise.level.waitings.filter(level_id=exercise.level.id)
    k_id = exercise.knowledge.id

    data = {}
 
    data['listing_w'] = render_to_string('qcm/ajax_load_modal.html', { 'waitings': waitings , 'k_id' : k_id , 'exercise' : exercise   })
 
    return JsonResponse(data)


@csrf_exempt
@user_passes_test(user_is_creator)
def change_knowledge(request):

    exercise_id  = request.POST.get('exercise_id', None)
    knowledge_id = request.POST.get('knowledge_id', None)
    exercise = Exercise.objects.get(pk=exercise_id)


    if knowledge_id :
        Exercise.objects.filter(pk=exercise_id).update(knowledge_id = knowledge_id)
 

    return redirect( 'admin_associations', exercise.level.id)


@csrf_exempt
def ajax_sort_exercise_from_admin(request):
    """ tri des exercices""" 
    exercise_ids = request.POST.get("valeurs")
    exercise_tab = exercise_ids.split("-") 

    try :
        for i in range(len(exercise_tab)-1):
            Exercise.objects.filter(pk = exercise_tab[i]).update(ranking = i)
    except :
        pass

    data = {}
    return JsonResponse(data)



def show_exercise(request, id):
    exercise = Exercise.objects.get(id=id)

    request.session['level_id'] = exercise.level.id
    form = AuthenticationForm() 
    u_form = UserForm()
    t_form = TeacherForm()
    s_form = StudentForm()

    context = {'exercise': exercise,   'form': form , 'u_form' : u_form , 's_form' : s_form , 't_form' : t_form , 'levels' : [],   'communications' : [] , 'relationships' : []  }
 
    if exercise.supportfile.is_ggbfile :
        wForm = None
        url = "show_exercise.html" 
    elif exercise.supportfile.is_python :
        url = "basthon/index_shower.html"
        wForm = None
    else :
        wForm = WrittenanswerbystudentForm(request.POST or None, request.FILES or None )
        context = {'exercise': exercise,   'form': form , 'u_form' : u_form , 's_form' : s_form , 's_form' : s_form , 't_form' : t_form ,  'wForm' : wForm , 'levels' : [],   'communications' : [] , 'relationships' : []  }
        url = "qcm/show_teacher_writing.html"  

    return render(request, url , context)



def show_this_exercise(request, id):

    exercise  = Exercise.objects.get(pk = id)
    ranking   = exercise.level.ranking 
    level_inf = ranking - 1
    level_sup = ranking + 1

    if request.user.is_authenticated:
        today = time_zone_user(request.user)
        if request.user.is_teacher:
            teacher = Teacher.objects.get(user=request.user)
            parcours = Parcours.objects.filter(Q(teacher=teacher)|Q(coteachers=teacher), level__lte = level_sup, level__gte = level_inf   ,is_trash=0)
        elif request.user.is_student :
            student = Student.objects.get(user=request.user)
            parcours = None
        else :
            student = None
            parcours = None
    else :
        student = None
        parcours = None        
        today = timezone.now()

    start_time = time.time()

    if exercise.supportfile.is_ggbfile :
        wForm = None
        url = "qcm/show_exercise.html" 
    elif exercise.supportfile.is_python :
        url = "basthon/index_teacher.html"
        wForm = None
    else :
        wForm = WrittenanswerbystudentForm(request.POST or None, request.FILES or None )
        url = "qcm/show_teacher_writing.html" 


    context = {'exercise': exercise, 'start_time': start_time, 'parcours': parcours , 'communications' : [] , 'relationships' : [] , 'today' : today , 'wForm' : wForm }

    return render(request, url, context)



def show_this_index_exercise(request, id):

    exercise  = Exercise.objects.get(pk = id)



    if exercise.supportfile.is_ggbfile :
        wForm = None
        url = "qcm/show_index_exercise.html" 
    elif exercise.supportfile.is_python :
        url = "basthon/index_teacher.html"
        wForm = None
    else :
        wForm = WrittenanswerbystudentForm(request.POST or None, request.FILES or None )
        url = "qcm/show_teacher_writing.html" 


    context = {'exercise': exercise, }

    return render(request, url, context)



def show_this_exercise_test(request, id):

    exercise  = Exercise.objects.get(pk = id)
    ranking   = exercise.level.ranking 
    level_inf = ranking - 1
    level_sup = ranking + 1

    if request.user.is_authenticated:
        today = time_zone_user(request.user)
        if request.user.is_teacher:
            teacher = Teacher.objects.get(user=request.user)
            parcours = Parcours.objects.filter(Q(teacher=teacher)|Q(coteachers=teacher), level__lte = level_sup, level__gte = level_inf   ,is_trash=0)
        elif request.user.is_student :
            student = Student.objects.get(user=request.user)
            parcours = None
        else :
            student = None
            parcours = None
    else :
        student = None
        parcours = None        
        today = timezone.now()

    start_time = time.time()

    if exercise.supportfile.is_ggbfile :
        wForm = None
        url = "qcm/show_exercise_test.html" 
    elif exercise.supportfile.is_python :
        url = "basthon/index_teacher.html"
        wForm = None
    else :
        wForm = WrittenanswerbystudentForm(request.POST or None, request.FILES or None )
        url = "qcm/show_teacher_writing.html"

    file = open("/var/www/sacado/ressources/ggbfilesBase64"+str(exercise.supportfile.ggbfile)[8:]+"b64","r")
    source = file.read()
    file.close()

    context = { 'source_64' :  source  ,  'exercise': exercise, 'start_time': start_time, 'parcours': parcours , 'communications' : [] , 'relationships' : [] , 'today' : today , 'wForm' : wForm }

    return render(request, url, context)








def show_all_type_exercise(request,ids): # vue coté prof de l'exercice autocorrigé  du customexercise
    """vue de tous les types d'exercices depuis un supportfile """
    supportfile = Supportfile.objects.get(pk = ids)
    today = timezone.now()
    #1 , 2 , 12 n'utilisent pas ces conditions
    loops = [0]*supportfile.situation
    context = { 'supportfile' : supportfile, 'today' : today , 'loops' : loops,  'student' : None, 'only_show' : False}

    qtype_custom = Qtype.objects.get(pk=supportfile.qtype).custom
 
    if supportfile.is_python :
        url = "basthon/index_supportfile.html" 
    else :
        if supportfile.qtype == 20  :
            wForm = WrittenanswerbystudentForm(request.POST or None, request.FILES or None ) 
            w_a = False
            context.update ( { 'form' : wForm , 'w_a' : w_a } ) 
        else :
            context.update ( define_all_types( supportfile.situation , supportfile) ) 
        url = "qcm/qtype/"+qtype_custom+"_ans.html" 

    return render(request, url , context)



######################################################################################################################################################################
#########################################       Gestion des Exercices coté élèves      ###############################################################################
######################################################################################################################################################################
def get_list_values_if_variables_alea(n, supportfile):
    """ Renvoie une liste de liste des variables de chaque situation 
        Chaque variable a un nom, une variable et un loop qui définit la situation actuelle parmi les situations proposées"""
    supportvariables = supportfile.supportvariables.all()
    if supportvariables.count():
        liste_v = list() 
        for i in  range(n) :
            liste = []
            for variable in supportvariables :
                dico = dict() 
                number , is_integer , mini , maxi = 0 , variable.is_integer , variable.minimum , variable.maximum 
                if variable.is_notnull :
                    while number == 0 :
                        if is_integer :
                            number = random.randint(mini ,  maxi )
                        else :
                            number = round(mini + random.random()*(maxi-mini),2)
                else :
                    if is_integer :
                        number = random.randint(mini ,  maxi )
                    else :
                        number = round(mini + random.random()*(maxi-mini),2)
                dico['name'] = variable.name                    
                dico['val']  = number
                dico['loop'] = i+1
                liste.append(dico)
            liste_v.append(liste)
    else :
        liste_v = None
    return liste_v

def replace_bloc(texte,vars_list,i):
    """remplace les variables littérales par leur valeur et calcule éventuellement la partie à calculer.
    i représente le ième loop """
    if vars_list :
        tabs = texte.split('$')
        blocs = [ tab for tab in tabs]
        new = ""
        j = 0
        for bloc in blocs :
            varias = vars_list[i]
            if bloc != "" and j%2==1:
                for v in varias:
                    bloc = bloc.replace('{'+v['name']+'}',str(v['val']) )
                new += '$'+bloc+'$'
            else :
                new += bloc
            j += 1
    else :
        new = str(texte)

    if new and '?!' in new :
        renew = ""
        calcs = new.split('?!')
        k=0
        for calc in calcs :
            if calcs != "" and k%2==1:
                calc = eval(calc) 
            k+=1
            renew += str(calc)
    else :
        renew = new
    return renew


def alea_annoncements(n,supportfile) :

    vars_list = get_list_values_if_variables_alea(n,supportfile)

    annoncements , corrections , choices , shufflechoices , shufflesubchoices = list() , list() , list() , list() , list()

    s_choices = supportfile.supportchoices.all()
    nb_pseudo_support = supportfile.nb_pseudo
 

    if nb_pseudo_support: 
        su_choices = list(s_choices)
        random.shuffle(su_choices)
        s_choices = su_choices[0:nb_pseudo_support]

    if supportfile.qtype == 1 or supportfile.qtype == 13 or supportfile.qtype == 15 :
        if nb_pseudo_support : n = nb_pseudo_support
        else : n = s_choices.count()

    for i in range (n) : # n = nombre de loops

        if 0 < nb_pseudo_support < n : s_choices = s_choices*(n//nb_pseudo_support + 1)

        enonce  = supportfile.annoncement
        corrige = supportfile.correction
        new = replace_bloc(enonce,vars_list,i)
        annoncements.append(new)

        # if 'input' in enonce :
        #     if vars_list :
        #         new = replace_bloc(enonce,vars_list,i)
        #         annoncements.append(new)
        #     else :
        #        annoncements.append(enonce) 
        # else :
        #     annoncements.append(enonce)

        if '?!' in corrige :
            if vars_list :
                cor = replace_bloc(corrige,vars_list,i)
            corrections.append(cor)
        else :
            corrections.append(corrige)

        
        if supportfile.qtype<3 and vars_list : 
            this_choice = s_choices[i]
            new    = replace_bloc(this_choice.answer,vars_list,i)
            newbis = replace_bloc(this_choice.answerbis,vars_list,i)
            data = { 'id' : this_choice.id , 'answer' : new , 'answerbis' : newbis ,'imageanswer' : this_choice.imageanswer ,'imageanswerbis' : this_choice.imageanswerbis , 'retroaction' : this_choice.retroaction , 'is_correct' : this_choice.is_correct   } 
            shufflechoices.append(data)

        elif supportfile.qtype<3 : 
            this_choice = s_choices[i]
            new    = this_choice.answer 
            newbis = this_choice.answerbis
            data = { 'id' : this_choice.id , 'answer' : new , 'answerbis' : newbis ,'imageanswer' : this_choice.imageanswer ,'imageanswerbis' : this_choice.imageanswerbis , 'retroaction' : this_choice.retroaction , 'is_correct' : this_choice.is_correct   } 
            shufflechoices.append(data)

        elif 2<supportfile.qtype<5  :
            this_liste = list()
            for this_choice in s_choices : 
                new    = replace_bloc(this_choice.answer,vars_list,i)
                newbis = replace_bloc(this_choice.answerbis,vars_list,i)
                retroaction = replace_bloc(this_choice.retroaction,vars_list,i)
                data = { 'id' : this_choice.id , 'answer' : new , 'answerbis' : newbis ,'imageanswer' : this_choice.imageanswer ,'imageanswerbis' : this_choice.imageanswerbis , 'retroaction' : retroaction , 'is_correct' : this_choice.is_correct   } 
                this_liste.append(data)
            random.shuffle(this_liste)
            shufflechoices.append(this_liste)

        elif  supportfile.qtype == 5 :
            this_liste = list()
            for this_choice in s_choices : 
                new    = replace_bloc(this_choice.answer,vars_list,i)
                newbis = replace_bloc(this_choice.answerbis,vars_list,i)
                retroaction = replace_bloc(this_choice.retroaction,vars_list,i)
                data = { 'id' : this_choice.id , 'answer' : new , 'answerbis' : newbis ,'imageanswer' : this_choice.imageanswer ,'imageanswerbis' : this_choice.imageanswerbis , 'retroaction' : retroaction , 'is_correct' : this_choice.is_correct   } 
                this_liste.append(data)
            choices.append(this_liste) 
            random.shuffle(this_liste)
            shufflechoices.append(this_liste)

        elif  supportfile.qtype == 6 or supportfile.qtype == 8  or supportfile.qtype == 14 :


            this_liste = list()
            this_sub_liste = list()
            for this_choice in s_choices : 
                new    = replace_bloc(this_choice.answer,vars_list,i)
                newbis = replace_bloc(this_choice.answerbis,vars_list,i)
                retroaction = replace_bloc(this_choice.retroaction,vars_list,i)
                data = { 'id' : this_choice.id , 'answer' : new , 'answerbis' : newbis ,'imageanswer' : this_choice.imageanswer ,'imageanswerbis' : this_choice.imageanswerbis , 'retroaction' : retroaction , 'is_correct' : this_choice.is_correct   } 
                this_liste.append(data)
                this_choices = this_choice.supportsubchoices.all()
                if supportfile.nb_subpseudo :
                    this_sub_choices = list(this_choices)
                    random.shuffle(this_sub_choices)
                    this_choices = this_sub_choices[0:supportfile.nb_subpseudo]  
                for subchoice in this_choices:
                    new    = replace_bloc(subchoice.answer,vars_list,i)
                    retroaction = replace_bloc(subchoice.retroaction,vars_list,i)
                    label = replace_bloc(subchoice.label,vars_list,i)
                    subdata = { 'id' : subchoice.id , 'answer' : new , 'imageanswer' : subchoice.imageanswer   , 'retroaction' : retroaction , 'label' : label , 'is_correct' : subchoice.is_correct   } 
                    this_sub_liste.append(subdata)
            random.shuffle(this_liste)
            shufflechoices.append(this_liste)
            random.shuffle(this_sub_liste)
            shufflesubchoices.append(this_sub_liste)

        elif  supportfile.qtype == 7 :
            this_choice = s_choices[i]
            mystr = this_choice.answer
            mystr = mystr.replace('<p>','')
            mystr = mystr.replace('</p>','')
            mystr = mystr.replace('<strong>','####')
            mystr = mystr.replace('</strong>','####')
            tab   = mystr.split('####')
            
            my_str = ""
            for i in range(len(tab)) :
                if i%2 == 1:
                    this_word = ''.join(random.sample(tab[i],len(tab[i])))
                    word = this_word
                else :
                    word = "<small>"+tab[i]+'</small>' 
                my_str += word
            data = { 'id' : this_choice.id , 'answer' : my_str  , 'retroaction' : this_choice.retroaction   } 
            shufflechoices.append(data)
            random.shuffle(shufflechoices)
 
        elif  supportfile.qtype == 9 :

            this_choice = s_choices[i]
            words = list()
            mystr = this_choice.answer
            mystr = mystr.replace('<strong>','####')
            mystr = mystr.replace('</strong>','####')
            tab   = mystr.split('####')
            string = ""
            for j in range(len(tab)) :
                if j%2==1:
                    words.append(tab[j])

            choices.append(this_choice)
            shufflechoices.append(words) ## shufflechoices sont la liste des mots

        elif  supportfile.qtype == 13 :

            this_choice = s_choices[i]
            data = { 'id' : this_choice.id , 'answer' : this_choice.answer  , 'retroaction' : this_choice.retroaction   } 
            shufflechoices.append(data)
            random.shuffle(shufflechoices)
      
        elif  supportfile.qtype == 15 :

            this_liste = list()
            this_sub_liste = list()
            loop_choice = s_choices[i]
            this_liste.append(loop_choice)
            subchoices = list(loop_choice.supportsubchoices.all())
            random.shuffle(subchoices)
            if supportfile.nb_subpseudo :
                m = min( supportfile.nb_subpseudo, loop_choice.supportsubchoices.count() )
                subchoices = list(subchoices)[0:m]
            for subchoice in subchoices :
                new    = replace_bloc(subchoice.answer,vars_list,i)
                retroaction = replace_bloc(subchoice.retroaction,vars_list,i)
                label = replace_bloc(subchoice.label,vars_list,i)
                subdata = { 'id' : subchoice.id , 'answer' : new , 'imageanswer' : subchoice.imageanswer   , 'retroaction' : retroaction , 'label' : label , 'is_correct' : subchoice.is_correct   } 
                this_sub_liste.append(subdata)
            random.shuffle(this_liste)
            shufflechoices.append(this_liste)
            random.shuffle(this_sub_liste)
            shufflesubchoices.append(this_sub_liste)

        elif  supportfile.qtype == 18 :


            this_liste = list()
            this_sub_liste = list()
            for this_choice in s_choices : 
                xmin    = this_choice.xmin
                xmax    = this_choice.xmax
                tick    = this_choice.tick
                subtick = this_choice.subtick
                retroaction = replace_bloc(this_choice.retroaction,vars_list,i)
                if this_choice.precision :
                    xmin = random.randrange(xmin, xmin + this_choice.precision)
                    xmax = xmin + this_choice.xmax
                data = { 'id' : this_choice.id , 'tick' : tick , 'subtick' : subtick , 'xmin' : xmin  ,'xmax' : xmax  , 'precision' : this_choice.precision  ,'retroaction' : retroaction , 'is_correct' : this_choice.is_correct   } 
                this_liste.append(data)
                this_subchoices = this_choice.supportsubchoices.all()
                if this_choice.precision :
                    this_sub_list_alea = list()
                    for i in range(supportfile.nb_subpseudo) :
                        inside = True
                        while inside :
                            if subtick : 
                                nb_c = -1*math.floor(math.log10(1/(subtick)));
                                answer = round(random.uniform(xmin, xmax),nb_c)
                            else : answer      = random.randrange(xmin, xmax)
                            
                            if answer in this_sub_list_alea : inside = True
                            else : 
                                inside = False
                                this_sub_list_alea.append(answer)

                        retroaction = ""
                        subdata = { 'id' : 0 , 'answer' : answer , 'imageanswer' : ''  , 'retroaction' : retroaction , 'label' : answer , 'is_correct' : 0   } 
                        this_sub_liste.append(subdata)

                else : 
                    if supportfile.nb_subpseudo :
                        this_sub_choices = list(this_subchoices)
                        random.shuffle(this_sub_choices)
                        this_subchoices = this_sub_choices[0:supportfile.nb_subpseudo]  
                    for subchoice in this_subchoices:
                        answer      = replace_bloc(subchoice.answer,vars_list,i)
                        retroaction = replace_bloc(subchoice.retroaction,vars_list,i)
                        label       = replace_bloc(subchoice.label,vars_list,i)
                        subdata = { 'id' : subchoice.id , 'answer' : answer , 'imageanswer' : subchoice.imageanswer   , 'retroaction' : retroaction , 'label' : label , 'is_correct' : subchoice.is_correct   } 
                        this_sub_liste.append(subdata)
            shufflechoices.append(this_liste)
            shufflesubchoices.append(this_sub_liste)

        else :
            this_liste = list()
            this_choice = s_choices[i]
            this_liste.append(this_choice)
            random.shuffle(this_liste)
            shufflechoices.append(this_liste)
 
    return vars_list , annoncements , choices , shufflechoices , shufflesubchoices, corrections



def define_all_types(n, supportfile):

    if  supportfile.qtype==1 :  # VF

        vars_list , annoncements ,  choices , shufflechoices , shufflesubchoices, corrections = alea_annoncements(n,supportfile)
        context = { 'detail_vars' : vars_list  , 'annoncements' : annoncements  , 'shufflechoices' : shufflechoices , 'numexo' : 0  }

    elif  supportfile.qtype==2 :  # Réponse à compléter

        vars_list , annoncements ,  choices , shufflechoices , shufflesubchoices, corrections = alea_annoncements(n,supportfile)
        context = { 'detail_vars' : vars_list  , 'annoncements' : annoncements  , 'shufflechoices' : shufflechoices  , 'numexo' : 0  }

    elif  supportfile.qtype==3 or supportfile.qtype==4 :  # QCS et QCM
 
        vars_list , annoncements ,  choices , shufflechoices , shufflesubchoices, corrections = alea_annoncements(n,supportfile)
        context = { 'detail_vars' : vars_list  , 'annoncements' : annoncements  , 'shufflechoices' : shufflechoices  , 'numexo' : 0 }
        
    elif supportfile.qtype==5 : # paires

        vars_list , annoncements ,  choices , shufflechoices , shufflesubchoices, corrections = alea_annoncements(n,supportfile)
        context = { 'detail_vars' : vars_list  , 'annoncements' : annoncements  ,  'choices' : choices  ,  'shufflechoices' : shufflechoices  , 'numexo' : 0   }

    elif supportfile.qtype==6: # correspondances

        vars_list , annoncements ,  choices , shufflechoices , shufflesubchoices, corrections = alea_annoncements(n,supportfile)
        context = { 'detail_vars' : vars_list  , 'annoncements' : annoncements  ,  'choices' : choices  ,  'shufflechoices' : shufflechoices  , 'shufflesubchoices' : shufflesubchoices  ,  'numexo' : 0   }

    elif supportfile.qtype==7 : # anagrammes 

        vars_list , annoncements ,  choices , shufflechoices , shufflesubchoices, corrections = alea_annoncements(n,supportfile) 
        context = { 'detail_vars' : vars_list  , 'annoncements' : annoncements  ,  'choices' : choices  ,  'shufflechoices' : shufflechoices  , 'numexo' : 0 }
        

    elif supportfile.qtype==8 : # classement


        vars_list , annoncements ,  choices , shufflechoices , shufflesubchoices, corrections = alea_annoncements(n,supportfile)        

        this_solution = list()
        for shufflesubchoice in shufflesubchoices:
            i , sep , this_sub_solution = 0 , ",", ""
            for s in shufflesubchoice:
                if i == len(shufflesubchoice)-1  : 
                    sep = ""
                i+=1
                this_sub_solution += s['answer'] + sep
            this_solution.append(this_sub_solution)  

        context = { 'detail_vars' : vars_list  , 'annoncements' : annoncements  ,  'choices' : choices  ,  'shufflesubchoices' : shufflesubchoices   , 'numexo' : 0  ,'this_solution' : this_solution  } 

    elif supportfile.qtype==9 : # texte à trous

        vars_list , annoncements ,  choices , shufflechoices , shufflesubchoices, corrections = alea_annoncements(n,supportfile)
        context = { 'detail_vars' : vars_list  , 'annoncements' : annoncements  ,  'choices' : choices  ,  'shufflechoices' : shufflechoices  , 'numexo' : 0   }

 
    elif supportfile.qtype==10 : # puzzle
        pass

    elif supportfile.qtype==12 : #mots mélés   

        supportchoices = list(supportfile.supportchoices.all())
        random.shuffle(supportchoices)
        nb_pseudo = supportfile.nb_pseudo

        if nb_pseudo :
            supportchoices = supportchoices[0:nb_pseudo]

        context = { 'supportfile' : supportfile , 'supportchoices' : supportchoices , 'numexo' :  len(supportchoices) } 


    elif supportfile.qtype==13 : #mots secrets :  

        vars_list , annoncements ,  choices , shufflechoices , shufflesubchoices, corrections = alea_annoncements(n,supportfile)
        context = { 'detail_vars' : vars_list  , 'annoncements' : annoncements  ,  'choices' : choices  ,  'shufflechoices' : shufflechoices  , 'numexo' : len(shufflechoices)   }


    elif supportfile.qtype==14 : # Mémoire 
 
        vars_list , annoncements ,  choices , shufflechoices , shufflesubchoices, corrections = alea_annoncements(n,supportfile)
        try : length = int( len(shufflesubchoices[0])/len(shufflechoices[0]) )
        except : length = 1 
        context = { 'annoncements' : annoncements  ,   'shufflechoices' : shufflechoices  ,  'shufflesubchoices' : shufflesubchoices  , 'numexo' : len(shufflechoices)   , 'length' : length , 'numexo' : -1 }
 
  
    elif supportfile.qtype==15 : #Légender une image  

        vars_list , annoncements ,  choices , shufflechoices , shufflesubchoices, corrections = alea_annoncements(n,supportfile)
        context = { 'annoncements' : annoncements  ,  'choices' : choices  ,  'shufflesubchoices' : shufflesubchoices  , 'shufflechoices' : shufflechoices  , 'numexo' : 0   }



    elif supportfile.qtype==18 :

        vars_list , annoncements ,  choices , shufflechoices , shufflesubchoices, corrections = alea_annoncements(n,supportfile)
        scs = list()
        for s in shufflechoices :
            scs.append(s[0])
        context = { 'detail_vars' : vars_list  , 'annoncements' : annoncements ,  'shufflechoices' : scs ,  'shufflesubchoices' : shufflesubchoices    , 'supportfile' : supportfile , 'numexo' : 0 } 

    return context




@login_required(login_url= 'index')
def execute_exercise(request, idp,ide):
    """ Vue d'un exercice depuis un parcours -- Template de réponse """ 
    if not request.user.is_authenticated :
        messages.error(request,"Utilisateur non authentifié")
        return redirect("index")
        
    try :
        student = request.user.student
    except :
        messages.error(request,"Vous n'êtes pas élève ou pas connecté.")
        return redirect('index')

    parcours = Parcours.objects.get(id= idp)
    exercise = Exercise.objects.get(id= ide)


    if Relationship.objects.filter(parcours=parcours, exercise=exercise).count() == 0 :
        messages.error(request,"Cet exercercice n'est plus disponible.")
        return redirect("index")

    relation = Relationship.objects.get(parcours=parcours, exercise=exercise)
    request.session['level_id'] = exercise.level.id
    start_time =  time.time()


    today = time_zone_user(request.user)
    timer = today.time()
 
    if exercise.supportfile.qtype != 100 :
        return show_supportfile_student(request,relation  )

    else :
        context = {'exercise': exercise,  'start_time' : start_time,  'student' : student,  'parcours' : parcours,  'relation' : relation , 'timer' : timer ,'today' : today , 'communications' : [] , 'relationships' : [] }
        return render(request, 'qcm/show_relation.html', context)



def show_supportfile_student(request,relation): 
    """ Fonction de lecture d'un exercice depuis un parcours pour la def précédente""" 

    student = request.user.student
    today = timezone.now()
    #1 , 2 , 12 n'utilisent pas ces conditions
    loops = [0]*relation.situation
    supportfile = relation.exercise.supportfile

    start_time = time.time()
    context = {'supportfile' : supportfile,  'relation' : relation,   'today' : today , 'loops' : loops,  'student' : student , 'only_show' : False, 'start_time' : start_time}

    if supportfile.is_python or supportfile.qtype == 20 :
        return write_exercise(request,relation.id)
    else :
        qtype_template = Qtype.objects.get(pk=supportfile.qtype).custom
        context.update( define_all_types( relation.situation , supportfile) ) # création du contexte de tous les exercices 
        url = "qcm/qtype/"+qtype_template+"_ans.html" 

    return render(request, url , context)


##### Création du template pour les exercices de type 19 et 20
@login_required(login_url= 'index') 
def write_exercise(request,id): # Coté élève
    """ Enregistrement des réponses des élèves """ 
    try :
        student = request.user.student
    except :
        messages.error(request,"Vous n'êtes pas élève ou pas connecté.")
        return redirect('index')

    relationship = Relationship.objects.get(pk = id)

    tracker_execute_exercise(True ,  student.user , relationship.parcours.id  , relationship.exercise.id , 0)

    today = time_zone_user(student.user)
    if Writtenanswerbystudent.objects.filter(student = student, relationship = relationship ).exists() : 
        w_a = Writtenanswerbystudent.objects.get(student = student, relationship = relationship )
        wForm = WrittenanswerbystudentForm(request.POST or None, request.FILES or None, instance = w_a )  
    else :
        wForm = WrittenanswerbystudentForm(request.POST or None, request.FILES or None ) 
        w_a = False

    if request.method == "POST":
        if wForm.is_valid():
            w_f = wForm.save(commit=False)
            w_f.relationship = relationship
            w_f.student = student
            w_f.answer =  wForm.cleaned_data['answer']
            w_f.is_corrected = 0  # si l'élève soumets une production alors elle n'est pas corrigée 
            w_f.save()

            ### Envoi de mail à l'enseignant
            msg = "Exercice : "+str(unescape_html(cleanhtml(relationship.exercise.supportfile.annoncement)))+"\n Parcours : "+str(relationship.parcours.title)+", posté par : "+str(student.user) +"\n\n sa réponse est \n\n"+str(wForm.cleaned_data['answer'])
            if relationship.parcours.teacher.notification :
                sending_mail("SACADO Exercice posté",  msg , settings.DEFAULT_FROM_EMAIL , [relationship.parcours.teacher.user.email] )
                pass

            return redirect('show_parcours_student' , relationship.parcours.id )

    context = {'relationship': relationship, 'communications' : [] , 'w_a' : w_a , 'parcours' : relationship.parcours ,  'form' : wForm, 'today' : today  }

    if relationship.exercise.supportfile.is_python :
        url = "basthon/answer_interface.html" 
    else :
        url = "qcm/form_writing.html" 

    return render(request, url , context)


######################################################################################################################################################################
###############################             Checking des réponses via ajax                      ######################################################################
######################################################################################################################################################################
######################################################################################################################################################################
###############################             Fonctions auxilières                                ######################################################################
def shuffle_word(string):

    ls = len(string)
    strg = ""
    while ls > 0 :
        idx = random.randint(0,ls-1)
        strg += string[idx]
        string = string[0:idx]+string[idx+1:len(string)]
        ls = len(string)      
    return strg

def message_correction(score,old_score):
    if str(old_score) == str(score) :
        msg = "<i class='fa fa-times text-danger'></i> Tu as commis une erreur. Regarde attentivement la correction."
    else :
        msg = "<i class='fa fa-check text-success'></i> C'est bien. Ta réponse est juste. Continue."
    return msg


def calculate(this_item):
    tab_calculus = this_item.split('?!')
    calculate_value = eval(tab_calculus[1])
    return calculate_value

def calculate_str(this_item):
    renew = ""
    calcs = this_item.split('?!')
    k=0
    for calc in calcs :
        if calcs != "" and k%2==1:
            calc = eval(calc) 
        k+=1
        renew += str(calc)
    return renew


######################################################################################################################################################################
########################################### CHECK des solutions  ----  create_supportfile ligne 6227   ###############################################################
######################################################################################################################################################################
def check_solution_vf(request): ## 1 

    choice_id      = request.POST.get('choice_ids',None)
    supportfile_id = request.POST.get('supportfile_id',0)
    numexo         = int(request.POST.get('numexo',0))
    score          = int(request.POST.get('score',0))
    is_correct     = int(request.POST.get('is_correct',0))
    old_score      = score

    data = {}  
    supportfile   = Supportfile.objects.get(pk=supportfile_id) 
    supportchoice = Supportchoice.objects.get(pk=choice_id) 
 
    if int(supportchoice.is_correct) == is_correct : 
        numexo += 1
        score  += 1

    else : numexo += 1

    data['numexo'] = numexo  
    data['score']  = score

    data['this_correction_text']  =  supportfile.correction
    data['msg'] = message_correction(score,old_score)
 

    return JsonResponse(data)

def check_solution_answers(request):## 2

    supportfile_id = request.POST.get("supportfile_id")
    loop           = request.POST.get("loop")
    situation      = request.POST.get("situation")
    parcours_id    = request.POST.get("parcours_id")
    relation_id    = request.POST.get("relation_id")
    numexo         = int(request.POST.get('numexo',0)) 
    score          = int(request.POST.get('score',0))
    answers        = request.POST.getlist("answers")
    choice_id      = request.POST.get("choice_id")
    old_score      = score
 
    data = {}

    supportfile    = Supportfile.objects.get(pk=supportfile_id) 
    alea_variables = supportfile.supportvariables.all()

    index = int(loop)-1
    idx   = 2*(index)
    this_score = 0
    choices = supportfile.supportchoices.all()

    if choice_id == "0" :  # réponse avec 'input' dans l'énoncé
        for choice in choices :
            numexo += 1
            variable  = choice.answer
            calculus  = choice.answerbis 
            retroaction = choice.retroaction
            this_value = request.POST.getlist(variable)[idx]
            if '?!' in calculus :
                for alea_variable in alea_variables : 
                    alea_variable = str(alea_variable) 
                    var = request.POST.getlist(alea_variable)[index]
                    variable    = variable.replace("{"+alea_variable+"}",var)
                    calculus    = calculus.replace("{"+alea_variable+"}",var)
                    retroaction = retroaction.replace("{"+alea_variable+"}",var)
                calculus    = calculate(calculus) 
                retroaction = calculate_str(retroaction)       
            if str( this_value ) ==  str(calculus):
                score  += 1
 
    elif 'customvars' in request.POST : # réponse avec variable aléatoire
        choice = Supportchoice.objects.get(pk=choice_id)
        numexo += 1
        variable    = choice.answer
        calculus    = choice.answerbis
        retroaction = choice.retroaction
        for customvars in request.POST.getlist('customvars') :
            value = request.POST.getlist(customvars)[index]
            variable     = variable.replace("{"+customvars+"}",value)
            calculus     = calculus.replace("{"+customvars+"}",value)
            retroaction  = retroaction.replace("{"+customvars+"}",value)
 
        calc_calculus = calculate(calculus) 
        if str(answers[index]) == str(calc_calculus) :
            score  += 1
        retroaction   = calculate_str(retroaction)         

    else : # réponse sans variable
        choice      = Supportchoice.objects.get(pk=choice_id)
        retroaction = choice.retroaction 
        if str(answers[index]) in choice.answerbis.split("_|_") :
            numexo += 1
            score  += 1
        else  : numexo += 1
        if supportfile.correction :
            correction = "<hr/>" + supportfile.correction

    data['numexo'] = numexo  
    data['score']  = score
    data['this_correction_text']  =  retroaction+"<br/><br/>"+supportfile.correction
    data['msg'] = message_correction(score,old_score)
    return JsonResponse(data)

def check_solution_qcm_numeric(request):##3 - 4

    solutions      = request.POST.getlist('choice_ids',None)
    supportfile_id = request.POST.get('supportfile_id',0)
    numexo         = int(request.POST.get('numexo',0))
    score          = int(request.POST.get('score',0))
    old_score      = score
    data = {}
    supportfile       = Supportfile.objects.get(pk=supportfile_id) 
    supportchoice_ids = Supportchoice.objects.values_list('id',flat=True).filter(supportfile = supportfile,is_correct=1)
        
    solutions_int = list()
    for s  in solutions:
        solutions_int.append( int(s) )
 
    if set(solutions_int) == set(supportchoice_ids) : 
        numexo += 1
        score  += 1

    else : numexo += 1

    data['numexo'] = numexo  
    data['score']  = score
    data['this_correction_text']  =  supportfile.correction
    data['msg'] = message_correction(score,old_score)

    return JsonResponse(data) 

def check_solution_pairs(request):## 5

    supportfile_id = request.POST.get('supportfile_id',0)
    numexo         = int(request.POST.get('numexo',0))
    score          = int(request.POST.get('score',0))
    loop           = int(request.POST.get('loop',0))
    customvars     = request.POST.getlist('customvars',0) 
    answers        = request.POST.getlist('answers'+str(loop),None)
    choice_ids     = request.POST.getlist('choice_ids',None)

    old_score      = score
    data = {}
    supportfile  = Supportfile.objects.get(pk=supportfile_id) 


    supportchoices   = supportfile.supportchoices.filter(pk__in=choice_ids)
    supportvariables = supportfile.supportvariables.all()

    data_ans  = dict() 
    sep , sepa = " - " , ""
    string_pairs = ""
    for supportchoice in supportchoices :
        retroaction = supportchoice.retroaction
        if supportchoice.imageanswer :
            data_ans[supportchoice.imageanswer] = supportchoice.imageanswerbis #on crée le dictionnaire de réponse
            string_pairs += ""
        else :
            answer      = supportchoice.answer
            answerbis   = supportchoice.answerbis
            if supportvariables:
                for var in customvars :
                    value = request.POST.getlist(var)[loop-1]
                    answer      = answer.replace("{"+var+"}",value)
                    answerbis   = answerbis.replace("{"+var+"}",value)
                    retroaction = retroaction.replace("{"+var+"}",value)
                if '?!' in answerbis   : answerbis , sep , sepa  = calculate(answerbis) , " " , " : "
                if '?!' in retroaction : retroaction , sep , sepa = calculate_str(retroaction)  , " " , " : "
                      
                answerbis = "$"+str(answerbis)+"$"
            data_ans[answer] = answerbis #on crée le dictionnaire de réponse
            string_pairs += "La paire <b>"+ str(answer) + sep + str(answerbis)+" "+sepa+" </b>  "+ str(retroaction) + "<br/>"
    
    retroaction = string_pairs 
    numexo += 1
    this_score , j = 0,0
    for answer in answers :
        j+=1
        if supportvariables:
            for var in customvars :
                value = request.POST.getlist(var)[loop-1]
                answer = answer.replace("{"+var+"}",value)
                answer = answer.replace("----","")
            tab_answer = answer.split("====") 

            if data_ans[str(tab_answer[0])] == str(tab_answer[1]):
                this_score  += 1     

        else :
            answer = answer.replace("----","")
            tab_answer = answer.split("====") 
            if data_ans[str(tab_answer[0])] == str(tab_answer[1]):
                this_score  += 1

    if this_score == j : score +=1
 
    data['numexo'] = numexo  
    data['score']  = score
    cor =""
    if supportfile.correction : cor = "<br/><br/>"+supportfile.correction
    data['this_correction_text']  =  retroaction+cor
    data['msg'] = message_correction(score,old_score)
    return JsonResponse(data) 

def check_solution_regroup(request):## 6

    supportfile_id = request.POST.get('supportfile_id',0)
    answers = request.POST.getlist("answers",[])
    numexo  = int(request.POST.get("numexo",0))
    score   = int(request.POST.get("score",0))
    data = {}
    old_score = score

    numexo +=1
    this_score = 0
    j = 0
    
    for answer in answers :
        scores = list()
        choice_id, subchoice_id_str =  answer.split("====")
        supportchoice = Supportchoice.objects.get(pk=choice_id)
        supportsubchoices = supportchoice.supportsubchoices.all()
        answer_ids = subchoice_id_str.split("----")

        answer_ids = answer_ids[:len(answer_ids)-1]
        this_sub_score = 0
        supportsubchoices_values = supportchoice.supportsubchoices.values_list('id', flat=True)

        for answer_id in answer_ids :
            if answer_id != "" and  int(answer_id)  in list(supportsubchoices_values) : scores.append(1)
            else : scores.append(0)

        if sum(scores) == len(scores): this_score += 1

    if this_score == j : score +=1

    supportfile = Supportfile.objects.get(pk=supportfile_id) 
    correction_str = ""
    for choice in supportfile.supportchoices.all() :
        if choice.imageanswer :
            correction_str += r"<img src='{{ choice.imageanswer.url }}' width='150px' />"
        if choice.answer : 
            correction_str += str(choice.answer)
        for subchoice in choice.supportsubchoices.all() :
            if subchoice.imageanswer :
                correction_str += r"<img src='{{ choice.imageanswer.url }}' width='150px' />"
            if subchoice.answer : 
                correction_str += str(choice.answer)


    data['numexo'] = numexo  
    data['score']  = score
    data['this_correction_text'] = correction_str
    data['msg'] = message_correction(score,old_score)
    return JsonResponse(data) 

def check_anagram_answers(request):## 7

    supportfile_id = request.POST.get('supportfile_id',0)
    numexo         = int(request.POST.get('numexo',0))
    score          = int(request.POST.get('score',0))
    loop           = int(request.POST.get('loop',0))
    answers        = request.POST.getlist('answers',None)
    choice_id      = request.POST.get('choice_id',None)

    old_score      = score
    data = {}
    choice      = Supportchoice.objects.get(pk=choice_id) 
    
    texte = choice.answer
    texte     = texte.replace('<strong>','####')
    texte     = texte.replace('</strong>','####')
    locutions = texte.split('####')
    ans_to_do = list()

    for i in range(len(locutions)) :
        if i%2==1 : ans_to_do.append( locutions[i] )

    numexo +=1
    if ans_to_do[0]==answers[loop-1]:
        score += 1

    data['numexo'] = numexo  
    data['score']  = score
    data['this_correction_text'] = choice.answer
    data['msg'] = message_correction(score,old_score)
    return JsonResponse(data) 

def check_sort_answers(request):## 8   

    supportfile_id = request.POST.get('supportfile_id',0)
    numexo         = int(request.POST.get('numexo',0))
    score          = int(request.POST.get('score',0))
    loop           = int(request.POST.get('loop',0))
    answers        = request.POST.getlist('answers',None)
    old_score      = score
    data = {}
    supportfile = Supportfile.objects.get(pk=supportfile_id) 
    choices     = list(supportfile.supportchoices.order_by('id')) 
    answer_ids = list() 

    numexo +=1
    if supportfile.supportvariables.count() or supportfile.nb_pseudo : # avec VA , on on suppose que les answer sont des nombres
        ans_list = answers[loop-1].split(',')
        ans_list_sorted = answers[loop-1].split(',')
        ans_list_sorted.sort()
        this_score = -1
        
        for j in range(len(ans_list)):
            if ans_list[j] == ans_list_sorted[j]: 
                this_score += 1
    else : # Sans variable aléatoire
        j = 0
        this_score = 0
        for answer in answers[0].split(',') :
            if answer == choices[j].answer or answer == choices[j].imageanswer : 
                this_score += 1
            j+=1

    if this_score == j : score +=1

    data['numexo'] = numexo  
    data['score']  = score

    correction = ""
    for choice in choices :
        if choice.imageanswer :
            correction += r"<img src='{{ choice.imageanswer.url }}' width='140px' />"
        if choice.answer : 
            correction += " "+choice.answer
        if choice.retroaction :  
            correction += " "+choice.retroaction

    data['this_correction_text'] = correction
    data['msg'] = message_correction(score,old_score)
    return JsonResponse(data) 

def check_filltheblanks_answers(request):## 9   

    supportfile_id = request.POST.get('supportfile_id',0)
    numexo         = int(request.POST.get('numexo',0))
    score          = int(request.POST.get('score',0))
    loop           = int(request.POST.get('loop',0))
    answers        = request.POST.getlist('answers'+str(loop),None)
    choice_ids      = request.POST.getlist('choice_id',None)

    old_score      = score
    data = {}
    supportfile = Supportfile.objects.get(pk=supportfile_id) 
    choice      = Supportchoice.objects.get(pk=choice_ids[int(loop)-1]) 
    
    texte     = choice.answer
    texte     = texte.replace('<strong>','####')
    texte     = texte.replace('</strong>','####')
    locutions = texte.split('####')
    ans_to_do = list()

    for i in range(len(locutions)) :
        if i%2==1 : ans_to_do.append( locutions[i].strip() )
    
    for i in range(len(ans_to_do)) :
        numexo +=1
        if ans_to_do[i]==answers[i]:
            score += 1


    data['numexo'] = numexo  
    data['score']  = score
    data['this_correction_text'] = choice.answer
    data['msg'] = message_correction(score,old_score)
    return JsonResponse(data) 

def check_grid_answers(request):## 12 mot mélés   non nécessaire

    sender = int(request.POST.get('sender',0))
    score  = int(request.POST.get('score',0))
    word   = request.POST.get('word',None)
    l_word = len(word)

    data = {}
    true = "no"
    if sender < l_word*20:
        score += 1
        true = "yes"

    data['sender'] = sender 
    data['score']  = score
    data['word']   = word
    data['true']   = true
    return JsonResponse(data)  

def ajax_secret_letter(request):## 13 mot secret 

    secret_letter = request.POST.get('secret_letter',None)
    used_letter   = request.POST.get('used_letter',"")    
    index         = request.POST.get('index',None) # index de la lettre dans le mot
    loop          = request.POST.get('loop',None)
    choice_id     = request.POST.get('choice_id',None)
    position      = request.POST.get('position',None)
    score         = int(request.POST.get('score',0))
    nb_tries      = int(request.POST.get('nb_tries',0))

    data = {}
    word = Supportchoice.objects.get(pk=choice_id).answer
    word_length   = request.POST.get('word_length',len(word))

    response , win , new_slide = "false", "false", "false"
    input_idx = 0
 
    if secret_letter == '2'   : secret_letter = 'é'
    elif secret_letter == '7' : secret_letter = 'è' 
    elif secret_letter == '9' : secret_letter = 'ç'
    elif secret_letter == 'ù' : secret_letter = 'ù'
    elif secret_letter == '0' : secret_letter = 'à'

    new_string_word = ""
    if secret_letter.lower() == word[int(index)]   :
        response = "true"
        word_length   = int(word_length) - 1
        if word_length == 0 :
            win = "true"
            score += 1

    if nb_tries == 0 : new_slide = 'yes'

    data['used_letter'] = used_letter + secret_letter +" "
    data["word"]     = word  
    data["length"]   = word_length  
    data["length_i"] = word_length     
    data["win"]      = win
    data["response"] = response              
    data['input']    = input_idx 
    data['score']    = score
    data['slide']    = new_slide
    return JsonResponse(data)  

def check_secret_answers(request):## 13 mot secret  

    supportfile_id = request.POST.get('supportfile_id',0)
    numexo         = int(request.POST.get('numexo',0))
    score          = int(request.POST.get('score',0))
    loop           = int(request.POST.get('loop',0))
    answers        = request.POST.getlist('answers',None)
    choice_id      = request.POST.get('choice_id',None)

    old_score      = score
    data = {}
    supportfile = Supportfile.objects.get(pk=supportfile_id) 
    choice      = Supportchoice.objects.get(pk=choice_id) 
    
    for i in range(len(locutions)) :
        if i%2==1 : ans_to_do.append( locutions[i] )

    for i in range(len(ans_to_do)) :
        numexo +=1
        if ans_to_do[i]==answers[i]:
            score += 1

    data['numexo'] = numexo  
    data['score']  = score
    data['this_correction_text'] = choice.answer
    data['msg'] = message_correction(score,old_score)
    return JsonResponse(data) 

def check_memo_answers(request):

    subchoice_ids = request.POST.getlist('liste',None)
    length        = request.POST.get('length',0)
    data = {}
    supportsubchoice = Supportsubchoice.objects.get(pk=subchoice_ids[0])
    solutions        = supportsubchoice.supportchoice.supportsubchoices.values_list('id',flat=True)

    solutions_str = list()
    for s  in solutions:
        solutions_str.append( str(s) )

    if set(solutions_str) == set(subchoice_ids) : 
        test = "yes"
        length = int(length)-1
    else : test = "no"

    data['test']   = test  
    data['length'] = length

    return JsonResponse(data)  

def check_image_answers(request):


    score          = int(request.POST.get('score',0))
    numexo         = int(request.POST.get('numexo',0))
    loop           = int(request.POST.get('loop',0)) - 1
    answers        = request.POST.getlist('answers' + str(loop), [])
    choice_ids     = request.POST.getlist('choice_ids'+ str(loop), [])

    supportfile_id = request.POST.get('supportfile_id',0)

    data = {}
    old_score  = score
    numexo += 1

    this_score = -1
    for i in range( len (choice_ids) ) :
        supportsubchoice = Supportsubchoice.objects.get(pk=choice_ids[i])
        if supportsubchoice.label == answers[i]:
            this_score +=1
    if i == this_score : score +=1

    retroaction = ""
    if supportfile_id :
        supportfile = Supportfile.objects.get(pk=supportfile_id)
        choice = supportfile.supportchoices.all()[loop]
        retroaction += choice.retroaction+"<br/>"
    

    data = {}
    data['numexo'] = numexo
    data['score']  = score
    cor =""
    if supportfile.correction : cor = "<br/><br/>"+supportfile.correction
    data['this_correction_text']  =  retroaction+cor
    data['msg'] = message_correction(score,old_score)
    return JsonResponse(data) 

def check_axe_answers(request):## 18 axe 
    
    customvars     = request.POST.getlist('customvars',None)
    supportfile_id = request.POST.get('supportfile_id',None)
    loop           = int(request.POST.get('loop',None))-1
    answers        = request.POST.getlist('answers'+str(loop),None)
    score          = int(request.POST.get('score',0))
    numexo         = int(request.POST.get('numexo',0))
    old_score      = score
    retroaction    = ""
    subchoice_ids  = request.POST.getlist('subchoice_id'+str(loop),None)
    choice_id      = request.POST.get('choice_id'+str(loop),None)
    aleas          = request.POST.getlist('aleas'+str(loop),None)

    xmin      = request.POST.get('xmin'+str(loop),None)
    xmax      = request.POST.get('xmax'+str(loop),None)
    tick      = request.POST.get('tick'+str(loop),None)
    subtick   = request.POST.get('subtick'+str(loop),None)
    if xmin    : xmin   = float(xmin.replace(",","."))
    if xmax    : xmax   = float(xmax.replace(",","."))
    if tick    : tick   = float(tick.replace(",","."))
    if subtick : subtick   = float(subtick.replace(",","."))

    width_axe = float(request.POST.get('width_axe'+str(loop),None))

 
    this_score =-1
    numexo += 1
    for i in range(len(subchoice_ids)) :

        width_pixel  =  width_axe*tick/(xmax - xmin) 
        value = (float(answers[i])-15)/width_pixel 


        if subtick : precision = 1/subtick
        else : precision = 1/tick
        choice    = Supportchoice.objects.get(pk=choice_id )
        retroaction += choice.retroaction + " "
        if choice.precision :
            value = value + xmin
            if str(  float(aleas[i].replace(",","."))  - precision/2) <= str(value) <= str(  float(aleas[i].replace(",",".")) + precision/2):
                this_score +=1

        else :
            subchoice = Supportsubchoice.objects.get(pk=subchoice_ids[i])
            answer = float(subchoice.answer.replace(",","."))

            if str(  answer  - precision/2) <= str(value) <= str(  answer  + precision/2):
                this_score +=1
            


    if this_score == i : score +=1

    data = {}
    supportfile = Supportfile.objects.get(pk=supportfile_id)    
    data['numexo'] = numexo  
    data['score']  = score
    cor =""
    if supportfile.correction : cor = "<br/><br/>"+supportfile.correction
    data['this_correction_text']  =  retroaction+cor
    data['msg'] = message_correction(score,old_score)
    return JsonResponse(data)  



######################## A remettre comme sur sacado.xyz
def show_customexercise(request,idc): # vue coté prof de l'exercice autocorrigé  du customexercise

    customexercise = Customexercise.objects.get(pk = idc)
    today = timezone.now()
    #1 , 2 , 12 n'utilisent pas ces conditions
    loops = [0]*customexercise.pseudoalea_nb
    context = { 'customexercise' : customexercise, 'today' : today , 'loops' : loops,  'student' : None, 'only_show' : False}


    if  customexercise.qtype==3 or customexercise.qtype==4 :  # QCS et QCM

        shufflechoices = list()
        for choice in customexercise.customchoices.all():
            shufflechoices.append(choice)
            random.shuffle(shufflechoices)
        context.update( { 'shufflechoices' : shufflechoices } )

    elif customexercise.qtype==5 : # paires

        choices = list()
        shufflechoices = list()
        for choice in customexercise.customchoices.all():
                shufflechoices.append(choice)
                choices.append(choice)
        random.shuffle(shufflechoices)
        random.shuffle(choices)
        context.update( { 'choices' : choices , 'shufflechoices' : shufflechoices } )

    elif customexercise.qtype==6 : # correspondances
        subchoices = list()
        for choice in customexercise.customchoices.all():
            for subchoice in choice.customsubchoices.all():
                subchoices.append(subchoice)
        random.shuffle(subchoices)
        context.update( { 'subchoices' : subchoices  } )

    elif customexercise.qtype==7 : # anagrammes 

        choices = list()
        for choice in customexercise.customchoices.all():
            dico = {'id' : choice.id , 'word' : shuffle_word(choice.answer) }
            choices.append(dico)

        context.update( { 'choices' : choices  } )

    elif customexercise.qtype==8 : # anagrammes

        shufflechoices = list()
        for choice in customexercise.customchoices.all():
            shufflechoices.append(choice)
        random.shuffle(shufflechoices)
        context.update( { 'shufflechoices' : shufflechoices  } )

    elif customexercise.qtype==9 : # texte à trous

        words = list()
        mystr = customexercise.filltheblanks
        mystr = mystr.replace('<strong>','####')
        mystr = mystr.replace('</strong>','####')
        tab   = mystr.split('####')

        string = ""
        for i in range(len(tab)) :
            if i%2==1:
                words.append(tab[i])  

        context.update({'customexercise' : customexercise, 'words' : words })
 
    elif customexercise.qtype==10 : # puzzles

        shufflechoices = list()
        for customchoice in customexercise.customchoices.all():
            shufflesubchoices = list()
            for subchoice in customchoice.customsubchoices.all():
                shufflesubchoices.append(subchoice)
            random.shuffle(shufflesubchoices)
            puzzle = { 'customchoice' : customchoice , 'shufflesubchoices' : shufflesubchoices }
            shufflechoices.append(puzzle)
        context.update( { 'shufflechoices' : shufflechoices  } )

    elif customexercise.qtype==13 : #mots secrets : c 

        shufflechoices =list() 
        for choice in customexercise.customchoices.values('id','answer').all():
            shufflechoices.append(choice)
        random.shuffle(shufflechoices)
        secretword = shufflechoices[0]
        shuffle_ids = ""
        i = 1
        for s in shufflechoices :
            if i == len(shufflechoices) : sep = ""
            else : sep = "-"
            shuffle_ids += str(s["id"])+sep
            i+=1
        context.update({ 'shufflechoices' : shufflechoices, 'secretword' : secretword, 'shuffle_ids' : shuffle_ids  })

    elif customexercise.qtype==14 :

        subchoices = list()
        for choice in customexercise.customchoices.all():
            for subchoice in choice.customsubchoices.all():
                subchoices.append(subchoice)
        random.shuffle(subchoices)

        length = 0
        customchoice = customexercise.customchoices.first()
        length = customchoice.customsubchoices.count()

        context.update( { 'subchoices' : subchoices , 'length' : length , } )
 

    if customexercise.is_python :
        url = "basthon/index_custom.html" 
    else :
        url = "qcm/qtype/form_answer_all_types.html" 

    return render(request, url , context)


######################################################################################################################################################################
#########################################     Enregistrement des réultats     ########################################################################################
######################################################################################################################################################################
def get_the_score(request,supportfile,answer) :

    score , numexo  = 0 , 1

    list_vars = list()
    supportchoices = supportfile.supportchoices.all()

    for supportchoice in supportchoices :
        if 'input' in supportfile.annoncement :
            list_vars = supportchoice.answer.split('____')
            for list_var in list_vars : 
                var,  val = list_var.split('=')
                value = request.POST.getlist(var)[0]
                if str(val) == str(value) :
                    score += 1
        else :
            list_vars = supportchoice.answer.split('____')
            if answer in list_vars :
                score += 1

    return round(score/supportchoices.count(),2)*100 


def get_the_timer(time_begin) : 
    if time_begin :
        this_time = time_begin.split(",")[0]
        end_time  =  str(time.time()).split(".")[0]
        timer =  int(end_time) - int(this_time)
    else : 
        timer = 0
    return timer


@csrf_exempt    
def store_the_score_relation_ajax(request):

    p_id = request.POST.get("parcours_id",None)
    if p_id :
        parcours_id = int(p_id)
    else :
        messages.error(request, "Score non enregistré. Le parcours n'est pas reconnu.")
        return redirect('index')
 
    try:
        time_begin = request.POST.get("start_time",None)
        timer      = get_the_timer(time_begin)

        numexo = request.POST.get("numexo",None)    
        answer = request.POST.get("answer",None) 

        relation_id = int(request.POST.get("relation_id"))
        relation = Relationship.objects.get(pk = relation_id)
        data = {}
     
        student = Student.objects.get(user=request.user)

        if request.method == 'POST':
            score = request.POST.get("score",None)
            if score :
                if relation.exercise.supportfile.qtype != 100 and score: # cas des exercices non GGB
                    if relation.exercise.supportfile.qtype == 14 and numexo and  int(numexo) < int(score) : 
                        score = 100
                    elif numexo and  int(numexo) > 0: 
                        score = round(float(int(score)/int(numexo)),2)*100 
                    else : 
                        score = 0
                elif relation.exercise.supportfile.qtype == 100 :   # cas des exercices  GGB      
                    if numexo : numexo = int(numexo)-1   
                    score = round(float(request.POST.get("score")),2)*100 
                else :
                    score = 0
                if score > 100 :
                    score = 100
            else :
                score = get_the_score(request,relation.exercise.supportfile,answer)            

            # multi_studentanswer = Studentanswer.objects.filter(exercise  = relation.exercise , parcours  = relation.parcours ,  student  = student)
            # if multi_studentanswer.count() > 0 :
            #     this_studentanswer = multi_studentanswer.last()
            #     multi_studentanswer.filter(pk=this_studentanswer.id).update( numexo   = numexo, point    = score , secondes = timer )
            # else :
            #     try :
            #         this_studentanswer = Studentanswer.objects.create(exercise  = relation.exercise , parcours  = relation.parcours ,  student  = student, numexo= numexo,  point= score, secondes= timer    )
            #     except :
            #         pass

            #multi_studentanswer, create = Studentanswer.objects.update_or_create(exercise  = relation.exercise , parcours  = relation.parcours ,  student  = student , defaults={'numexo' : numexo,  'point': score, 'secondes': timer} )
            #if not create :
            #    Studentanswer.objects.filter(pk=multi_studentanswer.id).update( numexo   = numexo, point    = score , secondes = timer )


            Studentanswer.objects.create(exercise  = relation.exercise , parcours  = relation.parcours ,  student  = student , numexo= numexo,  point= score, secondes= timer )
            ##########################################################

            result, createded = Resultexercise.objects.get_or_create(exercise  = relation.exercise , student  = student , defaults = { "point" : score , })
            if not createded :
                Resultexercise.objects.filter(exercise  = relation.exercise , student  = student).update(point= score)

            # Moyenne des scores obtenus par savoir faire enregistré dans Resultknowledge
            knowledge = relation.exercise.knowledge
            scored = 0
            studentanswers = Studentanswer.objects.filter(student = student,exercise__knowledge = knowledge) 
            for studentanswer in studentanswers:
                scored += studentanswer.point 
            try :
                scored = scored/len(studentanswers)
            except :
                scored = 0
            result, created = Resultknowledge.objects.get_or_create(knowledge  = relation.exercise.knowledge , student  = student , defaults = { "point" : scored , })
            if not created :
                Resultknowledge.objects.filter(knowledge  = relation.exercise.knowledge , student  = student).update(point= scored)
            

            # Moyenne des scores obtenus par compétences enregistrées dans Resultskill
            skills = relation.skills.all()
            for skill in skills :
                Resultskill.objects.create(student = student, skill = skill, point = score) 
                resultskills = Resultskill.objects.filter(student = student, skill = skill).order_by("-id")[0:10]
                sco = 0
                for resultskill in resultskills :
                    sco += resultskill.point
                    try :
                        sco_avg = sco/len(resultskills)
                    except :
                        sco_avg = 0
                result, creat = Resultlastskill.objects.get_or_create(student = student, skill = skill, defaults = { "point" : sco_avg , })
                if not creat :
                    Resultlastskill.objects.filter(student = student, skill = skill).update(point = sco_avg) 
                
                if Resultggbskill.objects.filter(student = student, skill = skill, relationship = relation).count() < 2 :
                    result, creater = Resultggbskill.objects.get_or_create(student = student, skill = skill, relationship = relation, defaults = { "point" : score , })
                    if not creater :
                        Resultggbskill.objects.filter(student = student, skill = skill, relationship = relation).update(point = sco_avg)
                else :
                    result = Resultggbskill.objects.filter(student = student, skill = skill, relationship = relation).last()
                    result.point = sco_avg 
                    result.save()


            try :
                if relation.exercise.supportfile.annoncement != "" :
                    name_title = relation.exercise.supportfile.annoncement
                else :
                    name_title = relation.exercise.knowledge.name
                msg = "Exercice : "+str(unescape_html(cleanhtml(name_title)))+"\n Parcours : "+str(relation.parcours.title)+"\n Fait par : "+str(student.user)+"\n Nombre de situations : "+str(numexo)+"\n Score : "+str(score)+"%"+"\n Temps : "+str(convert_seconds_in_time(timer))
                rec = []
                for g in student.students_to_group.filter(teacher = relation.parcours.teacher):
                    if not g.teacher.user.email in rec : 
                        rec.append(g.teacher.user.email)

                if g.teacher.notification :
                    sending_mail("SacAdo Exercice posté",  msg , settings.DEFAULT_FROM_EMAIL , rec )
                    pass

                try :
                    rec_p = []
                    for parent in student.students_parent.filter(user__school_id = 50): 
                        rec_p.append(parent.user.email)
                        msg += "" # désincription
                        sending_mail("SacAdo Académie Exercice posté",  msg , settings.DEFAULT_FROM_EMAIL , rec_p )
                except :
                    pass
                    
            except:
                pass

            try :
                nb_done = 0
                for exercise in relation.parcours.exercises.all() :
                    if Studentanswer.objects.filter(exercise  = exercise , parcours  = relation.parcours ,  student  = student).count()>0 :
                        nb_done +=1

                if nb_done == relation.parcours.exercises.count() :
                    redirect('index')
            except:
                pass

            #####################################################################
            # Enregistrement à la volée pour les évaluations 
            #####################################################################
            is_ajax =  request.POST.get("is_ajax", None)
            init =  request.POST.get("init", None)
            if is_ajax :
                data = {}
                if init :
                    data["html"] = "<span class= 'verif_init_and_answer' >Exercice initialisé</span>"
                    data["numexo"] = -100
                else :
                    data["html"] = "<span class= 'verif_init_and_answer' >Score enregistré</span>"
                    data["numexo"] = this_studentanswer.numexo
                return JsonResponse(data)
            #####################################################################

        prepeval_id = request.session.get('prepeval_id', None)
        if prepeval_id :
            return redirect('show_prepeval' ,  prepeval_id )

        if relation.parcours.is_evaluation and relation.parcours.is_next :
            parcours      = relation.parcours
            new_rank      = relation.ranking + 1 
            i             = 0
            relationships = Relationship.objects.filter(parcours=parcours)

            for r in relationships :
                Relationship.objects.filter(pk=r.id).update(ranking = i)
                i += 1

            if new_rank < relationships.count():
                new_relation = Relationship.objects.get(parcours=parcours, ranking = new_rank)
                return redirect('execute_exercise' , parcours_id , new_relation.exercise.id )
            else :
                return redirect('show_parcours_student' ,  parcours_id )
        else :
            return redirect('show_parcours_student' , parcours_id )

    except :
        return redirect('show_parcours_student' , parcours_id )


 
######################################################################################################################################################################
#########################################   Fin de gestion des supportfiles   ########################################################################################
######################################################################################################################################################################
def ajax_assign_exercise_to_parcours(request):

    teacher = request.user.teacher
    exercise_id = request.POST.get('exercise_id', None)
    parcours_id = request.POST.get('parcours_id', None)

    data = {}
    parcours = Parcours.objects.get(pk = parcours_id)
    exercise    = Exercise.objects.get(pk=exercise_id)
    supportfile = exercise.supportfile
    skills      = supportfile.skills.all()
    relation    = Relationship.objects.create(parcours = parcours , exercise = exercise , document_id = 0 , type_id = 0 , ranking =  0 , is_publish= 1 , start= None , date_limit= None, duration= supportfile.duration, situation= supportfile.situation ) 
    
    students = parcours.students.all()
    relation.students.set(students)
    relation.skills.set(skills)

    return JsonResponse(data)



def ajax_customexercises_subjects_levels(request):

    teacher = request.user.teacher
    subject_ids   = request.POST.getlist('subject_ids', None)
    level_ids     = request.POST.getlist('level_ids', None)

    data = {}

    exercises  = Exercise.objects.filter(supportfile__author=teacher,supportfile__qtype__lt=100,knowledge__theme__subject_id__in=subject_ids)
    themes     = Theme.objects.filter(subject_id__in=subject_ids)
    knowledges = Knowledge.objects.filter(theme__subject_id__in=subject_ids)

    for level_id in level_ids :

        level = Level.objects.get(pk = level_id)
        customs_levels = list( level.exercises.filter(supportfile__author=teacher,knowledge__theme__subject_id__in=subject_ids) )   
        exercises = [ c for c in list(customs_levels) if c in list(exercises)]

        themes_levels = list( level.themes.filter(subject_id__in=subject_ids) )  
        themes = [ t for t in list(themes_levels) if t in list(themes)]

    if level_ids: 
        knowledges = Knowledge.objects.filter(theme__subject_id__in=subject_ids, level__id__in=level_ids)

    skills = Skill.objects.filter(subject_id__in=subject_ids)

    data['themes']          = serializers.serialize('json', set(themes)) 
    data['knowledges']      = serializers.serialize('json', knowledges )
    data['skills']          = serializers.serialize('json', skills)  


    context = {     'teacher' : teacher , 'exercises': set(exercises) , 'is_mathJax' : True ,   }
    data['customexercises'] = render_to_string('qcm/ajax_list_customexercises.html', context)

    return JsonResponse(data)


def ajax_customexercises_skills(request):

    teacher = request.user.teacher
    subject_ids   = request.POST.getlist('subject_ids', None)
    skill_ids     = request.POST.getlist('skill_ids', None)
    level_ids     = request.POST.getlist('level_ids', None)
    theme_ids     = request.POST.getlist('theme_ids', None)
    knowledge_ids = request.POST.getlist('knowledge_ids', None)

    customs = set()
    for level_id in level_ids :
        level = Level.objects.get(pk = level_id)
        customs.update(level.exercises.filter(supportfile__qtype__lt = 100 , supportfile__author = teacher , supportfile__theme__subject_id__in=subject_ids) )

    customs_skills = set()
    for skill_id in skill_ids :
        skill = Skill.objects.get(pk = skill_id)
        customs_skills.update(   Exercise.objects.filter(supportfile__qtype__lt = 100 ,supportfile__author = teacher ,supportfile__skills=skill)    )
 
    customs = [ c for c in list( customs_skills ) if c in list(customs) ]

    if theme_ids :
        customs_themes = set()
        for theme_id in theme_ids :
            theme = Theme.objects.get(pk = theme_id)
            customs_themes.update( theme.exercises.filter(supportfile__qtype__lt = 100 ,supportfile__author = teacher ) )

        customs = [ c for c in list( customs_themes ) if c in list(customs) ]    

    if knowledge_ids :
        customs_knowledges = set()
        for knowledge_id in knowledge_ids :
            knowledge = Knowledge.objects.get(pk = knowledge_id)
            customs_knowledges.update( knowledge.exercises.filter(supportfile__qtype__lt = 100 ,supportfile__author = teacher  ) )
            
        customs = [ c for c in list( customs_knowledges ) if c in list(customs) ]    

    data = {}
    context = {     'teacher' : teacher , 'exercises': set(customs) , 'is_mathJax' : True ,   }
    data['customexercises'] = render_to_string('qcm/ajax_list_customexercises.html', context)

    return JsonResponse(data)



def ajax_customexercises_themes(request):

    teacher = request.user.teacher
    subject_ids   = request.POST.getlist('subject_ids', None)
    skill_ids     = request.POST.getlist('skill_ids', None)
    level_ids     = request.POST.getlist('level_ids', None)
    theme_ids     = request.POST.getlist('theme_ids', None)
    knowledge_ids = request.POST.getlist('knowledge_ids', None)
    data = {}
    data["knowledges"] = None
    customs = set()
    for level_id in level_ids :
        level = Level.objects.get(pk = level_id)
        customs.update(level.exercises.filter(supportfile__qtype__lt = 100 , supportfile__author = teacher , supportfile__theme__subject_id__in=subject_ids) )

    if theme_ids :
        customs_themes = set()
        for theme_id in theme_ids :
            theme = Theme.objects.get(pk = theme_id)
            customs_themes.update( theme.exercises.filter(supportfile__qtype__lt = 100 ,supportfile__author = teacher ) )

        customs = [ c for c in list( customs_themes ) if c in list(customs) ]    


    if skill_ids :
        customs_skills = set()
        for skill_id in skill_ids :
            skill = Skill.objects.get(pk = skill_id)
            customs_skills.update(   Exercise.objects.filter(supportfile__qtype__lt = 100 ,supportfile__author = teacher ,supportfile__skills=skill)    )

        customs = [ c for c in list( customs_skills ) if c in list(customs) ]  


    if knowledge_ids :
        customs_knowledges = set()
        for knowledge_id in knowledge_ids :
            knowledge = Knowledge.objects.get(pk = knowledge_id)
            customs_knowledges.update( knowledge.exercises.filter(supportfile__qtype__lt = 100 ,supportfile__author = teacher  ) )
            
        customs = [ c for c in list( customs_knowledges ) if c in list(customs) ] 
    else :

        knowledges = Knowledge.objects.filter(theme_id__in=theme_ids, level__in=level_ids)
        data['knowledges']  = serializers.serialize('json', set(knowledges) ) 


 
    context = {     'teacher' : teacher , 'exercises': set(customs) , 'is_mathJax' : True ,   }
    data['customexercises'] = render_to_string('qcm/ajax_list_customexercises.html', context)

    return JsonResponse(data)


def ajax_customexercises_knowledges(request):

    teacher = request.user.teacher
    subject_ids   = request.POST.getlist('subject_ids', None)
    skill_ids     = request.POST.getlist('skill_ids', None)
    level_ids     = request.POST.getlist('level_ids', None)
    theme_ids     = request.POST.getlist('theme_ids', None)
    knowledge_ids = request.POST.getlist('knowledge_ids', None)
    data = {}

    customs = set()
    for knowledge_id in knowledge_ids :
        knowledge = Knowledge.objects.get(pk = knowledge_id)
        customs.update( knowledge.knowledge_customexercises.filter(teacher=teacher) )
            
    if skill_ids :
        customs_skills = set()
        for skill_id in skill_ids :
            skill = Skill.objects.get(pk = skill_id)
            customs_skills.update( skill.skill_customexercises.filter(teacher=teacher) )
        customs = [ c for c in list( customs_skills ) if c in list(customs) ]  

    data['customexercises'] = render_to_string('qcm/ajax_list_customexercises.html', { 'exercises': set(customs) , 'teacher' : teacher })

    return JsonResponse(data)


def ajax_get_skills(request):
    subject_id = request.POST.get('subject_id', None)
    data = {}
    if subject_id.isdigit():
        subject = Subject.objects.get(id=subject_id)
        skills = subject.skill.values_list('id', 'name')
        data['skills'] = list(skills)

    return JsonResponse(data)
 
 
def ajax_theme_exercice(request):

    level_id   = request.POST.get('level_id', None)
    subject_id = request.POST.get('subject_id', None)
    if level_id.isdigit():
        level      = Level.objects.get(id=level_id)
        themes     = level.themes.filter(subject_id = subject_id)
        knowledges = level.knowledges.filter(theme__in = themes)
        data = {'themes': serializers.serialize('json', themes), 'knowledges': serializers.serialize('json', knowledges) }
    else:
        data = {}
    return JsonResponse(data)


def ajax_theme_subject_levels(request):

    level_ids  = request.POST.getlist('level_ids', None)
    subject_id = request.POST.get('subject_id', None)

    data = {}
    themes = set()
    if subject_id and level_ids[0]!="" :
        for level_id in level_ids :
            level = Level.objects.get(id=level_id)
            lvls = level.themes.filter(subject_id=subject_id)
            themes.update( lvls )
        data = {'themes': serializers.serialize('json', themes)}  
    return JsonResponse(data)




def ajax_level_exercise(request):
    teacher = Teacher.objects.get(user= request.user)
    data = {} 
    level_id = request.POST.get('level_id', None)
    theme_ids = request.POST.getlist('theme_id', None)
    parcours_id = request.POST.get('parcours_id', None)

    if  parcours_id :
        parcours = Parcours.objects.get(id = int(parcours_id))
        ajax = True

    else :
        parcours = None
        ajax = False
        parcours_id = None

    if level_id and theme_ids and theme_ids[0] != "" : 
        exercises = Exercise.objects.filter(Q(supportfile__is_share=1)|Q(supportfile__author_id=teacher.user.id), level_id = level_id , theme_id__in= theme_ids ,  supportfile__is_title=0).order_by("theme","knowledge__waiting","knowledge","ranking")
        data['html'] = render_to_string('qcm/ajax_list_exercises.html', { 'exercises': exercises , "parcours" : parcours, "ajax" : ajax, "teacher" : teacher , 'parcours_id' : parcours_id })
 
    return JsonResponse(data)



def ajax_knowledge_exercise(request):
    theme_id = request.POST.get('theme_id', None)
    level_id = request.POST.get('level_id', None)
    data = {}
 
    knowledges = Knowledge.objects.filter(theme_id=theme_id,level_id=level_id )
    data = {'knowledges': serializers.serialize('json', knowledges)}


    return JsonResponse(data)



def ajax_knowledge_skills_subject_levels(request):
    subject_id = request.POST.get('subject_id', None)
    level_ids  = request.POST.getlist('level_ids', None)
    theme_ids  = request.POST.getlist('theme_ids', None)
    data = {}

    if subject_id and  level_ids[0]!="" and theme_ids[0]!="" :
        knowledges = Knowledge.objects.filter(theme__subject__id=subject_id,level_id__in=level_ids,theme_id__in=theme_ids )
        skills     = Skill.objects.filter(subject_id=subject_id)
        data = {'knowledges': serializers.serialize('json', knowledges) , 'skills': serializers.serialize('json', skills) }

    elif subject_id and  level_ids[0]!=""  :
        knowledges = Knowledge.objects.filter(theme__subject__id=subject_id,level_id__in=level_ids  )
        skills     = Skill.objects.filter(subject_id=subject_id)
        data = {'knowledges': serializers.serialize('json', knowledges) , 'skills': serializers.serialize('json', skills) }

    return JsonResponse(data)





@csrf_exempt
def ajax_create_title_parcours(request):
    ''' Création d'une section ou d'une sous-section dans un parcours '''
    teacher = Teacher.objects.get(user=request.user)

    parcours_id = int(request.POST.get('parcours_id', 0))

    code = str(uuid.uuid4())[:8]
    data = {}

    form = AttachForm(request.POST, request.FILES)

    if form.is_valid():
        
        supportfile = form.save(commit=False)
        supportfile.knowledge_id = 1762
        supportfile.author = teacher
        supportfile.code=code
        supportfile.level_id=13
        supportfile.theme_id=49
        supportfile.is_title=1
        supportfile.save()

        exe = Exercise.objects.create(knowledge_id=1762, level_id=13, theme_id=49, supportfile=supportfile)
        relation = Relationship.objects.create(exercise=exe, parcours_id=parcours_id, ranking=0)

        parcours = Parcours.objects.get(pk = parcours_id)
        for student in parcours.students.all():
            relation.students.add(student)



        if supportfile.attach_file != "" :
            attachment = "<a href='#' target='_blank'>"+ supportfile.title +"</a>"
        else :
            attachment = supportfile.title


        data["html"] = f'''<div class="panel-body separation_dashed" style="line-height: 30px;  border-top-right-radius:5px; border-top-left-radius:5px; background-color : #F2F1F0;id='new_title{exe.id}'">
        <a href='#' style='cursor:move;' class='move_inside'>
            <i class="fas fa-grip-vertical fa-xs" style="color:MediumSeaGreen;vertical-align: text-top;padding-right:5px;"></i>
        </a>
        <input type='hidden' class='div_exercise_id' value='{exe.id}' name='input_exercise_id' />
            <h3>{attachment}
                <a href='#' data-exercise_id='{exe.id}' data-parcours_id='{parcours_id}' class='pull-right erase_title'>
                    <i class='fa fa-times text-danger'></i>
                </a>
            </h3>
        </div>'''

    return JsonResponse(data)



def ajax_erase_title(request):

    exercise_id = int(request.POST.get('exercise_id', None))
    parcours_id = int(request.POST.get('parcours_id', None))    
 
    data = {}

    Relationship.objects.get(exercise_id=exercise_id, parcours_id=parcours_id ).delete()
    Exercise.objects.get(pk = exercise_id ).delete()
 
    return JsonResponse(data)




def relation_is_done(request, id ): #id  = id_content
    relationship = Relationship.objects.get(pk=id)
    return redirect('show_parcours_student' , relationship.parcours.id )


def content_is_done(request, id ): #id  = id_content
    return redirect('exercises' )

 



def ajax_search_exercise(request):

    code =  request.POST.get("search") 
    knowledges = Knowledge.objects.values_list('id',flat=True).filter(name__contains= code).distinct()
    data = {}
    too_much = 'no'

 

    if (knowledges.count())>2:
        too_much = 'yes'
        html = ""

    else :

        if request.user.user_type == 0 :
            student = True
            parcourses = request.user.student.students_to_parcours.values_list('id',flat=True).filter(is_publish=1).distinct()

        elif request.user.user_type == 2 :
            student = False
            parcourses = request.user.teacher.teacher_parcours.values_list('id',flat=True).distinct()

        relationships = Relationship.objects.filter(Q(exercise__knowledge_id__in = knowledges)|Q(exercise__supportfile__annoncement__contains= code)|Q(exercise__supportfile__code__contains= code) , parcours_id__in=parcourses)

        if relationships.count() > 15 :
            too_much = 'yes'
            html = ""
        else :
            html = render_to_string('qcm/search_exercises.html',{ 'relationships' : relationships , 'parcourses' : parcourses , 'student' : student })
     
    data['html'] = html       
    data['too_much'] = too_much
    return JsonResponse(data)



 


 



@login_required(login_url= 'index')
def show_evaluation(request, id):

    parcours = Parcours.objects.get(id=id)
    teacher =  parcours.teacher

    today = time_zone_user(parcours.teacher.user)

    if not teacher_has_permisson_to_parcourses(request,teacher,parcours) :
        return redirect('index')

    relationships_customexercises , nb_exo_only, nb_exo_visible  = ordering_number(parcours)

    role, group , group_id , access = get_complement(request, teacher, parcours)

    skills = Skill.objects.all()

    nb_exercises = parcours.exercises.filter(supportfile__is_title=0).count()

    context = {'relationships_customexercises': relationships_customexercises, 'parcours': parcours, 'teacher': teacher, 'skills': skills, 'communications' : [] ,  
                 'nb_exercises': nb_exercises, 'nb_exo_visible': nb_exo_visible,  
               'nb_exo_only': nb_exo_only, 'group_id': group_id, 'group': group, 'role' : role , 'today' : today }

    return render(request, 'qcm/show_parcours.html', context)





def ajax_charge_folders(request):

    teacher = Teacher.objects.get(user= request.user)
    data = {} 
    group_ids = request.POST.getlist('group_ids', None)

 
    if len(group_ids) :
        flds = set()
        for group_id in group_ids :
            group = Group.objects.get(pk=group_id)
            flds.update(group.group_folders.values_list("id","title").filter(is_trash=0))

        data['folders'] =  list( flds )
    else :
        data['folders'] =  []
 
    return JsonResponse(data)

 


def ajax_course_charge_parcours(request):

    teacher = Teacher.objects.get(user= request.user)
    data = {} 
    id_level = request.POST.get('id_level', None)
    id_subject = request.POST.get('id_subject', None)
    parcours = teacher.teacher_parcours.values_list("id","title").filter(subject_id = id_subject , level_id = id_level )

    data['parcours'] =  list( parcours )

    return JsonResponse(data)



@csrf_exempt   # PublieDépublie un parcours depuis form_group et show_group
def ajax_publish_course(request):  

    course_id = request.POST.get("course_id")
    statut = request.POST.get("statut")
    data = {}
    if statut=="true" or statut == "True":
        data["statut"]  = "false"
        data["publish"] = "Non publié"
        data["style"] = "#dd4b39"
        data["class"] = "legend-btn-danger"
        data["noclass"] = "legend-btn-success"
        data["label"] = "Non publié"
        Course.objects.filter(pk = int(course_id)).update(is_publish = 0)
    else:
        data["statut"] = "true"
        data["publish"] = "Publié" 
        data["style"] = "#00a65a"
        data["class"] = "legend-btn-success"
        data["noclass"] = "legend-btn-danger"
        data["label"] = "Publié"
        Course.objects.filter(pk = int(course_id)).update(is_publish = 1)

    return JsonResponse(data) 

 
 

@csrf_exempt   # PublieDépublie un parcours depuis form_group et show_group
def ajax_sharer_course(request):  

    course_id = request.POST.get("course_id")
    statut = request.POST.get("statut")
 
 
    data = {}
    if statut=="true" or statut == "True":
        statut = 0
        data["statut"]  = "false"
        data["share"]   = "Privé"
        data["style"]   = "#dd4b39"
        data["class"]   = "legend-btn-danger"
        data["noclass"] = "legend-btn-success"
        data["label"]   = "Privé"
    else:
        statut = 1
        data["statut"]  = "true"
        data["share"]   = "Mutualisé"
        data["style"]   = "#00a65a"
        data["class"]   = "legend-btn-success"
        data["noclass"] = "legend-btn-danger"
        data["label"]   = "Mutualisé"

 
 
    Course.objects.filter(pk = int(course_id)).update(is_share = statut)

    return JsonResponse(data) 


#####################################################################################################################################
#####################################################################################################################################
######   Correction des exercices
#####################################################################################################################################
#####################################################################################################################################


@login_required(login_url= 'index')
def correction_exercise(request,id,idp,ids=0):
    """
    script qui envoie au prof les fichiers à corriger custom et SACADO
    """

    teacher = Teacher.objects.get(user=request.user)
    stage = get_stage(teacher.user)
    formComment = CommentForm(request.POST or None)

    folder_id = request.session.get("folder_id",None)

    comments = Comment.objects.filter(teacher = teacher)

    if ids > 0 :
        student = Student.objects.get(pk=ids)
    else : 
        student = None

    nb = 0
    if idp == 0 :
        relationship = Relationship.objects.get(pk=id)

        if student :
            if Writtenanswerbystudent.objects.filter(relationship = relationship , student = student).exists():
                w_a = Writtenanswerbystudent.objects.get(relationship = relationship , student = student)
                annotations = Annotation.objects.filter(writtenanswerbystudent = w_a)
                nb = annotations.count()
            else :
                w_a = False
                annotations = [] 
        else :
            w_a = False 
            annotations = []

        context = {'relationship': relationship,  'teacher': teacher, 'stage' : stage , 'comments' : comments , 'folder_id' : folder_id   , 'formComment' : formComment , 'custom':  False , 'nb':nb, 'w_a':w_a, 'annotations':annotations,  'communications' : [] ,  'parcours' : relationship.parcours , 'parcours_id': relationship.parcours.id, 'group' : None , 'student' : student }
 
        return render(request, 'qcm/correction_exercise.html', context)
    else :
        customexercise = Customexercise.objects.get(pk=id)
        parcours = Parcours.objects.get(pk = idp)
        c_e = False 
        customannotations = []
        images_pdf = []

        if student :
            nb = 0
            images_pdf = []            
            if Customanswerbystudent.objects.filter(customexercise = customexercise ,  parcours = parcours , student_id = student).exists():
                c_e = Customanswerbystudent.objects.get(customexercise = customexercise ,  parcours = parcours , student_id = student)
                images_pdf = [] 
                customannotations = Customannotation.objects.filter(customanswerbystudent = c_e)
                nb = customannotations.count()                 
                if c_e.file :
                    images_pdf = c_e.file

                elif customexercise.is_image :
                    images_pdf = Customanswerimage.objects.filter(customanswerbystudent = c_e)
                elif customexercise.is_realtime :
                    images_pdf = Customanswerimage.objects.filter(customanswerbystudent = c_e).last() 

        context = {'customexercise': customexercise,  'teacher': teacher, 'stage' : stage , 'images_pdf' : images_pdf   ,  'comments' : comments   , 'formComment' : formComment , 'nb':nb, 'c_e':c_e, 'customannotations':customannotations,  'custom': True,  'communications' : [], 'parcours' : parcours, 'group' : None , 'parcours_id': parcours.id, 'student' : student }
 
        return render(request, 'qcm/correction_custom_exercise.html', context)



 
def ajax_closer_exercise(request):

    today = time_zone_user(request.user)
    now = today.now()
    custom =  int(request.POST.get("custom")) 
    exercise_id =  int(request.POST.get("exercise_id")) 

    data = {}

    if custom == 1:
        parcours_id =  int(request.POST.get("parcours_id"))
        if Customexercise.objects.filter(pk = exercise_id).exclude(lock = None).exists() :
            Customexercise.objects.filter(pk = exercise_id ).update(lock = None)   
            data["html"] = "<i class='fa fa-unlock'></i>"    
            data["btn_off"] = "btn-danger"
            data["btn_on"] = "btn-default" 
        else :    
            Customexercise.objects.filter(pk = exercise_id ).update(lock = now) 
            data["html"] = "<i class='fa fa-lock'></i>" 
            data["btn_off"] = "btn-default"
            data["btn_on"] = "btn-danger"      
    else :
        if Relationship.objects.filter(pk = exercise_id,is_lock = 1).exists():
            Relationship.objects.filter(pk = exercise_id).update(is_lock = 0) 
            data["html"] = "<i class='fa fa-unlock'></i>"    
            data["btn_off"] = "btn-danger"
            data["btn_on"] = "btn-default" 
        else :
            Relationship.objects.filter(pk = exercise_id).update(is_lock = 1)  
            data["html"] = "<i class='fa fa-lock'></i>"    
            data["btn_off"] = "btn-default"
            data["btn_on"] = "btn-danger"    
    return JsonResponse(data) 



def ajax_correction_viewer(request):

    custom =  int(request.POST.get("custom")) 
    exercise_id =  int(request.POST.get("exercise_id")) 

    data = {}


    if custom == 1:
        parcours_id =  int(request.POST.get("parcours_id"))
        if Customexercise.objects.filter(pk = exercise_id).exclude(is_publish_cor = 1).exists() :
            Customexercise.objects.filter(pk = exercise_id ).update(is_publish_cor = 1)   
            data["html"] = "<i class='fa fa-eye-slash'></i>"    
            data["btn_off"] = "btn-danger"
            data["btn_on"] = "btn-default" 
        else :    
            Customexercise.objects.filter(pk = exercise_id ).update(is_publish_cor = 0)  
            data["html"] = "<i class='fa fa-eye'></i>" 
            data["btn_off"] = "btn-default"
            data["btn_on"] = "btn-danger"      
    else :
        if Relationship.objects.filter(pk = exercise_id,is_correction_visible = 1).exists():
            Relationship.objects.filter(pk = exercise_id).update(is_correction_visible = 0) 
            data["html"] = "<i class='fa fa-eye-slash'></i>"    
            data["btn_off"] = "btn-danger"
            data["btn_on"] = "btn-default" 
        else :
            Relationship.objects.filter(pk = exercise_id).update(is_correction_visible = 1)  
            data["html"] = "<i class='fa fa-eye'></i>"    
            data["btn_off"] = "btn-default"
            data["btn_on"] = "btn-danger"    
    return JsonResponse(data) 


 



@csrf_exempt  
def ajax_save_annotation(request):

    data = {}

    custom =  int(request.POST.get("custom"))
    answer_id =  request.POST.get("answer_id") 
    attr_id = request.POST.get("attr_id") 
    style = request.POST.get("style") 
    classe = request.POST.get("classe") 
    studentcontent = request.POST.get("studentcontent") 

    if custom :
        annotation, created = Customannotation.objects.get_or_create(customanswerbystudent_id = answer_id,attr_id = attr_id , defaults = {  'classe' : classe, 'style' : style , 'content' : studentcontent} )
        if not created :
            Customannotation.objects.filter(customanswerbystudent_id = answer_id, attr_id = attr_id).update(content = studentcontent, style = style)
    else :
        annotation, created = Annotation.objects.get_or_create(writtenanswerbystudent_id = answer_id,attr_id = attr_id , defaults = {  'classe' : classe, 'style' : style , 'content' : studentcontent} )
        if not created :
            Annotation.objects.filter(writtenanswerbystudent_id = answer_id, attr_id = attr_id).update(content = studentcontent, style = style)

    return JsonResponse(data)  



@csrf_exempt  
def ajax_remove_annotation(request):
    """
    Suppression d'une appréciation par un enseignant
    """

    data = {}
    custom =  int(request.POST.get("custom"))
    attr_id = request.POST.get("attr_id") 
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    answer_id = request.POST.get("answer_id") 
    try :
        if custom :
            Customannotation.objects.get(customanswerbystudent_id = answer_id,  attr_id = attr_id ).delete()
        else :  
            Annotation.objects.get(writtenanswerbystudent_id  = answer_id, attr_id = attr_id).delete()
    except :
        pass

    return JsonResponse(data)  


####Sélection des élèves par AJAX --- N'est pas utilisé ---A supprimer éventuellement avec son url 
def ajax_choose_student(request): # Ouvre la page de la réponse des élèves à un exercice non auto-corrigé

    relationship_id =  int(request.POST.get("relationship_id")) 
    student_id =  int(request.POST.get("student_id"))
    student = Student.objects.get(pk = student_id)   
    data = {}
    custom = int(request.POST.get("custom"))

 
    comments = Comment.objects.filter(teacher = teacher)
 
    if request.POST.get("custom") == "0" :

        relationship = Relationship.objects.get(pk = int(relationship_id))
        teacher = relationship.parcours.teacher
        if Writtenanswerbystudent.objects.filter(relationship = relationship , student = student).exists():
            w_a = Writtenanswerbystudent.objects.get(relationship = relationship , student = student)
        else :
            w_a = False 
     
        context = { 'relationship' : relationship , 'student': student ,   'w_a' : w_a,   'teacher' : teacher, 'comments' : comments      }

        html = render_to_string('qcm/ajax_correction_exercise.html', context )   

    else :

        customexercise = Customexercise.objects.get(pk = relationship_id)
        parcours_id =  int(request.POST.get("parcours_id"))
        parcours = Parcours.objects.get(pk = parcours_id)
        teacher = customexercise.teacher
        if Customanswerbystudent.objects.filter(customexercise = customexercise ,  parcours = parcours , student = student).exists():
            c_e = Customanswerbystudent.objects.get(customexercise = customexercise ,   parcours = parcours , student = student )
        else :
            c_e = False 

        context = { 'customexercise' : customexercise , 'student': student ,   'c_e' : c_e , 'parcours_id' :  parcours_id,   'teacher' : teacher , 'comments' : comments  }

        html = render_to_string('qcm/ajax_correction_exercise_custom.html', context )
     
    data['html'] = html       

    return JsonResponse(data)







def ajax_exercise_evaluate(request): # Evaluer un exercice non auto-corrigé

    student_id =  int(request.POST.get("student_id"))
    value =  int(request.POST.get("value"))
    typ =  int(request.POST.get("typ")) 
    data = {}

    student = Student.objects.get(user_id = student_id)  

    stage = get_stage(student.user) 


    tab_label = ["","text-danger","text-warning","text-success","text-primary"]
    tab_value = [-1, stage["low"]-1,stage["medium"]-1,stage["up"]-1,100]       


    if typ == 0 : 

        knowledge_id = request.POST.get("knowledge_id",None)       
        skill_id = request.POST.get("skill_id",None)

        relationship_id =  int(request.POST.get("relationship_id"))   
        relationship = Relationship.objects.get(pk = relationship_id)

        Writtenanswerbystudent.objects.filter(relationship  = relationship  , student  = student).update(is_corrected = 1)

        if tab_value[value] > -1 :
            if knowledge_id :
                studentanswer, creator = Studentanswer.objects.get_or_create(parcours = relationship.parcours, exercise = relationship.exercise, student = student , defaults={"point" : tab_value[value] , 'secondes' : 0} )
                if not creator :
                    Studentanswer.objects.filter(parcours  = relationship.parcours, exercise = relationship.exercise , student  = student).update(point= tab_value[value])
                # Moyenne des scores obtenus par savoir faire enregistré dans Resultknowledge
                knowledge = relationship.exercise.knowledge
                scored = 0
                studentanswers = Studentanswer.objects.filter(student = student,exercise__knowledge = knowledge) 
                for studentanswer in studentanswers:
                    scored +=  studentanswer.point 
                try :
                    scored = scored/len(studentanswers)
                except :
                    scored = 0
                result, created = Resultknowledge.objects.get_or_create(knowledge  = relationship.exercise.knowledge , student  = student , defaults = { "point" : scored , })
                if not created :
                    Resultknowledge.objects.filter(knowledge  = relationship.exercise.knowledge , student  = student).update(point= scored)
                
                resultat, crtd = Writtenanswerbystudent.objects.get_or_create(relationship  = relationship  , student  = student , defaults = { "is_corrected" : 1 , })
                if not crtd :
                    Writtenanswerbystudent.objects.filter(relationship  = relationship  , student  = student).update(is_corrected = 1)


            if skill_id :
            # Moyenne des scores obtenus par compétences enregistrées dans Resultskill
                skill = Skill.objects.get(pk = skill_id )
                Resultskill.objects.create(student = student, skill = skill, point = tab_value[value]) 
                resultskills = Resultskill.objects.filter(student = student, skill = skill).order_by("-id")[0:10]
                sco = 0
                for resultskill in resultskills :
                    sco += resultskill.point
                    try :
                        sco_avg = sco/len(resultskills)
                    except :
                        sco_avg = 0
                result, creat = Resultlastskill.objects.get_or_create(student = student, skill = skill, defaults = { "point" : sco_avg , })
                if not creat :
                    Resultlastskill.objects.filter(student = student, skill = skill).update(point = sco_avg) 

                result, creater = Resultggbskill.objects.get_or_create(student = student, skill = skill, relationship = relationship, defaults = { "point" : tab_value[value] , })
                if not creater :
                    Resultggbskill.objects.filter(student = student, skill = skill, relationship = relationship).update(point = tab_value[value]) 

    else :
       
        customexercise_id =  int(request.POST.get("customexercise_id"))  
 
        parcours_id =  int(request.POST.get("parcours_id")) 
        knowledge_id = request.POST.get("knowledge_id",None)       
        skill_id = request.POST.get("skill_id",None)

        Customanswerbystudent.objects.filter(parcours_id = parcours_id , customexercise_id = customexercise_id, student = student).update(is_corrected = 1)

        if tab_value[value] > -1 :
  
            if skill_id : 
                result, created = Correctionskillcustomexercise.objects.get_or_create(parcours_id = parcours_id , customexercise_id = customexercise_id, student  = student , skill_id = skill_id   , defaults = { "point" : tab_value[value]  })
                if not created :
                    Correctionskillcustomexercise.objects.filter(parcours_id = parcours_id , customexercise_id = customexercise_id, student  = student, skill_id = skill_id ).update(point= tab_value[value] )

            if knowledge_id : 
                result, created = Correctionknowledgecustomexercise.objects.get_or_create(parcours_id = parcours_id , customexercise_id = customexercise_id, student  = student , knowledge_id = knowledge_id  ,  defaults = {  "point" : tab_value[value]  })
                if not created :
                    Correctionknowledgecustomexercise.objects.filter(parcours_id = parcours_id , customexercise_id = customexercise_id, student  = student , knowledge_id = knowledge_id ).update(point= tab_value[value] )

    data['eval'] = "<i class = 'fa fa-check text-success pull-right'></i>"

    return JsonResponse(data)  


 

def ajax_annotate_exercise_no_made(request): # Marquer un exercice non fait

    student_id =  int(request.POST.get("student_id"))
    exercise_id =  int(request.POST.get("exercise_id"))  
    parcours_id =  int(request.POST.get("parcours_id")) 
    custom =  int(request.POST.get("custom")) 
    data = {}
    if custom :
        Customanswerbystudent.objects.update_or_create(parcours_id = parcours_id , customexercise_id = exercise_id, student_id = student_id,defaults={"answer":"", "comment":"Non rendu", "point":0,"is_corrected":1})
    else :
        Writtenanswerbystudent.objects.update_or_create(relationship_id = exercise_id , student_id = student_id,defaults={"answer":"", "comment":"Non rendu",  "is_corrected":1})     

    return JsonResponse(data)  




def ajax_mark_evaluate(request): # Evaluer un exercice custom par note

    student_id =  int(request.POST.get("student_id"))
    mark =  request.POST.get("mark")
    data = {}
    student = Student.objects.get(user_id = student_id) 
    if int(request.POST.get("custom")) == 1 :

        customexercise_id =  int(request.POST.get("customexercise_id"))  
        parcours_id =  int(request.POST.get("parcours_id")) 
        this_custom = Customanswerbystudent.objects.filter(parcours_id = parcours_id , customexercise_id = customexercise_id, student = student)
        this_custom.update(is_corrected= 1)
        this_custom.update(point= mark)
        exercise =  Customexercise.objects.get(pk = customexercise_id)

    else :

        relationship_id =  int(request.POST.get("relationship_id"))  
        this_exercise = Writtenanswerbystudent.objects.filter(relationship_id = relationship_id ,   student = student)
        this_exercise.update(is_corrected= 1)
        this_exercise.update(point= mark)
        relationship = Relationship.objects.get(pk = relationship_id)
        exercise = relationship.exercise.supportfile.annoncement

    if student.user.email :
        msg = "Vous venez de recevoir la note : "+ str(mark)+" pour l'exercice "+str(exercise) 
        sending_mail("SacAdo Exercice posté",  msg , settings.DEFAULT_FROM_EMAIL , [student.user.email] )


    data['eval'] = "<i class = 'fa fa-check text-success pull-right'></i>"             

    return JsonResponse(data)  





def ajax_comment_all_exercise(request): # Ajouter un commentaire à un exercice non auto-corrigé

    student_id =  int(request.POST.get("student_id"))
    comment =  cleanhtml(unescape_html(request.POST.get("comment")))

    exercise_id =  int(request.POST.get("exercise_id"))  

    saver =  int(request.POST.get("saver"))

    student = Student.objects.get(user_id = student_id)  

    if int(request.POST.get("typ")) == 0 :
        relationship = Relationship.objects.get(pk = exercise_id)
        Writtenanswerbystudent.objects.filter(relationship = relationship, student = student).update(comment = comment )
        Writtenanswerbystudent.objects.filter(relationship = relationship, student = student).update(is_corrected = 1 )
        exercise = relationship.exercise.supportfile.annoncement
        if saver == 1:
            Generalcomment.objects.create(comment=comment, teacher = relationship.parcours.teacher)

    else  :
        parcours_id =  int(request.POST.get("parcours_id"))     
        exercise = Customexercise.objects.get(pk = exercise_id)
        Customanswerbystudent.objects.filter(customexercise = exercise, student = student, parcours_id = parcours_id).update(comment = comment )
        Customanswerbystudent.objects.filter(customexercise = exercise, student = student, parcours_id = parcours_id).update(is_corrected = 1 )

        if saver == 1:
            Generalcomment.objects.create(comment=comment, teacher = exercise.teacher)

    if student.user.email :
        msg = "Vous venez de recevoir une appréciation pour l'exercice "+str(exercise)+"\n\n  "+str(comment) 
        sending_mail("SacAdo Exercice posté",  msg , settings.DEFAULT_FROM_EMAIL , [student.user.email] )

    data = {}
    data['eval'] = "<i class = 'fa fa-check text-success pull-right'></i>"          
    return JsonResponse(data)  




@csrf_exempt
def ajax_audio_comment_all_exercise(request): # Ajouter un commentaire à un exercice non auto-corrigé


    data = {}
    student_id =  int(request.POST.get("id_student"))
    audio_text = request.FILES.get("id_mediation")
    student = Student.objects.get(user_id = student_id)

    id_relationship =  int(request.POST.get("id_relationship"))  

    if int(request.POST.get("custom")) == 0 :
        exercise = Relationship.objects.get(pk = id_relationship)

        if Writtenanswerbystudent.objects.filter(student = student , relationship = exercise).exists() :
            w_a = Writtenanswerbystudent.objects.get(student = student , relationship = exercise) # On récupère la Writtenanswerbystudent
            form = WAnswerAudioForm(request.POST or None, request.FILES or None,instance = w_a )
        else :
            form = WAnswerAudioForm(request.POST or None, request.FILES or None )

        if form.is_valid() :
            nf =  form.save(commit = False)
            nf.audio = audio_text
            nf.relationship = exercise
            nf.student = student
            nf.is_corrected = True                     
            nf.save()

    else  :

        parcours_id =  int(request.POST.get("id_parcours"))  
        parcours = Parcours.objects.get(pk = parcours_id)
        exercise = Customexercise.objects.get(pk = id_relationship)
        
        if Customanswerbystudent.objects.filter(customexercise  = exercise, student = student , parcours = parcours).exists() :
            c_e = Customanswerbystudent.objects.get(customexercise  = exercise, student = student , parcours = parcours) # On récupère la Customanswerbystudent
            form = CustomAnswerAudioForm(request.POST or None, request.FILES or None,instance = c_e )
        else :
            form = CustomAnswerAudioForm(request.POST or None, request.FILES or None )

        if form.is_valid() :
            nf =  form.save(commit = False)
            nf.audio = audio_text
            nf.customexercise = exercise
            nf.student = student
            nf.parcours = parcours
            nf.is_corrected = True    
            nf.save()


    if student.user.email :
        msg = "Vous venez de recevoir une appréciation orale pour l'exercice "+str(exercise)+"\n\n  "+str(comment) 
        sending_mail("SacAdo Exercice posté",  msg , settings.DEFAULT_FROM_EMAIL , [student.user.email] )

    data = {}
    data['eval'] = "<i class = 'fa fa-check text-success pull-right'></i>"          
    return JsonResponse(data)  




@csrf_exempt  
def audio_remediation(request):

    data = {}
    idr =  int(request.POST.get("id_relationship"))
    relationship = Relationship.objects.get(pk=idr) 
    form = RemediationForm(request.POST or None, request.FILES or None )

    if form.is_valid():
        nf =  form.save(commit = False)
        nf.mediation = request.FILES.get("id_mediation")
        nf.relationship = relationship
        nf.audio = True

        nf.save()
    else:
        print(form.errors)

    return JsonResponse(data)  





def ajax_read_my_production(request): # Propose à un élève de lire sa copie depuis son parcours

    student_id =  int(request.POST.get("student_id"))
    exercise_id =  int(request.POST.get("exercise_id"))  
    custom =  int(request.POST.get("custom")) 
    student = Student.objects.get(pk=student_id)

    data = {}

    if custom :
        customexercise = Customexercise.objects.get(pk=exercise_id)
        response = Customanswerbystudent.objects.get(customexercise  = customexercise , student  = student )
        annotations = Customannotation.objects.filter(customanswerbystudent  = response)

        context = { 'customexercise' : customexercise , 'student': student ,   'custom' : True , 'response' :  response,   'annotations' : annotations   }

    else :
        relationship = Relationship.objects.get(pk=exercise_id)
        response = Writtenanswerbystudent.objects.get(relationship  = relationship  , student  = student )
        annotations = Annotation.objects.filter(writtenanswerbystudent = response)
 
        context = { 'relationship' : relationship , 'student': student ,   'custom' : False , 'response' :  response,   'annotations' : annotations   }

    html = render_to_string('qcm/ajax_student_restitution.html', context )
     
    data['html'] = html    
            

    return JsonResponse(data) 

 
###################################################################
######   Création des commentaires de correction
###################################################################
@csrf_exempt  
def ajax_create_or_update_appreciation(request):

    data = {}
    comment_id = request.POST.get("comment_id",None)
    comment = request.POST.get("comment",None)
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    # Choix du formulaire à compléter
    if comment_id :
        appreciation = Comment.objects.get(pk = int(comment_id) )
        formComment = CommentForm(request.POST or None, instance = appreciation ) # Formulaire existant
    else :
        formComment = CommentForm(request.POST or None ) # Formulaire nouvelle appréciation
 
    if formComment.is_valid(): # Analyse du formulaire
        nf =  formComment.save(commit = False)
        nf.teacher = teacher
        nf.save() # Enregistrement

    if comment_id :
        data["comment_id"] = nf.pk
        data["comment"] = nf.comment
    else :
        nb = Comment.objects.filter(teacher= teacher).count() + 1
        data["html"] = "<button id='comment"+str(nb)+"' data-nb="+str(nb)+" data-text=\""+str(nf.comment)+"\" class='btn btn-default comment'>"+str(nf.comment)+"</button>"

    return JsonResponse(data)  





@csrf_exempt  
def ajax_remove_my_appreciation(request):

    data = {}
    comment_id = request.POST.get("comment_id")
    appreciation = Comment.objects.get(pk = int(comment_id) )
    appreciation.delete()

    return JsonResponse(data)  


#####################################################################################################################################
#####################################################################################################################################
######   Fin des outils de correction
#####################################################################################################################################
#####################################################################################################################################





def ajax_add_criterion(request):
    data      = {}
    level     = request.POST.get("level")
    subject   = request.POST.get("subject")
    knowledge = request.POST.get("knowledge")
    skill     = request.POST.get("skill")
    label     = request.POST.get("label")

    Criterion.objects.create(label=label, subject_id=subject,  level_id=level ,  knowledge_id=knowledge ,  skill_id=skill  )
 
    if  knowledge and skill :
        data["criterions"] = list(Criterion.objects.values_list('id','label').filter(Q( knowledge_id=knowledge)| Q(skill_id=skill ) ,  subject_id=subject,  level_id=level ))
    elif  knowledge  :
        data["criterions"] = list(Criterion.objects.values_list('id','label').filter(knowledge_id=knowledge,  subject_id=subject,  level_id=level ))
    elif  skill  :
        data["criterions"] = list(Criterion.objects.values_list('id','label').filter(skill_id=skill,  subject_id=subject,  level_id=level ))
    else :
        data["criterions"] = list(Criterion.objects.values_list('id','label').filter(  subject_id=subject,  level_id=level ))

    return JsonResponse(data)  


def ajax_auto_evaluation(request):
    data      = {}
    customexercise_id     = request.POST.get("customexercise_id")
    parcours_id   = request.POST.get("parcours_id")
    student_id = request.POST.get("student_id")
    criterion_id    = request.POST.get("criterion_id")
    position     = request.POST.get("position")
    auto , created = Autoposition.objects.get_or_create( customexercise_id=customexercise_id, parcours_id=parcours_id,  student_id=student_id ,  criterion_id=criterion_id , defaults={  'position' : position }  )
    return JsonResponse(data)  




@login_required(login_url= 'index')   
def parcours_delete_custom_exercise(request,idcc,id ): # Suppression d'un exercice non autocorrigé dans un parcours

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')
    custom = Customexercise.objects.get(pk=idcc)

    folder_id = request.session.get("folder_id",0)


    if not authorizing_access(teacher, custom,True):
        messages.error(request, "  !!!  Redirection automatique  !!! Violation d'accès. Contacter SACADO...")
        return redirect('index')

    if id == 0 :   
        custom.delete() 
        return redirect('exercises')
    else :
        parcours = Parcours.objects.get(pk=id)
        custom.parcourses.remove(parcours)
        custom.delete() 
        return redirect('show_parcours', folder_id , id )
 




@login_required(login_url= 'index') 
def write_custom_exercise(request,id,idp): # Coté élève - exercice non autocorrigé
 
    user = request.user
    student = user.student
    customexercise = Customexercise.objects.get(pk = id)
    parcours = Parcours.objects.get(pk = idp)
    today = time_zone_user(user)

    try :
        tracker_execute_exercise(True , user , idp  , id , 1) 
    except :
        pass


    if customexercise.is_realtime :
        on_air = True
    else :
        on_air = False   
 

    if Customanswerbystudent.objects.filter(student = student, customexercise = customexercise ).exists() : 
        c_e = Customanswerbystudent.objects.get(student = student, customexercise = customexercise )
        cForm = CustomanswerbystudentForm(request.POST or None, request.FILES or None, instance = c_e )
        images = Customanswerimage.objects.filter(customanswerbystudent = c_e) 

    else :
        cForm = CustomanswerbystudentForm(request.POST or None, request.FILES or None )
        c_e = False
        images = False

    if customexercise.is_image :
        form_ans = inlineformset_factory( Customanswerbystudent , Customanswerimage , fields=('image',) , extra=1)
    else :
        form_ans = None


    if request.method == "POST":
        if cForm.is_valid():
            w_f = cForm.save(commit=False)
            w_f.customexercise = customexercise
            w_f.parcours_id = idp
            w_f.student = student
            w_f.is_corrected = 0
            w_f.save()

            if customexercise.is_image :
                form_images = form_ans(request.POST or None,  request.FILES or None, instance = w_f)
                for form_image in form_images :
                    if form_image.is_valid():
                        form_image.save()

            ### Envoi de mail à l'enseignant
            msg = "Exercice : "+str(unescape_html(cleanhtml(customexercise.instruction)))+"\n Parcours : "+str(parcours.title)+", posté par : "+str(student.user) +"\n\n sa réponse est \n\n"+str(cForm.cleaned_data['answer'])

            if customexercise.teacher.notification :
                sending_mail("SACADO Exercice posté",  msg , settings.DEFAULT_FROM_EMAIL , [customexercise.teacher.user.email] )
                pass

            return redirect('show_parcours_student' , idp )

    context = {'customexercise': customexercise, 'communications' : [] , 'c_e' : c_e , 'form' : cForm , 'images':images, 'form_ans' : form_ans , 'parcours' : parcours ,'student' : student, 'today' : today , 'on_air' : on_air}

    if customexercise.is_python :
        url = "basthon/index_custom.html" 
    else :
        pad_student = str(student.user.id)+"_"+str(idp)+"_"+str(customexercise.id)
        context.update(pad_student=pad_student)
        url = "qcm/form_writing_custom.html" 

    return render(request, url , context)
 

 

 






#################################################################################################################
#################################################################################################################
################   Canvas
#################################################################################################################
#################################################################################################################
@login_required(login_url= 'index') 
def show_canvas(request):
    user = request.user
    context = { "user" :  user  }
 
    return render(request, 'qcm/show_canvas.html', context)



@login_required(login_url= 'index') 
def ajax_save_canvas(request):

    actions           = request.POST.get("actions",None)
    customexercise_id = request.POST.get("customexercise_id",0)
    parcours_id       = request.POST.get("parcours_id",0)

    try :
        student = request.user.student
    except :
        messages.error(request,"Vous n'êtes pas élève ou pas connecté.")
        return redirect('index')

    customexercise    = Customexercise.objects.get(pk = customexercise_id)
    parcours          = Parcours.objects.get(pk = parcours_id)
    today             = time_zone_user(student.user).now()
    data = {}
 

    if request.method == "POST":
        c_ans , created = Customanswerbystudent.objects.get_or_create(customexercise_id = customexercise_id , parcours_id = parcours_id , student = student , defaults = { 'date' : today , 'answer' : actions} )
        if not created :
            Customanswerbystudent.objects.filter(customexercise_id = customexercise_id , parcours_id = parcours_id , student = student ).update(date = today)
            Customanswerbystudent.objects.filter(customexercise_id = customexercise_id , parcours_id = parcours_id , student = student ).update(answer = actions)
 
    return JsonResponse(data)
 

def ajax_delete_custom_answer_image(request):
    data = {}
    custom = request.POST.get("custom")
    image_id = request.POST.get("image_id")
    Customanswerimage.objects.get(pk = int(image_id)).delete()
    return JsonResponse(data)  



@login_required(login_url= 'index') 
def asking_parcours_sacado(request,pk):
    """demande de parcours par un élève"""

    try :
        student = request.user.student
    except :
        messages.error(request,"Vous n'êtes pas élève ou pas connecté.")
        return redirect('index')
    
    group = Group.objects.get(pk = pk)

    teacher_id = get_teacher_id_by_subject_id(group.subject.id)

    teacher = Teacher.objects.get(pk=teacher_id)

    subject = group.subject
    level = group.level

    parcourses = teacher.teacher_parcours.filter(level = level, subject = subject)


    test = attribute_all_documents_of_groups_to_a_new_students((group,), student)

    if test :
        test_string = "Je viens de récupérer les exercices."
    else :
        test_string = "Je ne parviens pas à récupérer les exercices."    

    msg = "Je souhaite utiliser les parcours Sacado de mon niveau de "+str(level)+", mon enseignant ne les utilise pas. "+test_string+" Merci.\n\n"+str(student)

    sending_mail("Demande de parcours SACADO",  msg , settings.DEFAULT_FROM_EMAIL , ["brunoserres33@gmail.com", "sacado.asso@gmail.com"] )

    return redirect("dashboard_group",pk)

#######################################################################################################################################################################
############### VUE ENSEIGNANT
#######################################################################################################################################################################

def show_write_exercise(request,id): # vue pour le prof de l'exercice non autocorrigé par le prof

    relationship = Relationship.objects.get(pk = id)
    parcours = relationship.parcours
    today = timezone.now()

    wForm = WrittenanswerbystudentForm(request.POST or None, request.FILES or None )

    context = { 'relationship' : relationship, 'communications' : [] ,  'parcours' : parcours , 'today' : today ,  'form' : wForm,  'student' : None, }

    if relationship.exercise.supportfile.is_python :
        url = "basthon/index.html" 
    else :
        return show_all_type_exercise(request,relationship.exercise.supportfile.id) 

    return render(request, url , context)


def show_custom_exercise(request,id,idp): # vue pour le prof de l'exercice non autocorrigé par le prof

    customexercise = Customexercise.objects.get(pk = id)
    parcours = Parcours.objects.get(pk = idp)
    today = timezone.now()

    context = { 'customexercise' : customexercise, 'communications' : [] ,  'parcours' : parcours , 'today' : today , 'student' : None, }

    if customexercise.is_python :
        url = "basthon/index_custom.html" 
    else :
        url = "qcm/form_writing_custom.html" 

    return render(request, url , context)


def show_custom_sequence(request,idc): # vue pour le prof de l'exercice non autocorrigé par le prof

    customexercise = Customexercise.objects.get(pk = idc)
    today = timezone.now()

    context = { 'customexercise' : customexercise, 'today' : today , 'student' : None, 'only_show' : False }

    if customexercise.is_python :
        url = "basthon/index_custom.html" 
    else :
        url = "qcm/form_writing_custom.html" 

    return render(request, url , context)


#######################################################################################################################################################################
#######################################################################################################################################################################
#################   Task
#######################################################################################################################################################################
#######################################################################################################################################################################

  
def detail_task_parcours(request,id,s,c):

  
    parcours = Parcours.objects.get(pk=id) 
    teacher = parcours.teacher

    today = time_zone_user(teacher.user)
    date_today = today.date() 

    role, group , group_id , access = get_complement(request, teacher, parcours)

    if not teacher_has_permisson_to_parcourses(request,teacher,parcours) :
        return redirect('index')

    if s == 0 : # groupe

 
        relationships = Relationship.objects.filter(Q(is_publish = 1)|Q(start__lte=today), parcours =parcours,exercise__supportfile__is_title=0).exclude(date_limit=None).order_by("-date_limit") 
        customexercises = Customexercise.objects.filter( parcourses = parcours,  )


        context = {'relationships': relationships, 'customexercises': customexercises ,  'parcours': parcours ,  'today':today ,  'communications' : [] ,  'date_today':date_today ,  'group_id' : group_id ,  'role' : role ,  }
 
        return render(request, 'qcm/list_tasks.html', context)
    else : # exercice
        if c == 0:
            exercise = Exercise.objects.get(pk=s)
            students = students_from_p_or_g(request,parcours) 
            details_tab = []
            for s in students :
                details = {}
                details["student"]=s.user
                try : 
                    studentanswer = Studentanswer.objects.filter(exercise= exercise, student = s).last()
                    details["point"]= studentanswer.point
                    details["numexo"]=  studentanswer.numexo
                    details["date"]= studentanswer.date 
                    details["secondes"]= convert_seconds_in_time(int(studentanswer.secondes))
                except :
                    details["point"]= ""
                    details["numexo"]=  ""
                    details["date"]= ""
                    details["secondes"]= ""
                details_tab.append(details)
                relationship = Relationship.objects.get( parcours =parcours,exercise= exercise)

        else :
            exercise = Customexercise.objects.get(pk=s)
            students = students_from_p_or_g(request,parcours) 
            details_tab = []
            for s in students :
                details = {}
                details["student"]=s.user
                try : 
                    customanswer = Customanswerbystudent.objects.filter(exercise= exercise, parcours = parcours, student = s).last()
                    details["point"]= customanswer.point
                    details["numexo"]=  customanswer.comment
                    details["date"]= ""
                    details["secondes"]= ""
                except :
                    details["point"]= ""
                    details["numexo"]=  ""
                    details["date"]= ""
                    details["secondes"]= ""
                details_tab.append(details)
                relationship = Customexercise.objects.get( parcours =parcours,exercise= exercise)


         
        context = {'details_tab': details_tab, 'parcours': parcours ,   'exercise' : exercise , 'relationship': relationship,  'date_today' : date_today, 'communications' : [] ,  'group_id' : group_id , 'role' : role }

        return render(request, 'qcm/task.html', context)


@login_required(login_url= 'index') 
def detail_task(request,id,s):

    parcours = Parcours.objects.get(pk=id) 
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    today = time_zone_user(teacher.user) 

    role, group , group_id , access = get_complement(request, teacher, parcours)

    if not teacher_has_permisson_to_parcourses(request,teacher,parcours) :
        return redirect('index')

    if s == 0 : # groupe
 
        relationships = Relationship.objects.filter(Q(is_publish = 1)|Q(start__lte=today), parcours =parcours,exercise__supportfile__is_title=0).exclude(date_limit=None).order_by("-date_limit")  
        context = {'relationships': relationships, 'parcours': parcours , 'today':today ,   'communications' : [],  'role' : role ,  'group_id' : group_id }
        return render(request, 'qcm/list_tasks.html', context)
    else : # exercice

        exercise = Exercise.objects.get(pk=s)
        students = students_from_p_or_g(request,parcours) 
        details_tab = []
        for s in students :
            details = {}
            details["student"]=s.user
            try : 
                studentanswer = Studentanswer.objects.filter(exercise= exercise, student = s).last()
                details["point"]= studentanswer.point
                details["numexo"]=  studentanswer.numexo
                details["date"]= studentanswer.date 
                details["secondes"]= convert_seconds_in_time(int(studentanswer.secondes))
            except :
                details["point"]= ""                      
                details["numexo"]=  ""
                details["date"]= ""
                details["secondes"]= ""
            details_tab.append(details)

        relationship = Relationship.objects.get( parcours =parcours,exercise= exercise)


        context = {'details_tab': details_tab, 'parcours': parcours ,   'exercise' : exercise , 'relationship': relationship,  'today' : today ,  'communications' : [],  'role' : role ,  'group_id' : group_id}

        return render(request, 'qcm/task.html', context)


@login_required(login_url= 'index') 
def all_my_tasks(request):
    today = time_zone_user(request.user) 
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')
    parcourses = Parcours.objects.filter(is_publish=  1,teacher=teacher ,is_trash=0)
    relationships = Relationship.objects.filter(Q(is_publish = 1)|Q(start__lte=today), parcours__teacher=teacher, date_limit__gte=today,exercise__supportfile__is_title=0).order_by("parcours") 
    context = {'relationships': relationships, 'parcourses': parcourses, 'parcours': None,  'communications' : [] , 'relationships' : [] , 'group_id' : None  , 'role' : False , }
    return render(request, 'qcm/all_tasks.html', context)


@login_required(login_url= 'index') 
def these_all_my_tasks(request):
    today = time_zone_user(request.user) 
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index') 
    parcourses = Parcours.objects.filter(is_publish=  1,teacher=teacher ,is_trash=0)
    relationships = Relationship.objects.filter(Q(is_publish = 1)|Q(start__lte=today), parcours__teacher=teacher, exercise__supportfile__is_title=0).exclude(date_limit=None).order_by("parcours") 
    context = {'relationships': relationships, 'parcourses': parcourses, 'parcours': None,  'communications' : [] ,  'relationships' : [] ,'group_id' : None  , 'role' : False , } 
    return render(request, 'qcm/all_tasks.html', context)



 
@login_required(login_url= 'index') 
def group_tasks(request,id):


    group = Group.objects.get(pk = id)
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')
    today = time_zone_user(request.user) 

    nb_parcours_teacher = teacher.teacher_parcours.count() # nombre de parcours pour un prof
    students = group.students.prefetch_related("students_to_parcours")
    parcourses_tab = []
    for student in students :
        parcourses = student.students_to_parcours.all()
        for p in parcourses :
            if len(parcourses_tab) >= nb_parcours_teacher :
                break
            else :
                parcourses_tab.append(p)

    role, group , group_id , access = get_complement(request, teacher, group)
    group = Group.objects.get(pk = id)

    relationships = Relationship.objects.filter(Q(is_publish = 1)|Q(start__lte=today), parcours__in=parcourses_tab, date_limit__gte=today,exercise__supportfile__is_title=0).order_by("parcours") 
    context = { 'relationships': relationships , 'group' : group , 'parcours' : None , 'communications' : [] , 'relationships' : [] , 'group_id' : group.id , 'role' : role , }

    return render(request, 'qcm/group_task.html', context)


@login_required(login_url= 'index')
def group_tasks_all(request,id):

    group = Group.objects.get(pk = id)
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')
    today = time_zone_user(teacher.user) 
    nb_parcours_teacher = teacher.teacher_parcours.count() # nombre de parcours pour un prof

    students = group.students.prefetch_related("students_to_parcours")
    parcourses_tab = []
    for student in students :
        parcourses = student.students_to_parcours.all()
        for p in parcourses :
            if len(parcourses_tab) >= nb_parcours_teacher :
                break
            else :
                parcourses_tab.append(p)

    role, group , group_id , access = get_complement(request, teacher, group)
    group = Group.objects.get(pk = id)
    
    relationships = Relationship.objects.filter(Q(is_publish = 1)|Q(start__lte=today),  parcours__in=parcourses_tab, exercise__supportfile__is_title=0).exclude(date_limit=None).order_by("parcours") 
    context = { 'relationships': relationships ,    'group' : group , 'parcours' : None , 'relationships' : [] , 'communications' : [] ,  'group_id' : group.id , 'role' : role ,  }
    
    return render(request, 'qcm/group_task.html', context )



@login_required(login_url= 'index')
def my_child_tasks(request,id):
    user = request.user
    today = time_zone_user(user) 
    parent = user.parent
    student = Student.objects.get(pk = id) 

    if not student in parent.students.all() :
        return redirect('index')

    relationships = Relationship.objects.filter(Q(is_publish = 1)|Q(start__lte=today), parcours__students = student, exercise__supportfile__is_title=0).exclude(date_limit=None).order_by("date_limit")


    context = {'relationships': relationships,  'communications' : [] ,  'relationships' : [] ,  'parent' : parent , 'student' : student , } 
    return render(request, 'qcm/my_child_tasks.html', context)




#######################################################################################################################################################################
#######################################################################################################################################################################
#################   Remédiation
#######################################################################################################################################################################
#######################################################################################################################################################################
@csrf_exempt 
@user_passes_test(user_is_superuser)
def create_remediation(request,idr): # Pour la partie superadmin

    relationship = Relationship.objects.get(pk=idr) 
    form = RemediationForm(request.POST or None,request.FILES or None, teacher = relationship.parcours.teacher)

    if form.is_valid():
        nf =  form.save(commit = False)
        nf.relationship = relationship
        nf.save()
        nf.exercises.add(exercise)
        form.save_m2m()
        return redirect('admin_exercises')

    context = {'form': form,  'exercise' : exercise}

    return render(request, 'qcm/form_remediation.html', context)

 
@csrf_exempt 
@user_passes_test(user_is_superuser)
def update_remediation(request,idr, id): # Pour la partie superadmin

    remediation = Remediation.objects.get(id=id)
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')
    exercise = Exercise.objects.get(pk=ide) 
    form = RemediationUpdateForm(request.POST or None, request.FILES or None, instance=remediation, teacher = teacher  )
 
    if form.is_valid():
        nf.save()
        return redirect('exercises')

    context = {'form': form,  'exercise' : exercise}

    return render(request, 'qcm/form_remediation.html', context )


@csrf_exempt 
@user_passes_test(user_is_superuser)
def delete_remediation(request, id): # Pour la partie superadmin
    remediation = Remediation.objects.get(id=id)
    remediation.delete()

    return redirect('exercises')



@csrf_exempt 
def show_remediation(request, id):

    remediation = Remediation.objects.get(id=id)

    if remediation.video != "" :
        video_url = remediation.video
    else : 
        try : 
            video_url = None         
            ext = remediation.mediation[-3:]
            if ext == "ggb" : 
                ggb_file = True
            else :
                ggb_file = False
        except :
            video_url = None        
            ggb_file = False

    context = {'remediation': remediation, 'video_url': video_url, 'ggb_file': ggb_file   }
    
    return render(request, 'qcm/show_remediation.html', context)



@csrf_exempt 
def ajax_remediation(request):

    parcours_id =  request.POST.get("parcours_id",None) 

 
    if parcours_id :
        parcours_id =  int(request.POST.get("parcours_id"))
        customexercise_id =  int(request.POST.get("customexercise_id"))
        customexercise = Customexercise.objects.get( id = customexercise_id)

        form = RemediationcustomForm(request.POST or None,request.FILES or None, teacher = customexercise.teacher)
        data = {}

        remediations = Remediationcustom.objects.filter(customexercise = customexercise)

        context = {'form': form,  'customexercise' : customexercise ,  'remediations' : remediations , 'relationship' : None , 'parcours_id' : parcours_id } 

    else :
        relationship_id =  int(request.POST.get("relationship_id"))
        relationship = Relationship.objects.get( id = relationship_id)

        form = RemediationForm(request.POST or None,request.FILES or None, teacher = relationship.parcours.teacher)
        data = {}

        remediations = Remediation.objects.filter(relationship = relationship)

        context = {'form': form,  'relationship' : relationship ,  'remediations' : remediations, 'customexercise' : None , 'parcours_id' : relationship.parcours.id  } 
    
    html = render_to_string('qcm/ajax_remediation.html',context)
    data['html'] = html       

    return JsonResponse(data)





@csrf_exempt  
def json_create_remediation(request,idr,idp,typ):

    if typ == 0 :
        relationship = Relationship.objects.get(pk=idr) 
        form = RemediationForm(request.POST or None, request.FILES or None , teacher = relationship.parcours.teacher)
     
        if form.is_valid():
            nf =  form.save(commit = False)
            nf.relationship = relationship
            nf.save()  
            form.save_m2m()

    else :
        customexercise = Customexercise.objects.get(pk=idr) 
        form = RemediationcustomForm(request.POST or None, request.FILES or None, teacher = customexercise.teacher)
     
        if form.is_valid():
            nf =  form.save(commit = False)
            nf.customexercise = customexercise
            nf.save()  
            form.save_m2m()

    return redirect( 'show_parcours', 0, idp )
    



@csrf_exempt  
def json_delete_remediation(request,id,idp,typ):

    parcours = Parcours.objects.get(pk=idp) 
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    if parcours.teacher == teacher :
        if typ == 0 :
            remediation = Remediation.objects.get(id=id)
        else :
            remediation = Remediationcustom.objects.get(id=id)  
        remediation.delete()

    return redirect( 'show_parcours', 0, idp )

 

@csrf_exempt  
def audio_remediation(request):

    data = {}
    idr =  int(request.POST.get("id_relationship"))
    is_custom = request.POST.get("is_custom")
    if int(is_custom) == 0 : # 0 pour les exos GGB
        relationship = Relationship.objects.get(pk=idr) 
        form = RemediationForm(request.POST or None, request.FILES or None , teacher = relationship.parcours.teacher)
        if form.is_valid():
            nf =  form.save(commit = False)
            nf.mediation = request.FILES.get("id_mediation")
            nf.relationship = relationship
            nf.audio = True
            nf.save()  
            form.save_m2m()
        else:
            print(form.errors)

    else :
        customexercise = Customexercise.objects.get( id = idr)
        form = RemediationcustomForm(request.POST or None,request.FILES or None, teacher = customexercise.teacher)
        if form.is_valid():
            nf =  form.save(commit = False)
            nf.mediation = request.FILES.get("id_mediation")
            nf.customexercise = customexercise
            nf.audio = True
            nf.save()  
            form.save_m2m()
        else:
            print(form.errors)


    return JsonResponse(data)  




@csrf_exempt 
def ajax_remediation_viewer(request): # student_view

    remediation_id =  int(request.POST.get("remediation_id"))
    if request.POST.get("is_custom") == "0" :
        remediation = Remediation.objects.get( id = remediation_id)
    else :
        remediation = Remediationcustom.objects.get( id = remediation_id)    

    cookie_rgpd_accepted = request.COOKIES.get('cookie_rgpd_accepted',None)
    cookie_rgpd_accepted =  cookie_rgpd_accepted  == "True" 

    print(cookie_rgpd_accepted)

    data = {}
    context = { 'remediation' : remediation ,  "cookie_rgpd_accepted" : cookie_rgpd_accepted } 
    html = render_to_string('qcm/ajax_remediation_viewer.html',context)
    data['html'] = html       

    return JsonResponse(data)


#######################################################################################################################################################################
#######################################################################################################################################################################
#################   constraint
#######################################################################################################################################################################
#######################################################################################################################################################################



@csrf_exempt  
def ajax_infoExo(request):
    code = request.POST.get("codeExo")
    data={}
    if Relationship.objects.filter(exercise__supportfile__code = code ).exists() or code == "all" :
        html = "<i class='fa fa-check text-success'></i>"
        test = 1
    else :
        html = "ERREUR"
        test = 0

    data["html"] = html 
    data["test"] = test
    return JsonResponse(data)


@csrf_exempt  
def ajax_create_constraint(request):

    relationship_id = int(request.POST.get("relationship_id"))

    this_relationship = Relationship.objects.get(pk = relationship_id)
    code = request.POST.get("codeExo") 
    score = request.POST.get("scoreMin")

    data = {}
    if code == "all" : # si tous les exercices précédents sont cochés
        parcours_id = int(request.POST.get("parcours_id"))
        
        relationships = Relationship.objects.filter(parcours_id = parcours_id, ranking__lt= this_relationship.ranking)
        for relationship in relationships :
            Constraint.objects.get_or_create(code = relationship.exercise.supportfile.code, relationship = this_relationship, defaults={"scoremin" : score , } )
        data["html"] = "<div id='constraint_saving0'><i class='fa fa-minus-circle'></i> Tous les exercices à "+score+"% <a href='#'  class='pull-right delete_constraint' data-relationship_id='"+str(relationship_id)+"' data-is_all=1 ><i class='fa fa-trash'></i> </a></div>"
        data["all"] = 1
    else :
        constraint, created = Constraint.objects.get_or_create(code = code, relationship = this_relationship, defaults={"scoremin" : score , } )
        data["html"] = "<div id='constraint_saving'"+str(constraint.id)+"><i class='fa fa-minus-circle'></i> Exercice "+code+" à "+score+"% <a href='#'  class='pull-right delete_constraint' data-constraint_id='"+str(constraint.id)+"' data-relationship_id='"+str(relationship_id)+"' data-is_all=0 ><i class='fa fa-trash'></i> </a></div>"
        data["all"] = 0
 
    return JsonResponse(data)
 

@csrf_exempt  
def ajax_delete_constraint(request):

    data={}
    is_all  = int(request.POST.get("is_all"))
    relationship_id = int(request.POST.get("relationship_id")) 
    if is_all == 1 :
        constraints = Constraint.objects.filter(relationship_id = relationship_id)
        for c in constraints :
            c.delete()
        data["html"] = 0
        data["nbre"] = 0
    else :
        constraint_id = int(request.POST.get("constraint_id"))     
        constraint = Constraint.objects.get(id = constraint_id )
        code = constraint.code
        data["html"] = code
        constraint.delete()
        nbre = Constraint.objects.filter(relationship_id = relationship_id).count() 
        data["nbre"] = nbre
    return JsonResponse(data)




@login_required(login_url= 'index')
def peuplate_custom_parcours(request,idp):

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    parcours = Parcours.objects.get(id=idp)

    context = {'parcours': parcours, 'teacher': teacher ,  'type_of_document' : 1 }

    return render(request, 'qcm/form_peuplate_custom_parcours.html', context)
 

def ajax_find_peuplate_sequence(request):

    id_parcours      = request.POST.get("id_parcours",0)
    subject_id       = request.POST.get("id_subject",0) 
    level_id         = request.POST.get("id_level",None) 
    type_of_document = request.POST.get("type_of_document",None)
    keyword          = request.POST.get("keyword",None)

    theme_id    = request.POST.getlist("theme_id",None) 
    level = Level.objects.get(pk=level_id)
    data = {}  

    if type_of_document == "2":
        if keyword :
            courses = Course.objects.filter(  Q(teacher__user=request.user)|Q(is_share =  1) ).filter( Q(title__icontains=keyword)|Q(annoncement__icontains=keyword) ,   teacher__user__school = request.user.school , subject_id=subject_id,level=level )
        else :
            courses = Course.objects.filter( Q(teacher__user=request.user)|Q(is_share =  1) ,teacher__user__school = request.user.school , subject_id=subject_id,level=level )
        context = { "courses" : courses }    
        data['html']    = render_to_string( 'qcm/course/ajax_course_peuplate_sequence.html' , context)
    else :
        if keyword :
            customs = Customexercise.objects.filter(  Q(teacher__user=request.user)|Q(is_share =  1) ,instruction__icontains=keyword ,  teacher__user__school = request.user.school  )
        else :
            customs = Customexercise.objects.filter( Q(teacher__user=request.user)|Q(is_share =  1) ,teacher__user__school = request.user.school )
        
        context = { "customs" : customs }
        data['html']    = render_to_string( 'qcm/ajax_custom_peuplate_sequence.html' , context)

    return JsonResponse(data)  


@login_required(login_url= 'index') 
def clone_course_sequence(request, idc):
    """ cloner un cours dans une sequence """

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    course = Course.objects.get(pk=idc) # parcours à cloner.pk = None

    course.pk = None
    course.teacher = teacher
    course.save()

    parcours_id = request.session.get("parcours_id",None)  
    if parcours_id :
        parcours = Parcours.objects.get(pk = parcours_id)
        relation = Relationship.objects.create(parcours = parcours , exercise_id = None , document_id = course.id  , type_id = 2 , ranking =  200 , is_publish= 1 , start= None , date_limit= None, duration= 10, situation= 0 ) 
        students = parcours.students.all()
        relation.students.set(students)
        return redirect('show_parcours' , 0, parcours_id )
    else :
        return redirect('list_quizzes')
 



@login_required(login_url= 'index')
def clone_custom_sequence(request, idc):
    """ cloner un parcours """

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    customexercise = Customexercise.objects.get(pk=idc) # parcours à cloner.pk = None
    skills     = customexercise.skills.all()
    knowledges = customexercise.knowledges.all()   
     
    customexercise.pk = None
    customexercise.teacher = teacher
    customexercise.code = str(uuid.uuid4())[:8]
    customexercise.save()

    customexercise.skills.set(knowledges) 
    customexercise.knowledges.set(knowledges)  


    parcours_id = request.session.get("parcours_id",None)  
    if parcours_id :
        parcours = Parcours.objects.get(pk = parcours_id)
        relation = Relationship.objects.create(parcours = parcours , exercise_id = None , document_id = customexercise.id  , type_id = 1 , ranking =  200 , is_publish= 1 , start= None , date_limit= None, duration= 10, situation= 0 ) 
        students = parcours.students.all()
        relation.students.set(students)
        customexercise.students.set(students)

        return redirect('show_parcours' , 0, parcours_id )
    else :
        return redirect('list_quizzes')



#######################################################################################################################################################################
#######################################################################################################################################################################
#################   exports PRONOTE ou autre
#######################################################################################################################################################################
#######################################################################################################################################################################
def get_level(tot,stage):
    if tot < stage["low"] :
        clr = "red"
    elif tot < stage["medium"] : 
        clr = "yellow"
    elif tot < stage["up"] : 
        clr = "green"
    else  : 
        clr = "blue" 
    return clr



def export_results_after_evaluation(request):

    skill = request.POST.get("skill",None)  
    knowledge =   request.POST.get("knowledge",None)  

    mark  = request.POST.get("mark",None) 
    mark_on  = request.POST.get("mark_on")  
    signature  = request.POST.get("signature",None) 
    parcours_id  = request.POST.get("parcours_id") 
    parcours = Parcours.objects.get(pk = int(parcours_id) ) 
    elements = []     

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="'+str(parcours.title)+'.pdf"'

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

    style_cell = TableStyle(
            [
                ('SPAN', (0, 1), (1, 1)),
                ('TEXTCOLOR', (0, 1), (-1, -1),  colors.Color(0,0.7,0.7))
            ]
        )


    title = ParagraphStyle('title',  fontSize=20, textColor=colors.HexColor("#00819f"),)                   
    title_black = ParagraphStyle('title', fontSize=20, )
    subtitle = ParagraphStyle('title', fontSize=16,  textColor=colors.HexColor("#00819f"),)
 
    normal = ParagraphStyle(name='Normal',fontSize=12,)    
    red = ParagraphStyle(name='Normal',fontSize=12,  textColor=colors.HexColor("#cb2131"),) 
    yellow = ParagraphStyle(name='Normal',fontSize=12,  textColor=colors.HexColor("#ffb400"),)
    green = ParagraphStyle(name='Normal',fontSize=12,  textColor=colors.HexColor("#1bc074"),)
    blue = ParagraphStyle(name='Normal',fontSize=12,  textColor=colors.HexColor("#005e74"),)
    small = ParagraphStyle(name='Normal',fontSize=10,)    

    stage = get_stage(request.user)    
    exercises = []
    relationships = Relationship.objects.filter(parcours=parcours,is_publish = 1,exercise__supportfile__is_title=0).prefetch_related('exercise__supportfile').order_by("ranking")
    parcours_duration = parcours.duration #durée prévue pour le téléchargement
    for r in relationships :
        parcours_duration += r.duration
        exercises.append(r.exercise)

    group_id = request.session.get("group_id",None) 
    try :
        if group_id :
            group = Group.objects.get(pk = group_id )
            students = parcours.only_students(group)
        else :
            students = students_from_p_or_g(request,parcours)
    except:
        students = students_from_p_or_g(request,parcours)

    for s in students :
        skills =  skills_in_parcours(request,parcours) 
        knowledges = knowledges_in_parcours(parcours)
        data_student = get_student_result_from_eval(s, parcours, exercises,relationships,skills, knowledges,parcours_duration)
 

        #logo = Image('D:/uwamp/www/sacado/static/img/sacadoA1.png')
        logo = Image('https://sacado.xyz/static/img/sacadoA1.png')
        logo_tab = [[logo, "SACADO \nSuivi des acquisitions de savoir faire" ]]
        logo_tab_tab = Table(logo_tab, hAlign='LEFT', colWidths=[0.7*inch,5*inch])
        logo_tab_tab.setStyle(TableStyle([ ('TEXTCOLOR', (0,0), (-1,0), colors.Color(0,0.5,0.62))]))
        
        elements.append(logo_tab_tab)
        elements.append(Spacer(0, 0.2*inch))


        ##########################################################################
        #### Parcours
        ##########################################################################
        paragraph = Paragraph( str(parcours.title) , title_black )
        elements.append(paragraph)
        elements.append(Spacer(0, 0.2*inch))
        ##########################################################################
        #### Elève
        ##########################################################################
        paragraph = Paragraph( str(s.user.last_name).strip()+" "+str(s.user.first_name).strip() , title )
        elements.append(paragraph)
        elements.append(Spacer(0, 0.4*inch)) 

        ##########################################################################
        #### Nombre d'exercices traités
        ##########################################################################
        paragraph = Paragraph( "Nombre d'exercices traités : " + str(data_student["nb_exo"]) +  " sur " + str(data_student["total_nb_exo"])+" proposés"  , normal )
        elements.append(paragraph)
        elements.append(Spacer(0, 0.1*inch)) 
        ##########################################################################
        #### Nombre d'exercices traités
        ##########################################################################
        paragraph = Paragraph( "Durée du travail (h:m:s) : " + str(data_student["duration"]) , normal )
        elements.append(paragraph)
        elements.append(Spacer(0, 0.1*inch)) 


        if knowledge : 
            ##########################################################################
            #### Savoir faire ciblés
            ##########################################################################
            elements.append(Spacer(0, 0.3*inch)) 
            paragraph = Paragraph( "Savoir faire ciblés : "   , subtitle )
            elements.append(paragraph)
            elements.append(Spacer(0, 0.1*inch)) 

            tableauK = []
 
            for knwldg in knowledges :
                data = []
                data.append(knwldg.name[:80])
                tot_k = total_by_knowledge_by_student(knwldg,relationships,parcours,s)
                couleur = get_level(tot_k,stage)                
                if tot_k < 0 :
                    tot_k, couleur = "NE", "n"
                if couleur == "red" :
                    paragraphknowledge = Paragraph(  str(tot_k)  , red )
                elif couleur == "yellow" :
                    paragraphknowledge = Paragraph( str(tot_k)  , yellow )
                elif couleur == "green" :
                    paragraphknowledge = Paragraph(  str(tot_k)  , green )
                elif couleur == "blue" :
                    paragraphknowledge = Paragraph( str(tot_k)  , blue )
                else :
                    paragraphknowledge = Paragraph( str(tot_k)  , normal )


                data.append(paragraphknowledge)
                tableauK.append(data) 
            tk = Table(tableauK)
            elements.append(tk)
            elements.append(Spacer(0, 0.05*inch)) 


       
        if skill : 
            tableauSkill = []
            ##########################################################################
            #### Compétences ciblées
            ##########################################################################
            elements.append(Spacer(0, 0.3*inch)) 
            paragraph = Paragraph( "Compétences ciblées : "   , subtitle )
            elements.append(paragraph)
            elements.append(Spacer(0, 0.1*inch)) 

            for skll in  skills:
                data = []
                data.append(skll)
                tot_s = total_by_skill_by_student(skll,relationships,parcours,s)
                couleur = get_level(tot_s,stage)                
                if tot_s < 0 :
                    tot_s, couleur = "NE", "n"

                if couleur == "red" :
                    paragraphskill = Paragraph(  str(tot_s)   , red )
                elif couleur == "yellow" :
                    paragraphskill = Paragraph( str(tot_s)  , yellow )
                elif couleur == "green" :
                    paragraphskill = Paragraph(  str(tot_s)   , green )
                elif couleur == "blue" :
                    paragraphskill = Paragraph( str(tot_s)   , blue )
                else :
                    paragraphskill = Paragraph( str(tot_s)   , normal )

                data.append(paragraphskill)
                tableauSkill.append(data) 
            tSk = Table(tableauSkill)
            elements.append(tSk)
            elements.append(Spacer(0, 0.05*inch)) 



        if mark : 

            ##########################################################################
            #### Score par exercice 
            ##########################################################################
            elements.append(Spacer(0, 0.3*inch)) 
            paragraph = Paragraph( "Score par exercice "   , subtitle )
            elements.append(paragraph)
            elements.append(Spacer(0, 0.1*inch)) 

            i = 1
            dataset  = []
            for st_answer in data_student["score_tab"] :
                dataset.append( (str(i)+". " , unescape_html(st_answer.exercise.supportfile.title) ,  str(st_answer.point) + "%") ) 
                i += 1 

            if len(dataset) > 0 :
                table = Table(dataset, colWidths=[0.2*inch, 6.9*inch,0.7*inch], rowHeights=20)
                elements.append(table)
                elements.append(Spacer(0, 0.3*inch)) 
                ##########################################################################
                #### Note sur
                ##########################################################################
                exo_sacado = request.POST.get("exo_sacado",0)  
                if data_student["percent"] != "" :

                    final_mark = float(data_student["score_total"]) * (float(mark_on) - float(exo_sacado)) + float(data_student["percent"]) * float(exo_sacado)/100

                    coefficient = data_student["nb_exo"]  /  data_student["total_nb_exo"] 
                    final_mark = math.ceil( coefficient *  final_mark)
                    paragraphsco = Paragraph( "Note globale : " + str(final_mark)+"/"+mark_on  , normal )
                else :
                    paragraphsco = Paragraph( "Note globale : NE"  , normal )

                elements.append(Spacer(0, 0.1*inch)) 
                elements.append(paragraphsco)
                elements.append(Spacer(0, 0.1*inch))
                paragraphscoExplain = Paragraph( "Cette note prend en compte les résultats par rapport au nombre d'exercices traités."   , small )
                elements.append(paragraphscoExplain)
                elements.append(Spacer(0, 0.1*inch)) 
            else :
                paragraphNull = Paragraph( "Aucun exercice n'a été traité."   , normal )
                elements.append(paragraphNull)
                elements.append(Spacer(0, 0.1*inch)) 
 
        if signature : 
            paragraph = Paragraph( "Signature parent "   , subtitle )
            elements.append(paragraph)
 
        elements.append(PageBreak())

    doc.build(elements)

    return response


def export_notes_after_evaluation(request):

    parcours_id = request.POST.get("parcours_id")  
    parcours = Parcours.objects.get(pk = parcours_id)  

    note_sacado  = request.POST.get("note_sacado",0)  
    note_totale  = request.POST.get("note_totale")  

    this_clic = request.POST.get("this_clic_notes")

    try : 
        students = parcours.only_students(group)
    except:
        students = students_from_p_or_g(request,parcours) 


    if this_clic == "csv" :

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment;filename=Notes_exercice_{}.csv'.format(parcours.id)
        response.write(u'\ufeff'.encode('utf8'))
        writer = csv.writer(response)
        
        fieldnames = ("Nom", "Prénom", "Situations proposées", "Réponse juste", "Score rapporté aux meilleurs scores SACADO" , "Score rapporté à tous les exercices SACADO proposés" , "Note proposée"  )
        writer.writerow(fieldnames)

        skills = skills_in_parcours(request,parcours)
        knowledges = knowledges_in_parcours(parcours)
        relationships = Relationship.objects.filter(parcours=parcours,is_publish = 1,exercise__supportfile__is_title=0)
        parcours_duration = parcours.duration #durée prévue pour le téléchargement
        exercises = []
        for r in relationships :
            parcours_duration += r.duration
            exercises.append(r.exercise)


        for student in students :
            data_student = get_student_result_from_eval(student, parcours, exercises,relationships,skills, knowledges,parcours_duration) 
            
            if data_student["percent"] != "" :

                try :
                    final_mark = float(data_student["score_total"]) * (float(note_totale) - float(note_sacado)) + float(data_student["percent"]) * float(note_sacado)/100
                    coefficient = data_student["nb_exo"]  /  data_student["total_nb_exo"] 
                    final_mark = math.ceil( coefficient *  final_mark)
                    final_mark_coeff =  float(data_student["score_real_coeff"]) * (float(note_totale) - float(note_sacado)) + float(data_student["percent"]) * float(note_sacado)/100
                except :
                    final_mark = "N.Not" 
                    final_mark_coeff = "N.Not"
            else :
                final_mark = "N.Not"
                final_mark_coeff = "N.Not" 

            writer.writerow( (str(student.user.last_name).lower().strip() , str(student.user.first_name).lower().strip() , data_student["total_nb_exo"] , data_student["nb_exo"],  data_student["percent"] ,  final_mark,  final_mark_coeff ) )
        return response


    else :

        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="etablissement.xls"'

        wb = xlwt.Workbook(encoding='utf-8')

        ptitle = parcours.title
        if  len(parcours.title) > 15:
            ptitle = parcours.title[:15]
        ws = wb.add_sheet(ptitle)

        # Sheet header, first row
        row_num = 0

        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        skills = skills_in_parcours(request,parcours)
        knowledges = knowledges_in_parcours(parcours)
        relationships = Relationship.objects.filter(parcours=parcours,is_publish = 1,exercise__supportfile__is_title=0)
        parcours_duration = parcours.duration #durée prévue pour le téléchargement
        exercises = []
        for r in relationships :
            parcours_duration += r.duration
            exercises.append(r.exercise)


        columns = [ 'Nom' , 'Prénom' ,  'Total des exercices'  ,  "Nombres d'exercices traités" ,  "Pourcentage",   "Note non coeff" , "Note coefficientée" ] 



        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)


        # Sheet body, style par défaut, on enlève le gras
        font_style = xlwt.XFStyle()

        students_detail = []
        for student in students :
            data_student = get_student_result_from_eval(student, parcours, exercises,relationships,skills, knowledges,parcours_duration) 

            if data_student["percent"] != "" :
                try :
                    final_mark = float(data_student["score_total"]) * (float(note_totale) - float(note_sacado)) + float(data_student["percent"]) * float(note_sacado)/100
                    coefficient = data_student["nb_exo"]  /  data_student["total_nb_exo"] 
                    final_mark = math.ceil( coefficient *  final_mark)
                    final_mark_coeff = float(data_student['score_real_coeff']) * (float(note_totale) - float(note_sacado)) + float(data_student["percent"]) * float(note_sacado)/100

                except :
                    final_mark = "N.Not" 
                    final_mark_coeff = "N.Not"  
            else :
                final_mark = "N.Not" 
                final_mark_coeff = "N.Not"  

            data_s = [ str(student.user.last_name).lower().strip() , str(student.user.first_name).lower().strip() ,  data_student["total_nb_exo"] , data_student["nb_exo"],   data_student["percent"] ,  final_mark , final_mark_coeff  ]



            students_detail.append(data_s)


        ############################################################################################## 

        row_ns = 0
        for i in range(len(students_detail)): ## full_content est le tableau final pour l'export.
            row_ns += 1
            for col_num in range(len(students_detail[i])):
                ws.write(row_ns, col_num, students_detail[i][col_num] , font_style)
        wb.save(response)
        return response


def export_skills_after_evaluation(request):

    parcours_id = request.POST.get("parcours_id")  
    parcours = Parcours.objects.get(pk = parcours_id)  
    nb_skill = int(request.POST.get("nb_skill"))

    this_clic = request.POST.get("this_clic_skills")

    try : 
        students = parcours.only_students(group)
    except:
        students = students_from_p_or_g(request,parcours) 


    if this_clic == "csv" :

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment;filename=Skills_exercice_{}.csv'.format(parcours.id)
        response.write(u'\ufeff'.encode('utf8'))
        writer = csv.writer(response)
        

        skills = skills_in_parcours(request,parcours)

        label_in_export = ["Nom", "Prénom"]
        for ski in skills :
            if not ski.name in label_in_export : 
                label_in_export.append(ski.name)

        writer.writerow(label_in_export)
     
        for student in students :
            skill_level_tab = [str(student.user.last_name).capitalize().strip(),str(student.user.first_name).capitalize().strip()]

            for skill in  skills:
                total_skill = 0
     
                scs = student.student_correctionskill.filter(skill = skill, parcours = parcours)
                nbs = scs.count() 
                offseter = min(nb_skill, nbs)

                if offseter > 0 :
                    result_custom_skills  = scs[:offseter]
                else :
                    result_custom_skills  = scs

                nbsk = 0
                for sc in result_custom_skills :
                    total_skill += int(sc.point)
                    nbsk += 1

                # Ajout éventuel de résultat sur la compétence sur un exo SACADO
                result_skills_set = set()
                result_skills__ = Resultggbskill.objects.filter(skill= skill,student=student,relationship__parcours = parcours).order_by("-id")
                result_skills_set.update(set(result_skills__))
                result_skills = list(result_skills_set)
                nb_result_skill = len(result_skills)
                offset = min(nb_skill, nb_result_skill)

                if offset > 0 :
                    result_sacado_skills  = result_skills[:offset]
                else :
                    result_sacado_skills  = result_skills

                for result_sacado_skill in result_sacado_skills:
                    total_skill += result_sacado_skill.point
                    nbsk += 1
                ################################################################

                if nbsk != 0 :
                    tot_s = total_skill//nbsk
                    level_skill = get_level_by_point(student,tot_s)
                else :
                    level_skill = "A"

                skill_level_tab.append(level_skill)
     
            writer.writerow( skill_level_tab )
        return response

    else :
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="etablissement.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ptitle = parcours.title
        if  len(parcours.title) > 15:
            ptitle = parcours.title[:15]
        ws = wb.add_sheet(ptitle)

        # Sheet header, first row
        row_num = 0

        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        skills = skills_in_parcours(request,parcours)

        label_in_export = ['Nom',  'Prénom'] 
        
        for ski in skills :
            if not ski.name in label_in_export : 
                label_in_export.append(ski.name)

        for col_num in range(len(label_in_export)):
            ws.write(row_num, col_num, label_in_export[col_num], font_style)

        # Sheet body, remaining rows
        font_style = xlwt.XFStyle()

        students_detail = []
        for student in students :
            skill_level_tab = [str(student.user.last_name).capitalize().strip(),str(student.user.first_name).capitalize().strip()]

            for skill in  skills:
                total_skill = 0
     
                scs = student.student_correctionskill.filter(skill = skill, parcours = parcours)
                nbs = scs.count() 
                offseter = min(nb_skill, nbs)

                if offseter > 0 :
                    result_custom_skills  = scs[:offseter]
                else :
                    result_custom_skills  = scs

                nbsk = 0
                for sc in result_custom_skills :
                    total_skill += int(sc.point)
                    nbsk += 1

                # Ajout éventuel de résultat sur la compétence sur un exo SACADO
                result_skills_set = set()
                result_skills__ = Resultggbskill.objects.filter(skill= skill,student=student,relationship__parcours = parcours).order_by("-id")
                result_skills_set.update(set(result_skills__))
                result_skills = list(result_skills_set)
                nb_result_skill = len(result_skills)
                offset = min(nb_skill, nb_result_skill)

                if offset > 0 :
                    result_sacado_skills  = result_skills[:offset]
                else :
                    result_sacado_skills  = result_skills

                for result_sacado_skill in result_sacado_skills:
                    total_skill += result_sacado_skill.point
                    nbsk += 1
                ################################################################

                if nbsk != 0 :
                    tot_s = total_skill//nbsk
                    level_skill = get_level_by_point(student,tot_s)
                else :
                    level_skill = "A"

                skill_level_tab.append(level_skill)
            students_detail.append(skill_level_tab)     
        ############################################################################################## 

        row_ns = 0
        for i in range(len(students_detail)): ## full_content est le tableau final pour l'export.
            row_ns += 1
            for col_num in range(len(students_detail[i])):
                ws.write(row_ns, col_num, students_detail[i][col_num] , font_style)
        wb.save(response)
        return response      



def export_knowledges_after_evaluation(request):

    parcours_id   = request.POST.get("parcours_id")  
    parcours      = Parcours.objects.get(pk = parcours_id)  

    this_clic = request.POST.get("this_clic_knowledges")

    try : 
        students = parcours.only_students(group)
    except:
        students = students_from_p_or_g(request,parcours) 

    if this_clic == "csv" : 

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment;filename=Knowledges_parcours_{}.csv'.format(parcours.id)
        response.write(u'\ufeff'.encode('utf8'))
        writer = csv.writer(response)
        
        knowledges = knowledges_in_parcours(parcours)

        label_in_export = ["Nom", "Prénom"]
        for kn in knowledges :
            if not kn.name in label_in_export : 
                label_in_export.append(kn.name)

        writer.writerow(label_in_export)

        for student in students :
            knowledge_level_tab = [str(student.user.last_name).capitalize().strip(),str(student.user.first_name).capitalize().strip()]

            for knwldg in knowledges :
                total = total_by_knowledge_by_student(knwldg,"",parcours,student)
                if total == -10 : res = "A"
                else : res  = get_level_by_point(student,total_by_knowledge_by_student(knwldg,"",parcours,student))
                knowledge_level_tab.append(res)
     
            writer.writerow( knowledge_level_tab )
        return response

    else :

        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="etablissement.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ptitle = parcours.title
        if  len(parcours.title) > 15:
            ptitle = parcours.title[:15]
        ws = wb.add_sheet(ptitle)
        # Sheet header, first row
        row_num = 0

        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        knowledges = knowledges_in_parcours(parcours)

        columns = ['Nom',  'Prénom'] 

        for k in knowledges:
            columns.append(k.name)

        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        # Sheet body, remaining rows
        font_style = xlwt.XFStyle()

        students_detail = []
        for student in students :
            knowledge_level_tab = [str(student.user.last_name).capitalize().strip(),str(student.user.first_name).capitalize().strip()]

            for knwldg in knowledges :
                total = total_by_knowledge_by_student(knwldg,"",parcours,student)
                if total == -10 : res = "A"
                else : res  = get_level_by_point(student,total_by_knowledge_by_student(knwldg,"",parcours,student))
                knowledge_level_tab.append(res)

            students_detail.append(knowledge_level_tab)

     
        ############################################################################################## 

        row_ns = 0
        for i in range(len(students_detail)): ## full_content est le tableau final pour l'export.
            row_ns += 1
            for col_num in range(len(students_detail[i])):
                ws.write(row_ns, col_num, students_detail[i][col_num] , font_style)
        wb.save(response)
        return response  


def export_note_custom(request,id,idp):

    customexercise = Customexercise.objects.get(pk=id)
    parcours = Parcours.objects.get(pk=idp)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename=Notes_exercice_{}_{}.csv'.format(customexercise.id,parcours.id)
    writer = csv.writer(response)
    fieldnames = ("Eleves", "Notes")
    writer.writerow(fieldnames)

    try : 
        students = parcours.only_students(group)
    except:
        students = students_from_p_or_g(request,parcours) 

    for student in students :
        full_name = str(student.user.last_name).lower() +" "+ str(student.user.first_name).lower() 
        try :
            studentanswer = Customanswerbystudent.objects.get(student=student, customexercise=customexercise,  parcours=parcours) 
            score = float(studentanswer.point)
        except :
            score = "Abs"
        writer.writerow( (full_name , score) )
    return response
 
 
def export_note(request,idg,idp):

    group = Group.objects.get(pk=idg)
    parcours = Parcours.objects.get(pk=idp)
    value = int(request.POST.get("on_mark")) 
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename=Notes_{}_{}.csv'.format(group.name,parcours.id)
    writer = csv.writer(response)
    fieldnames = ("Eleves", "Notes")
    writer.writerow(fieldnames)
    for student in group.students.order_by("user__last_name") :
        full_name = str(student.user.last_name).lower() +" "+ str(student.user.first_name).lower() 
        try :
            studentanswer = Studentanswer.objects.filter(student=student, parcours=parcours).last() 
            if value :
                score = float(studentanswer.point * value/100)
            else :
                score = float(studentanswer.point) 
        except :
            score = "Abs"
        writer.writerow( (full_name , score) )
    return response


def export_result_parcours_exercises(request):
 

    parcours_id = request.POST.get("parcours_id")  
    is_twenty   = request.POST.get("is_twenty",None)  


    parcours      = Parcours.objects.get(pk = parcours_id)  

    relationships = Relationship.objects.filter(parcours=parcours, exercise__supportfile__is_title=0).prefetch_related('exercise').order_by("ranking")
    customexercises = parcours.parcours_customexercises.all() 

    this_clic = request.POST.get("this_clic_notes")

    try : 
        students = parcours.only_students(group)
    except:
        students = students_from_p_or_g(request,parcours) 

    if this_clic == "csv" : 

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment;filename=resultat_parcours_{}.csv'.format(parcours.id)
        response.write(u'\ufeff'.encode('utf8'))
        writer = csv.writer(response)
        
        label_in_export = ["Nom Prénom"]
        i=1
        for relationship in relationships :
            label_in_export.append("Exercice " + str(i))
            i+=1

        writer.writerow(label_in_export)

        for student in students :
            listing = []
            listing.append( str(student.user.last_name).capitalize().strip() +" " +str(student.user.first_name).capitalize().strip()  )


            base_studentanswer = Studentanswer.objects.filter(parcours=parcours,student=student)
            for relationship in relationships :
                studentanswer      = base_studentanswer.filter(exercise=relationship.exercise).last()
                if studentanswer :
                    point    = studentanswer.point
                    if is_twenty : point = int(point)//5
                else :
                    point    = "Non not."
                listing.append( str(point))

            writer.writerow( listing )
        return response

    else :

        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="resultat_parcours_'+str(parcours_id)+'.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ptitle = parcours.title
        if  len(parcours.title) > 15:
            ptitle = parcours.title[:15]
        ws = wb.add_sheet(ptitle)
        # Sheet header, first row
        row_num = 0

        font_style = xlwt.XFStyle()
        font_style.font.bold = True


        columns = ['Nom',  'Prénom'] 

        i=1
        for relationship in relationships :
            columns.append("Exercice " + str(i))
            i+=1

        #ECRITURE DE LA LIGNE 0 : celle des labels
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        # Sheet body, remaining rows
        font_style = xlwt.XFStyle()


        students_detail = []
        for student in students :
            listing = []
            listing.append(str(student.user.last_name).capitalize().strip())
            listing.append(str(student.user.first_name).capitalize().strip() )
     
            base_studentanswer = Studentanswer.objects.filter(parcours=parcours,student=student)
            for relationship in relationships :
                studentanswer      = base_studentanswer.filter(exercise=relationship.exercise).last()
                if studentanswer :
                    point = studentanswer.point                    
                    if is_twenty : point = int(point)//5
                else :
                    point = "Non not."
                listing.append(  point )
            students_detail.append(listing)
        ############################################################################################## 

        row_ns = 0
        for i in range(len(students_detail)): ## full_content est le tableau final pour l'export.
            row_ns += 1
            for col_num in range(len(students_detail[i])):
                ws.write(row_ns, col_num, students_detail[i][col_num] , font_style)
        wb.save(response)
        return response  
 
 
#######################################################################################################################################################################
#######################################################################################################################################################################
##################    Course     
#######################################################################################################################################################################
#######################################################################################################################################################################


@login_required(login_url= 'index')
def list_courses(request):

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    request.session["tdb"] = "Documents"  
    request.session["subtdb"] = "Courses"

    parcours_dataset = Parcours.objects.filter(Q(teacher=teacher)|Q(coteachers=teacher), is_trash=0 ,is_evaluation=0, is_archive=0).exclude(course=None).order_by("subject", "level", "title").distinct()
    parcours_courses = list()
    for parcours in parcours_dataset :
        this_courses = dict()
        this_courses["parcours"] = parcours
        this_courses["courses"]  = parcours.course.all()
        parcours_courses.append(this_courses)


    nb_archive = Course.objects.filter(  teacher=teacher ,  parcours__is_archive=1).count()

    return render(request, 'qcm/course/my_courses.html', { 'parcours_courses' : parcours_courses , 'nb_archive' : nb_archive })

 



@login_required(login_url= 'index')
def list_courses_archives(request):

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    request.session["tdb"] = "Documents"  
    request.session["subtdb"] = "Courses"

    parcours_dataset = Parcours.objects.filter(Q(teacher=teacher)|Q(coteachers=teacher), is_trash=0 ,is_evaluation=0, is_archive=1).exclude(course=None).order_by("subject", "level", "ranking")
    parcours_courses = list()
    for parcours in parcours_dataset :
        this_courses = dict()
        this_courses["parcours"] = parcours
        this_courses["courses"]  = parcours.course.all
        parcours_courses.append(this_courses)
 

    return render(request, 'qcm/course/my_courses_archives.html', { 'parcours_courses' : parcours_courses  })



@login_required(login_url= 'index')
def only_create_course(request):
 
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    request.session["tdb"] = "Documents"  
    request.session["subtdb"] = "Courses"

    form    = CourseNPForm(request.POST or None, teacher = teacher)
    if request.method == "POST" :
        if form.is_valid():
            nf              = form.save(commit = False)
            nf.teacher      = teacher
            nf.author       = teacher
            nf.parcours_id  = request.POST.get("parcours")
            nf.save()
            return redirect('courses')
        else:
            print(form.errors)
    
    context = {  'form': form , 'teacher': teacher, 'course': None ,   }

    return render(request, 'qcm/course/form_np_course.html', context)



@login_required(login_url= 'index')
def only_update_course(request,idc):
    """
    idc : course_id et id = parcours_id pour correspondre avec le decorateur
    """
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    request.session["tdb"] = "Documents"  
    request.session["subtdb"] = "Courses"

    course  =  Course.objects.get(pk=idc)
    form    =  CourseNPForm(request.POST or None, instance = course , teacher = teacher , initial = {   'subject' : course.parcours.subject  , 'level' : course.parcours.level })
    if request.method == "POST" :
        if form.is_valid():
            nf =  form.save(commit = False)
            nf.teacher = teacher
            nf.author = teacher
            nf.save()
            messages.success(request,"Modification réussie. Fermer l'onglet ou cliquez sur l'onglet précédent.")
        else:
            print(form.errors)

    context = {  'form': form , 'teacher': teacher, 'course': course , 'parcours': course.parcours ,    }

    return render(request, 'qcm/course/form_np_course.html', context)





@login_required(login_url= 'index')
def create_course(request, idc , id ):
    """
    idc : course_id et id = parcours_id pour correspondre avec le decorateur
    """
    parcours = Parcours.objects.get(pk =  id)
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    request.session["tdb"] = "Documents"  
    request.session["subtdb"] = "Courses"

    role, group , group_id , access = get_complement(request, teacher, parcours)
    
    if not teacher_has_permisson_to_parcourses(request,teacher,parcours) :
        return redirect('index')

    form = CourseForm(request.POST or None , parcours = parcours )
    relationships = Relationship.objects.filter(parcours = parcours,exercise__supportfile__is_title=0).order_by("ranking")
    if request.method == "POST" :
        if form.is_valid():
            nf =  form.save(commit = False)
            nf.parcours = parcours
            nf.teacher = teacher
            nf.author = teacher
            nf.subject = parcours.subject
            nf.level = parcours.level
            nf.save()
            try :
                return redirect('show_course' , 0 , id)
            except :
                return redirect('index')
        else:
            print(form.errors)

    context = {'form': form,   'teacher': teacher, 'parcours': parcours , 'relationships': relationships , 'course': None , 'communications' : [], 'group' : group, 'group_id' : group_id , 'role' : role }

    return render(request, 'qcm/course/form_course.html', context)




@login_required(login_url= 'index')
def create_course_sequence(request, id ):
    """
    idc : course_id et id = parcours_id pour correspondre avec le decorateur
    """
    parcours = Parcours.objects.get(pk =  id)
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    request.session["tdb"] = "Documents"  
    request.session["subtdb"] = "Courses"

    relationships = Relationship.objects.filter(parcours = parcours,exercise__supportfile__is_title=0).order_by("ranking")
    if parcours.is_sequence :
        role, group , group_id , access = get_complement(request, teacher, parcours)
        
        if not teacher_has_permisson_to_parcourses(request,teacher,parcours) :
            return redirect('index')

        form = CourseForm(request.POST or None , parcours = parcours )
        if request.method == "POST" :
            if form.is_valid():
                nf =  form.save(commit = False)
                nf.parcours = parcours
                nf.teacher = teacher
                nf.author = teacher
                nf.subject = parcours.subject
                nf.level = parcours.level
                nf.save()
                relation = Relationship.objects.create(parcours = parcours , exercise_id = None , document_id = nf.id  , type_id = 2 , ranking =  200 , is_publish= 1 , start= None , date_limit= None, duration= 10, situation= 0 ) 
                students = parcours.students.all()
                relation.students.set(students)
                try :
                    return redirect('show_course' , 0 , id)
                except :
                    return redirect('index')
            else:
                print(form.errors)

        context = {'form': form,   'teacher': teacher, 'parcours': parcours , 'relationships': relationships , 'course': None , 'communications' : [], 'group' : group, 'group_id' : group_id , 'role' : role }


    else :
        messages.error(request,"Le cours doit être inclus dans une séquence. ")


    return render(request, 'qcm/course/form_course.html', context)




@login_required(login_url= 'index')
def create_custom_sequence(request, id ):
    """
    idc : course_id et id = parcours_id pour correspondre avec le decorateur
    """
    parcours = Parcours.objects.get(pk =  id)

    request.session["tdb"] = "Documents"  
    request.session["subtdb"] = "Courses"

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    relationships = Relationship.objects.filter(parcours = parcours,exercise__supportfile__is_title=0).order_by("ranking")
    if parcours.is_sequence :
        role, group , group_id , access = get_complement(request, teacher, parcours)
        
        if not teacher_has_permisson_to_parcourses(request,teacher,parcours) :
            return redirect('index')

        form = CustomexerciseForm(request.POST or None, request.FILES or None , teacher = teacher , parcours = parcours) 
        if request.method == "POST" :
            if form.is_valid():
                nf = form.save(commit=False)
                nf.teacher = teacher
                if nf.is_scratch :
                    nf.is_image = True
                nf.save()
                form.save_m2m()
                nf.parcourses.add(parcours)
                nf.students.set( parcours.students.all() )  

                relation = Relationship.objects.create(parcours = parcours , exercise_id = None , document_id = nf.id  , type_id = 1 , ranking =  200 , is_publish= 1 , start= None , date_limit= None, duration= 10, situation= 0 ) 
                students = parcours.students.all()
                relation.students.set(students)
                try :
                    return redirect('show_parcours' , 0 , id)
                except :
                    return redirect('index')
            else:
                print(form.errors)

        context = {'form': form,   'teacher': teacher, 'parcours': parcours , 'relationships': relationships , 'course': None , 'communications' : [], 'group' : group, 'group_id' : group_id , 'role' : role }


    else :
        messages.error(request,"Le cours doit être inclus dans une séquence. ")


    return render(request, 'qcm/form_exercise_custom.html', context)




@login_required(login_url= 'index')
def update_course(request, idc, id  ):
    """
    idc : course_id et id = parcours_id pour correspondre avec le decorateur
    """
    parcours = Parcours.objects.get(pk =  id)

    request.session["tdb"] = "Documents"  
    request.session["subtdb"] = "Courses"

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    course = Course.objects.get(id=idc)
    course_form = CourseForm(request.POST or None, instance=course , parcours = parcours )
    relationships = Relationship.objects.filter(parcours = parcours,exercise__supportfile__is_title=0).order_by("ranking")
    if request.user.user_type == 2 :
        teacher = parcours.teacher
    else :
        teacher = None

    if request.method == "POST" :
        if course_form.is_valid():
            nf = course_form.save(commit = False)
            nf.parcours = parcours
            nf.teacher = teacher
            nf.author = teacher
            nf.subject = parcours.subject
            nf.level = parcours.level
            nf.save()
            if request.user.user_type == 0 :
                student = Student.objects.get(user = request.user )
                course.students.add(student)


            messages.success(request, 'Le cours a été modifié avec succès !')
            try :
                return redirect('show_course' , 0 , id)
            except :
                return redirect('index')
        else :
            print(course_form.errors)

    role, group , group_id , access = get_complement(request, teacher, parcours)


    context = {'form': course_form,  'course': course, 'teacher': teacher , 'parcours': parcours  , 'relationships': relationships , 'communications' : [] , 'group' : group, 'group_id' : group_id , 'role' : role }

    return render(request, 'qcm/course/form_course.html', context )


@login_required(login_url= 'index')
def delete_course(request, idc , id  ):
    """
    idc : course_id et id = parcours_id pour correspondre avec le decorateur
    """

    request.session["tdb"] = "Documents"  
    request.session["subtdb"] = "Courses"

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')
    
    try :
        course = Course.objects.get( id = idc )
        parcours  = Parcours.objects.get( id = id )
        if not teacher_has_permisson_to_parcourses(request,teacher,parcours) :
            return redirect('index')
        course.delete()

    except :
        course = Course.objects.get(id=idc)
        if course.teacher == teacher or teacher.user.is_superuser :
            course.delete()

    if id > 0 :
        return redirect('show_course', 0, id)
    try :
        return redirect('list_parcours_group' , request.session.get("group_id"))
    except :
        return redirect('index')  




@login_required(login_url= 'index')
def peuplate_course_parcours(request,idp):

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    parcours = Parcours.objects.get(id=idp)

    role, group , group_id , access = get_complement(request, teacher, parcours)

    request.session["tdb"] = "Documents"  
    request.session["subtdb"] = "Courses"

    if not authorizing_access(teacher,parcours, access ):
        messages.error(request, "  !!!  Redirection automatique  !!! Violation d'accès. Contacter SACADO...")
        return redirect('index')

    
    courses = Course.objects.filter(parcours=parcours)


    context = {'parcours': parcours, 'teacher': teacher , 'courses' : courses , 'type_of_document' : 2 }

    return render(request, 'qcm/form_peuplate_course_parcours.html', context)




@login_required(login_url= 'index')
def show_course(request, idc , id ) :
    """
    idc : course_id et id = parcours_id pour correspondre avec le decorateur
    """
    parcours = Parcours.objects.get(pk =  id)
    teacher = Teacher.objects.get(user= request.user)

    role, group , group_id , access = get_complement(request, teacher, parcours)

    request.session["tdb"] = "Documents"  
    request.session["subtdb"] = "Courses"

    if not teacher_has_permisson_to_parcourses(request,teacher,parcours) :
        return redirect('index')
  
    courses = parcours.course.all().order_by("ranking") 

    if len(courses) > 0 :
        course = list(courses)[0]
    else :
        course = None
 
    
    context = {  'courses': courses, 'course': course, 'teacher': teacher , 'parcours': parcours , 'group_id' : group_id, 'communications' : [] , 'relationships' : [] , 'group' : group ,  'group_id' : group_id , 'role' : role }
    return render(request, 'qcm/course/show_course.html', context)

 
@login_required(login_url= 'index')
def show_one_course(request, idc  ) :
    """
    idc : course_id et id = parcours_id pour correspondre avec le decorateur
    """
    request.session["tdb"] = "Documents"  
    request.session["subtdb"] = "Courses"

    teacher = Teacher.objects.get(user= request.user)
    course = Course.objects.get(pk=idc) 

    context = {  'course': course, 'teacher': teacher   }
    return render(request, 'qcm/course/show_one_course.html', context)



@login_required(login_url= 'index')
def show_courses_from_folder(request,  idf ) :
    """
    idc : course_id et id = parcours_id pour correspondre avec le decorateur
    """
    folder = Folder.objects.get(pk =  idf)
    teacher = Teacher.objects.get(user= request.user)

    request.session["tdb"] = "Documents"  
    request.session["subtdb"] = "Courses"

    role, group , group_id , access = get_complement(request, teacher, folder)
    
    if not teacher_has_permisson_to_folder(request,teacher,folder) :
        return redirect('index')

    courses = set()
    for parcours in folder.parcours.filter(is_publish=1) :
        courses.update(parcours.course.all().order_by("ranking") )

    if len(courses) > 0 :
        course = list(courses)[0]
    else :
        course = None
 
    
    context = {  'courses': courses, 'course': course, 'teacher': teacher , 'folder': folder , 'group_id' : group_id, 'communications' : [] , 'relationships' : [] , 'group' : group ,  'group_id' : group_id , 'role' : role }
    return render(request, 'qcm/course/show_courses_from_folder.html', context)



def ajax_parcours_get_course(request):
    """ Montre un cours"""
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    sacado_asso = False
    if teacher.user.school   :
        sacado_asso = True

    course_id =  request.POST.get("course_id",0)
    if int(course_id) > 0 : 
        course = Course.objects.get(pk=course_id)
    else:
        course = None


    parcours_id =  request.POST.get("parcours_id",0)

    if int(parcours_id) :
        parcours = Parcours.objects.get(pk = parcours_id)
    else :
        parcours = None

    try :
        role, group , group_id , access = get_complement(request, teacher, parcours)
        request.session["parcours_id"] = parcours.id
        request.session["group_id"] = group_id
    except :
        group = None

    parcourses =  teacher.teacher_parcours.order_by("level")    

    context = {  'course': course , 'parcours': parcours ,  'parcourses': parcourses , 'teacher' : teacher , 'sacado_asso' : sacado_asso , 'group' : group }
    data = {}
    data['html'] = render_to_string('qcm/course/ajax_parcours_get_course.html', context)
 
    return JsonResponse(data)
 


def ajax_parcours_clone_course(request):
    """ Clone un parcours depuis la liste des parcours"""
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    all_parcours = request.POST.get("all_parcours")
    checkbox_value = request.POST.get("checkbox_value")
    course_id = request.POST.get("course_id",None)

    if course_id  : 
        course = Course.objects.get(pk=int(course_id))
        if checkbox_value != "" :
            checkbox_ids = checkbox_value.split("-")
            for checkbox_id in checkbox_ids :
                try :
                    if all_parcours == "0" :
                        course.pk = None
                        course.teacher = teacher
                        course.parcours_id = int(checkbox_id)
                        course.save()
                    else :
                        courses = course.parcours.course.all()
                        for course in courses :
                            course.pk = None
                            course.teacher = teacher
                            course.parcours_id = int(checkbox_id)
                            course.save()
                except :
                    pass

    else :
        parcours_id = int(request.POST.get("parcours_id"))
        parcours = Parcours.objects.get(pk = parcours_id) 
        if checkbox_value != "" :
            checkbox_ids = checkbox_value.split("-")
            for checkbox_id in checkbox_ids :
                try :
                    courses = parcours.course.all()
                    for course in courses :
                        course.pk = None
                        course.teacher = teacher
                        course.parcours_id = int(checkbox_id)
                        course.save()
                except :
                    pass

    data = {}
    data["success"] = "<i class='fa fa-check text-success'></i>"

    return JsonResponse(data)


@login_required(login_url= 'index')  
def get_this_course_for_this_parcours(request,typ,id_target,idp):
    """ Clone un parcours depuis la liste ver un parcours de provenance """

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    if typ==1  : 
        course = Course.objects.get(pk=int(idp))
        course.pk = None
        course.teacher = teacher
        course.parcours_id = id_target
        course.save()

    else :
        parcours = Parcours.objects.get(pk = idp)

        courses = parcours.course.all()
        for course in courses :
            course.pk = None
            course.teacher = teacher
            course.parcours_id = id_target
            course.save()
     
    return redirect("show_course" , 0, id_target )

 
 


@login_required(login_url= 'index')
def all_courses(request):
 
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    context = {  'teacher': teacher ,    }
    return render(request, 'qcm/course/list_courses.html', context )



@login_required(login_url= 'index')
def get_course_in_this_parcours(request,id):

    parcours = Parcours.objects.get(pk = id) 
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    teacher_id = get_teacher_id_by_subject_id(parcours.subject.id) 

    role, group , group_id , access = get_complement(request, teacher, parcours)
    request.session["parcours_id"] = parcours.id
    request.session["group_id"] = group_id

    courses = Course.objects.filter( Q(parcours__teacher__user__school = teacher.user.school)| Q(parcours__teacher__user_id=teacher_id),is_share = 1).exclude(parcours__teacher = teacher).order_by("parcours__level","parcours")

    return render(request, 'qcm/course/list_courses.html', {  'teacher': teacher , 'group': group , 'courses':courses,   'parcours': parcours, 'relationships' : [] ,  'communications': [] , })
 


@login_required(login_url= 'index')
def course_custom_show_shared(request):
    
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    teacher = request.user.teacher
    role, group , group_id , access = get_complement(request, teacher, parcours)
    request.session["parcours_id"] = parcours.id
    request.session["group_id"] = group_id


    courses = Course.objects.filter( Q(parcours__teacher__user__school = teacher.user.school)| Q(parcours__teacher__user_id=2480),is_share = 1).exclude(teacher = teacher).order_by("parcours","parcours__level")

    return render(request, 'qcm/course/list_courses.html', {  'teacher': teacher , 'courses':courses, 'group': group ,  'parcours': None, 'relationships' : [] ,  'communications': [] , })
  




def ajax_course_custom_show_shared(request):
    
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')
 
    data = {} 

    subject_id = request.POST.get('subject_id',0)
    level_id = request.POST.get('level_id',0)
    courses = []
    keywords = request.POST.get('keywords',None)

    parcours_id = request.POST.get('parcours_id',None)
    if parcours_id :
        parcours = Parcours.objects.get(pk = parcours_id)
        try :
            teacher = request.user.teacher
        except :
            messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
            return redirect('index')
        role, group , group_id , access = get_complement(request, teacher, parcours)
        request.session["parcours_id"] = parcours.id
        request.session["group_id"] = group_id


        template = 'qcm/course/ajax_list_courses_for_parcours.html'
    else :
        parcours = None
        group = None
        template = 'qcm/course/ajax_list_courses.html'

    subject = Subject.objects.get(pk=int(subject_id))
    teacher_id = get_teacher_id_by_subject_id(subject.id)

    if int(level_id) > 0 :
        
        level = Level.objects.get(pk=int(level_id))
        theme_ids = request.POST.getlist('theme_id')

        datas = []
        themes_tab = []

        for theme_id in theme_ids :
            themes_tab.append(theme_id) 

        if len(themes_tab) > 0 and themes_tab[0] != "" :

            exercises = Exercise.objects.filter(theme_id__in= themes_tab, level_id = level_id)

            parcours_set = set()
            for exercise in exercises :
                parcours_set.update(exercise.exercises_parcours.all())

            parcours_tab = list(parcours_set)
            courses += list(Course.objects.filter( Q(parcours__teacher__user__school = teacher.user.school)| Q(parcours__teacher__user_id=teacher_id),is_share = 1, parcours__subject = subject, parcours__in = parcours_tab ).exclude(teacher = teacher) )

        else :
            courses += list(Course.objects.filter( Q(parcours__teacher__user__school = teacher.user.school)| Q(parcours__teacher__user_id=teacher_id), parcours__subject = subject, parcours__level = level,is_share = 1 ).exclude(teacher = teacher)   )   
    
    else :
        courses += list(Course.objects.filter( Q(parcours__teacher__user__school = teacher.user.school)| Q(parcours__teacher__user_id=teacher_id), parcours__subject = subject, is_share = 1 ).exclude(teacher = teacher)  )     


    if keywords :
        for keyword in keywords.split(' '):
            courses += list(Course.objects.filter(Q(title__icontains=keyword)| Q(annoncement__icontains=keyword)| Q(parcours__teacher__user_id=teacher_id), parcours__subject = subject, is_share = 1).exclude(teacher = teacher))

    elif int(level_id) == 0 : 
        courses  += list(Course.objects.filter( Q(parcours__teacher__user__school = teacher.user.school)| Q(parcours__teacher__user_id=teacher_id), parcours__subject = subject, is_share = 1).exclude(teacher = teacher))


    data['html'] = render_to_string(template , {'courses' : courses, 'teacher' : teacher, 'parcours' : parcours  ,  'group': group })
 
    return JsonResponse(data)


def ajax_show_hide_course(request):

    course_id = request.POST.get('course_id',0)
    data = {}
    course = Course.objects.get(pk = course_id)
    if course.is_publish :
        Course.objects.filter(pk = course_id).update(is_publish=0)
        data['html'] = False
    else :
        Course.objects.filter(pk = course_id).update(is_publish=1)    
        data['html'] = True
    return JsonResponse(data)


# Semble ne pas etre utilisé ....
def ajax_course_custom_for_this_parcours(request):
    
    teacher = Teacher.objects.get(user= request.user)
 
    data = {} 

    level_id = request.POST.get('level_id',0)

    courses = []
    keywords = request.POST.get('keywords',None)

    parcours_id = request.POST.get('parcours_id',None)
    if parcours_id :
        parcours = Parcours.objects.get(pk = parcours_id)
    else :
        parcours = None

    if int(level_id) > 0 :
        
        level = Level.objects.get(pk=int(level_id))
        theme_ids = request.POST.getlist('theme_id')

        datas = []
        themes_tab = []

        for theme_id in theme_ids :
            themes_tab.append(theme_id) 

        if len(themes_tab) > 0 and themes_tab[0] != "" :

            exercises = Exercise.objects.filter(theme_id__in= themes_tab, level_id = level_id)

            parcours_set = set()
            for exercise in exercises :
                parcours_set.update(exercise.exercises_parcours.all())

            parcours_tab = list(parcours_set)
            courses += list(Course.objects.filter( Q(parcours__teacher__user__school = teacher.user.school)| Q(parcours__teacher__user_id=2480),is_share = 1, parcours__in = parcours_tab ) )

        else :
            courses += list(Course.objects.filter( Q(parcours__teacher__user__school = teacher.user.school)| Q(parcours__teacher__user_id=2480), parcours__level = level,is_share = 1 ) )      
    

    if keywords :
        for keyword in keywords.split(' '):
            courses += list(Course.objects.filter(Q(title__icontains=keyword)| Q(annoncement__icontains=keyword),is_share = 1))

    elif int(level_id) == 0 : 
        courses = Course.objects.filter( Q(parcours__teacher__user__school = teacher.user.school)| Q(parcours__teacher__user_id=2480),is_share = 1).exclude(teacher = teacher)


    data['html'] = render_to_string('qcm/course/ajax_list_courses_for_parcours.html', {'courses' : courses, 'teacher' : teacher  , 'parcours' : parcours   })
 
    return JsonResponse(data)






@student_can_show_this_course
def show_course_student(request, idc , id ):
    """
    idc : course_id et id = parcours_id pour correspondre avec le decorateur
    """
    this_user = request.user
    parcours = Parcours.objects.get(pk =  id)
    today = time_zone_user(this_user)
    courses = parcours.course.filter(Q(is_publish=1)|Q(publish_start__lte=today),Q(is_publish=1)|Q(publish_end__gte=today)).order_by("ranking")  
    course = courses.first() 

    context = {  'courses': courses,  'course': course, 'parcours': parcours , 'group_id' : None, 'communications' : []}
    return render(request, 'qcm/course/show_course_student.html', context)
 


@student_can_show_this_course
def show_course_sequence_student(request, idc , id ):
    """
    idc : course_id et id = parcours_id pour correspondre avec le decorateur
    """
    this_user = request.user
    parcours = Parcours.objects.get(pk =  id)
    today = time_zone_user(this_user)  
    course = Course.objects.get(pk=idc) 

    context = { 'course': course, 'parcours': parcours , 'group_id' : None, 'communications' : []}
    return render(request, 'qcm/course/show_course_sequence_student.html', context)
 





 
def ajax_parcours_shower_course(request):
    course_id =  int(request.POST.get("course_id"))
    course = Course.objects.get(pk=course_id)
    data = {}
    data['title'] = course.title
    context = {  'course': course   }
 
    data['html'] = render_to_string('qcm/course/ajax_shower_course.html', context)

    return JsonResponse(data)



@csrf_exempt 
def ajax_course_viewer(request):
    """ Lis un cours à partir d'une pop up """

    relation_id =  request.POST.get("relation_id",None)
    data = {}
    if relation_id : 
        relationship = Relationship.objects.get( id = int(relation_id))
        courses = Course.objects.filter(relationships = relationship).order_by("ranking")

        if request.user.user_type == 2 :
            is_teacher = True
            teacher = request.user.teacher
        else : 
            is_teacher = False
            teacher = None 
        context = { 'courses' : courses , 'parcours' : relationship.parcours , 'is_teacher' : is_teacher , 'teacher' : teacher  }
        html = render_to_string('qcm/course/course_viewer.html',context)
        data['html'] = html       

    return JsonResponse(data)


@csrf_exempt 
def ajax_this_course_viewer(request):  

    course_id =  request.POST.get("course_id",None)
    course = Course.objects.get(pk=course_id)
    data = {}
 
    
    parcours_id =  int(request.POST.get("parcours_id"))
    parcours = Parcours.objects.get(pk=parcours_id)

    data = {}
    data['title'] = course.title

    user_rq = request.user 
    if user_rq.user_type == 2 :
        teacher = request.user.teacher

        url = 'qcm/course/ajax_shower_course_teacher.html'
    else :
        teacher = None
        url = 'qcm/course/ajax_shower_course.html'        



    context = {  'course': course , 'parcours': parcours , 'teacher' : teacher  , 'user' : user_rq  }
 
 
    html = render_to_string(url, context )
    data['html'] = html       
    data['title'] = course.title   

    return JsonResponse(data)


#######################################################################################################################################################################
#######################################################################################################################################################################
##################    Demand     
#######################################################################################################################################################################
#######################################################################################################################################################################


@login_required(login_url= 'index')
def list_demands(request):

    demands = Demand.objects.order_by("done")

    return render(request, 'qcm/demand/show_demand.html', {'demands': demands,  })



@login_required(login_url= 'index')
def create_demand(request):
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    form = DemandForm(request.POST or None  )
    if request.method == "POST" :
        if form.is_valid():
            nf =  form.save(commit = False)
            nf.teacher = teacher
            nf.save()
            messages.success(request, 'La demande a été envoyée avec succès !')
            rec = ['brunoserres33@gmal.com', 'philippe.demaria83@gmal.com', ]
            sending_mail("SacAdo Demande d'exercice",  "Demande d'exercice.... voir dans Demande d'exercices sur sacado.xyz\n Nous essaierons de réaliser l'exercice au plus proche de vos idées." , settings.DEFAULT_FROM_EMAIL , rec )

            sender = [teacher.user.email,]
            sending_mail("SacAdo Demande d'exercice",  "Votre demande d'exercice est en cours de traitement." , settings.DEFAULT_FROM_EMAIL , sender )


            return redirect('index')

        else:
            print(form.errors)

    context = {'form': form,   'teacher': teacher, 'parcours': None , 'relationships': None , 'course': None , }

    return render(request, 'qcm/demand/form_demand.html', context)



@login_required(login_url= 'index')
def update_demand(request, id):
 
    demand = Demand.objects.get(id=id)
    demand_form = DemandForm(request.POST or None, instance=demand, )
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')
    
    if request.method == "POST" :
        if demand_form.is_valid():
            nf =  form.save(commit = False)
            nf.teacher = teacher
            nf.save()
 

            messages.success(request, 'La demande a été modifiée avec succès !')
            return redirect('index')
        else :
            print(demand_form.errors)

    context = {'form': demand_form,  'demand': demand, 'teacher': teacher , 'parcours': None  , 'relationships': relationships , }

    return render(request, 'qcm/demand/form_demand.html', context )



@login_required(login_url= 'index')
def delete_demand(request, id  ):
    """
    idc : demand_id et id = parcours_id pour correspondre avec le decorateur
    """
    demand = Demand.objects.get(id=idc)
    demand.delete()
    return redirect('index')  



@login_required(login_url= 'index')
def show_demand(request, id ):
    """
    idc : demand_id et id = parcours_id pour correspondre avec le decorateur
    """
    demand = Demand.objects.get(pk =  id)

    user = request.user 
    teacher = user.teacher
    context = {  'demands': demands, 'teacher': teacher , 'parcours': None , 'group_id' : None, 'communications' : []}
    return render(request, 'qcm/demand/show_demand.html', context)






 
@csrf_exempt
def ajax_chargeknowledges(request):
    id_theme =  request.POST.get("id_theme")
    theme = Theme.objects.get(id=id_theme)
 
    data = {}
    ks = Knowledge.objects.values_list('id', 'name').filter(theme=theme)
    data['knowledges'] = list(ks)
 
    return JsonResponse(data)


@csrf_exempt
def ajax_demand_done(request) :

    code = request.POST.get("code") #id de l'e
    id =  request.POST.get("id")

    Demand.objects.filter(id=id).update(done=1)
    Demand.objects.filter(id=id).update(code=code)

    demand = Demand.objects.get(id=id)

    rec = [demand.teacher.user.email]

    sending_mail("SacAdo Demande d'exercice",  "Bonjour " + str(demand.teacher.user.get_full_name())+ ", \n\n Votre exercice est créé. \n\n Pour tester votre exercice, https://sacado.xyz/qcm/show_exercise/"+str(code)  +"\n\n Bonne utilisation de sacado." , settings.DEFAULT_FROM_EMAIL , rec )
    data={}
    return JsonResponse(data)




#######################################################################################################################################################################
#######################################################################################################################################################################
##################    Mastering     
#######################################################################################################################################################################
#######################################################################################################################################################################

def create_mastering(request,id):

    relationship = Relationship.objects.get(pk = id)
    stage = get_stage(request.user)
    form = MasteringForm(request.POST or None, request.FILES or None, relationship = relationship )


    base_m       = Mastering.objects.filter(relationship = relationship)

    masterings_q = base_m.filter(scale = 4).order_by("ranking")
    masterings_t = base_m.filter(scale = 3).order_by("ranking")
    masterings_d = base_m.filter(scale = 2).order_by("ranking")
    masterings_u = base_m.filter(scale = 1).order_by("ranking")
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    if not teacher_has_permisson_to_parcourses(request,teacher,relationship.parcours) :
        return redirect('index')

    if request.method == "POST" :
        if form.is_valid():
            nf = form.save(commit = False)
            nf.scale = int(request.POST.get("scale"))
            nf.save()
            form.save_m2m()
        else:
            print(form.errors)

    context = {'form': form,   'relationship': relationship , 'parcours': relationship.parcours , 'relationships': [] ,  'communications' : [] ,  'course': None , 'stage' : stage , 'teacher' : teacher ,  'group': None,
                'masterings_q' : masterings_q, 'masterings_t' : masterings_t, 'masterings_d' : masterings_d, 'masterings_u' : masterings_u}

    return render(request, 'qcm/mastering/form_mastering.html', context)




#@user_is_relationship_teacher 
def parcours_mastering_delete(request,id,idm):

    m = Mastering.objects.get(pk = idm)
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    if not teacher_has_permisson_to_parcourses(request,teacher,m.relationship.parcours) :
        return redirect('index')

    m.delete()
    return redirect('create_mastering', id )






@csrf_exempt # PublieDépublie un exercice depuis organize_parcours
def ajax_sort_mastering(request):

    try :
        relationship_id = request.POST.get("relationship_id")
        mastering_ids = request.POST.get("valeurs")
        mastering_tab = mastering_ids.split("-") 
     
        for i in range(len(mastering_tab)-1):
            Mastering.objects.filter(relationship_id = relationship_id , pk = mastering_tab[i]).update(ranking = i)
    except :
        pass

    data = {}
    return JsonResponse(data) 




@csrf_exempt  # PublieDépublie un exercice depuis organize_parcours
def ajax_populate_mastering(request): 
    # Cette fonction est appelé pour les exercices ou pour les customexercises. Du coup pour éviter une erreur, si la relationship n'existe pas on ne fait rien, juste le css

    scale = int(request.POST.get("scale"))
    exercise_id = int(request.POST.get("exercise_id"))
    rs = request.POST.get("relationship_id",None) # Permet de garder le jeu du css
    if rs :
        relationship_id = int(rs)
        relationship = Relationship.objects.get(pk = relationship_id) 
    exercise = Exercise.objects.get(pk = exercise_id)
    statut = request.POST.get("statut") 
    data = {}    

    if statut=="true" or statut == "True":
        if rs :
            m = Mastering.objects.get(relationship=relationship, exercise = exercise)  
            m.delete()         
        statut = 0
        data["statut"] = "False"
        data["class"] = "btn btn-danger"
        data["noclass"] = "btn btn-success"
        data["html"] = "<i class='fa fa-times'></i>"
        data["no_store"] = False

    else:
        statut = 1
        if rs :
            if Mastering.objects.filter(relationship=relationship, exercise = exercise).count() == 0 :
                mastering = Mastering.objects.create(relationship=relationship, exercise = exercise, scale= scale, ranking=0)  
                data["statut"] = "True"
                data["no_store"] = False

            else :
                data["statut"] = "False"
                data["no_store"] = True
           
        else :
            data["statut"] = "True"
            data["no_store"] = False

    return JsonResponse(data) 



def mastering_student_show(request,id):

    relationship = Relationship.objects.get(pk = id)
    teacher = relationship.parcours.teacher
    stage = Stage.objects.get(school= teacher.user.school)

    student = Student.objects.get(user= request.user)
    studentanswer = Studentanswer.objects.filter(student=student, exercise = relationship.exercise, parcours = relationship.parcours).last()

    if studentanswer : 
        score = studentanswer.point
        if score > stage.up :
            masterings = Mastering.objects.filter(scale = 4, relationship = relationship)
        elif score > stage.medium :
            masterings = Mastering.objects.filter(scale = 3, relationship = relationship)
        elif score > stage.low :
            masterings = Mastering.objects.filter(scale = 2, relationship = relationship)
        else :
            masterings = Mastering.objects.filter(scale = 1, relationship = relationship)
    else :
        score = False
        masterings = []
    context = { 'relationship': relationship , 'masterings': masterings , 'parcours': None , 'relationships': [] ,  'communications' : [] ,  'score': score , 'group': None, 'course': None , 'stage' : stage , 'student' : student }

    return render(request, 'qcm/mastering/mastering_student_show.html', context)




@csrf_exempt  
def ajax_mastering_modal_show(request):

    mastering_id =  int(request.POST.get("mastering_id"))
    mastering = Mastering.objects.get( id = mastering_id)

    data = {}
    data['nocss'] = "modal-exo"
    data['css'] = "modal-md"
    data['duration'] = "<i class='fa fa-clock'></i> "+ str(mastering.duration)+" min."
    data['consigne'] = "<strong>Consigne : </strong>"+ str(mastering.consigne)
   
    form = None
    if mastering.writing  :
        resp = 0
        data['nocss'] = "modal-md"
        data['css'] = "modal-exo"
        student = Student.objects.get(user = request.user)
        mdone = Mastering_done.objects.filter( mastering = mastering , student = student)
        if mdone.count() == 1 :
            md = Mastering_done.objects.get( mastering = mastering , student = student)
            form = MasteringcustomDoneForm(instance = md )
        else :
            form = MasteringcustomDoneForm(request.POST or None )
    elif mastering.video != "" :
        resp = 1
    elif mastering.exercise :
        resp = 2
        data['duration'] = "<i class='fa fa-clock'></i> "+ str(mastering.exercise.supportfile.duration)+" min." 
        data['consigne'] = "Exercice"
        data['nocss'] = "modal-md"
        data['css'] = "modal-exo"
    elif len(mastering.courses.all()) > 0 :
        resp = 3
        data['css'] = "modal-exo"
        data['nocss'] = "modal-md"
    elif mastering.mediation != "" :
        resp = 4
        data['nocss'] = "modal-md"
        data['css'] = "modal-exo"

    context = { 'mastering' : mastering , 'resp' : resp , 'form' : form }

    html = render_to_string('qcm/mastering/modal_box.html',context)
    data['html'] = html       

    return JsonResponse(data)





def mastering_done(request):

    mastering = Mastering.objects.get(pk = request.POST.get("mastering"))
    student = Student.objects.get(user=request.user)

    mdone = Mastering_done.objects.filter( mastering = mastering , student = student)

    if mdone.count() == 0 : 
        form = MasteringDoneForm(request.POST or None )
    else :
        md = Mastering_done.objects.get( mastering = mastering , student = student)
        form = MasteringDoneForm(request.POST or None , instance = md )
    if form.is_valid() :
        nf = form.save(commit = False)
        nf.student =  student
        nf.mastering =  mastering
        nf.save()

    return redirect('mastering_student_show', mastering.relationship.id)








#######################################################################################################################################################################
#######################################################################################################################################################################
##################    Mastering Custom    
#######################################################################################################################################################################
#######################################################################################################################################################################

def create_mastering_custom(request,id,idp):
    customexercise = Customexercise.objects.get(pk = id)
    stage = Stage.objects.get(school= request.user.school)
    form = MasteringcustomForm(request.POST or None, request.FILES or None, customexercise = customexercise )

    parcours = Parcours.objects.get(pk= idp)

    masterings_q = Masteringcustom.objects.filter(customexercise = customexercise , scale = 4).order_by("ranking")
    masterings_t = Masteringcustom.objects.filter(customexercise = customexercise , scale = 3).order_by("ranking")
    masterings_d = Masteringcustom.objects.filter(customexercise = customexercise , scale = 2).order_by("ranking")
    masterings_u = Masteringcustom.objects.filter(customexercise = customexercise , scale = 1).order_by("ranking")
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    if request.method == "POST" :
        exercise_id = request.POST.get("exercises",None)
        if form.is_valid():
            nf = form.save(commit = False)
            nf.scale = int(request.POST.get("scale"))
            nf.exercise_id = exercise_id            
            nf.save()
            form.save_m2m()
        else:
            print(form.errors)

    context = {'form': form,   'customexercise': customexercise , 'parcours': parcours , 'relationships': [] ,  'communications' : [] ,  'course': None , 'stage' : stage , 'teacher' : teacher ,  'group': None,
                'masterings_q' : masterings_q, 'masterings_t' : masterings_t, 'masterings_d' : masterings_d, 'masterings_u' : masterings_u}

    return render(request, 'qcm/mastering/form_mastering_custom.html', context)


#@user_is_customexercice_teacher 
def parcours_mastering_custom_delete(request,id,idm,idp):

    m = Masteringcustom.objects.get(pk = idm)
    m.delete()
    return redirect('create_mastering_custom', id ,idp )

@csrf_exempt # PublieDépublie un exercice depuis organize_parcours
def ajax_sort_mastering_custom(request):

    try :
        relationship_id = request.POST.get("relationship_id")
        mastering_ids = request.POST.get("valeurs")
        mastering_tab = mastering_ids.split("-") 
     
        for i in range(len(mastering_tab)-1):
            Mastering.objects.filter(relationship_id = relationship_id , pk = mastering_tab[i]).update(ranking = i)
    except :
        pass

    data = {}
    return JsonResponse(data) 
 

def mastering_custom_student_show(request,id):

    customexercise = Customexercise.objects.get(pk = id)
    stage = Stage.objects.get(school= customexercise.teacher.user.school)

    student = Student.objects.get(user = request.user)
    studentanswer = Customanswerbystudent.objects.filter(student=student, customexercise = customexercise, parcours__in= customexercise.parcourses.all()).last()

    skill_answer = Correctionskillcustomexercise.objects.filter(student=student, customexercise = customexercise, parcours__in= customexercise.parcourses.all()).last()
    

    knowledge_answer = Correctionknowledgecustomexercise.objects.filter(student=student, customexercise = customexercise, parcours__in= customexercise.parcourses.all()).last()


    if skill_answer or studentanswer or knowledge_answer : 
        score = skill_answer.point
        if score > stage.up :
            masterings = Masteringcustom.objects.filter(scale = 4, customexercise = customexercise)
        elif score > stage.medium :
            masterings = Masteringcustom.objects.filter(scale = 3, customexercise = customexercise)
        elif score > stage.low :
            masterings = Masteringcustom.objects.filter(scale = 2, customexercise = customexercise)
        else :
            masterings = Masteringcustom.objects.filter(scale = 1, customexercise = customexercise)
    else :
        score = False
        masterings = []

    context = { 'customexercise': customexercise , 'masterings': masterings , 'parcours': None , 'relationships': [] ,  'communications' : [] ,  'score': score , 'group': None, 'course': None , 'stage' : stage , 'student' : student }

    return render(request, 'qcm/mastering/mastering_custom_student_show.html', context)


@csrf_exempt  
def ajax_mastering_custom_modal_show(request):

    mastering_id =  int(request.POST.get("mastering_id"))
    mastering = Masteringcustom.objects.get( id = mastering_id)

    data = {}
    data['nocss'] = "modal-exo"
    data['css'] = "modal-md"
    data['duration'] = "<i class='fa fa-clock'></i> "+ str(mastering.duration)+" min."
    data['consigne'] = "<strong>Consigne : </strong>"+ str(mastering.consigne)
   
    form = None
    if mastering.writing  :
        resp = 0
        data['nocss'] = "modal-md"
        data['css'] = "modal-exo"
        student = Student.objects.get(user = request.user)
        mdone = Masteringcustom_done.objects.filter( mastering = mastering , student = student)
        if mdone.count() == 1 :
            md = Masteringcustom_done.objects.get( mastering = mastering , student = student)
            form = MasteringcustomDoneForm(instance = md )
        else :
            form = MasteringcustomDoneForm(request.POST or None )
    elif mastering.video != "" :
        resp = 1
    elif mastering.exercise :
        resp = 2
        data['duration'] = "<i class='fa fa-clock'></i> "+ str(mastering.customexercise.duration)+" min." 
        data['consigne'] = "Exercice"
        data['nocss'] = "modal-md"
        data['css'] = "modal-exo"
    elif len(mastering.courses.all()) > 0 :
        resp = 3
        data['css'] = "modal-exo"
        data['nocss'] = "modal-md"
    elif mastering.mediation != "" :
        resp = 4
        data['nocss'] = "modal-md"
        data['css'] = "modal-exo"

    context = { 'mastering' : mastering , 'resp' : resp , 'form' : form }

    html = render_to_string('qcm/mastering/modal_box.html',context)
    data['html'] = html       

    return JsonResponse(data)



def mastering_custom_done(request):
 
    mastering = Masteringcustom.objects.get(pk = request.POST.get("mastering"))
    student = Student.objects.get(user=request.user)

    mdone = Masteringcustom_done.objects.filter( mastering = mastering , student = student)

    if mdone.count() == 0 : 
        form = MasteringcustomDoneForm(request.POST or None )
    else :
        md = Masteringcustom_done.objects.get( mastering = mastering , student = student)
        form = MasteringcustomDoneForm(request.POST or None , instance = md )
    if form.is_valid() :
        nf = form.save(commit = False)
        nf.student =  student
        nf.mastering =  mastering
        nf.save()

    return redirect('mastering_custom_student_show', mastering.customexercise.id)


##################################################################################################################################################
##################################################################################################################################################
##################################################       FOLDER      #############################################################################    
##################################################################################################################################################
##################################################################################################################################################

def affectation_students_in_folder_and_affectation_groups_in_folder(nf,group_ids,parcours_ids):

    all_students = set()
    for group_id in group_ids :    
        group = Group.objects.get(pk = group_id)
        group_students = group.students.all()
        all_students.update( group_students )
    nf.students.set(all_students) 

    for parcours_id in parcours_ids:
        parcours = Parcours.objects.get(pk=parcours_id)
        parcours.groups.set(group_ids)

    return all_students


@login_required(login_url= 'index') 
def create_folder(request,idg):
    """ 'parcours_is_folder' : True pour les vignettes et différencier si folder ou pas """
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    if idg > 0 :
        group_id = idg
        group = Group.objects.get(pk = idg)
        students = group.students.all()
        form = FolderForm(request.POST or None, request.FILES or None, teacher = teacher, subject = group.subject, level = group.level, initial = {'subject': group.subject,'level': group.level,'groups': [group] ,'coteachers': group.teachers.all()  } )
        images = get_images_for_parcours_or_folder(group)
    else :
        group_id = None        
        group = None
        form = FolderForm(request.POST or None, request.FILES or None, teacher = teacher, subject = None, level = None, initial = None )
        images = []
        students = None

    if request.method == "POST" :
        if form.is_valid():
            nf = form.save(commit=False)
            nf.author = teacher
            if group :
                nf.teacher = group.teacher
                nf.level = group.level
                nf.subject = group.subject
            else :
                nf.teacher = teacher
            if request.POST.get("this_image_selected",None) : # récupération de la vignette précréée et insertion dans l'instance du parcours.
                nf.vignette = request.POST.get("this_image_selected",None)
            nf.save() 
            form.save_m2m()

            # Tous les élèves des groupes cochés sont affecté au nouveau dossier
            group_ids = request.POST.getlist("groups",[])
            parcours_ids = request.POST.getlist("parcours",[])
            all_students = affectation_students_in_folder_and_affectation_groups_in_folder(nf,group_ids,parcours_ids)
            affectation_students_to_contents_parcours_or_evaluation( parcours_ids , all_students )
            #Gestion de la coanimation
            set_coanimation_teachers(nf,  group_ids,teacher)

            if group :    
                return redirect ("list_parcours_group", idg ) 
            elif request.POST.get("to_index"):
                return redirect('index') 
            else :
                return redirect ("folders") 
        else:
            print(form.errors)

    context = {'form': form,  'parcours_is_folder' : True,   'teacher': teacher, 'group': group,  'group_id': group_id,  'images' : images ,    'parcours': None,   'role' : True }

    return render(request, 'qcm/form_folder.html', context)
 

@login_required(login_url= 'index')
@folder_exists
def update_folder(request,id,idg):
    """ 'parcours_is_folder' : True pour les vignettes et différencier si folder ou pas """
    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    folder  = Folder.objects.get(id=id)
    images  = []

    if idg == 0 :
        if len( folder.groups.all() ) > 0 :
            group = folder.groups.first()
            group_id = group.id
            images = get_images_for_parcours_or_folder(group)
        else :
            group = None
            group_id = None
            images = get_images_for_parcours_or_folder(group)

    if idg == 999999999999999999 :
        group = None
        group_id = None            
        images = get_images_for_parcours_or_folder(group)
    elif idg == 0 :
        group_id = None
        group = None
        images = []
    else :
        group = Group.objects.get(pk = idg)
        group_id = group.id
        images = []

    form = FolderForm(request.POST or None, request.FILES or None, instance = folder , teacher = teacher, subject = folder.subject, level = folder.level )
    if request.method == "POST" :
        if form.is_valid():
            nf = form.save(commit=False)
            if request.POST.get("this_image_selected",None) : # récupération de la vignette précréée et insertion dans l'instance du parcours.
                nf.vignette = request.POST.get("this_image_selected",None)
            nf.save() 
            form.save_m2m()  

            # Tous les élèves des groupes cochés sont affecté au nouveau dossier
            group_ids = request.POST.getlist("groups",[])
            parcours_ids = request.POST.getlist("parcours",[])
            all_students = affectation_students_in_folder_and_affectation_groups_in_folder(nf,group_ids,parcours_ids)
            affectation_students_to_contents_parcours_or_evaluation( parcours_ids , all_students )
            change_coanimation_teachers(nf, folder , group_ids , teacher)
            
            if idg == 0 :
                return redirect('folders') 
            elif idg == 999999999999999999 :
                return redirect('index') 
            elif request.POST.get("to_index"):
                return redirect('index') 
            elif group_id :
                return redirect ("list_parcours_group", group_id )
            else :
                return redirect ("parcours")
 
        else:
            print(form.errors)
 
    context = {'form': form, 'teacher': teacher,  'group': group,  'group_id': group_id,  'folder': folder,  'images' : images ,   'relationships': [], 'role' : True }
 
    return render(request, 'qcm/form_folder.html', context)
 

@login_required(login_url= 'index')
@folder_exists
def folder_archive(request,id,idg):

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    if folder.teacher == teacher :
        folder = Folder.objects.get(id=id)
        folder.is_archive = 1
        folder.save()
        parcourses = folder.parcours.all()
     
        for p in parcourses :
            p.is_archive = 1
            p.save()

        return redirect('list_parcours_group' , idg )
        messages.error(request,"Dossier" + folder.title +" archivé")
    else :
        messages.error(request,"Vous n'avez pas les droits d'accès")
        return redirect('index')





@login_required(login_url= 'index')
@folder_exists
def folder_unarchive(request,id,idg):

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    if folder.teacher == teacher :
        folder = Folder.objects.get(id=id)
        folder.is_archive = 0
        folder.is_favorite = 0
        folder.save()
        subparcours = folder.parcours.all()
     
        for p in subparcours :
            p.is_archive = 0
            p.is_favorite = 0
            p.save()
        messages.error(request,"Dossier" + folder.title +" désarchivé")
    else :
        messages.error(request,"Vous n'avez pas les droits d'accès")
        return redirect('index')
 
    return redirect('parcours') 
 


@login_required(login_url= 'index')
@folder_exists
def delete_folder(request,id,idg):

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    folder  = Folder.objects.get(id=id)
    if folder.teacher.user.id == 2480 :
        messages.error(request, "  !!!  Redirection automatique  !!! Suppression interdite.")
        return redirect('index')


    if folder.teacher == teacher or request.user.is_superuser :
        Folder.objects.filter(pk=folder.id).update(is_trash=1)

    else :
        messages.error(request, "Vous ne pouvez pas supprimer le dossier "+ folder.title +". Contacter le propriétaire.")
    if idg == 999999999999999999 :
        return redirect ("index" )  
    elif idg == 0 :
        return redirect ("parcours" )  
    else :
        return redirect ("list_parcours_group", idg )  








@login_required(login_url= 'index')
def parcours_delete_from_folder(request):

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    parcours_id =  request.POST.get("parcours_id",None) 
    if parcours_id :
        folder = Folder.objects.get( pk = int(parcours_id))

        if parcours.teacher == teacher :
            Folder.objects.filter(pk=folder.id).update(is_trash=1)
    data = {}
         
    return JsonResponse(data)


@login_required(login_url= 'index')
@folder_exists
def delete_folder_and_contents(request,id,idg):

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    folder = Folder.objects.get(id=id)

    if folder.teacher.id == 2480 :
        messages.error(request, "  !!!  Redirection automatique  !!! Suppression interdite.")
        return redirect('index')

    if not authorizing_access(teacher,parcours, True ):
        messages.error(request, "  !!!  Redirection automatique  !!! Violation d'accès. Contacter SACADO...")
        return redirect('index')

    if parcours.teacher == teacher or request.user.is_superuser :
        for p in folder.parcours.all()  :
            if p.teacher == teacher or request.user.is_superuser :
                p.is_trash=1
                p.save()
        parcours.is_trash=1
        parcours.save()
        messages.success(request, "Le dossier "+ parcours.title +" et les parcours associés sont supprimés.")
    
    else :
        messages.error(request, "Vous ne pouvez pas supprimer le dossier "+ parcours.title +". Contacter le propriétaire.")
    
    if idg == 0 :
        return redirect ("parcours" )  
    else :
        return redirect ("list_parcours_group", idg )  



def ajax_subparcours_check(request):
    parcours_id =  request.POST.get("parcours_id",None) 
    data = {}
         
    return JsonResponse(data)




def actioner_pef(request):

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    idps = request.POST.getlist("selected_parcours")
    idfs = request.POST.getlist("selected_folders")

    if  request.POST.get("action") == "deleter" :  
        for idp in idps :
            parcours = Parcours.objects.get(id=idp) 
            parcours.students.clear()

            if not authorizing_access(teacher, parcours, False ):
                messages.error(request, "  !!!  Redirection automatique  !!! Violation d'accès. Contacter SACADO...")
                return redirect('index')


            studentanswers = Studentanswer.objects.filter(parcours = parcours)
            for s in studentanswers :
                s.delete()
            parcours.is_trash=1
            parcours.save()
 

        for idf in idfs :
            folder = Folder.objects.get(id=idf)
            for parcours in folder.parcours.all():
                parcours.students.clear()

                if not authorizing_access(teacher, parcours, False ):
                    messages.error(request, "  !!!  Redirection automatique  !!! Violation d'accès. Contacter SACADO...")
                    return redirect('index')

                studentanswers = Studentanswer.objects.filter(parcours = parcours)
                for s in studentanswers :
                    s.delete()
                parcours.is_trash=1
                parcours.save()
            folder.delete()

 
    elif request.POST.get("action") == "archiver" :  
 

        for idp in idps :
            parcours = Parcours.objects.get(id=idp) 
            parcours.is_archive = 1
            parcours.is_favorite = 0
            parcours.save()
 

        for idf in idfs :
            folder = Folder.objects.get(id=idf) 
            folder.is_archive = 1
            folder.is_favorite = 0
            folder.save()
            subparcours = folder.parcours.all()
            for p in subparcours :
                p.is_archive = 1
                p.is_favorite = 0
                p.save()
 
    else :

        for idp in idps :
            parcours = Parcours.objects.get(id=idp) 
            parcours.is_archive = 0
            parcours.is_favorite = 0
            parcours.save()


        for idf in idfs :
            folder = Folder.objects.get(id=idf) 
            folder.is_archive = 0
            folder.is_favorite = 0
            folder.save()
            subparcours = folder.parcours.all()
            for p in subparcours :
                p.is_archive = 0
                p.is_favorite = 0
                p.save()

    return redirect('parcours')






def actioner_course(request):

    try :
        teacher = request.user.teacher
    except :
        messages.error(request,"Vous n'êtes pas enseignant ou pas connecté.")
        return redirect('index')

    idps = request.POST.getlist("selected_parcours")

    for idp in idps :
        course = Course.objects.get(id=idp) 
        course.students.clear()
        course.delete()
 
    return redirect('courses')











# def ajax_group_to_parcours(request):
#     """ reaffecter un groupe à un parcours"""
#     teacher     = request.user.teacher 
#     parcours_id = request.POST.get("parcours_id",None) 
#     group_id    = request.POST.get("group_id",None) 

#     if parcours_id and group_id :
#         parcours = Parcours.objects.get(pk = parcours_id)
#         group    = Group.objects.get(pk = group_id)
#         parcours.groups.add(group)
#     data = {} 
#     data['html'] = "<small><i class='fa fa-check text-success'></i> Attribué à "+ group.name  +"</small>"    

#     return JsonResponse(data)




#######################################################################################################################################################################
#######################################################################################################################################################################
#################   Testeurs
#######################################################################################################################################################################
#######################################################################################################################################################################
@user_passes_test(user_is_testeur)
def admin_testeur(request):

    user = request.user
    reporting_s , reporting_p , reporting_c = [] , [] , []
    reportings = DocumentReport.objects.exclude(is_done=1)
    for r in reportings :
        if r.document == "supportfile" :
            reporting_s.append(r.id)
        if r.document == "parcours" :
            reporting_p.append(r.id)
        if r.document == "cours" :
            reporting_c.append(r.id)

    parcourses = Parcours.objects.filter(teacher__user_id = 2480,is_trash=0).exclude(pk__in=reporting_s).order_by("level")
    supportfiles = Supportfile.objects.filter(is_title=0).exclude(pk__in=reporting_p).order_by("level","theme","knowledge__waiting","knowledge","ranking")
    courses = Course.objects.filter(teacher__user_id = 2480).exclude(pk__in=reporting_c).order_by("parcours")
    form_reporting = DocumentReportForm(request.POST or None )

    context = { "user" :  user , "parcourses" :  parcourses , "supportfiles" :  supportfiles , "courses" :  courses ,  "form_reporting" :  form_reporting , }
 
    return render(request, 'qcm/dashboard_testeur.html', context)




@user_passes_test(user_is_testeur)
def reporting(request ):

    user = request.user    
    form_reporting = DocumentReportForm(request.POST or None )
    if form_reporting.is_valid() :
        nf = form_reporting.save(commit=False)
        nf.user = request.user
        nf.document = request.POST["document"]
        nf.save()

        rec = ["nicolas.villemain@claudel.org" , "brunoserres33@gmail.com " , "sacado.asso@gmail.com"]
        if nf.report != "<p>RAS</p>" :
            sending_mail("SACADO "+nf.document+" à modifier", str(nf.document)+" #"+str(nf.document_id)+" doit recevoir les modifications suivantes : \n\n "+str(cleanhtml(nf.report))+"\n\n"+str(request.user) , settings.DEFAULT_FROM_EMAIL , rec )
        else :
            DocumentReport.objects.filter(pk=int(nf.document_id)).update(is_done=1)
            sending_mail("SACADO "+nf.document+" #"+str(nf.document_id)+" vérifié", str(nf.document)+" dont l'id: "+str(nf.document_id)+" est validé sans erreur par "+str(request.user) , settings.DEFAULT_FROM_EMAIL , rec )

    return redirect('admin_testeur')


@user_passes_test(user_is_testeur)
def reporting_list(request, code ):

    tab = ["supportfile","parcours","course"]
    user = request.user  
    reportings = DocumentReport.objects.filter(document=tab[code], is_done=0).exclude(report="<p>RAS</p>")

    context = { "user" :  user , "reportings" : reportings , "doc" : tab[code] , "code" : code }
 
    return render(request, 'qcm/reporting_list.html', context)
 


@user_passes_test(user_is_testeur)
def repaired_reporting(request, pk,code ):

    DocumentReport.objects.filter(pk=pk).update(is_done=1)
    return redirect( 'admin_testeur', code)


def simulator(request):
    context = {}
    return render(request, 'qcm/simulator.html', context )




#############################################################################################################################################
#############################################################################################################################################
####   Préparation aux évaluations
#############################################################################################################################################
#############################################################################################################################################
def structure_idx(liste):
    listes,origins = [],[]
    for i in range(len(liste)) :
        if liste[i] != 2 :
            origins.append( i )
            try :
                if liste[i+1]==2:
                    listes.append(origins)
                    origins = []
            except :
                listes.append(origins)
                origins = []
    return listes

def list_idx(listes):
    nlistes = []
    for liste in listes :
        if len(liste)<4: congruence,odd = 2,0
        elif 3<len(liste)<7: congruence,odd = 2,0
        elif 6<len(liste)<10: congruence,odd = 2,1
        elif 9<len(liste)<13: congruence,odd = 3,0
        else : congruence,odd = 3,1
        i=0
        for c in liste:
            if i%congruence==odd  : nlistes.append(c)
            i+=1
    return nlistes 


def make_slots(this_parcours, parcours_ids, nf,student):

    delta     = nf.date - nf.date_created # nombre de jours
    durations = [0,5,5,5,10,10,10,10,15,20,25,30,45,60] # par niveau
    nb_days   = int(delta.days)-1
    days      = list()*int(nb_days)
    today     = datetime.now().date()

    # creation du parcours global
    for parcours_id in parcours_ids :
        parcours      = Parcours.objects.get(pk=parcours_id)
        relationships = parcours.parcours_relationship.exclude(type_id=1).exclude(exercise__supportfile__is_title=1).order_by('ranking')[2:]
        rank = 1
        for relationship in relationships :
            skills = relationship.skills.all()             
            relationship.pk=None
            relationship.situation=3
            try :
                if relationship.exercise.supportfile.level < 10 : duree = 3
                else : duree = 5 
            except : duree = 3
            relationship.duration = duree
            relationship.parcours = this_parcours
            relationship.ranking  = rank
            try :
                relationship.save()
                relationship.students.add(student)
                relationship.skills.set(skills)
            except : pass
            rank += 1


    nb_relationships_by_day = this_parcours.parcours_relationship.count()//nb_days
    # Création des slots
    for i in range(nb_days) : # i représente le slot du ième jour
        j = nb_days-i
        this_day  = today + timedelta(days = i+1)
        this_slot = Slot.objects.create(date = this_day, content = "<b>Jour J-"+str(j)+".</b> ", prepeval = nf ,done=0)
        relationships  = this_parcours.parcours_relationship.order_by('ranking')[i*nb_relationships_by_day:(i+1)*nb_relationships_by_day]
        documents_list = this_parcours.parcours_relationship.values_list("type_id",flat=True).order_by('ranking')[i*nb_relationships_by_day:(i+1)*nb_relationships_by_day]
        stte_idx = list_idx( structure_idx( list(documents_list) ) )

        # enlève de cette liste les exos qui sont dans studentanswer
        for j in range(len(relationships)):
            if j in stte_idx :
                this_slot.relationships.add(relationships[j])
            elif relationships[j].type_id == 2 :
                if Course.objects.get(pk = relationships[j].document_id ).forme != "" :
                    this_slot.relationships.add(relationships[j])


def get_details_from_student(student):
    adhesion = student.adhesions.last()
    teacher_id = 2480
    subject_id = 1
    level_id = adhesion.level.id
    return teacher_id, subject_id , level_id


def prep_eval(request,id):

    student = Student.objects.get(user_id=id)
    request.session["tdb"] = "prep_eval" # permet l'activation du surlignage de l'icone dans le menu gauche
    request.session["subtdb"] = ""

    prepevals  = Prepeval.objects.filter(student  = student).order_by("-date")
    parcourses = Parcours.objects.filter(students = student)

    form    = PrepevalForm(request.POST or None)
    teacher_id, subject_id, level_id = get_details_from_student(student)

    if request.method == 'POST':
        parcours_ids = request.POST.getlist('parcours_ids')
        if len(parcours_ids) == 0 :
            messages.error(request,"Vous devez sélectionner au moins un thème.")
            return redirect('prep_eval',id)
        if form.is_valid():
            nf = form.save(commit=False)
            if nf.date == "" :
                messages.error(request,"Vous devez sélectionner une date.")
                return redirect('prep_eval',id)
            nf.student = student
            this_parcours = Parcours.objects.create(title="Révision du "+str(nf.date), teacher_id = teacher_id, author_id = teacher_id, subject_id = subject_id,  is_publish=1 , level_id = level_id , is_sequence=1)
            nf.parcours = this_parcours
            nf.save()
            nf.o_parcours.set(parcours_ids)
            slots = make_slots(this_parcours, parcours_ids , nf,student)
            this_parcours.students.add(student)

    context = {  'prepevals' : prepevals , 'parcourses' : parcourses  , 'form' : form  , 'student' : student }
 
    return render(request, 'qcm/prep_eval.html', context)


def show_prepeval(request,idp):

    request.session["tdb"] = "prep_eval" # permet l'activation du surlignage de l'icone dans le menu gauche
    request.session["subtdb"] = ""
    request.session["prepeval_id"] = idp


    prepeval = Prepeval.objects.get(pk=idp)
    slots    = prepeval.slots.all()
    today    = date.today() 

    context = {'prepeval' : prepeval , 'slots' : slots , 'today' : today }

    return render(request, 'qcm/show_prep_eval.html', context)


def delete_prepeval(request,ids,idp):
    Prepeval.objects.filter(pk=idp).delete()
    return redirect('prep_eval', ids)



