import html
import random
import re
import csv
import pytz
from datetime import datetime 
from django.utils import timezone
from django.http import HttpResponseRedirect , HttpResponse
from django.shortcuts import  redirect
from school.models import Stage
from django.contrib import messages
from django.contrib.auth.hashers import make_password
  
from operator import attrgetter
from django.core.mail import send_mail
from django.apps import apps
import uuid


def delete_session_key(request,key):
    # supprime la clé key d'une session
    if request.session.has_key(key) :
        del request.session[key]  





def get_strong_username(request ,ln, fn):
    """
    retourne un username plus compliqué
    """
    User = apps.get_model('account', 'User')
    ok = True
    i = 0
    code = str(uuid.uuid4())[:3] 
    name = str(ln).replace(" ","")    
    un = str(name) + str(fn)[0] + "_" +   code 
    while ok:
        if User.objects.filter(username=un).count() == 0:
            ok = False
            is_changed = False 
        else:
            i += 1
            un = un + str(i)
            is_changed = True 
    return un 


def get_username(request ,ln, fn):
    """
    retourne un username
    """
    User = apps.get_model('account', 'User')
    ok = True
    i = 0
    name = str(ln).replace(" ","") 
    un = str(name) + "." + str(fn)[0]+str(uuid.uuid4())[:2] 
    while ok:
        if User.objects.filter(username=un).count() == 0:
            ok = False
            is_changed = False 
        else:
            i += 1
            un = un + str(i)
            is_changed = True 
    return un 



def get_username_manuel(texte):
    """
    retourne un username
    """
    User = apps.get_model('account', 'User')
    ok = True
    i = 0
    un = str(texte)
    is_changed = False 
    while ok:
        if User.objects.filter(username=un).count() == 0:
            ok = False
        else:
            i += 1
            un = un + str(i)
            is_changed = True 
    return un , is_changed




def separate_values(request, line, is_group,simple) :

            
    if ";" in line:
        fields = line.split(";")
    elif "," in line:
        fields = line.split(",")

    if is_group == 0 :
        group_name = str(fields[0])
        level = fields[1]
        i ,j ,k , l = 2, 3, 4 , 5 

    elif is_group == 1 :

        group_name = None
        level = fields[0]
        i ,j ,k , l =  1, 2 , 3 , 4

    elif is_group == 2 :

        group_name = None
        level = None
        i ,j ,k , l =  0, 1 , 2 , 3

    ln = cleanhtml(str(fields[i]).lower().capitalize())
    fn = cleanhtml( str(fields[j]).lower().capitalize())
 
    if request.POST.get("manage_username") == "auto" :
        if simple == 1 :
            username =  get_strong_username(request, ln,fn)
        else :
            username =  get_username(request, ln,fn)
        is_username_changed = False
        try:
            if fields[k] != "":
                email = fields[k]
            else:
                email = ""
        except:
            email = ""
    else :
        username , is_username_changed = get_username_manuel(str(fields[k]))
        try:
            if fields[l] != "":
                email = fields[l]
            else:
                email = ""
        except:
            email = ""

    password = make_password("sacado2020")

    return ln, fn, username , password , email , group_name , level , is_username_changed


 



def convert_seconds_in_time(secondes):
    if secondes : secondes = int(secondes)
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


def student_parcours_studied(student):  
    parces = student.students_to_parcours.all()
    if parces.filter(linked=1,is_publish=1).count() > 0 :
        parcourses = parces
    else :
        parcourses = parces.filter(linked=0)
    return parcourses



