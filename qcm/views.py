#################################
#### Auteur : philipe Demaria 
#### pour SACADO
#################################

from django.conf import settings # récupération de variables globales du settings.py
from django.shortcuts import render, redirect
from account.models import  Student, Teacher, User,Resultknowledge, Resultskill, Resultlastskill
from account.forms import StudentForm, TeacherForm, UserForm
from django.contrib.auth.forms import  AuthenticationForm
from django.forms.models import modelformset_factory
from django.forms import inlineformset_factory
from django.contrib.auth.decorators import  permission_required,user_passes_test, login_required
from sendmail.forms import  EmailForm
from group.forms import GroupForm 
from group.models import Group , Sharing_group
from school.models import Stage, School
from qcm.models import  Folder , Parcours , Blacklist , Studentanswer, Exercise, Exerciselocker ,  Relationship,Resultexercise, Generalcomment , Resultggbskill, Supportfile,Remediation, Constraint, Course, Demand, Mastering, Masteringcustom, Masteringcustom_done, Mastering_done, Writtenanswerbystudent , Customexercise, Customanswerbystudent, Comment, Correctionknowledgecustomexercise , Correctionskillcustomexercise , Remediationcustom, Annotation, Customannotation , Customanswerimage , DocumentReport , Tracker , Criterion , Autoposition
from qcm.forms import FolderForm , ParcoursForm , Parcours_GroupForm, RemediationForm ,  AudioForm , UpdateSupportfileForm, SupportfileKForm, RelationshipForm, SupportfileForm, AttachForm ,   CustomexerciseNPForm, CustomexerciseForm ,CourseForm , CourseNPForm , DemandForm , CommentForm, MasteringForm, MasteringcustomForm , MasteringDoneForm , MasteringcustomDoneForm, WrittenanswerbystudentForm,CustomanswerbystudentForm , WAnswerAudioForm, CustomAnswerAudioForm , RemediationcustomForm , CustomanswerimageForm , DocumentReportForm, CriterionForm
from tool.forms import QuizzForm
from socle.models import  Theme, Knowledge , Level , Skill , Waiting , Subject
from bibliotex.models import Bibliotex
from tool.models import Quizz
from flashcard.models import Flashpack
from django.http import JsonResponse 
from django.core import serializers
from django.template.loader import render_to_string
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from tool.consumers import *
import uuid
import time
import math
import json
import random
from datetime import datetime , timedelta
from django.db.models import Q , Avg
from django.core.mail import send_mail
from group.decorators import user_is_group_teacher 
from qcm.decorators import user_is_parcours_teacher, user_can_modify_this_course, student_can_show_this_course , user_is_relationship_teacher, user_is_customexercice_teacher , parcours_exists , folder_exists
from account.decorators import user_can_create, user_is_superuser, user_is_creator , user_is_testeur
##############bibliothèques pour les impressions pdf  #########################
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
from html import escape
from operator import attrgetter
from itertools import chain
cm = 2.54
import os
import re
import pytz
import csv
import html
from general_fonctions import *
 

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
    teacher  = parcours.teacher

    # folder   = parcours.folders.get(teacher = teacher , level = parcours.level , subject = parcours.subject)

    customexercises = parcours.parcours_customexercises.all()
    courses         = parcours.course.all()  
    quizzes         = parcours.quizz.all()
    flashpacks      = parcours.flashpacks.all()
    bibliotexs      = parcours.bibliotexs.all()

    # clone      
    # parcours.pk = None
    # parcours.teacher = teacher
    # parcours.is_publish = 1
    # parcours.is_archive = 0
    # parcours.is_share = 0
    # parcours.is_favorite = 1
    # parcours.code = str(uuid.uuid4())[:8]
    parcours.is_sequence = 1
    parcours.save()
    # folder.parcours.add(parcours)    
    # fin du clone

    for c  in customexercises : 
        relationc = Relationship.objects.create(parcours = parcours , exercise_id = None , document_id = c.id  , type_id = 1 , ranking =  100 , is_publish= c.is_publish  , start= None , date_limit= None, duration= c.duration, situation= 0 ) 
        relationc.students.set(students)

    for course in courses : 
        relation = Relationship.objects.create(parcours = parcours , exercise_id = None , document_id = course.id  , type_id = 2 , ranking =  200 , is_publish= course.is_publish  , start= None , date_limit= None, duration= course.duration, situation= 0 ) 
        relation.students.set(students)
    
    for quizz in quizzes : 
        relationq = Relationship.objects.create(parcours = parcours , exercise_id = None , document_id = quizz.id  , type_id = 3 , ranking =  300 , is_publish= quizz.is_publish , start= None , date_limit= None, duration= 10, situation= 0 ) 
        relationq.students.set(students)

    for flashpack in flashpacks : 
        relationf = Relationship.objects.create(parcours = parcours , exercise_id = None , document_id = flashpack.id  , type_id = 4 , ranking =  400 , is_publish= flashpack.is_publish  , start= None , date_limit= None, duration= 10, situation= 0 ) 
        relationf.students.set(students)

    for bibliotex in bibliotexs : 
        relationb = Relationship.objects.create(parcours = parcours , exercise_id = None , document_id = bibliotex.id  , type_id = 5 , ranking =  500 , is_publish= bibliotex.is_publish  , start= None , date_limit= None, duration= 10, situation= 0 ) 
        relationb.students.set(students)



    return redirect('show_parcours' , 0 , parcours.id  ) 




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

    teacher = request.user.teacher
 
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

    if parcours_or_group.teacher == teacher:
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
    parcourses = list(teacher.teacher_parcours.filter(is_evaluation=is_evaluation,is_archive=is_archive,is_trash=0).order_by("subject","level"))


    for sg in sharing_groups :
        pcs = group_has_parcourses(sg.group,is_evaluation ,is_archive )
        for p in pcs :
            if p not in parcourses:
                parcourses.append(p) 
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
    return test_has_permisson

def teacher_has_permisson_to_parcourses(request,teacher,parcours):


    test_has_permisson = teacher_has_permisson_to_share_inverse_parcourses(request,teacher,parcours)

    if test_has_permisson or parcours in teacher_has_parcourses(teacher,0,0) or parcours in teacher_has_parcourses(teacher,0,1) or parcours in teacher_has_parcourses(teacher,1,0) or parcours in teacher_has_parcourses(teacher,1,1):
        has_permisson = True
    elif request.user.is_superuser or request.user.is_creator or request.user.is_testeur :
        has_permisson = True
    else :
        messages.error(request, "  !!!  Redirection automatique  !!! Violation d'accès.")
        has_permisson = False
    return has_permisson 


def teacher_has_permisson_to_folder(request,teacher,folder):

    has_permisson = False
    if teacher in folder.coteachers.all() or folder.teacher == teacher :
        has_permisson = True

    return has_permisson 




def skills_in_parcours(request,parcours):

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


def total_by_knowledge_by_student(knowledge,relationships, parcours,student) : # résultat d'un élève par comptétnece sur un parcours donné
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
    teacher = request.user.teacher
    return render(request, 'advises.html', {'teacher': teacher})


@login_required(login_url= 'index')
def associate_parcours(request,id):
    teacher = request.user.teacher
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

