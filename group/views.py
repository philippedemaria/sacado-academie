from django.conf import settings # récupération de variables globales du settings.py
from django.shortcuts import render, redirect, get_object_or_404
from account.models import Student, Teacher, Parent, Adhesion, User, Resultknowledge, Resultlastskill, Resultskill
from account.forms import UserForm
from group.models import Group, Sharing_group
from socle.models import Knowledge, Theme, Level, Skill
from qcm.models import Exercise, Parcours, Relationship, Studentanswer, Resultexercise , Resultggbskill, Customexercise , Tracker , Folder
from group.forms import GroupForm , GroupTeacherForm
from flashcard.models import Flashpack
from sendmail.models import Email
from sendmail.forms import EmailForm
from school.models import Stage
from django.contrib.auth import login, authenticate
from django.http import JsonResponse
from django.core import serializers
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.core.mail import send_mail
import uuid
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test
from group.decorators import user_is_group_teacher
from account.decorators import user_can_create
from templated_email import send_templated_mail
from django.db.models import Q
from django.db.models import Avg, Count, Min, Sum

############### bibliothèques pour les impressions pdf  #########################
import os
from reportlab.platypus.flowables import Flowable
from django.utils import formats, timezone
from io import BytesIO, StringIO
from django.http import  HttpResponse

from .fonctionsPdf import *
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, inch, landscape , letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image , PageBreak,Frame , PageTemplate
from reportlab.platypus.tables import Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import yellow, red, black, white, blue , Color
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.axes import XCategoryAxis,YValueAxis

from reportlab.graphics.shapes import Drawing,Rect,String,Line
from textwrap import TextWrapper
from reportlab.graphics.charts.textlabels import Label
from reportlab.lib.enums import TA_JUSTIFY,TA_LEFT,TA_CENTER,TA_RIGHT
from html import escape
cm = 2.54
#################################################################################
import re
import pytz
from datetime import datetime, date , timedelta
from general_fonctions import *
import qrcode
import qrcode.image.svg
from io import BytesIO
from math import sin,cos


def get_username_teacher(request ,ln):
    """
    retourne un username
    """
    ok = True
    i = 0
    code = str(uuid.uuid4())[:3] 
    if request.user.school :
        suffixe = request.user.school.country.name[2]
    else :
        suffixe = ""
    name = str(ln).replace(" ","_")    
    un = name + "_" + suffixe + code 

    while ok:
        if User.objects.filter(username=un).count() == 0:
            ok = False
        else:
            i += 1
            un = un + str(i)
 
    return un 



def get_all_documents_from_group(group,student):

 
    for folder  in group.group_folders.all() :
        folder.students.add(student)
        for parcours in folder.parcours.all() :
            parcours.groups.add(group)
            parcours.students.add(student)
            for course in parcours.course.all() :
                course.students.add(student)
            #################################################
            # clone tous les exercices rattachés au parcours 
            #################################################
            for relationship in parcours.parcours_relationship.all() :    
                relationship.students.add(student)

    for parcours in group.group_parcours.filter(folders=None) : 
        relationships = parcours.parcours_relationship.all() 
        courses = parcours.course.all()
        #################################################
        # clone le parcours
        #################################################
        parcours.groups.add(group)
        parcours.students.add(student)
        for course in courses :
            course.students.add(student)

        #################################################
        # clone tous les exercices rattachés au parcours 
        #################################################
        for relationship in parcours.parcours_relationship.all() : 
            relationship.students.add(student)
 

 

def set_username_student_profile(name):
    ok = True
    i = 0
    code = str(uuid.uuid4())[:3]    
    un = name + "_" + code 

    while ok:
        if User.objects.filter(username=un).count() == 0:
            ok = False
        else:
            i += 1
            un = un + str(i)
 
    return un 

 



def student_dashboard(request,group_id):

    student = Student.objects.get(user=request.user.id)
    #######Groupes de l'élève. 
    # si plusieurs matières alors on envoi =e sur dashboard_group 
    # si une seule matière alors  sur dashboard
    groups = student.students_to_group.all()

    parcourses_on_fire = []

    student_index = False
    if groups.count() > 1  :
        template = "dashboard.html" 
        student_index = True
    else :
        template =  "group/dashboard_group.html"  

    today = time_zone_user(request.user)        
    timer = today.time()


    # trackers= Tracker.objects.filter( user = request.user)
    # for tracker in trackers:
    #     tracker.delete()

    if int(group_id) > 0 :

        template =  "group/dashboard_group.html"  
        group = Group.objects.get(pk = group_id)
        request.session["group_id"] = group_id 

        folders = student.folders.filter( is_publish=1 , subject = group.subject,level = group.level,is_archive=0, groups = group , is_trash=0).order_by("ranking")
        
        #bases = group.group_parcours.filter(Q(is_publish=1) | Q(start__lte=today, stop__gte=today), students =student , subject = group.subject, level = group.level , folders = None, is_archive =0 , is_trash=0).distinct()

        # parcourses = bases.filter(is_evaluation=0, is_sequence=0).order_by("ranking")
        # sequences  = bases.filter(is_evaluation=0, is_sequence=1).order_by("ranking")
        # evaluations = bases.filter(is_evaluation=1).order_by("ranking")

        #last_exercises_done = student.answers.filter(exercise__knowledge__theme__subject=group.subject).order_by("-date")[:5]

    else :

        group = student.students_to_group.first()

        try :
            folders = student.folders.filter( is_publish=1 , subject = group.subject,level = group.level,is_archive=0, groups = group , is_trash=0).order_by("ranking")
        except :
            folders = student.folders.filter( is_publish=1 , is_archive=0, is_trash=0).order_by("ranking")

        # bases = student.students_to_parcours
        # parcourses = bases.filter(is_evaluation=0, folders = None, is_publish=1,is_trash=0, is_sequence=0).order_by("ranking")
        # sequences = bases.filter(is_evaluation=0, folders = None, is_publish=1,is_trash=0, is_sequence=1).order_by("ranking")
        # evaluations = bases.filter(Q(is_publish=1) | Q(start__lte=today, stop__gte=today), folders = None, is_evaluation=1,is_trash=0).order_by("ranking")
        # last_exercises_done = student.answers.order_by("-date")[:5]
   
        parcourses_on_fire = student.students_to_parcours.filter(Q(is_publish=1) | Q(start__lte=today, stop__gte=today), is_active=1,  is_archive =0 , is_trash=0).distinct()

    #flashpacks = Flashpack.objects.filter(Q(answercards=None) | Q(answercards__rappel=today), Q(stop=None) | Q(stop__gte=today), students=student,is_global=1).exclude(madeflashpack__date=today).distinct()

        #customexercises_set = set()
    nb_custom = 0
    # for p in parcourses :
    #     custom_exercises = Customexercise.objects.filter(Q(is_publish=1) | Q(start__lte=today), parcourses = p , date_limit__gte=today).order_by("date_limit")
    #     nb_custom += custom_exercises.count()
    #     customexercises_set.update(set(custom_exercises))
    #customexercises = list(customexercises_set)

    # relationships = Relationship.objects.filter(Q(is_publish=1) | Q(start__lte=today), parcours__in=parcourses, date_limit__gte=today).order_by("date_limit")
    # nb_relationships =  relationships.count()


    # exercise_tab = []
    # for r in relationships:
    #     if r not in exercise_tab:
    #         exercise_tab.append(r.exercise)
    # num = 0
    # for e in exercise_tab:
    #     if Studentanswer.objects.filter(student=student, exercise=e).count() > 0:
    #         num += 1


    # for c in customexercises :
    #     if c.customexercise_custom_answer.filter(student=student).count() > 0:
    #         num += 1

    # try:
    #     ratio = int(num / (nb_relationships+nb_custom) * 100)
    # except:
    #     ratio = 0

    # ratiowidth = int(0.9*ratio)


    # responses = request.user.user_response.exclude(is_read=1)

    # studentanswers =  student.answers.all()
    # exercises = Exercise.objects.filter(pk__in=studentanswers.values_list('exercise', flat=True))
    
    # relationships_in_late = student.students_relationship.filter(Q(is_publish = 1)|Q(start__lte=today), parcours__in=parcourses, is_evaluation=0, date_limit__lt=today).exclude(exercise__in=exercises).order_by("date_limit")
    # relationships_in_tasks = student.students_relationship.filter(Q(is_publish = 1)|Q(start__lte=today), parcours__in=parcourses, date_limit__gte=today).exclude(exercise__in=exercises).order_by("date_limit")

    context = {'student_id': student.user.id, 'student': student, 
                #'relationships': relationships, 'timer' : timer ,  'last_exercises_done' : last_exercises_done, 'responses' : responses , 
               #'evaluations': evaluations, 'ratio': ratio,
                'today' : today ,   
                'group' : group , 'groups' : groups ,
               #'ratiowidth': ratiowidth, 'relationships_in_late': relationships_in_late, 'index_tdb' : True, 
               'folders' : folders, #'parcourses_on_fire' : parcourses_on_fire ,  
               #'relationships_in_tasks': relationships_in_tasks , 'student_index' : student_index , 

                # 'customexercises': customexercises, 'flashpacks' : flashpacks,'evaluations': evaluations,'parcourses': parcourses, 'sequences' : sequences
               }

 
    return template, context


 


def knowledges_of_a_student(student):
    parcourses_tab = []
    parcourses_student_tab, exercise_tab = [] ,  []
    parcourses = student_parcours_studied(student)
    parcourses_student_tab.append(parcourses)
    for parcours in parcourses :
        if not parcours in parcourses_tab :
            parcourses_tab.append(parcours)

    for parcours in parcourses_tab :
        exercises = parcours.exercises.order_by("theme")
        for exercise in exercises:
            if not exercise in exercise_tab :
                exercise_tab.append(exercise)
    
    knowledges = []
    for exercise in exercise_tab :
        if not exercise.knowledge in knowledges:
            knowledges.append(exercise.knowledge)

    return knowledges