def code_couleur(score,teacher):

    try :
        stage = Stage.objects.get(school = teacher.user.school)
        if score < stage.low :
            #return Image('D:/uwamp/www/sacado/static/img/code_red.png')
            return Image('https://sacado.xyz/static/img/code_red.png')
        elif score < stage.medium :
            #return Image('D:/uwamp/www/sacado/static/img/code_orange.png')
            return Image('https://sacado.xyz/static/img/code_orange.png')
        elif score < stage.up :
            #return Image('D:/uwamp/www/sacado/static/img/code_green.png')
            return Image('https://sacado.xyz/static/img/code_green.png')
        else :
            #return Image('D:/uwamp/www/sacado/static/img/code_darkgreen.png')
            return Image('https://sacado.xyz/static/img/code_darkgreen.png')

    except :
        if score < 25 :
            #return Image('D:/uwamp/www/sacado/static/img/code_red.png')
            return Image('https://sacado.xyz/static/img/code_red.png')
        elif score < 50 :
            #return Image('D:/uwamp/www/sacado/static/img/code_orange.png')
            return Image('https://sacado.xyz/static/img/code_orange.png')
        elif score < 75 :
            #return Image('D:/uwamp/www/sacado/static/img/code_green.png')
            return Image('https://sacado.xyz/static/img/code_green.png')
        else :
            #return Image('D:/uwamp/www/sacado/static/img/code_darkgreen.png')
            return Image('https://sacado.xyz/static/img/code_darkgreen.png')




def sending_mail(ob , m , a ,r) :
    try : 
        send_mail(ob, m, a, r)
    except :
        pass


def time_zone_user(user):
    try :
        if user.time_zone :
            time_zome = user.time_zone
            timezone.activate(pytz.timezone(time_zome))
            today = timezone.localtime(timezone.now())
        else:
            today = timezone.now()
    except :
        today = timezone.now()

    return today


 
def attribute_all_documents_to_student(parcourses,student):
    """  assigner les documents et renvoie Vrai ou Faux suivant l'attribution """
    try :
        for p in parcourses:
            p.students.add(student)

            relationships = p.parcours_relationship.all()
            for r in relationships:
                r.students.add(student)

            customexercises = p.parcours_customexercises.all()
            for c in customexercises:
                c.students.add(student)

            courses = p.course.all()
            for course in courses:
                course.students.add(student)

        test = True
    except :
        test = False
    return test



def attribute_all_documents_to_students(parcourses, students ):
    """  assigner les documents   """
    try :
        for p in parcourses:
            p.students.set(students)

            relationships = p.parcours_relationship.all()
            for r in relationships:
                r.students.set(students)

            customexercises = p.parcours_customexercises.all()
            for c in customexercises:
                c.students.set(students)

            courses = p.course.all()
            for course in courses:
                course.students.set(students)

            bibliotexs = p.bibliotexs.all()
            for b in bibliotexs:
                b.students.set(students)

            flashpacks = p.flashpacks.all()
            for f in flashpacks:
                f.students.set(students)

            quizz = p.quizz.all()
            for q in quizz:
                q.students.set(students)

        test = True
    except :
        test = False
    return test

 
# def attribute_all_documents_of_parcours_to_group(group,parcours):
#     """  assigner les documents   """
    
#     students = group.students.all()
#     parcours.students.set(students)
#     relationships = parcours.parcours_relationship.all()
#     for r in relationships:
#         r.students.set(students)

#     customexercises = parcours.parcours_customexercises.all()
#     for c in customexercises:
#         c.students.set(students)

#     courses = parcours.course.all()
#     for course in courses:
#         course.students.set(students)


# def attribute_all_documents_of_folder_to_group(group,folder):
#     """  assigner les documents   """
    
#     students = group.students.all()
#     folder.students.set(students)
#     for parcours in folder.parcours.all() :
#         attribute_all_documents_of_parcours_to_group(group,parcours)


# def attribute_all_documents(group,student):
#     """  assigner les documents   """
#     # Assigne les dossiers et leurs contenus 
#     group.students.add(student)
#     for folder in group.group_folders.all():
#         folder.students.add(student)

#         for parcours in folder.parcours.all():
#             parcours.students.add(student)

#             relationships = parcours.parcours_relationship.all()
#             for r in relationships:
#                 r.students.add(student)

#             customexercises = parcours.parcours_customexercises.all()
#             for c in customexercises:
#                 c.students.add(student)