def get_parcours_default(request):
    teacher = request.user.teacher
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
                relation = Relationship.objects.create(parcours_id=parcours_id, exercise_id = exercise_id, ranking = 100, maxexo = parcours.maxexo ,
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



@login_required(login_url= 'index')
def peuplate_parcours(request,id):
    teacher = request.user.teacher
    levels =  teacher.levels.all() 
    parcours = Parcours.objects.get(id=id)

    role, group , group_id , access = get_complement(request, teacher, parcours)


    if not authorizing_access(teacher,parcours, access ):
        messages.error(request, "  !!!  Redirection automatique  !!! Violation d'accès.")
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
                    r = Relationship.objects.create(parcours = nf , exercise = exercise , ranking =  i, situation = exercise.supportfile.situation , duration = exercise.supportfile.duration )  
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
    teacher = request.user.teacher
    levels =  teacher.levels.all() 
 
    parcours = Parcours.objects.get(id=id)

    role, group , group_id , access = get_complement(request, teacher, parcours)

    if not authorizing_access(teacher,parcours, access ):
        messages.error(request, "  !!!  Redirection automatique  !!! Violation d'accès.")
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
                    r = Relationship.objects.create(parcours = nf , exercise = exercise , ranking =  i, situation = exercise.supportfile.situation , duration = exercise.supportfile.duration )  
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

    teacher = request.user.teacher
    parcours = Parcours.objects.get(pk = id)
    relationships = parcours.parcours_relationship.order_by("ranking")
    customexercises = Customexercise.objects.filter(parcourses = parcours).order_by("ranking") 

    nb_rc = relationships.count() + customexercises.count()

    role, group , group_id , access = get_complement(request, teacher, parcours)

    if not authorizing_access(teacher,parcours, access ):
        messages.error(request, "  !!!  Redirection automatique  !!! Violation d'accès.")
        return redirect('index')
 

    context = {'relationships': relationships, 'parcours': parcours,     'communications':[],  'form': None,  
                'teacher': teacher, 'customexercises' : customexercises , 'nb_rc' : nb_rc ,
                'exercises': None , 'folder' : folder ,
                 'levels': None , 
                'themes' : None ,
                'user': request.user , 
                'group_id' : group_id , 'group' : group , 'role' : role }

    return render(request, 'qcm/form_individualise_parcours.html', context )



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
        messages.error(request, "  !!!  Redirection automatique  !!! Violation d'accès.")
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

                    else:
                        relationship.students.add(student)
                        if Blacklist.objects.filter(relationship=relationship, student = student , customexercise = None   ).count()  > 0 :
                            Blacklist.objects.get(relationship=relationship, student = student , customexercise = None   ).delete()
                        data["statut"] = "True"
                        data["class"] = "btn btn-success"
                        data["noclass"] = "btn btn-default"
                        data["alert"] = False


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
                else:
                    relationship.students.add(student) 
                    if Blacklist.objects.filter(relationship=relationship, student = student ,customexercise = None ).count() > 0 :
                        Blacklist.objects.get(relationship=relationship, student = student ,customexercise = None ).delete()
                    
                    data["statut"] = "True"
                    data["class"] = "btn btn-success"
                    data["noclass"] = "btn btn-default"
                    data["alert"] = False

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
        messages.error(request, "  !!!  Redirection automatique  !!! Violation d'accès.")
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
 

############################################################################################################################################
############################################################################################################################################
##################     Listes dossiers parcours évaluation archives  #######################################################################
############################################################################################################################################
############################################################################################################################################
@login_required(login_url= 'index')
def list_folders(request):

    teacher = request.user.teacher
    today   = time_zone_user(teacher.user)

    folders   = teacher_has_folders(teacher, 0  ) #  is_archive
    nb_base =  len( folders  )   
    nb_archive =  len( teacher_has_folders(teacher, 1  )  ) 
 
    request.session["tdb"] = False # permet l'activation du surlignage de l'icone dans le menu gauche

 
    groups = teacher.has_groups()

    if request.session.has_key("group_id"):
        del request.session["group_id"]
    if request.session.has_key("folder_id"):
        del request.session["folder_id"]

    return render(request, 'qcm/list_folders.html', { 'folders' : folders ,    'groups' : groups , 'nb_base' : nb_base , 
                    'parcours' : None , 'group' : None , 'today' : today ,  'teacher' : teacher , 'nb_archive' : nb_archive })

@login_required(login_url= 'index')
def list_folders_archives(request):

    teacher = request.user.teacher
    today   = time_zone_user(teacher.user)

    folders   = teacher_has_folders(teacher, 1  ) #  is_archive
    nb_base =  len( folders  )   
 
 
    request.session["tdb"] = False # permet l'activation du surlignage de l'icone dans le menu gauche

 
    groups = teacher.has_groups()

    if request.session.has_key("group_id"):
        del request.session["group_id"]
    if request.session.has_key("folder_id"):
        del request.session["folder_id"]

    return render(request, 'qcm/list_folders_archives.html', { 'folders' : folders ,    'groups' : groups , 'nb_base' : nb_base , 
                    'parcours' : None , 'group' : None , 'today' : today ,  'teacher' : teacher ,  })



@login_required(login_url= 'index')
def list_parcours(request):

    teacher = request.user.teacher
    today   = time_zone_user(teacher.user)

    folds   = teacher_has_folders(teacher, 0  ) #  is_archive
    folders = folders_contains_evaluation(folds, False,0)

    parcourses = Parcours.objects.filter(Q(teacher=teacher)|Q(coteachers=teacher),folders=None,is_evaluation=0,is_sequence=0, is_archive=0,is_trash=0)

    nb_archive =  len(  teacher_has_own_parcourses_and_folder(teacher,0,1,0 )   )   
    nb_base = len( folders ) + parcourses.count()
    request.session["tdb"] = False # permet l'activation du surlignage de l'icone dans le menu gauche
 
    groups = teacher.has_groups()

    if request.session.has_key("group_id"):
        del request.session["group_id"]
    if request.session.has_key("folder_id"):
        del request.session["folder_id"]

    return render(request, 'qcm/list_parcours.html', { 'folders' : folders , 'parcourses' : parcourses , 'nb_base' : nb_base ,  'groups' : groups ,
                    'parcours' : None , 'group' : None , 'today' : today ,  'teacher' : teacher , 'nb_archive' : nb_archive })



@login_required(login_url= 'index')
def list_archives(request):

    teacher = request.user.teacher
    today = time_zone_user(teacher.user)

    folders = teacher_has_folders(teacher, 1  ) #  is_archive
    parcourses = Parcours.objects.filter(Q(teacher=teacher)|Q(coteachers=teacher),folders=None,is_archive=1,is_sequence=0,is_trash=0)
    nb_archive =  len(  teacher_has_own_parcourses_and_folder(teacher,0,1,0 )   )   
 
 
    request.session["tdb"] = False # permet l'activation du surlignage de l'icone dans le menu gauche
 
    return render(request, 'qcm/list_archives.html', { 'folders' : folders , 'parcourses' : parcourses ,  
                                                        'today' : today ,  'teacher' : teacher , 'nb_base' : nb_archive   })



@login_required(login_url= 'index')
def list_sequences(request):

    teacher = request.user.teacher
    today   = time_zone_user(teacher.user)

    folds   = teacher_has_folders(teacher, 0  ) #  is_archive
    folders = folders_contains_evaluation(folds, False,1)

    parcourses = Parcours.objects.filter(Q(teacher=teacher)|Q(coteachers=teacher),folders=None,is_evaluation=0, is_archive=0,is_sequence=1,is_trash=0)

    nb_archive =  len(  teacher_has_own_parcourses_and_folder(teacher,0,1,1)   )   
    nb_base = len( folders ) + parcourses.count()
    request.session["tdb"] = False # permet l'activation du surlignage de l'icone dans le menu gauche
 
    groups = teacher.has_groups()

    if request.session.has_key("group_id"):
        del request.session["group_id"]
    if request.session.has_key("folder_id"):
        del request.session["folder_id"]

    return render(request, 'qcm/list_sequences.html', { 'folders' : folders , 'parcourses' : parcourses , 'nb_base' : nb_base ,  'groups' : groups ,
                    'parcours' : None , 'group' : None , 'today' : today ,  'teacher' : teacher , 'nb_archive' : nb_archive })



@login_required(login_url= 'index')
def list_sequences_archives(request):

    teacher = request.user.teacher
    today = time_zone_user(teacher.user)

    folders = teacher_has_folders(teacher, 1  ) #  is_archive
    parcourses = Parcours.objects.filter(Q(teacher=teacher)|Q(coteachers=teacher),folders=None,is_archive=1,is_sequence=1,is_trash=0)
    nb_archive =  len(  teacher_has_own_parcourses_and_folder(teacher,0,1,1 )   )   
 
 
    request.session["tdb"] = False # permet l'activation du surlignage de l'icone dans le menu gauche
 
    return render(request, 'qcm/list_archives.html', { 'folders' : folders , 'parcourses' : parcourses ,  
                                                        'today' : today ,  'teacher' : teacher , 'nb_base' : nb_archive   })




@login_required(login_url= 'index')
def list_evaluations(request):

    teacher = request.user.teacher
    today = time_zone_user(teacher.user)

    folds = teacher_has_folders(teacher, 0  ) #  is_archive
    folders = folders_contains_evaluation(folds, True,0)

    parcourses = Parcours.objects.filter(Q(teacher=teacher)|Q(coteachers=teacher),folders=None,is_evaluation=1,is_archive=0,is_trash=0)
    nb_archive =  len(  teacher_has_own_parcourses_and_folder(teacher,1,1,0 )   )   
    nb_base = len( folders ) + parcourses.count()
    request.session["tdb"] = False # permet l'activation du surlignage de l'icone dans le menu gauche
 
    groups = teacher.has_groups()

    delete_session_key(request, "group_id") 
    delete_session_key(request, "folder_id") 
 
    return render(request, 'qcm/list_evaluations.html', { 'folders' : folders , 'parcourses' : parcourses , 'nb_base' : nb_base ,  'groups' : groups ,
                    'parcours' : None , 'group' : None , 'today' : today ,  'teacher' : teacher , 'nb_archive' : nb_archive })


 

@login_required(login_url= 'index')
def list_evaluations_archives(request):
    teacher = request.user.teacher
    parcourses = teacher_has_parcourses(teacher,1 ,1 ) #  is_evaluation ,is_archive 
    nb_base = len( parcourses )  
    today = time_zone_user(teacher.user)
    delete_session_key(request, "group_id")

    return render(request, 'qcm/list_evaluations_archives.html', { 'parcourses' : parcourses, 'parcours' : None , 'teacher' : teacher , 'communications' : [] ,  'today' : today ,  'nb_base' : nb_base   })


@login_required(login_url= 'index')
def list_parcours_group(request,id):

    teacher = request.user.teacher
    today = time_zone_user(request.user)
    group = Group.objects.get(pk = id) 

    #On entre dans un groupe donc on garde sa clé dans la session
    request.session["group_id"] = id

    role, group , group_id , access = get_complement(request, teacher, group)

    group = Group.objects.get(pk = id) 

    if not authorizing_access(teacher,group, access ):
        messages.error(request, "  !!!  Redirection automatique  !!! Violation d'accès.")
        return redirect('index')

    #On sort du dossier donc on enlève sa clé de la session
    request.session.pop('folder_id', None)

    folders     = group.group_folders.filter(Q(teacher=teacher)|Q(author=teacher)|Q(coteachers = teacher), subject = group.subject, level = group.level , is_favorite=1, is_archive=0, is_trash=0 ).distinct().order_by("ranking")

    bases       = group.group_parcours.filter(Q(teacher=teacher)|Q(author=teacher)|Q(coteachers = teacher), subject = group.subject, level = group.level , is_favorite=1, folders = None, is_trash=0).distinct()


    evaluations = bases.filter( is_evaluation=1).order_by("ranking")
    parcourses  = bases.exclude(is_evaluation=1,is_sequence=1).order_by("ranking")
    sequences   = bases.filter(is_sequence=1).order_by("ranking")

    parcours_tab = evaluations | parcourses

    ###efface le realtime de plus de 30min
    clear_realtime(parcours_tab , today.now() ,  1800 )
    nb_bases = bases.count() + folders.count()

    context =  { 'folders': folders , 'teacher' : teacher , 'group': group,  'parcours' : None ,  'role' : role , 'today' : today ,
                 'parcourses': parcourses , 'evaluations' : evaluations , 'sequences' : sequences , 'nb_bases' : nb_bases }

    return render(request, 'qcm/list_parcours_group.html', context )


@login_required(login_url= 'index')
def list_sub_parcours_group(request,idg,idf):

    teacher = request.user.teacher
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


    context = {'parcours_tab': parcours_tab , 'teacher' : teacher , 'group' : group ,  'folder' : folder, 'sequences' : sequences ,  'quizzes' : quizzes ,  'bibliotexs' : bibliotexs,   'flashpacks' : flashpacks,    'role' : role , 'today' : today , 'accordion' : accordion  }

    return render(request, 'qcm/list_sub_parcours_group.html', context )


@login_required(login_url= 'index')
def list_sub_parcours_group_student(request,idg,idf):

    rq_user = request.user
    if rq_user.is_authenticated :
        student = rq_user.student
        today   = time_zone_user(rq_user)
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
    
    else :
        return redirect("index")


@login_required(login_url= 'index')
def change_situations_in_all_relationships(request,idf,idp):

    parcours      = Parcours.objects.get(id=idp)
    relationships = parcours.parcours_relationship.filter(exercise__supportfile__is_title=0)
    teacher       = request.user.teacher
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
    teacher       = request.user.teacher
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
    teacher       = request.user.teacher
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
    teacher = request.user.teacher
    role, group , group_id , access = get_complement(request, teacher, parcours)
 

    if not authorizing_access(teacher,parcours, True ):
        messages.error(request, "  !!!  Redirection automatique  !!! Violation d'accès.")
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
    student = request.user.student
    if parcours.is_achievement : 
 
        students = parcours.students.order_by("user__last_name")
        context = {'students': students, 'parcours': parcours, 'student':student,  }
        return render(request, 'qcm/progression_group_student.html', context)
    else :
        messages.error(request,"accès interdit")
        return redirect('index')



@login_required(login_url= 'index')
def all_parcourses(request,is_eval):
    teacher = request.user.teacher
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
        else :
            group = None   
    except :
        group = None

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

 
    return render(request, 'qcm/list_parcours_shared.html', { 'is_eval' : is_eval ,  'teacher' : teacher ,   'parcourses': parcourses , 'inside' : inside ,   'parcours' : parcours , 'group' : group   })



def ajax_all_parcourses(request):

    teacher = request.user.teacher
    data = {}
    is_eval = int(request.POST.get('is_eval',0))
    level_id = request.POST.get('level_id',0)
    subject_id = request.POST.get('subject_id',None)


    teacher_id = get_teacher_id_by_subject_id(subject_id)

    # if request.user.is_superuser :
    #     if is_eval == 2 :
    #         parcours_ids = Parcours.objects.values_list("id",flat=True).distinct().filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id),is_share = 1,is_sequence = 1).order_by('level','ranking')
    #     else :
    #         parcours_ids = Parcours.objects.values_list("id",flat=True).distinct().filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id),is_share = 1,is_evaluation = is_eval).order_by('level','ranking')
    # else :
    #     if is_eval == 2 :
    #         parcours_ids = Parcours.objects.values_list("id",flat=True).distinct().filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id),is_share = 1,is_sequence = 1).order_by('level','ranking')
    #     else :
    #         parcours_ids = Parcours.objects.values_list("id",flat=True).distinct().filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id),is_share = 1,is_evaluation = is_eval).exclude(exercises=None ,teacher=teacher).order_by('level','ranking')

    keywords = request.POST.get('keywords',None)



    if int(level_id) > 0 :
        level = Level.objects.get(pk=int(level_id))
        theme_ids = request.POST.getlist('theme_id',[])

        if len(theme_ids) > 0 :

            if theme_ids[0] != '' :
                themes_tab = []

                for theme_id in theme_ids :
                    themes_tab.append(theme_id) 

                if keywords :
                    if is_eval == 2 :
                        parcourses = Parcours.objects.filter( Q(teacher__user_id=teacher_id)|Q(exercises__supportfile__title__icontains = keywords) |Q(teacher__user__first_name__icontains = keywords) |Q(teacher__user__last_name__icontains = keywords)  ,is_share = 1, is_sequence = 1, 
                                                        exercises__knowledge__theme__in = themes_tab,  teacher__user__school = teacher.user.school,  level_id = int(level_id),is_trash=0).order_by('teacher','ranking').distinct() 
                    else :
                        parcourses = Parcours.objects.filter( Q(teacher__user_id=teacher_id)|Q(exercises__supportfile__title__icontains = keywords) |Q(teacher__user__first_name__icontains = keywords) |Q(teacher__user__last_name__icontains = keywords)  ,is_share = 1, is_evaluation = is_eval, 
                                                        exercises__knowledge__theme__in = themes_tab,  teacher__user__school = teacher.user.school,  level_id = int(level_id),is_trash=0).order_by('teacher','ranking').distinct() 
                
                else :
                    if is_eval == 2 :
                        parcourses = Parcours.objects.filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id),is_share = 1, is_sequence = 1, 
                                                            exercises__knowledge__theme__in = themes_tab, level_id = int(level_id),is_trash=0).order_by('teacher','ranking').distinct()                           
                    else :
                        parcourses = Parcours.objects.filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id),is_share = 1, is_evaluation = is_eval, 
                                                            exercises__knowledge__theme__in = themes_tab, level_id = int(level_id),is_trash=0).order_by('teacher','ranking').distinct() 


                    
            else :
                if keywords :
                    if is_eval == 2 :
                        parcourses = Parcours.objects.filter(Q(teacher__user_id=teacher_id)|Q(teacher__user__first_name__icontains= keywords) |Q(teacher__user__last_name__icontains = keywords)   |Q(exercises__supportfile__title__icontains = keywords),is_share = 1, is_sequence = 1, 
                                                            teacher__user__school = teacher.user.school ,  level_id = int(level_id) ,is_trash=0).exclude(teacher=teacher).order_by('teacher','ranking').distinct() 
                    else :
                        parcourses = Parcours.objects.filter(Q(teacher__user_id=teacher_id)|Q(teacher__user__first_name__icontains= keywords) |Q(teacher__user__last_name__icontains = keywords)   |Q(exercises__supportfile__title__icontains = keywords),is_share = 1, is_evaluation = is_eval,
                                                            teacher__user__school = teacher.user.school ,  level_id = int(level_id) ,is_trash=0).exclude(teacher=teacher).order_by('teacher','ranking').distinct() 
                else :
                    if is_eval == 2 :
                        parcourses = Parcours.objects.filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id),is_share = 1, is_sequence = 1, level_id = int(level_id),is_trash=0).order_by('teacher','ranking').distinct()                             
                    else :
                        parcourses = Parcours.objects.filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id),is_share = 1, is_evaluation = is_eval, level_id = int(level_id),is_trash=0).order_by('teacher','ranking').distinct()   
        else :

            if keywords :
                if is_eval == 2 :
                    parcourses = Parcours.objects.filter( Q(teacher__user_id=teacher_id)|Q(teacher__user__first_name__icontains = keywords) |Q(teacher__user__last_name__icontains = keywords)  |Q(exercises__supportfile__title__icontains = keywords),teacher__user__school = teacher.user.school,is_share = 1,is_sequence = 1,
                                                        level_id = int(level_id) ,is_trash=0).order_by('teacher','ranking').distinct() 
                else :
                    parcourses = Parcours.objects.filter( Q(teacher__user_id=teacher_id)|Q(teacher__user__first_name__icontains = keywords) |Q(teacher__user__last_name__icontains = keywords)  |Q(exercises__supportfile__title__icontains = keywords),teacher__user__school = teacher.user.school,is_share = 1,is_evaluation = is_eval,
                                                        level_id = int(level_id) ,is_trash=0).order_by('teacher','ranking').distinct() 
            else :
                if is_eval == 2 :
                    parcourses = Parcours.objects.filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id),is_share = 1, is_sequence = 1, 
                                                        level_id = int(level_id),is_trash=0).order_by('teacher','ranking').distinct()                             
                else :
                    parcourses = Parcours.objects.filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id),is_share = 1, is_evaluation = is_eval, 
                                                            level_id = int(level_id),is_trash=0).order_by('teacher','ranking').distinct()   



    else :
        if keywords:
            if is_eval == 2 :
                parcourses = Parcours.objects.filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id)|Q(teacher__user__first_name__icontains = keywords) |Q(teacher__user__last_name__icontains = keywords) |Q(exercises__supportfile__title__icontains = keywords) ,is_share = 1 , is_sequence = 1 ,is_trash=0).order_by('author','ranking').distinct()
            else :
                parcourses = Parcours.objects.filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id)|Q(teacher__user__first_name__icontains = keywords) |Q(teacher__user__last_name__icontains = keywords)|Q(exercises__supportfile__title__icontains = keywords)  ,is_share = 1 , is_evaluation = is_eval,is_trash=0).order_by('author','ranking').distinct()
        else :
            if is_eval == 2 :
                parcourses = Parcours.objects.filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id),is_share = 1,  is_sequence =1,is_trash=0).order_by('teacher').distinct()

            else :
                parcourses = Parcours.objects.filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id),is_share = 1,  is_evaluation = is_eval,is_trash=0).order_by('teacher').distinct()



    listing = request.POST.get('listing',None)


    if listing == "yes" :
        data['html'] = render_to_string('qcm/ajax_list_parcours_listing.html', {'parcourses' : parcourses, 'teacher' : teacher ,  }) 
    else :
        data['html'] = render_to_string('qcm/ajax_list_parcours.html', {'parcourses' : parcourses, 'teacher' : teacher ,  })
 


    return JsonResponse(data)