def count_unique(datas):
    tab, nb = [], 0
    for d in datas:
        if not d in tab:
            nb += 1
            tab.append(d)
    return nb


def include_students(request , liste, group):

    students_tab = liste.split("\r\n")

    for student_tab in students_tab:

        if ";" in student_tab:
            details =  student_tab.split(";")
        elif "," in student_tab:
            details =  student_tab.split(",")

        lname = str(cleanhtml(details[0])).strip()            
        fname = str(cleanhtml(details[1])).strip()
        password = make_password("sacado2020")
        username = get_username(request,lname , fname)
        email = ""

        try:
            for c in details[2] :
                if c == "@":
                    email = cleanhtml(details[2])
                else :
                    username = cleanhtml(details[2])
        except IndexError:
            pass
        
        try:
            for car in details[3] :
                email = cleanhtml(details[3])
        except IndexError:
            pass

        if email != "":
            send_templated_mail(
                template_name="student_registration_by_teacher",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                context={"last_name": lname, "first_name": fname, "username": username}, )

        user, created = User.objects.get_or_create(username=username,
                                                   defaults={"last_name": lname, "first_name": fname,  "time_zone": request.user.time_zone,
                                                             "password": password, "email": email, "school": request.user.school, "country": request.user.country,
                                                             "user_type": User.STUDENT})
        if created:
            code = str(uuid.uuid4())[:8] # code pour la relation avec les parents
            student = Student.objects.create(user=user, level=group.level, code=code)
        else :
            student = Student.objects.get(user=user)
        group.students.add(student)
        groups = [group]
        test = attribute_all_documents_of_groups_to_a_new_student(groups, student)

        if test :
            messages.success(request, "Les documents du groupe ont été attribué à {} {}.".format(fname, lname))
        else :
            messages.error(request, "Les documents du groupe n'ont pas pu être attribué à {} {}.".format(fname, lname))


 


# def include_students_in_a_model(request, liste,model):
 
#     students_tab = liste.split("\r\n")
#     tested = False
#     n = 0
#     for student_tab in students_tab :
#         details = student_tab.split(";")
#         try:
#             lname = str(cleanhtml(details[0]).replace(" ", "")).strip()            
#             fname = str(cleanhtml(details[1]).replace(" ", "")).strip()
#             password = make_password("sacado2020")
#             username = get_username(request,lname , fname)

#             try:
#                 for c in details[2] :
#                     if c == "@":
#                         email = cleanhtml(details[2])
#                     else :
#                         username = cleanhtml(details[2])
#             except IndexError:
#                 email = ""
                

#             try:
#                 for car in details[3] :
#                     if car == "@":
#                         email = cleanhtml(details[3])
#                     else :
#                         username = cleanhtml(details[3])
#             except IndexError:
#                 email = ""
 
#             try :
#                 if email != "" :
#                     send_mail("Inscription SacAdo", "Bonjour "+fname+", \n Votre enseignant vous a inscrit à SACADO.\n Vos identifiants sont \n Identifiant : "+username+"\n Mot de passe : sacado2020 \n Pour plus de sécurité, changez votre mot de passe lors de votre première connexion.\n Merci." , settings.DEFAULT_FROM_EMAIL , [email])
#             except :
#                 pass



#             user = User.objects.create(last_name=str(lname), first_name=str(fname), username=username, password=password, email=email,user_type=0)
#             code = str(uuid.uuid4())[:8] # code pour la relation avec les parents
#             student = Student.objects.create(user=user, level=group.level, code=code)
#             model.students.add(student)
#             n +=1 
#         except:
#             pass
#     if n == len(students_tab) :
#         tested = True

#     return tested



def convert_seconds_in_time(secondes):
    if secondes : secondes = int(secondes)
    if secondes < 60:
        return "{}s.".format(secondes)
    elif secondes < 3600:
        minutes = secondes // 60
        sec = secondes % 60
        if sec < 10:
            sec = f'0{sec}'
        return "{}min. {}s.".format(minutes, sec)
    else:
        hours = secondes // 3600
        minutes = (secondes % 3600) // 60
        sec = (secondes % 3600) % 60
        if sec < 10:
            sec = f'0{sec}'
        if minutes < 10:
            minutes = f'0{minutes}'
        return "{}h. {}min. {}s.".format(hours, minutes, sec)



def get_stage(group):

    teacher = group.teacher

    try :
        if teacher.user.school :
            school = teacher.user.school
            stage = Stage.objects.get(school = school)
        else : 
            stage = { "low" : 50 ,  "medium" : 70 ,  "up" : 85  }
    except :
            stage = { "low" : 50 ,  "medium" : 70 ,  "up" : 85  }        
    return stage


def get_complement(request, teacher, parcours_or_group):

    data = {}

    try :
        group_id = request.session.get("group_id",None)
        if group_id :
            group = Group.objects.get(pk = group_id)
        else :
            group = None   

        if Sharing_group.objects.filter(group = group  , teacher = teacher).exists() :
            sh_group = Sharing_group.objects.get(group = group , teacher = teacher)
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

    data["group_id"] = group_id
    data["group"] = group
    data["role"] = True
    data["access"] = access

    return data



def authorizing_access_group(request,teacher,group ):

    test = False
    if teacher.teacher_sharingteacher.filter(group = group).count() > 0 :
        test = True

    if group.teacher == teacher or test or request.user.is_manager :
        test = True   

    if not test :
        messages.error(request, "  !!!  Redirection automatique  !!! Violation d'accès.")
        return redirect('index')

#####################################################################################################################################
#####################################################################################################################################
####    Group
#####################################################################################################################################
#####################################################################################################################################




def dashboard_group(request, id):
    template, context = student_dashboard(request,id)
    return render(request, template , context )


def list_groups(request):
    groups = Group.objects.filter(teacher__user_id = request.user.id)
    return render(request, 'group/list_group.html', {'groups': groups, 'communications' : [] , })



def create_student_profile_inside(request, nf) : 

    first_name = str(request.user.first_name).replace(" ", "")
    last_name  = str(request.user.last_name).replace(" ","") 
    name       = last_name + "_e-test"
    username   = get_username_teacher(request,name)
    password   = make_password("sacado2020")  
    email      = ""

    if nf.students.filter( user__username__contains=name).count() == 0 :
        user,created = User.objects.get_or_create(username=username , defaults= { 'last_name' : last_name, 'first_name' : first_name,  'password' : password , 'email' : email, 'user_type' : 0})

        if created :
            mesg = "Bonjour\n\nVous venez de créer un groupe avec un profil élève. Identifiant : "+username+"\n\n Mot de passe : sacado2020 \n\n Ce mot de passe est générique. N'oubliez pas de le modifier. \n\n Merci." 
            try :
                send_mail("Identifiant Profil élève",  mesg , settings.DEFAULT_FROM_EMAIL , [email] )
            except :
                pass
            code = str(uuid.uuid4())[:8]                 
            student = Student.objects.create(user=user, level=nf.level, code=code)
            nf.students.add(student)
        else :
            student = Student.objects.get(user=user)
        st = True   

    else :
        st = False
    return st


 
def create_group(request):
    teacher = Teacher.objects.get(user_id=request.user.id)
    form = GroupTeacherForm(request.POST or None, teacher = teacher )


    if form.is_valid():
        nf = form.save(commit=False)
        nf.teacher = teacher
        nf.studentprofile = 1
        if teacher.user.school :
            nf.school = teacher.user.school
        nf.save()


        folders_ids  = request.POST.getlist("folder_ids")
        folders , parcourses = [] , []
        for f_id in folders_ids :
            folder = Folder.objects.get(pk=f_id)
            folders.append(folder)

        
        parcours_ids = request.POST.getlist("parcours_ids")
        for parcours_id in parcours_ids :
            parcours = Parcours.objects.get(pk=parcours_id)
            parcourses.append(parcours)

        stdts = request.POST.get("students")
        if stdts : 
            if len(stdts) > 0 :
                include_students(request , stdts,nf)
        student = create_student_profile_inside(request, nf) 
        duplicate_all_folders_of_group_to_a_new_student(nf , folders, teacher,  student)
        duplicate_all_parcours_of_group_to_a_new_student(nf , parcourses, teacher,  student)


        return redirect("show_group", nf.id)
    else:
        print(form.errors)

    context = {'form': form, 'teacher': teacher, 'group': None,   'students': None,}

    return render(request, 'group/form_group.html', context)



#@user_is_group_teacher
def update_group(request, id):


    teacher = Teacher.objects.get(user= request.user)
    group   = Group.objects.get(id=id)
    stdnts  = group.students.exclude(user__username = request.user.username).exclude(user__username__contains=  "_e-test").order_by("user__last_name")


    stu = group.students.values_list("user_id",flat=True)
    all_students = Student.objects.filter(user__user_type=0, level=group.level, user__school=teacher.user.school).exclude(user_id__in = stu ).order_by("user__last_name")

    authorizing_access_group(request,teacher,group )
    
    form = GroupTeacherForm(request.POST or None, teacher = teacher , instance=group )

    if form.is_valid():
        nf = form.save(commit = False)
        nf.teacher = teacher
        nf.code = group.code
        nf.studentprofile = 1
        if teacher.user.school :
            nf.school = teacher.user.school
        nf.save()


        folders_ids  = request.POST.getlist("folder_ids")
        folders , parcourses = [] , []
        for f_id in folders_ids :
            folder = Folder.objects.get(pk=f_id)
            folders.append(folder)

        
        parcours_ids = request.POST.getlist("parcours_ids")
        for parcours_id in parcours_ids :
            parcours = Parcours.objects.get(pk=parcours_id)
            parcourses.append(parcours)


        stdts = request.POST.get("students")
        if stdts : 
            if len(stdts) > 0 :
                include_students(request , stdts, group)
        try :
            student = group.students.filter(user__username__contains="_e-test").first()
            duplicate_all_folders_of_group_to_a_new_student(group , folders, teacher,  student)
            duplicate_all_parcours_of_group_to_a_new_student(group , parcourses, teacher,  student)
        except :
            pass
 
        return redirect("show_group", group.id)
    else:
        print(form.errors)

    context = {'form': form,   'group': group, 'teacher': teacher, 'students': stdnts, 'all_students' : all_students ,  }

    return render(request, 'group/form_group.html', context )