#             courses = parcours.course.all()
#             for course in courses:
#                 course.students.add(student)

#     # Assigne les parcours et leurs contenus 
#     for parcours in group.group_parcours.filter(folders=None):
#         parcours.students.add(student)

#         relationships = parcours.parcours_relationship.all()
#         for r in relationships:
#             r.students.add(student)

#         customexercises = parcours.parcours_customexercises.all()
#         for c in customexercises:
#             c.students.add(student)

#         courses = parcours.course.all()
#         for course in courses:
#             course.students.add(student)
#     test = True
 
#     return test




def attribute_all_documents_of_groups_to_a_new_student(groups, student):
    """  assigner les documents   """
    # Assigne les dossiers et leurs contenus à aprtir d'un groupe

    for group in groups :
        for folder in group.group_folders.all():
            folder.students.add(student)

            for parcours in folder.parcours.all():
                parcours.students.add(student)

                relationships = parcours.parcours_relationship.all()
                for r in relationships:
                    r.students.add(student)

                customexercises = parcours.parcours_customexercises.all()
                for c in customexercises:
                    c.students.add(student)

                courses = parcours.course.all()
                for course in courses:
                    course.students.add(student)

        # Assigne les parcours et leurs contenus 
        for parcours in group.group_parcours.filter(folders=None):
            parcours.students.add(student)
            relationships = parcours.parcours_relationship.all()
            for r in relationships:
                r.students.add(student)

            customexercises = parcours.parcours_customexercises.all()
            for c in customexercises:
                c.students.add(student)

            courses = parcours.course.all()
            for course in courses:
                course.students.add(student)
    test = True


    return test




def attribute_all_documents_of_groups_to_all_new_students(groups):
    """  assigner les documents   """
    # Assigne les dossiers et leurs contenus à aprtir d'un groupe
    studts = set()
    for group in groups :
        studts.update(group.students.all()) 
    
    students = list(studts)    


    for group in groups :
        for folder in group.group_folders.all():
            folder.students.add(*students)

            for parcours in folder.parcours.all():
                parcours.students.add(*students)

                relationships = parcours.parcours_relationship.all()
                for r in relationships:
                    r.students.add(*students)

                customexercises = parcours.parcours_customexercises.all()
                for c in customexercises:
                    c.students.add(*students)

                courses = parcours.course.all()
                for course in courses:
                    course.students.add(*students)

                bibliotexs = parcours.bibliotexs.all()
                for bibliotex in bibliotexs:
                    bibliotex.students.add(*students)

                flashpacks = parcours.flashpacks.all()
                for flashpack in flashpacks:
                    flashpack.students.add(*students)

                quizz = parcours.quizz.all()
                for quiz in quizz:
                    quiz.students.add(*students)

        # Assigne les parcours et leurs contenus 
        for parcours in group.group_parcours.filter(folders=None):
            parcours.students.add(*students)

            relationships = parcours.parcours_relationship.all()
            for r in relationships:
                r.students.add(*students)

            customexercises = parcours.parcours_customexercises.all()
            for c in customexercises:
                c.students.add(*students)

            courses = parcours.course.all()
            for course in courses:
                course.students.add(*students)


            bibliotexs = parcours.bibliotexs.all()
            for bibliotex in bibliotexs:
                bibliotex.students.add(*students)

            flashpacks = parcours.flashpacks.all()
            for flashpack in flashpacks:
                flashpack.students.add(*students)

            quizz = parcours.quizz.all()
            for quiz in quizz:
                quiz.students.add(*students)


    test = True
 
    return test


















def cleanhtml(raw_html): #nettoie le code des balises HTML
    cleantext = re.sub('<.*?>', '', raw_html)
    cleantext = re.sub('\n', '', cleantext)
    return cleantext

def unescape_html(string):
    '''HTML entity decode'''
    string = html.unescape(string)
    return string


def escape_chevron(string):
    '''HTML entity decode'''
    string = string.replace("<","&lt")
    string = string.replace(">","&gt")  
    return string