@login_required(login_url= 'index')
def all_folders(request):
    teacher = request.user.teacher
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
        else :
            group = None   
    except :
        group = None


    if request.user.school != None :
        inside = True
    else :
        inside = False

    return render(request, 'qcm/list_folders_shared.html', {  'teacher' : teacher ,   'parcourses': parcourses , 'inside' : inside ,  'group' : group   })



@login_required(login_url= 'index')
def ajax_all_folders(request):

    teacher = request.user.teacher
    data = {}
    level_id = request.POST.get('level_id',0)
    subject_id = request.POST.get('subject_id',None)
    listing = request.POST.get('listing',None)

    teacher_id = get_teacher_id_by_subject_id(subject_id)

    # if request.user.is_superuser :
    #     folders = Folder.objects.values_list("id",flat=True).distinct().filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id),is_share = 1).order_by('level')
    # else :
    #     folders = Folder.objects.values_list("id",flat=True).distinct().filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id),is_share = 1).exclude(teacher=teacher).order_by('level')

    keywords = request.POST.get('keywords',None)

    if int(level_id) > 0 :
        level = Level.objects.get(pk=int(level_id))

        if keywords:
            parcours_key = Parcours.objects.filter(Q(exercises__supportfile__title__icontains = keywords)|Q(exercises__supportfile__annoncement__icontains = keywords)|Q(teacher__user__first_name__icontains = keywords) |Q(teacher__user__last_name__icontains = keywords) )
            folders = Folder.objects.filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id),is_share = 1, parcours__in=parcours_key ,
                                             level  =  level   ).exclude(teacher=teacher).order_by('teacher','ranking').distinct()
        else :
            folders = Folder.objects.filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id),is_share = 1,  
                                                        level  =  level  ).exclude(teacher=teacher).order_by('teacher','ranking').distinct()
    else :
        if keywords:
            parcours_key = Parcours.objects.filter(Q(exercises__supportfile__title__icontains = keywords)|Q(exercises__supportfile__annoncement__icontains = keywords)|Q(teacher__user__first_name__icontains = keywords) |Q(teacher__user__last_name__icontains = keywords)   )
            folders = Folder.objects.filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id),is_share = 1, parcours__in=parcours_key ).exclude(teacher=teacher).order_by('teacher','ranking').distinct()
        else :
            folders = Folder.objects.filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id),is_share = 1 ).exclude(teacher=teacher).order_by('teacher','ranking').distinct()

    if listing == "yes" :
        data['html'] = render_to_string('qcm/ajax_list_folders_listing.html', {'folders' : folders, 'teacher' : teacher ,  }) 
    else :
        data['html'] = render_to_string('qcm/ajax_list_folders.html', {'folders' : folders, 'teacher' : teacher ,  })
 
    return JsonResponse(data)


@login_required(login_url= 'index')
def clone_folder(request, id ):
    """ cloner un dossier """
    folder = Folder.objects.get(pk = id)
    prcs   = folder.parcours.all()
 
    #################################################
    # clone le parcours
    #################################################
    folder.pk = None
    folder.teacher = request.user.teacher
    folder.is_publish = 0
    folder.is_archive = 0
    folder.is_share = 1
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
    for p in prcs :
        folder_id_tab.append(p.id) # liste des parcours du dossiers
        p.pk = None
        p.code = str(uuid.uuid4())[:8] 
        p.teacher = request.user.teacher
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

    i = 0
    for pid in folder_id_tab : # liste des parcours du dossiers
        pc = Parcours.objects.get(pk = pid)
        for course in pc.course.all() :
            old_relationships = course.relationships.all()
            # clone le cours associé au parcours
            course.pk = None
            course.parcours_id = new_folder_id_tab[i]
            course.save()
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
        for relationship in pc.parcours_relationship.all()  :
            try :
                relationship.pk = None
                relationship.parcours_id = new_folder_id_tab[i]
                relationship.save()    
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


@csrf_exempt
def ajax_chargethemes_parcours(request):
    level_id =  request.POST.get("id_level")
    id_subject =  request.POST.get("id_subject")
    teacher = request.user.teacher

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
    teacher = request.user.teacher

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
 
 
@login_required(login_url= 'index')
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



@login_required(login_url= 'index')
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
    teacher         = request.user.teacher
    levels          = teacher.levels.all()
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

        if request.POST.get("save_and_choose") :
            return redirect('peuplate_parcours', nf.id)
        elif group_id and idf == 0 :
            return redirect('list_parcours_group' , group_id)                
        elif group_id and idf > 0 :
                return redirect('list_sub_parcours_group' , group_id, idf ) 
        else:
            return redirect('parcours')
    else:
        print(form.errors)
 
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

    
#######################################################################################################################
###################  Modification
#######################################################################################################################

def update_parcours_or_evaluation(request, is_eval, id, is_sequence, idg=0 ): 
    """ 'parcours_is_folder' : False pour les vignettes et différencier si folder ou pas """
    teacher = Teacher.objects.get(user_id=request.user.id)
    levels = teacher.levels.all()
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
        messages.error(request, "  !!!  Redirection automatique  !!! Violation d'accès.")
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


            if request.POST.get("save_and_choose") :
                return redirect('peuplate_parcours', nf.id)
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
    teacher = request.user.teacher 

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
    teacher = request.user.teacher

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
    parcours.students.clear()

    teacher = request.user.teacher

    if not authorizing_access(teacher, parcours, False ):
        messages.error(request, "  !!!  Redirection automatique  !!! Violation d'accès.")
        return redirect('index')

 
    for r in parcours.parcours_relationship.all() :
        r.students.clear()
        r.skills.clear()
        ls = r.relationship_exerciselocker.all()
        for l in ls :
            l.delete()
        r.delete()

    for c in parcours.course.all() :
        c.students.clear()
        c.creators.clear()
        c.delete()

    studentanswers = Studentanswer.objects.filter(parcours = parcours)
    for s in studentanswers :
        s.delete()
 
    parcours.delete()

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
    relationships = Relationship.objects.filter(parcours=parcours).prefetch_related('exercise__supportfile').order_by("ranking")
    customexercises = Customexercise.objects.filter(parcourses=parcours).order_by("ranking") 
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
    if idf > 0 :
        folder = Folder.objects.get(id=idf)
    else :
        folder = None

    parcours = Parcours.objects.get(id=id)
    rq_user = request.user
    teacher = rq_user.teacher

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




def open_section_to_read(student, parcours, listing_order):
 
    list_bool , blocs = [] ,  [] 

    try :

        if student.adhesions.last().formule_id > 1 and parcours.is_sequence :
            # calcul des indices exercices des blocs dans la liste listing_order des document
            # le premier element du bloc est l'indice du titre du bloc
            blocs=[]
            for i,doc in enumerate(listing_order) :
                if doc.type_id==0 and doc.exercise.supportfile.is_title and not(doc.exercise.supportfile.is_subtitle):
                        blocs.append([i])
                else :
                    if doc.type_id==0 and not(doc.exercise.supportfile.is_title):
                        blocs[-1].append(i)
                    

            #---------- calcul du premier bloc qui n'a jamais ete traitÃ© par l'Ã©lÃ¨ve,
            # et tel que le bloc prÃ©cÃ©dent n'ait pas ete traitÃ© ou ait ete mal rÃ©ussi
            reussi=[]
            for i in range(len(blocs)):
                avg_student = student.answers.filter(exercise__in = [listing_order[j].exercise.id for j in blocs[i][1:]] , parcours = parcours).aggregate(average=Avg("point"))
                traite = avg_student['average']!=None
                reussi.append(traite and avg_student['average']>80) 
                if i!=0 and not(traite) and not(reussi[i-1]) :
                    break
            # i-1 : numero du dernier bloc Ã  afficher
            # constitution du dictionnaire pour chaque element de listing_order,
            # on calcule un dictionnaire contenant son id et un boolÃ©en pour l'affichage
            if i-1<len(blocs) : #il existe un bloc Ã  ne pas afficher
                limite=blocs[i][0]
            else :
                limite=len(listing_order)
            for i in range(len(listing_order)):
                list_bool.append({"doc":listing_order[i],"is_display":i<limite})

        else : 
            for i in range(len(listing_order)):
                list_bool.append({"doc":listing_order[i],"is_display":True})
    except :
        for i in range(len(listing_order)):
            list_bool.append({"doc":listing_order[i],"is_display":True})

    return list_bool