def delete_group(request, id):
    group = Group.objects.get(id=id)
    # Si le prof n'appartient pas à un établissement
    teacher = request.user.teacher
    authorizing_access_group(request,teacher,group )
    if not teacher.user.is_sacado_member :
        for student in group.students.all() :
            if not student.user.school :
                if Group.objects.filter(students=student).exclude(pk=group.id) == 0 : 
                    student.student_user.delete()
                    student.delete()
        if group.group_parcours.count() == 0  :
            group.delete()
            request.session.pop('group', None)
            request.session.pop('group_id', None)
            messages.success(request,"Groupe supprimé.")
        else :
            messages.error(request,"Le groupe ne peut pas être supprimé. Il contient des dossiers, parcours ou évaluations.")
        return redirect('index')
    else :
        if teacher.user.is_manager and group.teacher.user.school == request.user.school :
            if group.group_parcours.count() == 0  :
                group.delete()
                request.session.pop('group', None)
                request.session.pop('group_id', None)
                messages.success(request,"Groupe supprimé.")
            else :
                messages.error(request,"Le groupe ne peut pas être supprimé. Il contient des dossiers, parcours ou évaluations.")
        else :
            messages.error(request,"Vous ne pouvez pas supprimer le groupe, vous n'êtes pas son administrateur. Contacter l'administrateur de votre étalissement.")
        return redirect('school_groups')    





def delete_group_and_his_documents(request, id):
    group = Group.objects.get(id=id)
    # Si le prof n'appartient pas à un établissement
    teacher = request.user.teacher
    authorizing_access_group(request,teacher,group )
    if not teacher.user.is_sacado_member :
        for student in group.students.all() :
            if not student.user.school :
                if Group.objects.filter(students=student).exclude(pk=group.id) == 0 : 
                    student.student_user.delete()
                    student.delete()
        group.delete()
        request.session.pop('group', None)
        request.session.pop('group_id', None)
        messages.success(request,"Groupe supprimé.")
        return redirect('index')
    else :
        if teacher.user.is_manager and group.teacher.user.school == request.user.school :
            group.delete()
            request.session.pop('group', None)
            request.session.pop('group_id', None)
            messages.success(request,"Groupe supprimé.")
        else :
            messages.error(request,"Vous ne pouvez pas supprimer le groupe, vous n'êtes pas son administrateur. Contacter l'administrateur de votre étalissement.")
        return redirect('school_groups')    


















def delete_all_groups(request) :

    all_contents = request.POST.get("all_contents",None)
    group_ids = request.POST.getlist('group_ids')
    for g_id in group_ids :
        group = Group.objects.get(pk=g_id)
        if all_contents == "1" :
            for s in group.students.all():
                s.user.delete()
        group.delete()
    return redirect('school_groups')    
     

def show_group(request, id ):

    group = Group.objects.get(id=id)
    teacher = Teacher.objects.get(user=request.user)
    request.session["group_id"] = id
    data = get_complement(request, teacher, group)
    role = data['role']
    access = data['access']
    authorizing_access_group(request,teacher,group )

    factory = qrcode.image.svg.SvgImage
    img = qrcode.make('https://sacado-academie.fr/group/'+group.code , image_factory=factory, box_size=40)
    stream = BytesIO()
    img.save(stream)
    show_qr = stream.getvalue().decode()


    if request.method == "POST" :
        select_these_students = request.POST.getlist("select_these_students")

        for student_id in select_these_students :
            student = get_object_or_404(Student, user_id=student_id)
            results = Resultknowledge.objects.filter(student=student)
            for r in results :
                r.delete()
            res = Resultexercise.objects.filter(student=student)
            for re in res :
                re.delete()
            ress = Studentanswer.objects.filter(student=student)
            for rs in ress :
                rs.delete()
            student.user.delete()

    studentprofiles = group.students.filter(Q(user__username = request.user.username)|Q(user__username__contains= "_e-test")).order_by("user__last_name")
    students = group.students.exclude( user__username__contains= "_e-test").order_by("user__last_name")

    context = {  'group': group,  'communications' : [] , 'teacher' : group.teacher , 'students' : students , 'studentprofiles' : studentprofiles , 'show_qr' : show_qr }

    return render(request, 'group/show_group.html', context )



def aggregate_group(request):

    code_groupe = request.POST.get("groupe")
    student = Student.objects.get(user=request.user)

    if Group.objects.exclude(students = student).filter(code = code_groupe,lock=0).exists()  :    
        group = Group.objects.get(code = code_groupe)
        group.students.add(student)

    return redirect("index") 




def chargelisting(request):

    group_id = int(request.POST.get("group_id"))
    group = Group.objects.get(id=group_id)

    is_remove = False 
 
    data = {}

    data['html_modal_group_name'] = group.name 
   
    data['html_list_students'] = render_to_string('group/listingOfStudents.html', {  'group':group, 'is_remove' : is_remove })
 
 
    return JsonResponse(data)



def student_select_to_school(request):

    # récupération du groupe et de l'élève
    group_id = int(request.POST.get("group_id"))
    student_id = int(request.POST.get("student_id"))
    group = Group.objects.get(id=group_id) 
    student = Student.objects.get(user_id=student_id) 

    group.students.add(student)

    groups = [group]
    test = attribute_all_documents_of_groups_to_a_new_student(groups, student)

    data = {}

    data['html'] =  "<tr id='tr_school"+str(student.user.id)+"'><td>"+str(student.user.last_name)+"</td><td>"+str(student.user.first_name)+"</td><td>"+str(student.user.username)+"</td><td><a class='btn btn-xs btn-danger' data_student_id='"+str(student.user.id)+"' data_group_id='"+str(group.id)+"' ><i class='fa fa-trash'></i></a></td></tr>"
    return JsonResponse(data)




def ajax_delete_student_profiles(request):
    """ suppression du compte élève du prof """
    student_id = request.POST.get("student_id", None)
    student = get_object_or_404(Student, user_id=student_id)
    results = Resultknowledge.objects.filter(student=student)
    for r in results :
        r.delete()

    res = Resultexercise.objects.filter(student=student)
    for re in res :
        re.delete()
        
    ress = Studentanswer.objects.filter(student=student)
    for rs in ress :
        rs.delete()

    for g in student.students_to_group.all():
        g.studentprofile = False
        g.save()
    data={}
    student.user.delete()
    return JsonResponse(data)







def student_remove_from_school(request):

    group_id = int(request.POST.get("group_id"))
    student_id = int(request.POST.get("student_id"))
    group = Group.objects.get(id=group_id) 
    student = Student.objects.get(user_id=student_id) 

    for p in student.students_to_parcours.all() :
        p.students.remove(student) 
  
    for r in student.students_relationship.all() :
        r.students.remove(student) 

    group.students.remove(student)

    groups = student.students_to_group.exclude(Q(user__username = request.user.username)|Q(user__username__contains= "_e-test"))
    gr = ""
    for g in groups :
        gr = gr +str(g.name)+" "

    data = {}
    data['html'] =  "<tr id='tr"+str(student.user.id)+"'><td><input type='checkbox' class='student_select_to_school' data_student_id='"+str(student.user.id)+"' data_group_id='"+str(group.id)+"' /> </td><td>"+str(student.user.last_name)+"</td><td>"+str(student.user.first_name)+"</td><td>"+gr+"</td></tr>"
 
    return JsonResponse(data)
 


def chargelistgroup(request):

    parcours_id = int(request.POST.get("parcours_id"))
    parcours = Parcours.objects.get(id=parcours_id) 
    data = {}

    is_remove = True

    data['html_modal_group_name'] = parcours.title 
   
    data['html_list_students'] = render_to_string('group/listingOfStudents.html', {  'group':parcours, 'is_remove' : is_remove   })
    return JsonResponse(data)


def ajax_choose_parcours(request):

    level_id   = request.POST.get("level_id",None)
    subject_id = request.POST.get("subject_id",None) 

    if level_id and subject_id :
        folders  = Folder.objects.filter(level_id=level_id , subject_id = subject_id , teacher_id = 2480, is_share=1 ,is_trash=0)
    else :
        folders  = Folder.objects.filter(level_id=0 , subject_id = 0 ,teacher_id = 2480, is_share=1 ,is_trash=0)

    data = {}
    
    data['html'] = render_to_string('group/listingOfparcours.html', {   'folders':folders })
 
 
    return JsonResponse(data)





def sender_mail(request,form):
    if request.method == "POST" : 
        subject = request.POST.get("subject") 
        texte = request.POST.get("texte") 
        student_id = request.POST.get("student_id")
 
        student_user =  User.objects.get(pk=student_id)
        rcv = []
        if form.is_valid():
            nf = form.save(commit = False)
            nf.author =  request.user
            nf.save()
            nf.receivers.add(student_user)

            for r in nf.receivers.all():
                rcv.append(r.email)
            try :
                send_mail( cleanhtml(subject), cleanhtml(texte) , settings.DEFAULT_FROM_EMAIL , rcv)
            except :
                pass

        else :
            print(form.errors)
 