def cleantext(raw_html):
    """Renvoie à la ligne pour es paragraphe et les listes"""
    raw_less_p = raw_html.split('<p>')

    for rp in raw_less_p :
        r_less_li = rp.split('<li>')

        for rli in r_less_li :
            r_less_li = re.sub('<.*?>', '', rli)

        rp = re.sub('<.*?>', '', rp)

    return raw_less_p


def dt_naive_to_timezone(naive_date,timezone_user):

    try :
        naive_dt = datetime.combine(naive_date, datetime.min.time())
        tz = pytz.timezone(timezone_user)
        utc_dt = tz.localize(naive_dt, is_dst=None).astimezone(pytz.utc)
    except :
        naive_dt = datetime.combine(naive_date, datetime.min.time())
        tz = pytz.timezone("Europe/Paris")
        utc_dt = tz.localize(naive_dt, is_dst=None).astimezone(pytz.utc)        
    return utc_dt
 


def authorizing_access(teacher ,parcours_or_group, sharing_group): #sharing_group est un booléen

    try : 
        return teacher == parcours_or_group.teacher or  sharing_group 
    except : 
        return False


def authorizing_access_student(student , parcours_or_group): 

    try :
        return student in parcours_or_group.students.all()
    except : 
        return False


def authorizing_access_folder(user , folder): 

    try :
        return  user == folder.teacher or  user in folder.coteachers.all() 
    except : 
        return False

def group_has_parcourses(group,is_evaluation ,is_archive ):
    pses_tab = []

    for s in group.students.all() :
        pses = s.students_to_parcours.filter(is_evaluation=is_evaluation,is_archive=is_archive)
        for p in pses :
            if p not in  pses_tab :
                pses_tab.append(p)
 
    return pses_tab


def get_level_by_point(student, point):
    point = int(point)
    if student.user.school :
        school = student.user.school
        stage = Stage.objects.get(school = school)

        if point > stage.up :
            level = 4
        elif point > stage.medium :
            level = 3
        elif point > stage.low :
            level = 2
        else   :
            level = 1
 
    else : 
        stage = { "low" : 50 ,  "medium" : 70 ,  "up" : 85  }

        if point > stage["up"]  :
            level = 4
        elif point > stage["medium"]  :
            level = 3
        elif point > stage["low"]  :
            level = 2
        else :
            level = 1
    return level


def split_paragraph(paragraph,coupe) :

    name  = ""
    longueur = 0
    words = paragraph.split(" ")
    for word in words:
        if longueur + 1 + len(word) > coupe:
            name += "\n" + word
            longueur = 0
        else:
            name += " " + word
            longueur += len(word)

    return name 



def increment_chrono( obj , pattern , forme , flag  ):
    """ On incrémente le chrono selon le chrono qui arrive """

    if forme :
        chro = forme[0] +"-"+  str(pattern) 

        last_accountings = obj.objects.filter(chrono__contains = chro).order_by("chrono")
        if last_accountings.count() == 0 :
            new = "01"
        else :
            last_accounting = last_accountings.last()
            chrono = last_accounting.chrono.split("-")

            new = int(chrono[3])+1

            if new < 10 :
                new = "0" + str(new)
            else :
                new = str(new)

        ch = chro + "-" + new

    else :
        ch = ""
 
    return ch



def create_chrono(obj,forme):

    today = datetime.now().strftime("%Y-%m")
    this_chrono = increment_chrono( obj , today , forme , False )     
    return this_chrono


def update_chrono(obj, accounting,forme):

    this_chrono = accounting.chrono
    if forme :
        if this_chrono[0] != forme[0] :
            today = datetime.now().strftime("%Y-%m")
            this_chrono = increment_chrono( obj ,   today ,  forme , True )  

    return this_chrono


def this_year_from_today(today) :

    compare_date = datetime(today.year, 7, 31)
    if today > compare_date :
        year = str(today.year) +"-"+str(today.year+1)
    else :
        year = str(today.year-1) +"-"+str(today.year)
    return year