def ordering_number_for_student(parcours,student):
    """ créer une seule liste des exercices personnalisés et des exercices sacado coté eleve """

    listing_ordered = set()

    if parcours.is_sequence : 
        listing_order = student.students_relationship.filter(parcours=parcours, is_publish=1).order_by("ranking")
    else :
        relationships = student.students_relationship.filter(parcours=parcours, is_publish=1).prefetch_related('exercise__supportfile').order_by("ranking")
        customexercises = Customexercise.objects.filter(parcourses=parcours, students=student, is_publish=1).order_by("ranking")
        listing_ordered.update(relationships)
        listing_ordered.update(customexercises)
        listing_order = sorted(listing_ordered, key=attrgetter('ranking')) #set trié par ranking
    

    list_order = open_section_to_read(student, parcours, listing_order)

    nb_exo_only, nb_exo_visible  = [] , []   
    i , j = 0, 0

    for item in list_order :
        try :
            if not item["doc"].exercise.supportfile.is_title and not item["doc"].exercise.supportfile.is_subtitle:
                i += 1
            nb_exo_only.append(i)
            if not item["doc"].exercise.supportfile.is_title and not item["doc"].exercise.supportfile.is_subtitle and item["doc"].is_publish != 0:
                j += 1
            nb_exo_visible.append(j)
        except :
            i += 1
            nb_exo_only.append(i)
            if item["doc"].is_publish :
                j += 1
            nb_exo_visible.append(j)

    return list_order , nb_exo_only, nb_exo_visible


@login_required(login_url= 'index')
def show_parcours_student(request, id):

    if request.user.is_authenticated :
        folder = None
        folder_id = request.session.get('folder_id', None)
        if folder_id :
            folder = Folder.objects.get(id=folder_id)

        parcours = Parcours.objects.get(id=id)

        if parcours.stop :
            lock_all_exercises_for_this_student(parcours,request.user.student)

        user = request.user
        student = user.student
        today = time_zone_user(user)
        stage = get_stage(user)

        tracker_execute_exercise(True ,  user , id , None , 0)

        relationships_customexercises , nb_exo_only, nb_exo_visible  = ordering_number_for_student(parcours,student)
        nb_exercises = len(relationships_customexercises)

        nb_courses = parcours.course.filter(Q(is_publish=1)|Q(publish_start__lte=today,publish_end__gte=today)).count()
        nb_quizzes = parcours.quizz.filter(Q(is_publish=1)|Q(start__lte=today,stop__gte=today)).count()




        context = { 'stage' : stage , 'relationships_customexercises': relationships_customexercises, 'folder': folder, 'nb_courses' : nb_courses , 
                    'parcours': parcours, 'student': student, 'nb_exercises': nb_exercises,'nb_exo_only': nb_exo_only,  'nb_quizzes' : nb_quizzes ,
                    'today': today ,    }

        return render(request, 'qcm/show_parcours_student.html', context)
    else :
        return redirect('index') 



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
    teacher = request.user.teacher 

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


    teacher = request.user.teacher
 
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


@login_required(login_url= 'index')
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



@login_required(login_url= 'index')
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
 