#@user_is_group_teacher
def result_group(request, id):

    group = Group.objects.get(id=id)
    teacher = Teacher.objects.get(user=request.user)
    authorizing_access_group(request,teacher,group )

    parcourses_tab = []
    parcourses_student_tab, exercise_tab = [] ,  []
    for student in group.students.exclude(Q(user__username = request.user.username)|Q(user__username__contains= "_e-test")).order_by("user__id"):
        parcourses = student_parcours_studied(student) 
        if parcourses in parcourses_student_tab :
            break
        else :
            parcourses_student_tab.append(parcourses)
            for parcours in parcourses :
                if not parcours in parcourses_tab :
                    parcourses_tab.append(parcours)

    for parcours in parcourses_tab :
        exercises = parcours.exercises.all()
        for exercise in exercises:
            if not exercise in exercise_tab :
                exercise_tab.append(exercise)
    
    knowledges = []
    for exercise in exercise_tab :
        if not exercise.knowledge in knowledges:
            knowledges.append(exercise.knowledge)

    stage = get_stage(group)
 
    form = EmailForm(request.POST or None )

    context = { 'group': group,'form': form,  'teacher': teacher,  "knowledges" : knowledges, 'stage' : stage, 'theme': None , 'communications' : [] , 'relationships': []  , 'parcours_tab' : [] , 'parcours' : None }

    return render(request, 'group/result_group.html', context )



#@user_is_group_teacher
def result_group_theme(request, id, idt):

    teacher = Teacher.objects.get(user=request.user)
    group = Group.objects.get(id=id)
    students = group.students.exclude(Q(user__username = request.user.username)|Q(user__username__contains= "_e-test")).order_by("user__last_name")

    authorizing_access_group(request,teacher,group ) 
 
    form = EmailForm(request.POST or None )
    theme = Theme.objects.get(id=idt)
    knowledges = Knowledge.objects.filter(level = group.level,theme = theme) 

    number_of_parcours_of_this_level_by_this_teacher = group.teacher.teacher_parcours.filter(level = group.level).count()
    parcours_id_tab , parcours_tab = [] , []
    for student in group.students.all():
        parcourses = student.students_to_parcours.all()
        parcours_tab = [parcours for parcours in  parcourses if  parcours.id not in parcours_id_tab]
        if len(parcours_tab) == number_of_parcours_of_this_level_by_this_teacher :
            break
    stage = get_stage(group)
    context = {  'group': group, 'form': form, 'theme': theme, 'students': students, 'stage' : stage  , "knowledges" : knowledges, "teacher" : teacher,  'parcours_tab' : parcours_tab, 'parcours' : None  , 'communications' :  [] , 'relationships':  []   }

    return render(request, 'group/result_group.html', context )



#@user_is_group_teacher
def result_group_exercise(request, id):
    group = Group.objects.get(id=id)
    form = EmailForm(request.POST or None)
    stage = get_stage(group)

    teacher = Teacher.objects.get(user=request.user)

    authorizing_access_group(request,teacher,group ) 

    sender_mail(request,form)

    students = group.students.exclude(Q(user__username = request.user.username)|Q(user__username__contains= "_e-test")).order_by("user__last_name")

    context = {'group': group, 'form': form , 'stage' : stage  , 'students' : students  , 'teacher': teacher, 'theme' : None  , 'communications' : [], 'relationships': [] , 'parcours_tab' : [] , 'parcours' : None  }

    return render(request, 'group/result_group_exercise.html', context)



#@user_is_group_teacher
def result_group_skill(request, id):

    group = Group.objects.get(id=id)
    skills = Skill.objects.filter(subject=group.subject)
    students = group.students.exclude(Q(user__username = request.user.username)|Q(user__username__contains= "_e-test")).order_by("user__last_name")
    teacher = Teacher.objects.get(user=request.user)

    authorizing_access_group(request,teacher,group ) 

    form = EmailForm(request.POST or None )
    stage = get_stage(group)

    context = {  'group': group,'form': form,'skills': skills , 'students': students ,  'teacher': teacher, 'stage' : stage   ,  'theme' : None  , 'communications' : [], 'relationships': [] , 'parcours' : None  }

    return render(request, 'group/result_group_skill.html', context )





#@user_is_group_teacher
def result_group_waiting(request, id):

    group = Group.objects.get(id=id)
    students = group.students.exclude(Q(user__username = request.user.username)|Q(user__username__contains= "_e-test")).order_by("user__last_name")
    teacher = Teacher.objects.get(user=request.user)

    waitings = group.level.waitings.filter(theme__subject=group.subject)
 
    authorizing_access_group(request,teacher,group ) 

    form = EmailForm(request.POST or None )
    stage = get_stage(group)

    context = {  'group': group,'form': form,'waitings': waitings , 'students': students ,  'teacher': teacher, 'stage' : stage   ,  'theme' : None  , 'communications' : [], 'relationships': [] , 'parcours' : None  }

    return render(request, 'group/result_group_waiting.html', context )


#@user_is_group_teacher
def result_group_theme_exercise(request, id, idt):
    group = Group.objects.get(id=id)
    form = EmailForm(request.POST or None )
    theme = Theme.objects.get(id=idt)
    stage = get_stage(group)
    teacher = Teacher.objects.get(user=request.user)
    students = group.students.exclude(Q(user__username = request.user.username)|Q(user__username__contains= "_e-test")).order_by("user__last_name")
    authorizing_access_group(request,teacher,group ) 

    context = {  'group': group, 'form': form, 'theme': theme, 'students': students, 'teacher': teacher, "slug" : theme.slug , 'stage' : stage   , 'communications' : [], 'relationships': [] , 'parcours': None  }

    return render(request, 'group/result_group_theme_exercise.html', context )

 

def stat_group(request, id):
    group = Group.objects.get(id=id)
    form = EmailForm(request.POST or None )
    teacher = Teacher.objects.get(user=request.user)

    
    authorizing_access_group(request,teacher,group ) 

    stats = []
    for s in group.students.exclude(Q(user__username = request.user.username)|Q(user__username__contains= "_e-test")).order_by("user__last_name") :
        student = {}
        student["name"] = s 
        parcours = Parcours.objects.filter(students=s,is_publish=1,is_trash=0)
        nb_exo_total = 0
        for p in parcours :
            nb_exo_total += Relationship.objects.filter(parcours=p,is_publish=1).count()
        student["parcours"] = parcours 
        studentanswers = Studentanswer.objects.filter(parcours__in = parcours, student=s)
        nb_exo_done = 0
        nb_exo_done_tab = []
        for studentanswer in studentanswers :
            if studentanswer.id not in nb_exo_done_tab :
                nb_exo_done += 1
                nb_exo_done_tab.append(studentanswer.id)
        student["nb_exo"] = int(nb_exo_done)
        student["nb_exo_total"] = int(nb_exo_total)
        try :
            student["percent"] = int(nb_exo_done / nb_exo_total * 100)
        except : 
            student["percent"] = 0
        studentanswers = Studentanswer.objects.filter(student=s)
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
                student["duration"] = duration
                student["average_score"] = int(average_score)
                student["heure_max"] = tab_date[len(tab_date)-1]
                student["heure_min"] = tab_date[0]
                tab.sort()
                if len(tab)%2 == 0 :
                    med = (tab[(len(tab)-1)//2]+tab[(len(tab)-1)//2+1])/2 ### len(tab)-1 , ce -1 est causÃ© par le rang 0 du tableau
                else:
                    med = tab[(len(tab)-1)//2+1]
                student["median"] = int(med)
            else:
                average_score = int(score)
                student["duration"] = duration
                student["average_score"] = int(score)
                student["heure_max"] = tab_date[0]
                student["heure_min"] = tab_date[0]
                student["median"] = int(score)
        except :
            student["duration"] = ""
            student["average_score"] = ""
            student["heure_max"] = ""
            student["heure_min"] = ""
            student["median"] = ""
        stats.append(student)

    context = {  'group': group, 'form': form, 'stats':stats , 'teacher': teacher, 'parcours' : None }
 
    return render(request, 'group/stat_group.html', context )

 
def task_group(request, id):
    group = Group.objects.get(id=id)
    teacher = Teacher.objects.get(user=request.user)

    
    authorizing_access_group(request,teacher,group ) 


    stats = []
    for s in group.students.exclude(Q(user__username = request.user.username)|Q(user__username__contains= "_e-test")).order_by("user__last_name"):
        student = {}
        student["name"] = s
        parcours = Parcours.objects.filter(students=s,is_trash=0)
        student["parcours"] = parcours
        relationships = Relationship.objects.filter(parcours__in=parcours).exclude(date_limit=None).select_related('exercise')
        done, late, no_done = 0, 0, 0
        for relationship in relationships:
            nb_ontime = Studentanswer.objects.filter(student=s, exercise=relationship.exercise).count()

            utc_dt = dt_naive_to_timezone(relationship.date_limit, s.user.time_zone)

            nb = Studentanswer.objects.filter(student=s, exercise=relationship.exercise, date__lte=utc_dt).count()
            if nb_ontime == 0:
                no_done += 1
            elif nb > 0:
                done += 1
            else:
                late += 1
        student["nb"] = no_done + done + late
        student["no_done"] = no_done
        student["done"] = done
        student["late"] = late
        stats.append(student)

    context = {'group': group, 'stats': stats, 'teacher': teacher,}

    return render(request, 'group/task_group.html', context)




def select_exercise_by_knowledge(request):
    data = {}
    group_id = request.POST.get("group_id")
    group = Group.objects.get(id=int(group_id))
    teacher = Teacher.objects.get(user=request.user)
    authorizing_access_group(request,teacher,group ) 


    knowledge_id = request.POST.get("knowledge_id")
    knowledge = Knowledge.objects.get(id=int(knowledge_id))
    exercises = Exercise.objects.filter(knowledge=knowledge)

    data['html'] = render_to_string('qcm/select_exercise_by_knowledge.html',
                                    {'exercises': exercises, 'knowledge': knowledge, 'group': group,
                                     'teacher': teacher})
    return JsonResponse(data)




def associate_exercise_by_parcours(request,id,idt):


    group = Group.objects.get(id = id)
    teacher = Teacher.objects.get(user=request.user)
    authorizing_access_group(request,teacher,group )  
       
    theme = Theme.objects.get(id = idt)
    knowledge_id = request.POST.get("knowledge_id_modal") 
    knowledge = Knowledge.objects.get(id=int(knowledge_id))

    parcourses = Parcours.objects.filter(teacher = teacher, level = group.level,is_trash=0)
 
    return redirect('result_group_theme', group.id, theme.id)



def enroll(request, slug):
    '''
    Création d'un compte élève et inscription à un groupe via le lien donné par l'enseignant
    '''
    group = get_object_or_404(Group, code=slug)
    user_form = UserForm(request.POST or None)

    if request.method == 'POST':
        submit_button = request.POST.get("submit_button", None)
        if submit_button == "Enregistrer" :
            user_form = UserForm(request.POST)
            if user_form.is_valid() :
                user = user_form.save(commit=False)
                user.user_type = User.STUDENT
                password = request.POST.get("password1")
                username = request.POST.get("username")
                user.set_password(password)
                user.save()
                student = Student.objects.create(user=user, level=group.level)
                group.students.add(student)
                # Affections des DOSSIERS ET parcours
                messages.success(request, "Inscription réalisée avec succès ! Si vous avez renseigné votre email, vous avez reçu un mail de confirmation.")                
                groups = [group]
                test = attribute_all_documents_of_groups_to_a_new_student(groups, student)

                if test :
                    messages.success(request, "Les documents du groupe ont été attribué à {} {}.".format(user.first_name, user.last_name))
                else :
                    messages.error(request, "Les documents du groupe n'ont pas pu être attribué à {} {}.".format(user.first_name, user.last_name))

                try :    
                    if user_form.cleaned_data['email']:
                        send_mail('Création de compte sur Sacado',
                                  'Bonjour, votre compte SacAdo est maintenant disponible. \n\n Votre identifiant est '+str(username) +". \n Votre mot de passe est "+str(password)+'.\n\n Pour vous connecter, redirigez-vous vers https://sacado-academie.fr.\n Ceci est un mail automatique. Ne pas répondre.',
                                  settings.DEFAULT_FROM_EMAIL,
                                  [request.POST.get("email")])
                except :
                    pass 
                user = authenticate(username=username, password=password)
                login(request, user,  backend='django.contrib.auth.backends.ModelBackend' )
                request.session["user_id"] = request.user.id
            else :
                messages.error(request, "Inscription abandonnée !")
                return render(request, 'group/enroll.html', {"u_form": user_form, "slug": slug, "group": group, })    
        else :

            username = request.POST.get("this_username")
            group_id = request.POST.get("group_id")
            group = get_object_or_404(Group, pk=group_id)
            password = request.POST.get("this_password")
            
            user = authenticate(username=username, password=password)
            if user.is_authenticated :
                login(request, user,  backend='django.contrib.auth.backends.ModelBackend' )
                request.session["user_id"] = request.user.id
                group.students.add(user.student)
                messages.success(request, "Inscription réalisée avec succès ! Si vous avez renseigné votre email, vous avez reçu un mail de confirmation.")  
                groups = [group]
                test = attribute_all_documents_of_groups_to_a_new_student(groups, user.student)             
                if test :
                    messages.success(request, "Les documents du groupe ont été attribué à {} {}.".format(user.first_name, user.last_name))
                else :
                    messages.error(request, "Les documents du groupe n'ont pas pu être attribué à {} {}.".format(user.first_name, user.last_name))
            else :
                messages.error(request,"Utilisateur inconnu")

        return redirect('index') 

    return render(request, 'group/enroll.html', {"u_form": user_form, "slug": slug, "group": group, })


def radar(L):

    """dessine le radar d'une liste de listes [intitulé, note/100]
    valeur de retour : une "shape" de type Drawing
    """
    #print("radar : ",L)
    from reportlab.lib.units import cm
    
    haut=18*cm   #hauteur et largeur du rectangle encadrant
    larg=18*cm
    rayon=6*cm   #rayon du radar
    n=len(L)
    dangle=6.2832/n  #angle d'un secteur angulaire
    angle=1.5707   #angle de départ : pi/2 (verticale)
    deno=100  #note sur ?
    tick=10   #graduation tous les ?
    #cfond=Color(1,1,1) #couleur du fond
    cgrille=Color(0.8,0.8,0.8)  #couleur de la grille
    cligne=Color(1,0,0)         #couleur des la ligne des données
    w=TextWrapper(width=20)     #les intitules auront au plus 20 caractères
                                #de large, on les decoupe sur plusieurs lignes

    #-------------------------------------------------
    d=Drawing(larg,haut)
    d.add(String(larg/2,haut-0.5*cm,"Graphique des attendus", textAnchor="middle"))
    if n<=2 :  
        d.add(String(larg/2,haut/2,"pas assez de notes pour le graphique", textAnchor="middle"))
        return d
    
    for i in range(n) :
        a=angle+i*dangle
        # ----------- placement des intitulés
        intitule=Label()
        intitule.setOrigin(larg/2+(rayon+0.2*cm)*cos(a),haut/2+(rayon+0.2*cm)*sin(a))
        if 0.78 <(a % 6.28) <2.35 : 
            intitule.boxAnchor="s"
        elif 2.35 <= (a % 6.28) <3.92 : 
            intitule.boxAnchor="e"
        elif  3.92<=a % 6.28<5.5 :
            intitule.boxAnchor="n"
        else :
            intitule.boxAnchor="w"
        intitule.setText(w.fill(L[i][0]))
        d.add(intitule)
        #-------------------- la grille du radar
        d.add(Line(larg/2,haut/2,larg/2+rayon*cos(a),haut/2+rayon*sin(a), strokeColor=cgrille))
        for j in range(1,int(deno/tick)+1):
            r=rayon*j*tick/deno
            d.add(Line(larg/2+r*cos(angle+i*dangle),haut/2+r*sin(angle+i*dangle),\
                       larg/2+r*cos(angle+(i+1)*dangle),haut/2+r*sin(angle+(i+1)*dangle),\
                       strokeColor=cgrille ))

        #--------------------- la ligne des données  
        r1=L[i-1][1]*rayon/deno
        r2=L[i % n][1]*rayon/deno
        d.add(Line(larg/2+r1*cos(a),haut/2+r1*sin(a),larg/2+r2*cos(a+dangle),haut/2+r2*sin(a+dangle),\
                   strokeColor=cligne, strokeWidth=2))

    #------------------------ graduations
    
    for i in range(1,int(deno/tick)+1):
        r=rayon*(i-0.3)*tick/deno
        d.add(String(larg/2+r*cos(angle),haut/2+r*sin(angle),str(i*tick)))     
    return d


def diagBaton(data) :
    d = Drawing(400, 200)
    
    # code to produce the above chart
    bc = VerticalBarChart()
    couleurs=[[Color(0.95,0.95,0.95),Color(0.8,0.3,0.3) ], #non acquis
    [Color(0.95,0.95,0.95),Color(0.7,0.2,0.6) ],          #en cours
    [Color(0.95,0.95,0.95),Color(0.5,0.7,0.5) ],
    [Color(0.95,0.95,0.95),Color(0.2,0.2,0.8) ]]
    
    bc.x = 50
    bc.y = 10
    bc.height = 105
    bc.width = 300
    bc.data = data
    for i in range(len(data[0])):
        for j in range(len(data)):
            bc.bars[(j,i)].fillColor=couleurs[i%4][j%2]
    bc.strokeColor = black
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = 100
    bc.valueAxis.valueStep = 10
    bc.categoryAxis.labels.boxAnchor = 'ne'
    bc.categoryAxis.labels.dx = 8
    bc.categoryAxis.labels.dy = -2
    bc.categoryAxis.labels.angle = 30
    bc.categoryAxis.categoryNames = ['Non acquis', 'En cours ', 'Acquis', 'Expert']
    d.add(bc)
    return d
  

def print_statistiques(request, group_id, student_id):


    themes, subjects = [], []
    group = Group.objects.get(pk = group_id)
    teacher = Teacher.objects.get(user=request.user)

    authorizing_access_group(request,teacher,group ) 

    if student_id == 0  :
        students = group.students.exclude(Q(user__username = request.user.username)|Q(user__username__contains= "_e-test")).order_by("user__last_name")
        title_of_report = group.name+"_"+str(timezone.now().date())

        knows = Knowledge.objects.filter(level = group.level).order_by("level")
        for know in knows :
            if not know.theme in themes :
                themes.append(know.theme)
    else :
        student = Student.objects.get(pk = student_id)
        students = [student]
        title_of_report = student.user.last_name+"_"+student.user.first_name+"_"+str(timezone.now().date())

        knows = knowledges_of_a_student(student)
        for know in knows :
            if not know.theme in themes :
                themes.append(know.theme)

    subject = group.subject

    elements = []        

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="'+str(title_of_report)+'.pdf"'

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

    title = ParagraphStyle('title', 
                            fontSize=20, 
                            textColor=colors.HexColor("#00819f"),
                            )

    subtitle = ParagraphStyle('title', 
                            fontSize=16, 
                            textColor=colors.HexColor("#00819f"),
                            )
 
    normal = ParagraphStyle(name='Normal',fontSize=12,)    
    style_cell = TableStyle(
            [
                ('SPAN', (0, 1), (1, 1)),
                ('TEXTCOLOR', (0, 1), (-1, -1),  colors.Color(0,0.7,0.7))
            ]
        )


    for student in students :
        #logo = Image('D:/uwamp/www/sacado/static/img/sacadoA1.png')
        logo = Image('https://sacado-academie.fr/static/img/sacadoA1.png')
        logo_tab = [[logo, "SACADO \nBilan des acquisitions" ]]
        logo_tab_tab = Table(logo_tab, hAlign='LEFT', colWidths=[0.7*inch,5*inch])
        logo_tab_tab.setStyle(TableStyle([ ('TEXTCOLOR', (0,0), (-1,0), colors.Color(0,0.5,0.62))]))
        elements.append(logo_tab_tab)
        elements.append(Spacer(0, 0.1*inch))

        if timezone.now().month < 9 :
            scolar_year = str(timezone.now().year-1)+"-"+str(timezone.now().year)
        else :
            scolar_year = str(timezone.now().year)+"-"+str(timezone.now().year+1)


        studentanswers = student.answers.all()
        studentanswer_ids = studentanswers.values_list("id",flat=True).distinct() 
        nb_exo = studentanswer_ids.count() # Nombre d'exercices traités
        info = studentanswers.aggregate( duration =  Sum("secondes"), score =  Sum("point"), avg =  Avg("point"))
        scores = studentanswers.values_list("point",flat=True).order_by("point")
 
        score , duration , average_score = 0  , 0 , 0
        if info["score"]:
            score = info["score"]
        if info["duration"]:
            duration = info["duration"]
        if info["avg"]:
            average_score = int(info["avg"])

        try :
            if len(studentanswers)>1 :
                if len(scores)%2 == 0 :
                    med = (scores[(len(scores)-1)//2]+scores[(len(scores)-1)//2+1])/2 ### len(scores)-1 , ce -1 est causé par le rang 0 du tableau
                else:
                    med = scores[(len(scores)-1)//2+1]
                median = int(med)
            else :
                median = int(score)
        except :
            median = 0

        # Vérifie que le parcours par défaut est donné
        nb_k_p , nb_p = 0 , 0 
        parcourses = student_parcours_studied(student)

        knowledges , knowledge_ids  = [] ,  []

        knowledge_ids = Relationship.objects.values_list("exercise__knowledge_id", flat=True).filter(parcours__in = parcourses,exercise__theme__in= themes , exercise__level = student.level).distinct()
        nb_k_p += knowledge_ids.count()
        
        exercise_ids  = Relationship.objects.values_list("exercise_id", flat=True).filter(parcours__in = parcourses,exercise__theme__in= themes , exercise__level = student.level).distinct()
        nb_p += exercise_ids.count()

        knows_ids = student.answers.values_list("id",flat=True).filter(exercise__knowledge_id__in = knowledge_ids, exercise_id__in= exercise_ids)
        nb_k = knows_ids.count()

        # Les taux
        try :
            p_k = int(nb_k/nb_k_p * 100 )
            if p_k > 100 :
                p_k = 100
        except :
            p_k = 0
        try :
            p_e = int(nb_exo/nb_p * 100)
            if p_e > 100 :
                p_e = 100
        except :
            p_e = 0

        relationships = Relationship.objects.filter(parcours__in = parcourses).exclude(date_limit=None)
        done, late, no_done = 0 , 0 , 0 
        for relationship in relationships :

            ontime = student.answers.filter(exercise = relationship.exercise )
            nb_ontime = ontime.count()
            nb = ontime.filter(date__lte= relationship.date_limit ).count()
            if nb_ontime == 0 :
                no_done += 1
            elif nb > 0 :
                done += 1
            else :
                late += 1 
        t_r = no_done + done + late
 
        ##########################################################################
        #### Gestion de l'autonomie
        ##########################################################################
        if nb_exo > nb_p :
            nbr = nb_exo - nb_p
            complt = " dont "+str(nbr)+" en autonomie"
        else :
            complt = ""
        if nb_k > nb_k_p :
            nbrk = nb_k - nb_k_p
            complement = " dont "+str(nbrk)+" en autonomie" 
        else :
            complement = ""

 
        ##########################################################################
        #### Gestion des labels à afficher
        ##########################################################################
        labels = [str(student.user.last_name)+" "+str(student.user.first_name), "Classe de "+str(student.level)+", année scolaire "+scolar_year,"Temps de connexion : "+convert_seconds_in_time(duration), "Score moyen : "+str(average_score)+"%, score médian : "+str(median)+"%" , \
                 "Exercices SACADO proposés : " +str(nb_p) , "dont "+str(nb_exo)+" étudiés "+complt+", soit un taux d'étude de "+str(p_e)+"%",  \
                 "Tâches demandées : "+str(t_r),  "Remises en temps : "+str(done)+",  remises en retard : "+str(late)+", non remises : "+str(no_done),\
                 "Bilan des compétences ",]

        spacers , titles,subtitles = [1,3,5,7] ,[0],[4,6,8]

        i = 0
        for label in labels :
            if i in spacers : 
                height = 0.25
            else :
                height = 0.1
            if i in titles : 
                style = title
                height = 0.1
            elif i in subtitles :
                style = subtitle
                height = 0.1
            else :
                style = normal
            paragraph = Paragraph( label , style )
            elements.append(paragraph)
            elements.append(Spacer(0, height*inch))
            i+=1   



        ##########################################################################
        #### Gestion des compétences
        ##########################################################################
        sk_tab = []
        skills = Skill.objects.filter(subject= subject)
        for skill  in skills :
            try :
                resultlastskill  = skill.student_resultskill.get(student = student)
                sk_tab.append([skill.name, code_couleur(resultlastskill.point,teacher) ])
            except :
                sk_tab.append([skill.name,  "N.E"  ])


        try : # Test pour les élèves qui n'auront rien fait, il n'auront pas de th_tab donc il ne faut l'afficher 
            skill_tab = Table(sk_tab, hAlign='LEFT', colWidths=[5.2*inch,1*inch])
            skill_tab.setStyle(TableStyle([
                       ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                       ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                       ]))
        except : 
            skill_tab = Table(sk_tab, hAlign='LEFT', colWidths=[5.2*inch,1*inch])

        elements.append(skill_tab)
        ##########################################################################
        #### Gestion des themes
        ##########################################################################
        elements.append(Spacer(0, 0.25*inch))
        paragraph = Paragraph( "Bilan des attendus" , title )
        elements.append(paragraph)
        elements.append(Spacer(0, 0.15*inch))

        th_tab, bgc_tab = [] , [('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),('BOX', (0,0), (-1,-1), 0.25, colors.black),]

        bgc = 0        
        for theme  in themes :
            waiting_set = set(theme.waitings.filter(theme__subject = group.subject, level = group.level)) # on profite de cette boucle pour créer la liste des attendus
            th_tab.append([theme.name,  " " ])
            bgc_tab.append(  ('BACKGROUND', (0,bgc), (-1,bgc), colors.Color(0,0.5,0.62)) )

            for waiting in waiting_set :
                bgc += 1

                resultwaitings = student.results_e.filter(exercise__knowledge__waiting__name = waiting.name )

                som_ws = 0
                for result in resultwaitings :
                    som_ws += result.point
                try :
                    avg_ws = int(som_ws / len(resultwaitings))
                    th_tab.append([waiting.name,  code_couleur(avg_ws,teacher) ])
                except :
                    th_tab.append([waiting.name,  "N.E" ])
                
            bgc += 1

        try : # Test pour les élèves qui n'auront rien fait, il n'auront pas de th_tab donc il ne faut l'afficher 
            theme_tab = Table(th_tab, hAlign='LEFT', colWidths=[6*inch,1*inch])
            theme_tab.setStyle(TableStyle(bgc_tab))
        except : 
            theme_tab = Table(th_tab, hAlign='LEFT', colWidths=[6*inch,1*inch])

        elements.append(theme_tab)

        loop  = 0
        for theme  in themes :
            ##########################################################################
            #### Gestion des knowledges par thème
            ##########################################################################
            if len(knowledge_ids) > 0 :

                if loop%2 == 0 :
                    elements.append(PageBreak()) # Ouvre une nouvelle page - 2 thèmes
                loop +=1
                # Append le thème 
                paragraph = Paragraph( theme.name , title )  
                elements.append(paragraph)
                elements.append(Spacer(0, 0.2*inch)) 
                knowledge_tab = [['Savoir faire','Score','Nombre de \n fois étudié',]]
                #######


                for knowledge_id in knowledge_ids :
                    # Savoir faire
                    name_k = Knowledge.objects.get(pk = knowledge_id).name
                    name   = split_paragraph(name_k,80)

                    ##########################################################################
                    #### Affichage des résultats par knowledge
                    ##########################################################################                    
                    try :      
                        knowledgeResult = student.results_k.get(knowledge_id  = knowledge_id)
                        knowledgeResult_nb = student.answers.values_list("id",flat=True).filter(exercise__knowledge_id = knowledge_id ).count()          
                        knowledge_tab.append(      ( name ,  code_couleur(knowledgeResult.point,teacher) , knowledgeResult_nb )          )
                    except : 
                        knowledge_tab.append(      ( name ,   "N.E"  , 0  )        )
                
                ##########################################################################
                # Bordure du savoir faire
                ##########################################################################

                knowledge_tab_tab = Table(knowledge_tab, hAlign='LEFT', colWidths=[6*inch,0.5*inch,0.8*inch])
                knowledge_tab_tab.setStyle(TableStyle([
                           ('INNERGRID', (0,0), (-1,-1), 0.25, colors.gray),
                           ('BOX', (0,0), (-1,-1), 0.25, colors.gray),
                            ('BACKGROUND', (0,0), (-1,0), colors.Color(0,0.5,0.62))
                           ]))

                elements.append(knowledge_tab_tab)

        elements.append(PageBreak())

    doc.build(elements)

    return response

def envoieStatsEnMasse(request):
    #users=User.objects.filter(last_name="ceroi")
    listParents=Parent.objects.all()
    #listParents=Parent.objects.filter(user=users[len(users)-1])
    cr="" #le compte rendu de l'opération
    auj=datetime.now().replace(tzinfo=pytz.UTC) 
    for parent in listParents :
        for enfant in parent.students.all():
            adhs=Adhesion.objects.filter(student=enfant)
            for adh in adhs :
                if adh.start < auj  <= adh.stop and (auj - adh.start).days % parent.periodicity==0 :
                    try :
                        sendStats(parent,enfant,auj-timedelta(days=parent.periodicity),auj)
                        cr+="envoi à "+str(parent)+" : ok\n"
                    except :
                        cr+="envoi à "+str(parent)+" : échec\n"
    return render(request,'group/envoieMails.html',{'status':cr})






def print_monthly_statistiques(request):

    themes, subjects = [], []


    date_start = request.POST.get('date_start')
    date_stop  = request.POST.get('date_stop') 
    group_id   = request.POST.get('group_id')
    student_id = request.POST.get('student_id') 

    group = Group.objects.get(pk = group_id)

    if request.user.is_teacher :
        teacher = Teacher.objects.get(user=request.user)
        authorizing_access_group(request,teacher,group ) 
    elif request.user.is_parent :
        student = Student.objects.get(pk = student_id)
        if not student in request.user.parent.students.all() :
            return redirect('index')


    student = Student.objects.get(user_id = student_id)

    students = [student]
    title_of_report = student.user.last_name+"_"+student.user.first_name+"_"+str(timezone.now().date())

    elements = []        

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="'+str(title_of_report)+'.pdf"'

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
    title = ParagraphStyle('title', 
                            fontSize=20, 
                            textColor=colors.HexColor("#00819f"),
                            )
    subtitle = ParagraphStyle('title', 
                            fontSize=16, 
                            textColor=colors.HexColor("#00819f"),
                            )
    normal = ParagraphStyle(name='Normal',fontSize=12,)    
    style_cell = TableStyle(
            [
                ('SPAN', (0, 1), (1, 1)),
                ('TEXTCOLOR', (0, 1), (-1, -1),  colors.Color(0,0.7,0.7))
            ]
        )



    for student in students :
        #logo = Image('D:/uwamp/www/sacado/static/img/sacadoA1.png')
        logo = Image('https://sacado-academie.fr/static/img/sacadoA1.png')
        logo_tab = [[logo, "SACADO Académie\nBilan des acquisitions" ]]
        logo_tab_tab = Table(logo_tab, hAlign='LEFT', colWidths=[0.7*inch,5*inch])
        logo_tab_tab.setStyle(TableStyle([ ('TEXTCOLOR', (0,0), (-1,0), colors.Color(0,0.5,0.62))]))
        elements.append(logo_tab_tab)
        elements.append(Spacer(0, 0.1*inch))

        ys , ms, ds = date_stop.split("-")
        date_stopped = datetime( int(ys) , int(ms), int(ds)) + timedelta(days =1)

        studentanswers = student.answers.filter(date__lte = date_stopped , date__gte= date_start)

        studentanswer_ids = studentanswers.values_list("exercise_id",flat=True).distinct() 

        nb_exo = studentanswer_ids.count() # Nombre d'exercices traités
        info = studentanswers.aggregate( duration =  Sum("secondes"), score =  Sum("point"), avg =  Avg("point"))
        scores = studentanswers.values_list("point",flat=True).order_by("point")
 
        score , duration , average_score = 0  , 0 , 0
        if info["score"]:
            score = info["score"]
        if info["duration"]:
            duration = info["duration"]
        if info["avg"]:
            average_score = int(info["avg"])


        k_ids = studentanswers.values_list("exercise__knowledge_id", flat=True).distinct()
        nb_k_p = k_ids.count()

        exo_ids = studentanswers.values_list("exercise_id", flat=True).distinct()
        nb_e = exo_ids.count()

        skill_ids = studentanswers.values_list("exercise__supportfile__skills", flat=True).distinct()
        nb_skills = skill_ids.count()

        theme_ids = studentanswers.values_list("exercise__theme_id", flat=True).distinct()

        ##########################################################################
        #### Gestion des labels à afficher
        ##########################################################################
        labels = [str(student.user.last_name)+" "+str(student.user.first_name), "Classe de "+str(student.level)+", Du :"+str(date_start)+" au "+str(date_stop),"Temps de connexion : "+convert_seconds_in_time(duration), "Score moyen : "+str(average_score)+"%" , \
                 "Exercices SACADO travaillés : " +str(nb_e)]

        spacers , titles,subtitles = [1,3] ,[0],[5]

        i = 0
        for label in labels :
            if i in spacers : 
                height = 0.25
            else :
                height = 0.1
            if i in titles : 
                style = title
                height = 0.15
            elif i in subtitles :
                style = subtitle
                height = 0.1
            else :
                style = normal
            paragraph = Paragraph( label , style )
            elements.append(paragraph)
            elements.append(Spacer(0, height*inch))
            i+=1   

 
        ##########################################################################
        #### Gestion des themes
        ##########################################################################
        elements.append(Spacer(0, 0.25*inch))

        e_tab, bgc_tab = [] , [('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),('BOX', (0,0), (-1,-1), 0.25, colors.black),]
        w_tab = [] 
        bgc = 0  

        paragraphexo = Paragraph( "Résultats des exercices" , title )
        elements.append(paragraphexo)
        elements.append(Spacer(0, 0.15*inch))

        studentanswer_orders = studentanswers.prefetch_related('exercise') 

        exo_dict          = dict()
        exo_intitule_dict = dict()
        waitings_exo_dict = dict()
        waitings_intitule_dict = dict()

        for studentanswer  in studentanswer_orders :
            if  studentanswer.exercise.id in exo_dict :
                exo_dict[studentanswer.exercise.id].append(studentanswer.point)
            else :
                exo_dict[studentanswer.exercise.id] = [studentanswer.point]
                exo_intitule_dict[studentanswer.exercise.id] =  studentanswer.exercise.supportfile.title
            w_id = studentanswer.exercise.knowledge.waiting.id    
            if  w_id in waitings_exo_dict :
                waitings_exo_dict[w_id].append(studentanswer.point)
            else :
                waitings_exo_dict[w_id] = [studentanswer.point]
                waitings_intitule_dict[w_id] = studentanswer.exercise.knowledge.waiting.name   


        bgc_tab.append(  ('BACKGROUND', (0,bgc), (-1,bgc), colors.Color(0,0.5,0.62))  )

        for k,vs in exo_dict.items() :
            chn = ""
            for v in vs : 
                chn += str(v)+"%  "
            e_tab.append( (exo_intitule_dict[k], chn ) )

        liste_radar = []
        for n,ws in waitings_exo_dict.items() :
            liste_radar.append( [ waitings_intitule_dict[n], sum(ws)/len(ws) ] )

 

        if len(e_tab) > 0 :
            e_tab_tab = Table(e_tab, hAlign='LEFT', colWidths=[5.5*inch,1.8*inch])
            e_tab_tab.setStyle(TableStyle([
                           ('INNERGRID', (0,0), (-1,-1), 0.25, colors.gray),
                           ('BOX', (0,0), (-1,-1), 0.25, colors.gray),
                           ]))    
            elements.append(e_tab_tab)
 

        #elements.append(PageBreak())
        if len(liste_radar) > 0 :
            d = radar(liste_radar)
            elements.append(d)

    doc.build(elements)

    return response













#def print_ids(request, id):
    group = Group.objects.get(id=id)
    teacher = Teacher.objects.get(user=request.user)

    authorizing_access_group(request,teacher,group ) 


    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="identifiants_groupe'+group.name+'.pdf"'
    p = canvas.Canvas(response)
    i = 1

    img_file = 'https://sacado-academie.fr/static/img/sacado-icon-couleur.jpg'
    x_start  = 20
    for student in group.students.exclude(user__username__contains= "_e-test") :

    # Create the HttpResponse object with the appropriate PDF headers.
        string0 = "Bonjour {} {},".format(student.user.first_name, student.user.last_name) 
        string1 = "allez sur le site https://sacado-academie.fr et cliquez sur le bouton bleu Se connecter." 
        string2 = "Votre identifiant est : {}    . Votre mot de passe est :    sacado2020".format(student.user.username)
        p.setFont("Helvetica", 12)

        p.drawString(75, 900-100*i, string0)
        p.drawString(75, 880-100*i, string1)
        p.drawString(75, 860-100*i, string2)
        p.line(75, 830-100*i,550,830-100*i)
    
        y_start = 860-100*i
        p.drawImage(img_file, x_start, y_start, width=50, preserveAspectRatio=True )

        if i%8 == 0 :
            i = 1
            p.showPage()
        else : 
            i +=1
 
    p.save()
    return response 


def print_ids(request, id):
    group = Group.objects.get(id=id)
    teacher = Teacher.objects.get(user=request.user)
    authorizing_access_group(request,teacher,group ) 
 
    elements = []        
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Etiquette_identifiant_SACADO_'+group.name+'.pdf"'
    doc = SimpleDocTemplate(response,   pagesize=A4, 
                                        topMargin=0.3*inch,
                                        leftMargin=0.3*inch,
                                        rightMargin=0.3*inch,
                                        bottomMargin=0.3*inch     )

    sample_style_sheet = getSampleStyleSheet()

 
    students = group.students.exclude(user__username__contains= "_e-test").order_by("user__last_name")

    p = canvas.Canvas(response)
    i = 1
    img_file = 'https://sacado-academie.fr/static/img/sacado-icon-couleur.jpg'
    x_start  = 20
    for i in range(len(students)//2) :
        y_start = 860-100*i
        p.drawImage(img_file, x_start, y_start, width=50, preserveAspectRatio=True )


    normal = ParagraphStyle(name='Normal',fontSize=12,)    
    style_cell = TableStyle(
            [
                ('SPAN', (0, 1), (1, 1)),
                ('TEXTCOLOR', (0, 1), (-1, -1),  colors.Color(0,0.7,0.7))
            ]
        )

    logo = Image('https://sacado-academie.fr/static/img/sacado_print.jpg')
    logo.drawWidth  = 0.4*inch
    logo.drawHeight = 1.3*inch 
    
 
 
    dataset  = []
    grid = [] 

    for i in range(len(students)//2) :
        liste  =  []
        for student in students[2*i:2*(i+1)]  :
            liste.append(logo) 
            msg = "\n\n{} {},\nun accès à l'interface SACADO,".format(student.user.first_name.capitalize() , student.user.last_name.capitalize())
            msg += "\nsite d'entrainement personnalisé "
            msg += "\nauto-corrigé,vous a été fourni."
            msg += "\nVous pouvez vous connecter sur"
            msg += "\nsacado-academie.fr avec les identifiants suivants :"
            msg += "\n   Id : {} \n   Mot de passe : sacado2020".format(student.user.username)
            liste.append(msg) 
            grid.append( ('BOX', (0,i), (1,i), 0.25, colors.gray, None, (2,2,1)) )
            grid.append( ('BOX', (2,i), (3,i), 0.25, colors.gray, None, (2,2,1))  )


        dataset.append(liste)

    if len(students)%2==1 :
        msg = "\n\n{} {} un accès à l'interface SACADO,".format(students[len(students)-1].user.first_name.capitalize() , students[len(students)-1].user.last_name.capitalize())
        msg += "\nsite d'entrainement personnalisé "
        msg += "\nauto-corrigé,vous a été fourni."
        msg += "\nVous pouvez vous connecter sur"
        msg += "\nsacado-academie.fr avec le code suivant :"
        msg += "\n   Id : {} \n   Mot de passe : sacado2020".format(students[len(students)-1].user.username)          
        dataset.append( (logo,msg) )
        grid.append( ('BOX', (0,i+1), (1,i+1), 0.25, colors.gray, None, (2,2,1)) )
        grid.append( ('BOX', (2,i+1), (3,i+1), 0.25, colors.gray, None, (2,2,1)) )

 
    table = Table(dataset, colWidths=[0.5*inch,2.7*inch,0.5*inch,2.7*inch], rowHeights=110)
    table.setStyle(TableStyle(grid)) 
    elements.append(table)

    doc.build(elements) 

    return response






def print_list_ids(request, id):

    group = Group.objects.get(id=id)
    teacher = Teacher.objects.get(user=request.user)
    authorizing_access_group(request,teacher,group ) 
 
    elements = []        
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Liste_identifiant_SACADO_'+group.name+'.pdf"'
    doc = SimpleDocTemplate(response,   pagesize=A4, 
                                        topMargin=0.3*inch,
                                        leftMargin=0.3*inch,
                                        rightMargin=0.3*inch,
                                        bottomMargin=0.3*inch     )

    sample_style_sheet = getSampleStyleSheet()


    normal = ParagraphStyle(name='Normal',fontSize=12,)    
    style_cell = TableStyle(
            [
                ('SPAN', (0, 1), (1, 1)),
                ('TEXTCOLOR', (0, 1), (-1, -1),  colors.Color(0,0.7,0.7))
            ]
        )

    logo = Image('https://sacado-academie.fr/static/img/sacadoA1.png')
    logo_tab = [[logo, "SACADO \nListes des identifiants par élève" ]]
    logo_tab_tab = Table(logo_tab, hAlign='LEFT', colWidths=[0.7*inch,5*inch])
    logo_tab_tab.setStyle(TableStyle([ ('TEXTCOLOR', (0,0), (-1,0), colors.Color(0,0.5,0.62))]))
    elements.append(logo_tab_tab)
    elements.append(Spacer(0, 0.1*inch))

    paragraph = Paragraph( "Initialement, tous les élèves ont le même mot de passe : sacado2020" , normal )
    elements.append(paragraph)
    elements.append(Spacer(0, 0.1*inch))
    
    dataset  = [(" ", "Nom ","Prénom", "Identifiant")]
 

    i = 1
    for student in group.students.exclude(user__username__contains= "_e-test").order_by("user__last_name") :
        
        dataset.append((i, student.user.last_name.capitalize() , student.user.first_name.capitalize() , student.user.username))
        i +=1

    table = Table(dataset, colWidths=[0.3*inch,2*inch,2*inch,2*inch], rowHeights=20)
    table.setStyle(TableStyle([
    ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
    ('BOX', (0,0), (-1,-1), 0.25, colors.black),
    ('BACKGROUND',(0,0), (3,0),colors.gray),
    ])) 
    elements.append(table)
    doc.build(elements) 
    return response

 

def print_school_ids(request):
    """ Imprime la liste des identifiants par groupe """
    school = request.user.school
    teacher = request.user
 

    if request.user.is_manager  :

        users = school.users.filter(user_type=2)
        groups = Group.objects.filter(teacher__user__in=users).order_by("level__ranking")
 
     
        elements = []        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Liste_identifiant_SACADO_Etablissement.pdf"'
        doc = SimpleDocTemplate(response,   pagesize=A4, 
                                            topMargin=0.3*inch,
                                            leftMargin=0.3*inch,
                                            rightMargin=0.3*inch,
                                            bottomMargin=0.3*inch     )

        sample_style_sheet = getSampleStyleSheet()


        normal = ParagraphStyle(name='Normal',fontSize=12,)    
        style_cell = TableStyle(
                [
                    ('SPAN', (0, 1), (1, 1)),
                    ('TEXTCOLOR', (0, 1), (-1, -1),  colors.Color(0,0.7,0.7))
                ]
            )
 
        for group in groups :
            teacher = Teacher.objects.get(user=request.user)


            logo = Image('https://sacado-academie.fr/static/img/sacadoA1.png')
            logo_tab = [[logo, "SACADO "+group.name+"\nListes de identifiants par élève" ]]
            logo_tab_tab = Table(logo_tab, hAlign='LEFT', colWidths=[0.7*inch,5*inch])
            logo_tab_tab.setStyle(TableStyle([ ('TEXTCOLOR', (0,0), (-1,0), colors.Color(0,0.5,0.62))]))
            elements.append(logo_tab_tab)
            elements.append(Spacer(0, 0.1*inch))

            paragraph = Paragraph( "Initialement, tous les élèves ont le même mot de passe : sacado2020" , normal )
            elements.append(paragraph)
            elements.append(Spacer(0, 0.1*inch))

            dataset  = [(" ", "Nom ","Prénom", "Identifiant")]
         
            i = 1
            for student in group.students.exclude(user__username__contains= "_e-test").order_by("user__last_name") :
                
                dataset.append((i, student.user.last_name.capitalize() , student.user.first_name.capitalize() , student.user.username))
                i +=1

            table = Table(dataset, colWidths=[0.3*inch,2*inch,2*inch,2*inch], rowHeights=20)
            table.setStyle(TableStyle([
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
            ('BOX', (0,0), (-1,-1), 0.25, colors.black),
            ('BACKGROUND',(0,0), (3,0),colors.gray),
            ])) 
            elements.append(table)
            elements.append(PageBreak())

        doc.build(elements) 

        return response
    else :
        messages.error(request,"Vous n'êtes pas autorisé à imprimer les listes d'identifiants.")
        return redirect("school_groups")





def export_skills(request):

    group_id = request.POST.get("group_id")  
    group = Group.objects.get(pk = group_id)  
    nb_skill = int(request.POST.get("nb_skill"))

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename=Skills_group_{}.csv'.format(group_id)
    response.write(u'\ufeff'.encode('utf8'))
    writer = csv.writer(response)
    

    skills = Skill.objects.filter(subject = group.subject)

    label_in_export = ["Nom", "Prénom"]
    for ski in skills :
        if not ski.name in label_in_export : 
            label_in_export.append(ski.name) 

    writer.writerow(label_in_export)

    for student in group.students.exclude(user__username = request.user.username).order_by("user__last_name") :
        skill_level_tab = [str(student.user.last_name).capitalize(),str(student.user.first_name).capitalize()]

        for skill in  skills:
            total_skill = 0

            scs = student.student_correctionskill.filter(skill = skill)
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
            result_skills_ = Resultskill.objects.filter(skill= skill,student=student).order_by("-id")
            result_skills_set.update(set(result_skills_))
            result_skills__ = Resultggbskill.objects.filter(skill= skill,student=student).order_by("-id")
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





def schedule_task_group(request, id):
    
    group = Group.objects.get(id=id)
    teacher =   request.user.teacher
    request.session["group_id"] = group.id   

    relationships = Relationship.objects.filter(parcours__teacher = teacher).exclude(date_limit = None) 

    context = {  'group': group, 'relationships' : relationships , 'teacher' : teacher  }

    return render(request, 'schedule/base_group.html', context )