@login_required(login_url= 'index')
@parcours_exists
def result_parcours_waiting(request, id, is_folder):

    teacher = request.user.teacher
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

    studentanswer_ids =  Studentanswer.objects.values_list("id",flat=True).distinct().filter(student=s,  exercise__in = exercises , parcours=parcours).order_by("-date")
  
    #nb_exo_w = s.student_written_answer.filter(relationship__exercise__in = studentanswer_tab, relationship__parcours = parcours, relationship__is_publish = 1 ).count()
    nb_exo_ce = s.student_custom_answer.filter(parcours = parcours, customexercise__is_publish = 1 ).count()
    #nb_exo  = len(studentanswer_tab) + nb_exo_w + nb_exo_ce
    nb_exo  = studentanswer_ids.count()  +  nb_exo_ce
    student["nb_exo"] = nb_exo
    duration, score, total_numexo, good_answer = 0, 0, 0, 0
    tab, tab_date  , tab_title_exo , student_tab  = [], [], [] , []
    student["legal_duration"] = parcours.duration
    total_nb_exo = len(relationships)
    student["total_nb_exo"] = total_nb_exo       

    for studentanswer_id in  studentanswer_ids : 
        studentanswer = Studentanswer.objects.get(pk=studentanswer_id)
        duration += int(studentanswer.secondes)
        score += int(studentanswer.point)
        total_numexo += int(studentanswer.numexo)
        good_answer += int(studentanswer.numexo*studentanswer.point/100)
        tab.append(studentanswer.point)
        tab_date.append(studentanswer.date)
        tab_title_exo.append(studentanswer.exercise.supportfile.title)
        student_tab.append(studentanswer)

    try :
        student["tab_title_exo"] = tab_title_exo        
        student["good_answer"] = int(good_answer)
        student["total_numexo"] = int(total_numexo)
        student["last_connexion"] = studentanswer.date
        student["score"] = int(score)
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
            average_score = int(score/len(student_tab))
            student["average_score"] = int(average_score)
            tab.sort()
            if len(tab)%2 == 0 :
                med = (tab[len(tab)//2-1]+tab[(len(tab))//2])/2 ### len(tab)-1 , ce -1 est causé par le rang 0 du tableau
            else:
                med = tab[(len(tab)-1)//2]
            student["median"] = int(med)
  
        else :
            average_score = int(score)
            student["average_score"] = int(score)
            student["median"] = int(score)     
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


@login_required(login_url= 'index')
@parcours_exists
def stat_evaluation(request, id):

    teacher = request.user.teacher
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
        messages.error(request, "  !!!  Redirection automatique  !!! Violation d'accès.")
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

            relation = Relationship.objects.create(parcours = parcours , exercise = exercise , ranking=  r, is_publish= 1 , start= None , date_limit= None, duration= exercise.supportfile.duration, situation= exercise.supportfile.situation ) 
            relation.skills.set(exercise.supportfile.skills.all())   
            i +=1

    return redirect('exercises')

@login_required(login_url= 'index')
@parcours_exists
def clone_parcours(request, id, course_on ):
    """ cloner un parcours """

    teacher = request.user.teacher
    parcours = Parcours.objects.get(pk=id) # parcours à cloner
    relationships = parcours.parcours_relationship.all() 
    courses = parcours.course.filter(is_share = 1)
    # clone le parcours
    parcours.pk = None
    parcours.title = parcours.title+"-2"
    parcours.teacher = teacher
    parcours.is_publish = 0
    parcours.is_archive = 0
    parcours.is_share = 1
    parcours.is_favorite = 1
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
        try :
            relationship.pk = None
            relationship.parcours = parcours
            relationship.save()  
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




@login_required(login_url= 'index')
@parcours_exists
def clone_sequence(request, id ):
    """ cloner un parcours """

    teacher = request.user.teacher
    parcours = Parcours.objects.get(pk=id) # parcours à cloner
    relationships = parcours.parcours_relationship.all() 
    courses = parcours.course.filter(is_share = 1)
    # clone le parcours
    parcours.pk = None
    parcours.title = parcours.title+"-2"
    parcours.teacher = teacher
    parcours.is_publish = 1
    parcours.is_archive = 0
    parcours.is_share = 0
    parcours.is_favorite = 1
    parcours.is_sequence = 1
    parcours.code = str(uuid.uuid4())[:8]  
    parcours.save()

    # ajoute le group au parcours si group   
    try :
        group_id = request.session.get("group_id",None)
        if group_id :
            group = Group.objects.get(pk = group_id)
            students = group.students.all()
            parcours.groups.add(group)
            Parcours.objects.filter(pk = parcours.id).update(subject = group.subject)
            Parcours.objects.filter(pk = parcours.id).update(level = group.level)
            parcours.students.set(students)
            messages.success(request, "Duplication réalisée avec succès. Bonne utilisation. Vous pouvez placer le parcours dans le dossier en cliquant sur la config. du parcours")
        else :
            messages.error(request,"Non affecté au groupe et placé dans le tableau de bord pour réaffectation manuelle")
            group = None   
    except :
        messages.error(request,"Non affecté au groupe et placé dans le tableau de bord pour réaffectation manuelle")
        group = None

    # ajoute le group au parcours si group    
    try :
        folder_id = request.session.get("folder_id",None)
        if folder_id :
            folder = Folder.objects.get(pk = folder_id)
            parcours.folders.add(folder)
        else :
            messages.error(request,"Non affecté au dossier et placé dans le tableau de bord pour réaffectation manuelle")
            folder = None   
    except :
        messages.error(request,"Non affecté au dossier et placé dans le tableau de bord pour réaffectation manuelle")
        folder = None


    for relationship in relationships :
        try :
            relationship.pk = None
            relationship.parcours = parcours
            relationship.save()
        except : pass
        try    : relationship.students.set(students)
        except : pass  

    if folder_id :
        return redirect('list_sub_parcours_group', 0 , folder_id)
    if group_id :
        return redirect('list_parcours_group', group_id)
    else :
        return redirect('all_parcourses' , 2 )   


@login_required(login_url= 'index')
def ajax_parcours_get_exercise_custom(request):

    teacher = request.user.teacher 
    exercise_id =  int(request.POST.get("exercise_id"))
    customexercise = Customexercise.objects.get(pk=exercise_id)
    parcourses =  teacher.teacher_parcours.all()    

    context = {  'customexercise': customexercise , 'parcourses': parcourses , 'teacher' : teacher  }
    data = {}
    data['html'] = render_to_string('qcm/ajax_parcours_get_exercise_custom.html', context)
 
    return JsonResponse(data)
 

@login_required(login_url= 'index') 
def parcours_clone_exercise_custom(request):

    teacher = request.user.teacher
    exercise_id =  int(request.POST.get("exercise_id"))
    customexercise = Customexercise.objects.get(pk=exercise_id)

    checkbox_value = request.POST.get("checkbox_value")
    customexercise.pk = None
    customexercise.teacher = teacher
    customexercise.code = str(uuid.uuid4())[:8]  
    customexercise.save()

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

@login_required(login_url= 'index')
def exercise_custom_show_shared(request):
    
    user = request.user
    if user.is_teacher:  # teacher
        teacher = Teacher.objects.get(user=user) 
        customexercises = Customexercise.objects.filter(is_share = 1).exclude(teacher = teacher)
        return render(request, 'qcm/list_custom_exercises.html', {  'teacher': teacher , 'customexercises':customexercises, 'parcours': None, 'relationships' : [] ,  'communications': [] , })
    else :
        return redirect('index')   
 
@login_required(login_url= 'index')
def customexercise_shared_inside_parcours(request,idp):
    parcours = Parcours.objects.get(pk=idp)
    user = request.user
    if user.is_teacher:  # teacher
        teacher = Teacher.objects.get(user=user) 
        customexercises = Customexercise.objects.filter(is_share = 1).exclude(parcourses = parcours)
        return render(request, 'qcm/list_custom_exercises.html', {  'teacher': teacher , 'customexercises':customexercises, 'parcours': parcours,   })
    else :
        return redirect('index')   
 
 
@login_required(login_url= 'index')
def ajax_getter_parcours_exercice_custom(request):

    teacher        = request.user.teacher 
    exercise_id    = int(request.POST.get("exercise_id"))
    customexercise = Customexercise.objects.get(pk=exercise_id)
    parcours_id    = int(request.POST.get("parcours_id"))
    parcours       = Parcours.objects.get(pk=parcours_id)

    data = {}
    customexercise.parcourses.add(parcours)
 
    return JsonResponse(data)
 



@login_required(login_url= 'index')
def  exercise_error(request):

    message     = request.POST.get("message")  
    exercise_id = request.POST.get("exercise_id")
    parcours_id = request.POST.get("parcours_id",None)
    exercise = Exercise.objects.get(id = int(exercise_id))
    if request.user :
        usr = request.user
        email = " "
        if usr.email :
            email = usr.email
        msg = "Message envoyé par l'utilisateur #"+str(usr.id)+", "+usr.last_name+", "+email+" :\n\nL'exercice dont l'id est -- "+str(exercise_id)+" --  décrit ci-dessous : \n Savoir faire visé : "+exercise.knowledge.name+ " \n Niveau : "+exercise.level.name+  "  \n Thème : "+exercise.theme.name +" comporte un problème. \n  S'il est identifié par l'utilisateur, voici la description :  \n" + message   
        response = "\n\n Pour répondre, utiliser ces liens en remplaçant le - par un slash :  sacado-academie.fr-account-response_from_mail-"+str(usr.id)+"\n\n Pour voir l'exercice en question, utiliser ce lien en remplaçant le - par un slash :   sacado-academie.fr-qcm-show_this_exercise-"+str(exercise_id)+"-"

    else :
        usr = "non connecté"
        msg = "Message envoyé par l'utilisateur #Non connecté :\n\nL'exercice dont l'id est -- "+str(exercise_id)+" --  décrit ci-dessous : \n Savoir faire visé : "+exercise.knowledge.name+ " \n Niveau : "+exercise.level.name+  "  \n Thème : "+exercise.theme.name +" comporte un problème. \n  S'il est identifié par l'utilisateur, voici la description :  \n" + message   
        response = "\n\n Pour voir l'exercice en question, utiliser ce lien en remplaçant le - par un slash :   sacado-academie.fr-qcm-show_this_exercise-"+str(exercise_id)+"-"

    sending_mail("Avertissement SacAdo Exercice "+str(exercise_id),  msg + response , settings.DEFAULT_FROM_EMAIL , ["sacado.asso@gmail.com"])
 
    if request.user.is_teacher :
        
        return redirect( 'show_this_exercise', exercise_id) 
    else :
        return redirect( 'show_parcours_student', parcours_id) 



@login_required(login_url= 'index')
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




@login_required(login_url= 'index')
@parcours_exists
def result_parcours_exercise_students(request,id):
    teacher = request.user.teacher
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
        exercise_ids = request.POST.get("valeurs")
        exercise_tab = exercise_ids.split("-") 

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

    is_folder = request.POST.get("is_folder")
    if is_folder == "no" :
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
                    msg = "Pour le "+str(date)+": \n Un exercice vous est assigné. Rejoindre sacado-academie.fr. \n. Si vous ne souhaitez plus recevoir les notifications, désactiver la notification dans votre compte."
                    data["dateur"] = date 
                    students = r.students.all()
                    rec = []
                else :
                    Customexercise.objects.filter(pk = int(relationship_id)).update(date_limit = date)
                    ce = Customexercise.objects.get(pk = int(relationship_id))
                    data["class"] = "btn-success"
                    data["noclass"] = "btn-default"
                    msg = "Pour le "+str(date)+": \n Un exercice vous est assigné. Rejoindre sacado-academie.fr. Si vous ne souhaitez plus recevoir les notifications, désactiver la notification dans votre compte."
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
                    msg = "L'exercice https://sacado-academie.fr/qcm/show_this_exercise/"+str(r.exercise.id)+" : "+str(r.exercise)+" n'est plus une tâche \n. Si vous ne souhaitez plus recevoir les notifications, désactiver la notification dans votre compte."
                    date = "Tâche ?"  
                    data["dateur"] = date 
                    students = r.students.all()
                else :
                    Customexercise.objects.filter(pk = int(relationship_id)).update(date_limit = None)
                    ce = Customexercise.objects.get(pk = int(relationship_id))
                    data["class"] = "btn-success"
                    data["noclass"] = "btn-default"
                    msg = "L'exercice https://sacado-academie.fr/qcm/show_this_exercise/"+str(ce.id)+" : n'est plus une tâche \n Si vous ne souhaitez plus recevoir les notifications, désactiver la notification dans votre compte."
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
                msg = "Pour le "+str(date)+": \n Faire l'exercice : https://sacado-academie.fr/qcm/show_this_exercise/"+str(r.exercise.id)+" : " +str(r.exercise)+" \n. Si vous ne souhaitez plus recevoir les notifications, désactiver la notification dans votre compte. Ceci est un mail automatique. Ne pas répondre."
                students = r.students.all()
            else :
                Customexercise.objects.filter(pk = int(relationship_id)).update(start = date)
                Customexercise.objects.filter(pk = int(relationship_id)).update(date_limit = None)
                ce = Customexercise.objects.get(pk = int(relationship_id))
                msg = "Pour le "+str(date)+": \n Faire l'exercice : https://sacado-academie.fr/qcm/show_this_exercise/"+str(ce.id)+"\n Si vous ne souhaitez plus recevoir les notifications, désactiver la notification dans votre compte. Ceci est un mail automatique. Ne pas répondre."
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

                if rel.exercise.supportfile.is_ggbfile :
                    Relationship.objects.filter(pk = int(relationship_id)).update(situation = situation)
                    data["save"] = "<i class='fa fa-save'></i> "+str(situation)
                    data["situation"] = "<i class='fa fa-save'></i> "+str(situation)
                    data["annonce"] = ""
                    data["annoncement"]   = False

                else :
                    Relationship.objects.filter(pk = int(relationship_id)).update(instruction = situation)  
                    data["save"] = False
                    data["duration"] = ""
                    data["annonce"] = situation
                    data["annoncement"]   = True
            except : 
                pass

        except :
            try :
                situation =  request.POST.get("situation") 
                rel = Relationship.objects.get(pk = int(relationship_id))
                if rel.exercise.supportfile.is_ggbfile :
                    Relationship.objects.filter(pk = int(relationship_id)).update(situation = situation)
                    data["save"] = "<i class='fa fa-save'></i> "+str(situation) 
                    data["annonce"] = "" 
                    data["annoncement"]   = False                                 
                else :
                    Relationship.objects.filter(pk = int(relationship_id)).update(instruction = situation)   
                    data["save"] = False
                    data["annonce"] = situation
                    data["annoncement"]   = True
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

@login_required(login_url= 'index')
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



@login_required(login_url= 'index')
def delete_relationship(request,idr):

    relation = Relationship.objects.get(pk = idr)
    link =  relation.parcours.id
    if relation.parcours.teacher.user == request.user  :
        relation.delete()

    return redirect("show_parcours" , 0 , link ) 


@login_required(login_url= 'index')    
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


@login_required(login_url= 'index')
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
 


@login_required(login_url= 'index')
def real_time(request,id):
    """ module de real time"""
    parcours = Parcours.objects.get(pk = id)
    teacher = request.user.teacher
    today = time_zone_user(request.user).now()

    role, group , group_id , access = get_complement(request, teacher, parcours)
    connected_student_ids =  Tracker.objects.values_list("user_id",flat = True).filter(parcours = parcours ).distinct()

    if not teacher_has_permisson_to_parcourses(request,teacher,parcours) :
        return redirect('index')

    students = parcours.students.order_by("user__last_name").exclude(user__username__contains="_e-test")
    rcs      = rcs_for_realtime(parcours)

    return render(request, 'qcm/real_time.html', { 'teacher': teacher , 'parcours': parcours, 'rcs': rcs, 'students': students , 'group': group , 'role': role , 'access': access })



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



@login_required(login_url= 'index')
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
        levels = teacher.levels.all()
    elif status == 1 : 
        levels = Level.objects.all().order_by("id")

    for level in levels :
        levels_dict = {}
        levels_dict["name"]=level 

        datas.append(levels_dict)
    return datas


@login_required(login_url= 'index')
def list_exercises(request):
    
    user = request.user
    if user.is_authenticated :
        if user.is_teacher:  # teacher
            teacher = Teacher.objects.get(user=user)
            datas = all_levels(user, 0)
            request.session["tdb"] = False # permet l'activation du surlignage de l'icone dans le menu gauche
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


@login_required(login_url= 'index')
def ajax_list_exercises_by_level(request):
    """ Envoie la liste des exercice pour un seul niveau """
    teacher = request.user.teacher
    level_id =  int(request.POST.get("level_id"))  
 
    level = Level.objects.get(pk=level_id)
    exercises = Exercise.objects.filter(level_id = level_id , supportfile__is_title=0).order_by("theme","knowledge__waiting","knowledge","supportfile__ranking")
 
    data = {}
    data['html'] = render_to_string('qcm/ajax_list_exercises_by_level.html', { 'exercises': exercises  , "teacher" : teacher , "level_id" : level_id })
 
    return JsonResponse(data)




@login_required(login_url= 'index')
def ajax_list_exercises_by_level_and_theme(request):
    """ Envoie la liste des exercice pour un seul niveau """
    teacher = request.user.teacher
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

@login_required(login_url= 'index')
@parcours_exists
def parcours_exercises(request,id):
    user = request.user
    parcours = Parcours.objects.get(pk=id)
    student = Student.objects.get(user=user)

    relationships = Relationship.objects.filter(parcours=parcours,is_publish=1).order_by("exercise__theme")

    return render(request, 'qcm/student_list_exercises.html', {'parcours': parcours  , 'relationships': relationships, })

def exercises_level(request, id):

    level = Level.objects.get(pk=id)    
    exercises = Exercise.objects.filter(level=level,supportfile__is_title=0).order_by("theme","knowledge__waiting","knowledge","ranking")
    themes =  level.themes.all()
    form = AuthenticationForm() 
    u_form = UserForm()
    t_form = TeacherForm()
    s_form = StudentForm()
    return render(request, 'list_exercises.html', {'exercises': exercises, 'level':level , 'themes':themes , 'form':form , 'u_form':u_form , 's_form': s_form , 't_form': t_form , 'levels' : [] })


def exercises_level_subject(request, id, subject_id):
    exercises = Exercise.objects.filter(level_id=id,supportfile__is_title=0,theme__subject_id = subject_id).order_by("theme","knowledge__waiting","knowledge","ranking")
    level = Level.objects.get(pk=id)
    themes =  level.themes.all()
    form = AuthenticationForm() 
    u_form = UserForm()
    t_form = TeacherForm()
    s_form = StudentForm()
    return render(request, 'list_exercises.html', {'exercises': exercises, 'level':level , 'themes':themes , 'form':form , 'u_form':u_form , 's_form': s_form , 't_form': t_form , 'levels' : [] })



@user_passes_test(user_is_creator)
def create_supportfile(request):

    code = str(uuid.uuid4())[:8]
    teacher = request.user.teacher
    form = SupportfileForm(request.POST or None,request.FILES or None,teacher = teaher)
    is_ggbfile = request.POST.get("is_ggbfile")
    if request.user.is_superuser or request.user.is_extra :
        if form.is_valid():
            nf =  form.save(commit = False)
            nf.code = code
            nf.author = teacher
            if is_ggbfile :
                nf.annoncement = unescape_html(cleanhtml(nf.annoncement)) 
            try :   
                sending_to_teachers(teacher , nf.level,nf.theme.subject,"Un nouvel exercice")
            except:
                pass      
            nf.save()
            form.save_m2m()
            # le supprot GGB est placé comme exercice par défaut.
            Exercise.objects.create(supportfile = nf, knowledge = nf.knowledge, level = nf.level, theme = nf.theme )


            return redirect('admin_supportfiles' , nf.level.id )

    context = {'form': form,   'teacher': teacher, 'knowledge': None,  'knowledges': [], 'relationships': [],  'supportfiles': [],   'levels': [], 'parcours': None, 'supportfile': None, 'communications' : [] ,  }

    return render(request, 'qcm/form_supportfile.html', context)

@user_passes_test(user_is_creator)
def create_supportfile_knowledge(request,id):

    code = str(uuid.uuid4())[:8]
    knowledge = Knowledge.objects.get(id = id)
    teacher = request.user.teacher
    form = SupportfileKForm(request.POST or None,request.FILES or None, knowledge = knowledge )
    levels = Level.objects.all()
    supportfiles = Supportfile.objects.filter(is_title=0).order_by("level","theme","knowledge__waiting","knowledge","ranking")
    knowledges = Knowledge.objects.all().order_by("level")

    is_ggbfile = request.POST.get("is_ggbfile")

    if request.user.is_superuser or request.user.is_extra : 
        if form.is_valid():
            nf =  form.save(commit = False)
            nf.code = code
            nf.author = teacher
            nf.knowledge = knowledge
            if is_ggbfile :
                nf.annoncement = unescape_html(cleanhtml(nf.annoncement)) 
            try :
                sending_to_teachers(teacher , nf.level,nf.theme.subject,"Un nouvel exercice")   
            except :
                pass 
            nf.save()
            form.save_m2m()
            # le support GGB est placé comme exercice par défaut.
            Exercise.objects.create(supportfile = nf, knowledge = nf.knowledge, level = nf.level, theme = nf.theme )
            return redirect('admin_supportfiles' , nf.level.id )
        else :
            print(form.errors)


    context = {'form': form,   'teacher': teacher,  'knowledges': knowledges, 'relationships': [],  'knowledge': knowledge,  'supportfile': None,  'supportfiles': supportfiles,   'levels': levels , 'parcours': None, 'communications' : [] ,  }

    return render(request, 'qcm/form_supportfile.html', context)

@user_passes_test(user_is_creator)
def update_supportfile(request, id, redirection=0):

    teacher = request.user.teacher
    if request.user.is_superuser or request.user.is_extra :
        supportfile = Supportfile.objects.get(id=id)
        knowledge = supportfile.knowledge
        supportfile_form = UpdateSupportfileForm(request.POST or None, request.FILES or None, instance=supportfile, knowledge = knowledge)
        levels = Level.objects.all()
        supportfiles = Supportfile.objects.filter(is_title=0).order_by("level","theme","knowledge__waiting","knowledge","ranking")
        knowledges = Knowledge.objects.all().order_by("level")
        is_ggbfile = request.POST.get("is_ggbfile")
        if request.method == "POST":
            if supportfile_form.is_valid():
                nf = supportfile_form.save(commit=False)
                nf.code = supportfile.code
                if is_ggbfile :
                    nf.annoncement = unescape_html(cleanhtml(nf.annoncement)) 
                nf.save()
                supportfile_form.save_m2m()
                messages.success(request, "L'exercice a été modifié avec succès !")

                return redirect('admin_supportfiles', supportfile.level.id)

        context = {'form': supportfile_form, 'teacher': teacher, 'supportfile': supportfile, 'knowledges': knowledges, 'relationships': [] ,
                   'supportfiles': supportfiles, 'levels': levels, 'parcours': None, 'communications' : [] , 'knowledge' : knowledge ,   }

        return render(request, 'qcm/form_supportfile.html', context)



@user_passes_test(user_is_superuser)
def delete_supportfile(request, id):
    if request.user.is_superuser:
        supportfile = Supportfile.objects.get(id=id)
        if Relationship.objects.filter(exercise__supportfile=supportfile).count() == 0:
            supportfile.delete()
            messages.success(request, "Le support GGB a été supprimé avec succès !")
        else:
            messages.error(request, " Des parcours utilisent ce support GGB. Il n'est pas possible de le supprimer.")

    return redirect('admin_supportfiles', supportfile.level.id)


 
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




@csrf_exempt
def ajax_sort_supportfile(request):
    """ tri des supportfiles""" 


    exercise_ids = request.POST.get("valeurs")
    exercise_tab = exercise_ids.split("-") 
    for i in range(len(exercise_tab)-1):
        Supportfile.objects.filter( pk = exercise_tab[i]).update(ranking = i)



    data = {}
    return JsonResponse(data) 


 
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


@login_required(login_url= 'index')
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


@login_required(login_url= 'index')
def execute_exercise(request, idp,ide):

 
    parcours = Parcours.objects.get(id= idp)
    exercise = Exercise.objects.get(id= ide)
    if Relationship.objects.filter(parcours=parcours, exercise=exercise).count() == 0 :
        messages.error("Cet exercercice n'est plus disponible.")
        return redirect("index")

    relation = Relationship.objects.get(parcours=parcours, exercise=exercise)
    request.session['level_id'] = exercise.level.id
    start_time =  time.time()
    student = request.user.student
    today = time_zone_user(request.user)
    timer = today.time()
    try :
        tracker_execute_exercise(True, request.user , idp , ide , 0)
    except :
        pass

    context = {'exercise': exercise,  'start_time' : start_time,  'student' : student,  'parcours' : parcours,  'relation' : relation , 'timer' : timer ,'today' : today , 'communications' : [] , 'relationships' : [] }
    return render(request, 'qcm/show_relation.html', context)



@csrf_exempt    
def store_the_score_relation_ajax(request):

    p_id = request.POST.get("parcours_id",None)
    if p_id :
        parcours_id = int(p_id)
    else :        
        messages.error(request, "Score non enregistré. Le parcours n'est pas reconnu.")
        return redirect('index')

    try :
        time_begin = request.POST.get("start_time",None)

        if time_begin :
            this_time = request.POST.get("start_time").split(",")[0]
            end_time  =  str(time.time()).split(".")[0]
            timer =  int(end_time) - int(this_time)
        else : 
            timer = 0

        numexo = int(request.POST.get("numexo"))-1    
        relation_id = int(request.POST.get("relation_id"))
        relation = Relationship.objects.get(pk = relation_id)
        data = {}
     
        student = Student.objects.get(user=request.user)

        if request.method == 'POST':
            score = round(float(request.POST.get("score")),2)*100
            if score > 100 :
                score = 100
            ##########################################################
            ########################### Storage student answer
            ##########################################################
            # try :
            #     this_studentanswer, new_studentanswer =  Studentanswer.objects.get_or_create(exercise  = relation.exercise , parcours  = relation.parcours ,  student  = student, defaults = { "numexo" : numexo,  "point" : score, "secondes" : timer }   )
            #     if not new_studentanswer : 
            #         Studentanswer.objects.filter(pk = this_studentanswer.id).update( numexo   = numexo, point    = score , secondes = timer )
            # except :
            #     multi_studentanswer = Studentanswer.objects.filter(exercise  = relation.exercise , parcours  = relation.parcours ,  student  = student).last()
            #     multi_studentanswer.update( numexo   = numexo, point    = score , secondes = timer )
            multi_studentanswer = Studentanswer.objects.filter(exercise  = relation.exercise , parcours  = relation.parcours ,  student  = student)
            if multi_studentanswer.count() > 0 :
                this_studentanswer = multi_studentanswer.last()
                multi_studentanswer.filter(pk=this_studentanswer.id).update( numexo   = numexo, point    = score , secondes = timer )
            else :
                try :
                    this_studentanswer = Studentanswer.objects.create(exercise  = relation.exercise , parcours  = relation.parcours ,  student  = student, numexo= numexo,  point= score, secondes= timer    )
                except :
                    pass

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


def ajax_theme_exercice(request):
    level_id = request.POST.get('level_id', None)

    if level_id.isdigit():
        level = Level.objects.get(id=level_id)
        themes = level.themes.all()
        data = {'themes': serializers.serialize('json', themes)}
    else:
        data = {}

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

    if level_id and theme_ids[0] != "" : 
        exercises = Exercise.objects.filter(level_id = level_id , theme_id__in= theme_ids ,  supportfile__is_title=0).order_by("theme","knowledge__waiting","knowledge","ranking")
 
     
        data['html'] = render_to_string('qcm/ajax_list_exercises.html', { 'exercises': exercises , "parcours" : parcours, "ajax" : ajax, "teacher" : teacher , 'parcours_id' : parcours_id })
 
    return JsonResponse(data)



def ajax_knowledge_exercise(request):
    theme_id = request.POST.get('theme_id', None)
    level_id = request.POST.get('level_id', None)
    data = {}
 
    knowledges = Knowledge.objects.filter(theme_id=theme_id,level_id=level_id )
    data = {'knowledges': serializers.serialize('json', knowledges)}


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
        supportfile.knowledge_id = 1
        supportfile.author = teacher
        supportfile.code=code
        supportfile.level_id=1
        supportfile.theme_id=1
        supportfile.is_title=1
        supportfile.save()

        exe = Exercise.objects.create(knowledge_id=1, level_id=1, theme_id=1, supportfile=supportfile)
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
    knowledges = Knowledge.objects.filter(name__contains= code)

    if request.user.user_type == 0 :
        student = True
    else :
        student = False

    relationship = Relationship.objects.filter(Q(exercise__knowledge__in = knowledges)|Q(exercise__supportfile__annoncement__contains= code)|Q(exercise__supportfile__code__contains= code)).last()
    data = {}
    html = render_to_string('qcm/search_exercises.html',{ 'relationship' : relationship ,  'student' : student })
 
    data['html'] = html       

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
    teacher = request.user.teacher
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
    teacher = request.user.teacher

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


def create_accounting(request,tp):
 
    form     = AccountingForm(request.POST or None )
    form_abo = AbonnementForm(request.POST or None )
    formSet  = inlineformset_factory( Accounting , Detail , fields=('accounting','description','amount',) , extra=0)
    form_ds  = formSet(request.POST or None)
    today    = datetime.now()

    if request.method == "POST":
        if form.is_valid():
            nf = form.save(commit = False)
            nf.save()
            form_ds = formSet(request.POST or None, instance = nf)
            for form_d in form_ds :
                if form_d.is_valid():
                    form_d.save()


            if nf.is_abonnement :
                if form_abo.is_valid():

                    if nf.date_payment:
                        fa.active = 1
                    fa.save()



 
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


 
def parcours_update_custom_exercise(request,idcc,id): # Modification d'un exercice non autocorrigé dans un parcours

    custom = Customexercise.objects.get(pk=idcc)

    teacher = Teacher.objects.get(user= request.user)
    stage = get_stage(teacher.user)

    if id == 0 :

        if not authorizing_access(teacher, custom ,True):
            messages.error(request, "  !!!  Redirection automatique  !!! Violation d'accès.")
            return redirect('index')

        ceForm = CustomexerciseNPForm(request.POST or None, request.FILES or None , teacher = teacher ,  custom = custom, instance = custom ) 
        form_c = CriterionForm(request.POST or None, request.FILES or None , teacher = teacher , parcours = parcours)

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
            return redirect('exercises' )
     
        context = {  'teacher': teacher, 'stage' : stage ,  'communications' : [] , 'form' : ceForm , 'form_c':form_c , 'customexercise' : custom ,'parcours': None, }

    else :
 
        parcours = Parcours.objects.get(pk=id)
        if not teacher_has_permisson_to_parcourses(request,teacher,parcours) :
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

    print(customexercise_id , parcours_id , student_id , criterion_id , position)

    auto , created = Autoposition.objects.get_or_create( customexercise_id=customexercise_id, parcours_id=parcours_id,  student_id=student_id ,  criterion_id=criterion_id , defaults={  'position' : position }  )

    return JsonResponse(data)  




  
def parcours_delete_custom_exercise(request,idcc,id ): # Suppression d'un exercice non autocorrigé dans un parcours

    teacher = Teacher.objects.get(user=request.user)
    custom = Customexercise.objects.get(pk=idcc)

    folder_id = request.session.get("folder_id",0)


    if not authorizing_access(teacher, custom,True):
        messages.error(request, "  !!!  Redirection automatique  !!! Violation d'accès.")
        return redirect('index')

    if id == 0 :   
        custom.delete() 
        return redirect('exercises')
    else :
        parcours = Parcours.objects.get(pk=id)
        custom.parcourses.remove(parcours)
        custom.delete() 
        return redirect('show_parcours', folder_id , id )
 


def write_exercise(request,id): # Coté élève
 
    student = Student.objects.get(user = request.user)  
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
            w_f.answer = escape_chevron(wForm.cleaned_data['answer'])
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
        url = "basthon/index.html" 
    else :
        url = "qcm/form_writing.html" 

    return render(request, url , context)




def write_custom_exercise(request,id,idp): # Coté élève - exercice non autocorrigé
 
    if request.user.is_authenticated :
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
    else :
        return redirect("index")

 

 






#################################################################################################################
#################################################################################################################
################   Canvas
#################################################################################################################
#################################################################################################################
@login_required
def show_canvas(request):
    user = request.user
    context = { "user" :  user  }
 
    return render(request, 'qcm/show_canvas.html', context)



@login_required
def ajax_save_canvas(request):

    actions           = request.POST.get("actions",None)
    customexercise_id = request.POST.get("customexercise_id",0)
    parcours_id       = request.POST.get("parcours_id",0)
    student           = request.user.student  
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


 


def asking_parcours_sacado(request,pk):
    """demande de parcours par un élève"""
    group = Group.objects.get(pk = pk)

    teacher_id = get_teacher_id_by_subject_id(group.subject.id)

    teacher = Teacher.objects.get(pk=teacher_id)
    student = request.user.student

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
        url = "qcm/form_writing.html" 

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

    context = { 'customexercise' : customexercise, 'today' : today , 'student' : None, }

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


 
def detail_task(request,id,s):

    parcours = Parcours.objects.get(pk=id) 
    teacher = Teacher.objects.get(user= request.user)

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



def all_my_tasks(request):
    today = time_zone_user(request.user) 
    teacher = request.user.teacher 
    parcourses = Parcours.objects.filter(is_publish=  1,teacher=teacher ,is_trash=0)
    relationships = Relationship.objects.filter(Q(is_publish = 1)|Q(start__lte=today), parcours__teacher=teacher, date_limit__gte=today,exercise__supportfile__is_title=0).order_by("parcours") 
    context = {'relationships': relationships, 'parcourses': parcourses, 'parcours': None,  'communications' : [] , 'relationships' : [] , 'group_id' : None  , 'role' : False , }
    return render(request, 'qcm/all_tasks.html', context)



def these_all_my_tasks(request):
    today = time_zone_user(request.user) 
    teacher = request.user.teacher 
    parcourses = Parcours.objects.filter(is_publish=  1,teacher=teacher ,is_trash=0)
    relationships = Relationship.objects.filter(Q(is_publish = 1)|Q(start__lte=today), parcours__teacher=teacher, exercise__supportfile__is_title=0).exclude(date_limit=None).order_by("parcours") 
    context = {'relationships': relationships, 'parcourses': parcourses, 'parcours': None,  'communications' : [] ,  'relationships' : [] ,'group_id' : None  , 'role' : False , } 
    return render(request, 'qcm/all_tasks.html', context)



 

def group_tasks(request,id):


    group = Group.objects.get(pk = id)
    teacher = Teacher.objects.get(user= request.user)
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

    relationships = Relationship.objects.filter(Q(is_publish = 1)|Q(start__lte=today), parcours__in=parcourses_tab, date_limit__gte=today,exercise__supportfile__is_title=0).order_by("parcours") 
    context = { 'relationships': relationships , 'group' : group , 'parcours' : None , 'communications' : [] , 'relationships' : [] , 'group_id' : group.id , 'role' : role , }

    return render(request, 'qcm/group_task.html', context)


def group_tasks_all(request,id):

    group = Group.objects.get(pk = id)
    teacher = Teacher.objects.get(user= request.user)
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
    teacher = request.user.teacher
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

    cookie_rgpd_accepted = request.COOKIES.get('cookie_rgpd_accepted',None)
    cookie_rgpd_accepted =  cookie_rgpd_accepted  == "True" 

    print(cookie_rgpd_accepted)


    if parcours_id :
        parcours_id =  int(request.POST.get("parcours_id"))
        customexercise_id =  int(request.POST.get("customexercise_id"))
        customexercise = Customexercise.objects.get( id = customexercise_id)

        form = RemediationcustomForm(request.POST or None,request.FILES or None, teacher = customexercise.teacher)
        data = {}

        remediations = Remediationcustom.objects.filter(customexercise = customexercise)

        context = {'form': form,  'customexercise' : customexercise ,  'remediations' : remediations , 'relationship' : None , 'parcours_id' : parcours_id ,'cookie_rgpd_accepted' : cookie_rgpd_accepted  } 

    else :
        relationship_id =  int(request.POST.get("relationship_id"))
        relationship = Relationship.objects.get( id = relationship_id)

        form = RemediationForm(request.POST or None,request.FILES or None, teacher = relationship.parcours.teacher)
        data = {}

        remediations = Remediation.objects.filter(relationship = relationship)

        context = {'form': form,  'relationship' : relationship ,  'remediations' : remediations, 'customexercise' : None , 'parcours_id' : relationship.parcours.id ,'cookie_rgpd_accepted' : cookie_rgpd_accepted   } 
    
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

    if parcours.teacher == request.user.teacher :
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





def peuplate_custom_parcours(request,idp):

    teacher = request.user.teacher
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
            courses = Course.objects.filter( Q(title__icontains=keyword)|Q(annoncement__icontains=keyword) ,   teacher__user__school = request.user.school , subject_id=subject_id,level=level )
        else :
            courses = Course.objects.filter(teacher__user__school = request.user.school , subject_id=subject_id,level=level )
        context = { "courses" : courses }    
        data['html']    = render_to_string( 'qcm/course/ajax_course_peuplate_sequence.html' , context)
    else :
        if keyword :
            customs = Customexercise.objects.filter( instruction__icontains=keyword ,  teacher__user__school = request.user.school  )
        else :
            customs = Customexercise.objects.filter(teacher__user__school = request.user.school )
        
        context = { "customs" : customs }
        data['html']    = render_to_string( 'qcm/ajax_custom_peuplate_sequence.html' , context)

    return JsonResponse(data)  


 
def clone_course_sequence(request, idc):
    """ cloner un cours dans une sequence """

    teacher = request.user.teacher
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
 




def clone_custom_sequence(request, idc):
    """ cloner un parcours """

    teacher = request.user.teacher
    customexercise = Customexercise.objects.get(pk=idc) # parcours à cloner.pk = None
    customexercise.pk = None
    customexercise.teacher = teacher
    customexercise.code = str(uuid.uuid4())[:8]
    customexercise.save()

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
        logo = Image('https://sacado-academie.fr/static/img/sacadoA1.png')
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
        paragraph = Paragraph( str(s.user.last_name)+" "+str(s.user.first_name) , title )
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


    for student in parcours.students.order_by("user__last_name") :
        data_student = get_student_result_from_eval(student, parcours, exercises,relationships,skills, knowledges,parcours_duration) 
        
        if data_student["percent"] != "" :

            try :
                final_mark = float(data_student["score_total"]) * (float(note_totale) - float(note_sacado)) + float(data_student["percent"]) * float(note_sacado)/100

                coefficient = data_student["nb_exo"]  /  data_student["total_nb_exo"] 
                final_mark = math.ceil( coefficient *  final_mark)
            except :
                final_mark = "NE" 

        else :
            final_mark = "NE" 

        writer.writerow( (str(student.user.last_name).lower() , str(student.user.first_name).lower() , data_student["total_nb_exo"] , data_student["nb_exo"],  data_student["percent"] , data_student["ajust"] , final_mark ) )
    return response

def export_skills_after_evaluation(request):

    parcours_id = request.POST.get("parcours_id")  
    parcours = Parcours.objects.get(pk = parcours_id)  
    nb_skill = int(request.POST.get("nb_skill"))

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
 
    for student in parcours.students.order_by("user__last_name") :
        skill_level_tab = [str(student.user.last_name).capitalize(),str(student.user.first_name).capitalize()]

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

def export_note_custom(request,id,idp):

    customexercise = Customexercise.objects.get(pk=id)
    parcours = Parcours.objects.get(pk=idp)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename=Notes_exercice_{}_{}.csv'.format(customexercise.id,parcours.id)
    writer = csv.writer(response)
    fieldnames = ("Eleves", "Notes")
    writer.writerow(fieldnames)
    for student in parcours.students.order_by("user__last_name") :
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



#######################################################################################################################################################################
#######################################################################################################################################################################
##################    Course     
#######################################################################################################################################################################
#######################################################################################################################################################################


@login_required(login_url= 'index')
def list_courses(request):

    teacher = request.user.teacher
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

    teacher = request.user.teacher
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
 
    teacher =  request.user.teacher
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
    teacher =  request.user.teacher
    course  =  Course.objects.get(pk=idc)
    form    =  CourseNPForm(request.POST or None, instance = course , teacher = teacher , initial = {   'subject' : course.parcours.subject  , 'level' : course.parcours.level })
    if request.method == "POST" :
        if form.is_valid():
            nf =  form.save(commit = False)
            nf.teacher = teacher
            nf.author = teacher
            nf.save()
            return redirect('courses')
        else:
            print(form.errors)

    context = {  'form': form , 'teacher': teacher, 'course': course , 'parcours': course.parcours ,    }

    return render(request, 'qcm/course/form_np_course.html', context)




@login_required(login_url= 'index')
def only_update_course_from_sequence(request,idc=0,idf=0 , ids=0):
    """
    idc : course_id et id = parcours_id pour correspondre avec le decorateur
    """
    teacher =  request.user.teacher
    course  =  Course.objects.get(pk=idc)
    parcours  =  Parcours.objects.get(pk=ids)
    form    =  CourseNPForm(request.POST or None, instance = course , teacher = teacher , initial = {   'subject' : course.parcours.subject  , 'level' : course.parcours.level , 'parcours' : course.parcours })
    if request.method == "POST" :
        if form.is_valid():
            nf =  form.save(commit = False)
            nf.teacher = teacher
            nf.author = teacher
            nf.save()
            return redirect('show_parcours', idf , ids)
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
    teacher =  request.user.teacher


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
    teacher =  request.user.teacher
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
    teacher =  request.user.teacher
    relationships = Relationship.objects.filter(parcours = parcours,exercise__supportfile__is_title=0).order_by("ranking")
    if parcours.is_sequence :
        role, group , group_id , access = get_complement(request, teacher, parcours)
        
        if not teacher_has_permisson_to_parcourses(request,teacher,parcours) :
            return redirect('index')

        form = CustomexerciseForm(request.POST or None, request.FILES or None , teacher = teacher , parcours = parcours) 
        if request.method == "POST" :
            if form.is_valid():
                nf = ceForm.save(commit=False)
                nf.teacher = teacher
                if nf.is_scratch :
                    nf.is_image = True
                nf.save()
                ceForm.save_m2m()
                nf.parcourses.add(parcours)
                nf.students.set( parcours.students.all() )  

                relation = Relationship.objects.create(parcours = parcours , exercise_id = None , document_id = nf.id  , type_id = 1 , ranking =  200 , is_publish= 1 , start= None , date_limit= None, duration= 10, situation= 0 ) 
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


    return render(request, 'qcm/form_exercise_custom.html', context)







@login_required(login_url= 'index')
def update_course(request, idc, id  ):
    """
    idc : course_id et id = parcours_id pour correspondre avec le decorateur
    """
    parcours = Parcours.objects.get(pk =  id)
    teacher =  request.user.teacher
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
    try :
        teacher = Teacher.objects.get(user= request.user)
        course = Course.objects.get( id = idc )
        parcours  = Parcours.objects.get( id = id )
        if not teacher_has_permisson_to_parcourses(request,teacher,parcours) :
            return redirect('index')
        course.delete()

    except :
        teacher = Teacher.objects.get(user= request.user)
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

    teacher = request.user.teacher
    parcours = Parcours.objects.get(id=idp)

    role, group , group_id , access = get_complement(request, teacher, parcours)


    if not authorizing_access(teacher,parcours, access ):
        messages.error(request, "  !!!  Redirection automatique  !!! Violation d'accès.")
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
    teacher = request.user.teacher
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
    teacher = request.user.teacher

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


  
def get_this_course_for_this_parcours(request,typ,id_target,idp):
    """ Clone un parcours depuis la liste ver un parcours de provenance """

    teacher = request.user.teacher
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
 
    teacher = request.user.teacher

    context = {  'teacher': teacher ,    }
    return render(request, 'qcm/course/list_courses.html', context )



@login_required(login_url= 'index')
def get_course_in_this_parcours(request,id):
    parcours = Parcours.objects.get(pk = id) 
    user = request.user

    teacher_id = get_teacher_id_by_subject_id(parcours.subject.id) 

    if user.is_teacher:  # teacher
    
        teacher = request.user.teacher
        role, group , group_id , access = get_complement(request, teacher, parcours)
        request.session["parcours_id"] = parcours.id
        request.session["group_id"] = group_id

        courses = Course.objects.filter( Q(parcours__teacher__user__school = teacher.user.school)| Q(parcours__teacher__user_id=teacher_id),is_share = 1).exclude(parcours__teacher = teacher).order_by("parcours__level","parcours")

        return render(request, 'qcm/course/list_courses.html', {  'teacher': teacher , 'group': group , 'courses':courses,   'parcours': parcours, 'relationships' : [] ,  'communications': [] , })
    else :
        return redirect('index')  


@login_required(login_url= 'index')
def course_custom_show_shared(request):
    
    user = request.user
    if user.is_teacher:  # teacher
        teacher = request.user.teacher
        role, group , group_id , access = get_complement(request, teacher, parcours)
        request.session["parcours_id"] = parcours.id
        request.session["group_id"] = group_id


        courses = Course.objects.filter( Q(parcours__teacher__user__school = teacher.user.school)| Q(parcours__teacher__user_id=2480),is_share = 1).exclude(teacher = teacher).order_by("parcours","parcours__level")

        return render(request, 'qcm/course/list_courses.html', {  'teacher': teacher , 'courses':courses, 'group': group ,  'parcours': None, 'relationships' : [] ,  'communications': [] , })
    else :
        return redirect('index')   



@login_required(login_url= 'index')
def ajax_course_custom_show_shared(request):
    
    teacher = Teacher.objects.get(user= request.user)
 
    data = {} 

    subject_id = request.POST.get('subject_id',0)
    level_id = request.POST.get('level_id',0)
    courses = []
    keywords = request.POST.get('keywords',None)

    parcours_id = request.POST.get('parcours_id',None)
    if parcours_id :
        parcours = Parcours.objects.get(pk = parcours_id)
        teacher = request.user.teacher
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
        else : 
            is_teacher = False 
        context = { 'courses' : courses , 'parcours' : relationship.parcours , 'is_teacher' : is_teacher , 'teacher' : request.user.teacher  }
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



def clean_data_html(raw_html):  
    cleantext = re.sub('<.*?>', '', raw_html)
    cleantext = re.sub('\n', '', cleantext)
    return cleantext




def course_to_pdf(request,id,is_multiple):

    if is_multiple :
        parcours = Parcours.objects.get(pk=id)
        courses = parcours.course.filter(forme="COURS")
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="'+str(parcours.title)+'.pdf"'
    else :
        course = Course.objects.get(pk = id) 
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="'+str(course.title)+'.pdf"'

    elements = []     

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

    #logo = Image('D:/uwamp/www/sacado/static/img/sacadoA1.png')
    logo = Image('https://sacado-academie.fr/static/img/sacadoA1.png')
    logo_tab = [[logo, "SACADO ACADEMIE" ]]
    logo_tab_tab = Table(logo_tab, hAlign='LEFT', colWidths=[0.7*inch,5*inch])
    logo_tab_tab.setStyle(TableStyle([ ('TEXTCOLOR', (0,0), (-1,0), colors.Color(0,0.5,0.62))]))
    
    elements.append(logo_tab_tab)
    elements.append(Spacer(0, 0.2*inch))


    if is_multiple :
        ##########################################################################
        #### Parcours
        ##########################################################################
        parcours_title = Paragraph( str(parcours.title) , title )
        elements.append(parcours_title, title_black)
        elements.append(Spacer(0, 0.2*inch))
        ##########################################################################
        #### Elève
        ##########################################################################
        sommaire = Paragraph( "Sommaire" , subtitle )
        elements.append(paragraph)
        elements.append(Spacer(0, 0.4*inch)) 
        ##########################################################################
        #### Nombre d'exercices traités
        ##########################################################################
        i=1
        for c in courses :
            course_title  = Paragraph( str(i)+". "+ course.title  , normal )
            elements.append(course_title)
            elements.append(Spacer(0, 0.1*inch)) 
            i+=1

        elements.append(PageBreak())

        for c in courses :
            c_title        = Paragraph( c.title , subtitle )
            elements.append(c_title)
            elements.append(Spacer(0, 0.1*inch)) 
            course_content = Paragraph(  c.annoncement  , normal )
            elements.append(course_content)
            elements.append(PageBreak())

        course_teacher = Paragraph( parcours.teacher  , normal )


    else : # un seul cours

        c_title        = Paragraph( course.title , subtitle )
        elements.append(c_title)
        elements.append(Spacer(0, 0.1*inch)) 
        c_content = clean_data_html(course.annoncement)
        course_content = Paragraph( c_content , normal )
        elements.append(course_content)
        elements.append(PageBreak())     


        course_teacher = Paragraph(  course.teacher  , normal )
    
    elements.append(course_teacher)

    doc.build(elements)

    return response












#######################################################################################################################################################################
#######################################################################################################################################################################
##################    Demand     
#######################################################################################################################################################################
#######################################################################################################################################################################



def list_demands(request):

    demands = Demand.objects.order_by("done")

    return render(request, 'qcm/demand/show_demand.html', {'demands': demands,  })




def create_demand(request):
    teacher = request.user.teacher
    form = DemandForm(request.POST or None  )
    if request.method == "POST" :
        if form.is_valid():
            nf =  form.save(commit = False)
            nf.teacher = teacher
            nf.save()
            messages.success(request, 'La demande a été envoyée avec succès !')
            rec = ['brunoserres33@gmal.com', 'philippe.demaria83@gmal.com', ]
            sending_mail("SacAdo Demande d'exercice",  "Demande d'exercice.... voir dans Demande d'exercices sur sacado-academie.fr\n Nous essaierons de réaliser l'exercice au plus proche de vos idées." , settings.DEFAULT_FROM_EMAIL , rec )

            sender = [teacher.user.email,]
            sending_mail("SacAdo Demande d'exercice",  "Votre demande d'exercice est en cours de traitement." , settings.DEFAULT_FROM_EMAIL , sender )


            return redirect('index')

        else:
            print(form.errors)

    context = {'form': form,   'teacher': teacher, 'parcours': None , 'relationships': None , 'course': None , }

    return render(request, 'qcm/demand/form_demand.html', context)




def update_demand(request, id):
 
    demand = Demand.objects.get(id=id)
    demand_form = DemandForm(request.POST or None, instance=demand, )
    teacher = request.user.teacher
    
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




def delete_demand(request, id  ):
    """
    idc : demand_id et id = parcours_id pour correspondre avec le decorateur
    """
    demand = Demand.objects.get(id=idc)
    demand.delete()
    return redirect('index')  




def show_demand(request, id ):
    """
    idc : demand_id et id = parcours_id pour correspondre avec le decorateur
    """
    demand = Demand.objects.get(pk =  id)

    user = User.objects.get(pk = request.user.id)
    teacher = Teacher.objects.get(user = user)
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

    sending_mail("SacAdo Demande d'exercice",  "Bonjour " + str(demand.teacher.user.get_full_name())+ ", \n\n Votre exercice est créé. \n\n Pour tester votre exercice, https://sacado-academie.fr/qcm/show_exercise/"+str(code)  +"\n\n Bonne utilisation de sacado." , settings.DEFAULT_FROM_EMAIL , rec )
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

    masterings_q = Mastering.objects.filter(relationship = relationship , scale = 4).order_by("ranking")
    masterings_t = Mastering.objects.filter(relationship = relationship , scale = 3).order_by("ranking")
    masterings_d = Mastering.objects.filter(relationship = relationship , scale = 2).order_by("ranking")
    masterings_u = Mastering.objects.filter(relationship = relationship , scale = 1).order_by("ranking")
    teacher = request.user.teacher

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
    teacher = request.user.teacher
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
    teacher = request.user.teacher
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


 
def create_folder(request,idg):
    """ 'parcours_is_folder' : True pour les vignettes et différencier si folder ou pas """
    teacher = request.user.teacher 

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
            else :
                return redirect ("folders") 
        else:
            print(form.errors)

    context = {'form': form,  'parcours_is_folder' : True,   'teacher': teacher, 'group': group,  'group_id': group_id,  'images' : images ,    'parcours': None,   'role' : True }

    return render(request, 'qcm/form_folder.html', context)
 


@folder_exists
def update_folder(request,id,idg):
    """ 'parcours_is_folder' : True pour les vignettes et différencier si folder ou pas """
    teacher = request.user.teacher
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
    
    else :
        group = Group.objects.get(pk = idg)
        group_id = group.id
        images = get_images_for_parcours_or_folder(group)

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


            if group_id :
                return redirect ("list_parcours_group", group_id )
            else :
                return redirect ("parcours")
 
        else:
            print(form.errors)
 
    context = {'form': form, 'teacher': teacher,  'group': group,  'group_id': group_id,  'folder': folder,  'images' : images ,   'relationships': [], 'role' : True }
 
    return render(request, 'qcm/form_folder.html', context)
 

@folder_exists
def folder_archive(request,id,idg):

    folder = Folder.objects.get(id=id)
    folder.is_archive = 1
    folder.save()
    parcourses = folder.parcours.all()
 
    for p in parcourses :
        p.is_archive = 1
        p.save()

    return redirect('list_parcours_group' , idg )




@folder_exists
def folder_unarchive(request,id,idg):

    folder = Folder.objects.get(id=id)
    folder.is_archive = 0
    folder.is_favorite = 0
    folder.save()
    subparcours = folder.parcours.all()
 
    for p in subparcours :
        p.is_archive = 0
        p.is_favorite = 0
        p.save()

 
    return redirect('parcours')
 



@folder_exists
def delete_folder(request,id,idg):

    teacher = request.user.teacher 
    folder  = Folder.objects.get(id=id)
 
    if folder.teacher == teacher or request.user.is_superuser :
        if folder.parcours.count() == 0 :
            Folder.objects.filter(pk=folder.id).update(is_trash=1)
        else :
            messages.error(request, "Le dossier "+ folder.title +" n'est pas vide. La suppression n'est pas possible. Vous devez dissocier les parcours en les décochant depuis le dossier "+ folder.title +".")
    
    else :
        messages.error(request, "Vous ne pouvez pas supprimer le dossier "+ folder.title +". Contacter le propriétaire.")
    
    if idg == 0 :
        return redirect ("parcours" )  
    else :
        return redirect ("list_parcours_group", idg )  



def parcours_delete_from_folder(request):

    parcours_id =  request.POST.get("parcours_id",None) 
    if parcours_id :
        folder = Folder.objects.get( pk = int(parcours_id))
        if parcours.teacher == request.user.teacher :
            Folder.objects.filter(pk=folder.id).update(is_trash=1)
    data = {}
         
    return JsonResponse(data)


 
@folder_exists
def delete_folder_and_contents(request,id,idg):

    teacher = request.user.teacher 
    folder = Folder.objects.get(id=id)

    if not authorizing_access(teacher,parcours, True ):
        messages.error(request, "  !!!  Redirection automatique  !!! Violation d'accès.")
        return redirect('index')

    if parcours.teacher == teacher or request.user.is_superuser :
        for p in folder.parcours.all()  :
            if p.teacher == teacher or request.user.is_superuser :
                p.delete()
        parcours.delete()
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

    teacher = request.user.teacher 
    idps = request.POST.getlist("selected_parcours")
    idfs = request.POST.getlist("selected_folders")

    if  request.POST.get("action") == "deleter" :  
        for idp in idps :
            parcours = Parcours.objects.get(id=idp) 
            parcours.students.clear()

            if not authorizing_access(teacher, parcours, False ):
                messages.error(request, "  !!!  Redirection automatique  !!! Violation d'accès.")
                return redirect('index')

            for r in parcours.parcours_relationship.all() :
                r.students.clear()
                r.skills.clear()
                ls = r.relationship_exerciselocker.all()
                for l in ls :
                    l.delete()
                r.delete()

            for c in parcours.course.all() :
                c.students.clear()
                c.creators.clear()
                c.delete()

            studentanswers = Studentanswer.objects.filter(parcours = parcours)
            for s in studentanswers :
                s.delete()
            parcours.delete()
 

        for idf in idfs :
            folder = Folder.objects.get(id=idf)
            for parcours in folder.parcours.all():
                parcours = Parcours.objects.get(id=idp) 
                parcours.students.clear()

                if not authorizing_access(teacher, parcours, False ):
                    messages.error(request, "  !!!  Redirection automatique  !!! Violation d'accès.")
                    return redirect('index')

                for r in parcours.parcours_relationship.all() :
                    r.students.clear()
                    r.skills.clear()
                    ls = r.relationship_exerciselocker.all()
                    for l in ls :
                        l.delete()
                    r.delete()

                for c in parcours.course.all() :
                    c.students.clear()
                    c.creators.clear()
                    c.delete()

                studentanswers = Studentanswer.objects.filter(parcours = parcours)
                for s in studentanswers :
                    s.delete()
                parcours.delete()
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

    provenance = request.POST.get("from",None)
    
    if provenance == "sequence" :
        return redirect('sequences')

    elif  provenance == "evaluation" :
        return redirect('evaluations')

    else :
        return redirect('parcours')


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

