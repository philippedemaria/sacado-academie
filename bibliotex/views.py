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
from django.http import JsonResponse , FileResponse
from django.core import serializers
from django.template.loader import render_to_string
from django.contrib import messages
from qcm.models import Folder , Parcours , Relationship
from qcm.views import get_teacher_id_by_subject_id, all_levels
from group.models import Group , Sharing_group
from socle.models import  Knowledge , Level , Skill , Waiting , Subject
from bibliotex.models import  Bibliotex , Exotex , Relationtex , Blacklistex
from bibliotex.forms import  BibliotexForm , ExotexForm , RelationtexForm
from django.views.decorators.csrf import csrf_exempt
from tool.consumers import *

import uuid
import time
import math
import json
import random
from datetime import datetime , timedelta
from django.db.models import Q
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
import subprocess


##################################################################################################################################
##################################################################################################################################
##################################################################################################################################
def affectation_students_folders_groups(nf,group_ids,folder_ids):

    all_students = set()
    all_levels, all_subjects = [] , []
    for group_id in group_ids :    
        group = Group.objects.get(pk = group_id)
        group_students = group.students.all()
        all_students.update( group_students )   
        all_levels.append(group.level)
        all_subjects.append(group.subject)

    nf.levels.set(all_levels)
    nf.students.set(all_students) 
    nf.subjects.set(all_subjects) 

    for folder_id in folder_ids:
        folder = Folder.objects.get(pk=folder_id)
        folder.groups.set(group_ids)

    return all_students



def printer(request, relationtex_id, collection,output):
    """affiche un exo ou une collection d'exercices, soit en pdf (output="pdf")
    soit en html (output="html") """

    # ouverture du texte dans le fichier tex

    if output=="pdf" :
        preamb = settings.TEX_PREAMBULE_PDF_FILE

    elif output == "html" or output == "html_cor" :
        preamb = settings.TEX_PREAMBULE_FILE


    entetes=open(preamb,"r")
    elements=entetes.read()
    entetes.close()

    elements +=r"\begin{document}"+"\n"   

    ## Création du texte dans le fichier tex   
    if relationtex_id == 0 : # 0 pour la méthode POST
        if collection : 
            bibliotex_id = request.POST.get("print_bibliotex_id",None)  
            bibliotex    = Bibliotex.objects.get(pk = bibliotex_id)
            document     = "bibliotex" + str(relationtex_id)
            title        = bibliotex.title
            author       = bibliotex.teacher.user.civilite+" "+bibliotex.teacher.user.last_name


        else :
            relationtex_id = request.POST.get("print_exotex_id",None)  
            relationtex    =  Relationtex.objects.get(pk = relationtex_id) 
            document       = "relationtex" + str(relationtex_id)
            title          =  relationtex.exotex.title
            author         = "Équipe SACADO"

        elements +=r"\titreFiche{"+title+r"}{"+author+r"}"


        skills_printer     = request.POST.get("skills",None)  
        knowledges_printer = request.POST.get("knowledges",None)  
      
 

        today = datetime.now()
        if collection : 
            relationtexs = bibliotex.relationtexs.filter(Q( is_publish = 1 )|Q(start__lte=today , stop__gte= today)).order_by("ranking")
            i = 1
        else: relationtexs=[relationtex]

        j = 1
        for relationtex in relationtexs :
        
            skills_display = ""
            if skills_printer :   
                if relationtex.skills.count():
                    sks =  relationtex.skills.all()
                else :
                    sks =  relationtex.exotex.skills.all()
                for s in sks :
                    skills_display +=  s.name+". "
                

            elements += r"\exo {\bf " +  relationtex.exotex.title  +  r" }    \competence{" +skills_display+r"}"
            
            j+=1

            if knowledges_printer :  
                k_display = relationtex.exotex.knowledge.name
                elements += r"\savoirs{  \item " +  k_display 


                if relationtex.knowledges.count()          : kws =  relationtex.knowledges.all()
                elif  relationtex.exotex.knowledges.count(): kws =  relationtex.exotex.knowledges.all()
                else : kws = []
                
                for k in kws : 
                    elements += r" \item " +  k.name  

                elements += r"}"

            if output == "html" or output== "html_cor" :
                if  relationtex.correction : ctnt =  relationtex.correction
                else                       : ctnt =  relationtex.exotex.correction
            else :
                if  relationtex.content : ctnt =  relationtex.content
                else                    : ctnt =  relationtex.exotex.content


            elements += ctnt
            elements += r"\vspace{0,4cm}\\"
    else : #pour la création d'un exercise ou son update*

        try :
            relationtex = Relationtex.objects.get(pk = relationtex_id)
            title       =  relationtex.exotex.title
             
            if output== "html_cor" :
                if  relationtex.correction : ctnt =  relationtex.correction
                else                       : ctnt =  relationtex.exotex.correction
            else :
                ctnt =  relationtex.exotex.content 
 
        except :
            exotex         = Exotex.objects.get(pk = relationtex_id)
            title          =  exotex.title
            if output== "html_cor" :
                ctnt =  exotex.correction
            else : 
                ctnt =  exotex.content



        document       = "relationtex" + str(relationtex_id)
        author         = "Équipe SACADO"

        elements += ctnt
        elements += r"\vspace{0,4cm}"
    # Fermeture du texte dans le fichier tex
    elements +=  r"\end{document}"

    elements +=  settings.DIR_TMP_TEX    

    ################################################################# 
    ################################################################# Attention ERREUR si non modif
    # pour windows
    #file = settings.DIR_TMP_TEX+r"\\"+document
    # pour le serveur Linux
    file = settings.DIR_TMP_TEX+"/"+document
    ################################################################# 
    ################################################################# 

    f_tex = open(file+".tex","w")
    f_tex.write(elements)
    f_tex.close()


    if output=="pdf" :
        result = subprocess.run(["pdflatex", "-interaction","nonstopmode",  "-output-directory", settings.DIR_TMP_TEX ,  file ])
        return FileResponse(open(file+".pdf", 'rb'),  as_attachment=True, content_type='application/pdf')

    elif output == "html" or output== "html_cor" :
        #result = subprocess.run(["make4ht" ,  "-u" ,  file+".tex" , "mathml"] , cwd = settings.DIR_TMP_TEX )
        os.chdir(settings.DIR_TMP_TEX)
        os.system("make4ht -u "+document+".tex mathml")
        fhtml  = open(file+".html","r", errors='ignore')
        out    = ""
        recopie=False
        i=0
        for ligne in fhtml :
            ligne = ligne.replace('src="','src="https://sacado-academie.fr/ressources/tex/tmp_tex/')
            if "</body>" in ligne : recopie=False
            if recopie : out+=ligne
            if i  ==  9 : recopie=True
            i+=1
        return out


    else : 
        print("format output non reconnu")
        return 




def printer_bibliotex_by_student(bibliotex):
    """affiche un exo ou une collection d'exercices, en pdf (output="pdf") """

    # ouverture du texte dans le fichier tex

    preamb = settings.TEX_PREAMBULE_PDF_FILE

    entetes=open(preamb,"r")
    elements=entetes.read()
    entetes.close()

    elements +=r"\begin{document}"+"\n"   

    ## Création du texte dans le fichier tex   

 
    document     = "bibliotex" + str(bibliotex.id)
    title        = bibliotex.title
    author       = bibliotex.teacher.user.civilite+" "+bibliotex.teacher.user.last_name

    elements +=r"\titreFiche{"+title+r"}{"+author+r"}"

    today = datetime.now()
 
    relationtexs = bibliotex.relationtexs.filter(Q( is_publish = 1 )|Q(start__lte=today , stop__gte= today)).order_by("ranking")
 

    j = 1
    for relationtex in relationtexs :
    
        skills_display = ""
        if relationtex.skills.count():
            sks =  relationtex.skills.all()
        else :
            sks =  relationtex.exotex.skills.all()
        for s in sks :
            skills_display +=  s.name+". "
            

        elements += r"\exo {\bf " +  relationtex.exotex.title  +  r" }    \competence{" +skills_display+r"}"
        
        j+=1

  
        k_display = relationtex.exotex.knowledge.name
        elements += r"\savoirs{  \item " +  k_display 


        if relationtex.knowledges.count()          : kws =  relationtex.knowledges.all()
        elif  relationtex.exotex.knowledges.count(): kws =  relationtex.exotex.knowledges.all()
        else : kws = []
        
        for k in kws : 
            elements += r" \item " +  k.name  

        elements += r"}"

 
 
        if  relationtex.content : ctnt =  relationtex.content
        else                    : ctnt =  relationtex.exotex.content

        elements += r"\vspace{0,2cm}\\"
        elements += ctnt
        elements += r"\vspace{0,4cm}\\"




 
    # Fermeture du texte dans le fichier tex
    elements +=  r"\end{document}"

    elements +=  settings.DIR_TMP_TEX    

    ################################################################# 
    ################################################################# Attention ERREUR si non modif
    # pour windows
    #file = settings.DIR_TMP_TEX+r"\\"+document
    # pour le serveur Linux
    file = settings.DIR_TMP_TEX+"/"+document
    ################################################################# 
    ################################################################# 
    f_tex = open(file+".tex","w")
    f_tex.write(elements)
    f_tex.close()
    result = subprocess.run(["pdflatex", "-interaction","nonstopmode",  "-output-directory", settings.DIR_TMP_TEX ,  file ])
    return FileResponse(open(file+".pdf", 'rb'),  as_attachment=True, content_type='application/pdf')

 


#########################################################################################################################################
#########################################################################################################################################
######## Exotex
#########################################################################################################################################
#########################################################################################################################################

def admin_exotexs(request,idl):

    if request.user.is_superuser or request.user.is_extra :  # admin and more
        teacher = request.user.teacher
        level = Level.objects.get(pk=idl)
        exos = Exotex.objects.all()
        waitings = level.waitings.filter(theme__subject__in= teacher.subjects.all()).order_by("theme__subject" , "theme")

    return render(request, 'bibliotex/list_exotexs.html', { 'waitings': waitings, 'teacher':teacher , 'level':level   })


 
def my_exotexs(request):

    teacher = request.user.teacher 
    exos = Exotex.objects.filter( Q(author=teacher)|Q(teachers=teacher) )
    return render(request, 'bibliotex/list_exotexs.html', {'exos': exos,  })



@user_passes_test(user_is_creator)
def create_exotex_knowledge(request,idk):

    knowledge = Knowledge.objects.get(id = idk)
    teacher = request.user.teacher
    form = ExotexForm(request.POST or None,request.FILES or None, teacher = teacher , knowledge = knowledge , initial={'author':teacher,'teachers':teacher,'knowledge':knowledge} )

    if form.is_valid():
        nf = form.save(commit = False) 
        nf.author = teacher
        nf.teacher = teacher
        nf.save()

        save_html = True
        try :
            Exotex.objects.filter(pk= nf.id).update( content_html = printer(request, nf.id, False , "html" )   )
            if nf.correction :
                Exotex.objects.filter(pk= nf.id).update( correction_html = printer(request, nf.id, False , "html_cor" )   )
        except :
            save_html = False

        form.save_m2m()

        if save_html :
            messages.success(request, "L'exercice a été créé avec succès !")
        else :
            messages.error(request,"Le contenu html ne s'est pas enregistré. Modifier l'exercice et changer l'encodage.")

        return redirect('admin_exotexs', knowledge.level.id)
    else:
        print(form.errors)

    context = {'form': form, 'knowledge': knowledge , 'exotex': None }

    return render(request, 'bibliotex/form_exotex.html', context)



def set_exotex_in_bibliotex(request,id):

    bibliotex = Bibliotex.objects.get(id=id)
    teacher = request.user.teacher
    form = ExotexForm(request.POST or None,request.FILES or None, teacher = teacher , knowledge = None )

    if form.is_valid():
        nf = form.save(commit = False) 
        nf.author = teacher
        nf.teacher = teacher
        nf.is_share = 1
        knowledges = request.POST.getlist("knowledge")
        nf.knowledge = Knowledge.objects.get(pk = knowledges[0])
        try :
            nf.knowledges.set(knowledges[1::])
        except :
            pass

        nf.save()

        save_html = True
        try :
            Exotex.objects.filter(pk= nf.id).update( content_html = printer(request, nf.id, False , "html" )   )
            if nf.correction :
                Exotex.objects.filter(pk= nf.id).update( correction_html = printer(request, nf.id, False , "html_cor" )   )
        except :
            save_html = False

        bibliotex.exotexs.add(nf)
        form.save_m2m()  
        if save_html :
            messages.success(request, "L'exercice a été créé avec succès !")
        else :
            messages.error(request,"Le contenu html ne s'est pas enregistré. Modifier l'exercice et changer l'encodage.")


        return redirect('my_bibliotexs')
    else:
        print(form.errors)

    context = {'form': form, 'exotex': "init"  }

    return render(request, 'bibliotex/form_exotex.html', context)


 
def create_exotex(request):

    teacher = request.user.teacher
    form = ExotexForm(request.POST or None,request.FILES or None, teacher = teacher , knowledge = None )

    if form.is_valid():
        nf = form.save(commit = False) 
        nf.author = teacher
        nf.teacher = teacher
        nf.is_share = 1
        nf.save()

        save_html = True
        try :
            Exotex.objects.filter(pk= nf.id).update( content_html = printer(request, nf.id, False , "html" )   )
            if nf.correction :
                Exotex.objects.filter(pk= nf.id).update( correction_html = printer(request, nf.id, False , "html_cor" )   )
        except :
            save_html = False

        form.save_m2m()  

        if save_html :
            messages.success(request, "L'exercice a été créé avec succès !")
        else :
            messages.error(request,"Le contenu html ne s'est pas enregistré. Modifier l'exercice et changer l'encodage.")

        return redirect('admin_exotexs', nf.knowledge.level.id)
    else:
        print(form.errors)

    context = {'form': form, 'exotex': None  }

    return render(request, 'bibliotex/form_exotex.html', context)


 
def update_exotex(request, id):

    exotex = Exotex.objects.get(id=id)
    teacher = request.user.teacher
    form = ExotexForm(request.POST or None, request.FILES or None, instance=exotex , teacher = teacher , knowledge = exotex.knowledge )
    if request.method == "POST" :
        if form.is_valid():
            nf = form.save(commit = False) 
            nf.author = teacher
            nf.teacher = teacher
            nf.save()
            form.save_m2m()  

            save_html = True
            try :
                Exotex.objects.filter(pk= nf.id).update( content_html = printer(request, nf.id, False , "html" )   )
                if nf.correction :
                    Exotex.objects.filter(pk= nf.id).update( correction_html = printer(request, nf.id, False , "html_cor" )   )
            except :
                save_html = False


            if save_html :
                messages.success(request, "L'exercice a été créé avec succès !")
            else :
                messages.error(request,"Le contenu html ne s'est pas enregistré. Modifier l'exercice et changer l'encodage.")
            
            return redirect('admin_exotexs', exotex.knowledge.level.id)
        else:
            print(form.errors)

    context = {'form': form,  'exotex': exotex, 'knowledge': exotex.knowledge ,   }

    return render(request, 'bibliotex/form_exotex.html', context )


 
def delete_exotex(request, id):
    exotex = Exotex.objects.get(id=id)
    level_id = exotex.knowledge.level.id
    if request.user == exotex.author.user :
        exotex.delete()

    return redirect('admin_exotexs', level_id)


 

def ajax_action_exotex(request, id):
    pass
 



 
def update_relationtex(request, id):

    relationtex = Relationtex.objects.get(id=id)
    bibliotex_id = relationtex.bibliotex.id

    if relationtex.content : content = relationtex.content
    else : content = relationtex.exotex.content

    if relationtex.correction : correction = relationtex.correction
    else : correction = relationtex.exotex.correction

    teacher = request.user.teacher
    form = RelationtexForm(request.POST or None, request.FILES or None, instance = relationtex , teacher = teacher , initial = { 'content' : content , 'correction' : correction } )
    if request.method == "POST" :
        if form.is_valid():
            nf = form.save(commit = False) 
            nf.teacher = teacher
            nf.save()
            form.save_m2m()  

            Relationtex.objects.filter(pk= nf.id).update( content_html = printer(request, nf.id, False , "html" )   )
            if nf.correction :  
                Relationtex.objects.filter(pk= nf.id).update( correction_html = printer(request, nf.id, False , "html_cor" )   )

            messages.success(request, "L'exercice a été modifié avec succès !")
            return redirect('show_bibliotex', bibliotex_id )
        else:
            print(form.errors)

    context = {'form': form,  'relationtex': relationtex,   }

    return render(request, 'bibliotex/form_relationtex.html', context )


def delete_relationtex(request, id):
    relationtex  = Relationtex.objects.get(id=id)
    bibliotex_id = relationtex.bibliotex.id
 
    if request.user == relationtex.teacher.user :
        relationtex.delete()

    return redirect('show_bibliotex', bibliotex_id)



#########################################################################################################################################
#########################################################################################################################################
######## Bibliotex
#########################################################################################################################################
#########################################################################################################################################
def bibliotexs(request):
 
    bibliotexs = Bibliotex.objects.all()
    teacher = request.user.teacher
    return render(request, 'bibliotex/all_bibliotexs.html', {'bibliotexs': bibliotexs,'teacher': teacher,   })


 
def my_bibliotexs(request):

    request.session["folder_id"] = None
    request.session["group_id"] = None
    teacher = request.user.teacher

    dataset_user = teacher.teacher_bibliotexs
    dataset      = dataset_user.filter(is_archive=0)

    bibliotexs = dataset.filter(folders=None)
    bibliotexs_folders = dataset.values_list("folders", flat=True).exclude(folders=None).distinct().order_by("folders")


    request.session["tdb"] = False # permet l'activation du surlignage de l'icone dans le menu gauche

    list_folders = list()
    for folder in bibliotexs_folders :
        bibtexs_folders = dict()
        bibtexs_folders["folder"] = Folder.objects.get(pk=folder)
        teacher_bibliotexs = dataset.filter(folders=folder)
        bibtexs_folders["bibliotexs"] = teacher_bibliotexs  
        list_folders.append(bibtexs_folders)

    groups = teacher.has_groups() # pour ouvrir le choix de la fenetre modale pop-up
 
    request.session["tdb"] = False # permet l'activation du surlignage de l'icone dans le menu gauche
 
    nb_archive = dataset_user.filter(  is_archive=1).count()
    return render(request, 'bibliotex/list_bibliotexs.html', { 'list_folders': list_folders , 'bibliotexs': bibliotexs , 'teacher': teacher,  'groups': groups,   'nb_archive' : nb_archive  })



def my_bibliotex_archives(request):

    request.session["folder_id"] = None
    request.session["group_id"] = None
    teacher = request.user.teacher
 
    dataset = teacher.teacher_bibliotexs.filter(is_archive=1)

    bibliotexs = dataset.filter(folders=None)
    bibliotexs_folders = dataset.values_list("folders", flat=True).exclude(folders=None).distinct().order_by("folders")


    request.session["tdb"] = False # permet l'activation du surlignage de l'icone dans le menu gauche

 
    list_folders = list()
    for folder in bibliotexs_folders :
        bibtexs_folders = dict()
        bibtexs_folders["folder"] = Folder.objects.get(pk=folder)
        teacher_bibliotexs = dataset.filter(folders=folder)
        bibtexs_folders["bibliotexs"] = teacher_bibliotexs  
        list_folders.append(bibtexs_folders)

    groups = teacher.has_groups() # pour ouvrir le choix de la fenetre modale pop-up
 
    request.session["tdb"] = False # permet l'activation du surlignage de l'icone dans le menu gauche
 
    return render(request, 'bibliotex/list_bibliotexs_archives.html', { 'list_folders': list_folders , 'bibliotexs': bibliotexs , 'teacher': teacher,  'groups': groups  })



def ajax_my_bibliotexs(request):

    level_id = request.POST.get("level_id")
    subject_id = request.POST.get("subject_id")

    teacher = request.user.teacher 
    data = {}
    level =  Level.objects.get(pk = level_id)
    subject =  Subject.objects.get(pk = subject_id)
    bibliotexs = Bibliotex.objects.filter( Q(author=teacher)|Q(teacher=teacher)|Q(coteachers=teacher)  ,  subjects = subject   ,  levels = level ).distinct()

    data['html'] = render_to_string('bibliotex/ajax_list_bibliotexs.html', {'bibliotexs' : bibliotexs , })

    return JsonResponse(data)



def create_bibliotex_sequence(request,id):

    teacher = request.user.teacher
    folder_id = request.session.get("folder_id",None)
    group_id = request.session.get("group_id",None)
    if group_id :group = Group.objects.get(id=group_id)
    else : group = None
    if folder_id : folder = Folder.objects.get(id=folder_id)
    else : folder = None

    parcours = Parcours.objects.get(id=id)

    form = BibliotexForm(request.POST or None,request.FILES or None, teacher = teacher, folder = folder,  group = group, initial = { 'folders'  : [folder] ,  'groups'  : [group] ,  'parcours'  : [parcours]  } )

    if form.is_valid():
        nf = form.save(commit = False) 
        nf.author = teacher
        nf.teacher = teacher
        nf.save()
        form.save_m2m() 

        group_ids = request.POST.getlist("groups",[])
        folder_ids = request.POST.getlist("folders",[])
        nf.groups.set(group_ids)
        nf.folders.set(folder_ids)
        all_students = affectation_students_folders_groups(nf,group_ids,folder_ids)

        relation = Relationship.objects.create(parcours = parcours , exercise_id = None , document_id = nf.id  , type_id = 5 , ranking =  200 , is_publish= 1 , start= None , date_limit= None, duration= 10, situation= 0 ) 
        students = parcours.students.all()
        relation.students.set(students)


        return redirect('exercise_bibliotex_peuplate', nf.id)

    else:
        print(form.errors)

    context = {'form': form, 'bibliotex': None, 'folder': folder, 'group': group, 'parcours': parcours  }

    return render(request, 'bibliotex/form_bibliotex.html', context)





def ajax_find_peuplate_sequence(request):

    id_parcours = request.POST.get("id_parcours",0)
    subject_id  = request.POST.get("id_subject",0) 
    level_id    = request.POST.get("id_level",None) 
    keyword     = request.POST.get("keyword",None) 

    level       = Level.objects.get(pk=level_id)
    subject     = Subject.objects.get(pk=subject_id)

    if keyword :
        bibliotexs  = Bibliotex.objects.filter( title__icontains=keyword,    teacher__user__school = request.user.school , subjects=subject,levels=level )
    else :
        bibliotexs  = Bibliotex.objects.filter(teacher__user__school = request.user.school , subjects=subject,levels=level )
 

    if keyword and level_id :
        level = Level.objects.get(pk=level_id)
        bibliotexs  = Bibliotex.objects.filter( title__icontains=keyword, teacher__user__school = request.user.school , subjects=subject,levels=level  )
    elif keyword :
        bibliotexs  = Bibliotex.objects.filter( title__icontains=keyword, teacher__user__school = request.user.school , subjects=subject  )
    else :
        level = Level.objects.get(pk=level_id)
        bibliotexs  = Bibliotex.objects.filter(teacher__user__school = request.user.school , subjects=subject ,levels=level )



    context = { "bibliotexs" : bibliotexs }

    data = {}
    data['html']    = render_to_string( 'bibliotex/ajax_bibliotex_peuplate_sequence.html' , context)

    return JsonResponse(data)  



def clone_bibliotex_sequence(request, idb):
    """ cloner un parcours """

    teacher = request.user.teacher
    bibliotex = Bibliotex.objects.get(pk=idb) # parcours à cloner.pk = None
    relationtexs = bibliotex.relationtexs.all()
    bibliotex.pk = None
    bibliotex.teacher = teacher
    bibliotex.save()

    parcours_id = request.session.get("parcours_id",None) 
    if parcours_id :
        parcours = Parcours.objects.get(pk = parcours_id)
        relation = Relationship.objects.create(parcours = parcours , exercise_id = None , document_id = bibliotex.id  , type_id = 5 , ranking =  200 , is_publish= 1 , start= None , date_limit= None, duration= 10, situation= 0 ) 
        students = parcours.students.all()
        relation.students.set(students) 
                
    for r in relationtexs :
        r.pk = None
        r.teacher = teacher
        r.save()
        
        if parcours_id :
            r.students.set(students)



    return redirect('show_parcours' , 0, parcours_id )






 

def ajax_search_bibliotex(request):

    teacher = request.user.teacher
    data = {}

    level_id = request.POST.get('level_id',0)
    subject_id = request.POST.get('subject_id',None)

    teacher_id = get_teacher_id_by_subject_id(subject_id)

    if request.user.is_superuser :
        bibliotexs_ids = Bibliotex.objects.values_list("id",flat=True).distinct().filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id),is_share = 1).order_by('level','ranking')
    else :
        bibliotexs_ids = Bibliotex.objects.values_list("id",flat=True).distinct().filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id),is_share = 1).exclude(exotexs = None ,teacher=teacher).order_by('level','ranking')

    keywords = request.POST.get('keywords',None)

    if int(level_id) > 0 :
        level = Level.objects.get(pk=int(level_id))
        theme_ids = request.POST.getlist('theme_id',[])

        if len(theme_ids) > 0 :

            if theme_ids[0] != '' :

                print(theme_ids)

                if keywords :
                    bibliotexs = Bibliotex.objects.filter( Q(teacher__user_id=teacher_id)|Q(exotexs__content__icontains = keywords) |Q(teacher__user__first_name__icontains = keywords) |Q(teacher__user__last_name__icontains = keywords)  ,is_share = 1, 
                                                        exotexs__knowledge__theme__in = theme_ids,  teacher__user__school = teacher.user.school,  levels = level ).exclude(teacher=teacher).order_by('teacher').distinct() 
                else :
                    bibliotexs = Bibliotex.objects.filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id),is_share = 1, 
                                                            exotexs__knowledge__theme_id__in = theme_ids, levels = level ).exclude(teacher=teacher).order_by('teacher').distinct()
         
            else :
                if keywords :            
                    bibliotexs = Bibliotex.objects.filter(Q(teacher__user_id=teacher_id)|Q(teacher__user__first_name__icontains= keywords) |Q(teacher__user__last_name__icontains = keywords)   |Q(exotexs__content__icontains = keywords),is_share = 1,  
                                                            teacher__user__school = teacher.user.school ,  levels = level  ).exclude(teacher=teacher).order_by('teacher').distinct() 

                else :
                    bibliotexs = Bibliotex.objects.filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id),is_share = 1, 
                                                            levels = level ).exclude(teacher=teacher).order_by('teacher').distinct() 

        else :
            if keywords:
                bibliotexs = Bibliotex.objects.filter( Q(teacher__user_id=teacher_id)|Q(teacher__user__first_name__icontains = keywords) |Q(teacher__user__last_name__icontains = keywords)  |Q(exotexs__content__icontains = keywords),teacher__user__school = teacher.user.school,is_share = 1,
                                                        levels = level ).exclude(teacher=teacher).order_by('teacher').distinct() 
            else :
                bibliotexs = Bibliotex.objects.filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id),is_share = 1, 
                                                        levels = level ).exclude(teacher=teacher).order_by('teacher').distinct() 
    else :
        if keywords:
            bibliotexs = Bibliotex.objects.filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id)|Q(teacher__user__first_name__icontains = keywords) |Q(teacher__user__last_name__icontains = keywords)  , is_share = 1 ,  exotexs__content__icontains = keywords ).exclude(teacher=teacher).order_by('author','ranking').distinct()
        else :
            bibliotexs = Bibliotex.objects.filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id),is_share = 1 ).exclude(teacher=teacher).order_by('teacher').distinct()

    data['html'] = render_to_string('bibliotex/ajax_list_bibliotexs.html', {'bibliotexs' : bibliotexs, 'teacher' : teacher ,  })
 
    return JsonResponse(data)


 

def create_bibliotex(request,idf=0):


    teacher = request.user.teacher
    folder_id = request.session.get("folder_id",idf)
    group_id = request.session.get("group_id",None)
    if group_id :
        group = Group.objects.get(id=group_id)
    else :
        group = None

    if folder_id :
        folder = Folder.objects.get(id=folder_id)
    else :
        folder = None

    form = BibliotexForm(request.POST or None,request.FILES or None, teacher = teacher, folder = folder, group = group,  initial = { 'folders'  : [folder] ,  'groups'  : [group] } )

    if form.is_valid():
        nf = form.save(commit = False) 
        nf.author = teacher
        nf.teacher = teacher
        nf.save()
        form.save_m2m() 

        group_ids = request.POST.getlist("groups",[])
        folder_ids = request.POST.getlist("folders",[])
        nf.groups.set(group_ids)
        nf.folders.set(folder_ids)
        all_students = affectation_students_folders_groups(nf,group_ids,folder_ids)

        return redirect('exercise_bibliotex_peuplate', nf.id)

    else:
        print(form.errors)

    context = {'form': form, 'bibliotex': None, 'folder': folder, 'group': group  }

    return render(request, 'bibliotex/form_bibliotex.html', context)




def update_bibliotex(request, id):

    teacher = request.user.teacher
    bibliotex = Bibliotex.objects.get(id=id)
    folder_id = request.session.get("folder_id",None)
    group_id = request.session.get("group_id",None)
    if group_id :
        group = Group.objects.get(id=group_id)
    else :
        group = None

    if folder_id :
        folder = Folder.objects.get(id=folder_id)
    else :
        folder = None


    form = BibliotexForm(request.POST or None, request.FILES or None, instance=bibliotex, teacher = teacher , folder = folder, group = group,  )

    if form.is_valid():
        nf = form.save(commit = False) 
        nf.author = teacher
        nf.teacher = teacher
        nf.save()
        form.save_m2m() 

        group_ids = request.POST.getlist("groups",[])
        folder_ids = request.POST.getlist("folders",[])
        nf.groups.set(group_ids)
        nf.folders.set(folder_ids)
        all_students = affectation_students_folders_groups(nf,group_ids,folder_ids)

        return redirect('exercise_bibliotex_peuplate', nf.id)

    else:
        print(form.errors)

    context = {'form': form, 'bibliotex': bibliotex,   }

    return render(request, 'bibliotex/form_bibliotex.html', context)



 


def create_bibliotex_from_parcours(request,idp=0):


    teacher = request.user.teacher
    folder_id = request.session.get("folder_id",None)
    group_id = request.session.get("group_id",None)
    if group_id :group = Group.objects.get(id=group_id)
    else : group = None
    if folder_id : folder = Folder.objects.get(id=folder_id)
    else : folder = None

    parcours = Parcours.objects.get(id=idp)

    form = BibliotexForm(request.POST or None,request.FILES or None, teacher = teacher, folder = folder,  group = group, initial = { 'folders'  : [folder] ,  'groups'  : [group] ,  'parcours'  : [parcours]  } )

    if form.is_valid():
        nf = form.save(commit = False) 
        nf.author = teacher
        nf.teacher = teacher
        nf.save()
        form.save_m2m() 

        group_ids = request.POST.getlist("groups",[])
        folder_ids = request.POST.getlist("folders",[])
        nf.groups.set(group_ids)
        nf.folders.set(folder_ids)
        all_students = affectation_students_folders_groups(nf,group_ids,folder_ids)

        return redirect('exercise_bibliotex_peuplate', nf.id)

    else:
        print(form.errors)

    context = {'form': form, 'bibliotex': None, 'folder': folder, 'group': group, 'parcours': parcours  }

    return render(request, 'bibliotex/form_bibliotex.html', context)








def peuplate_bibliotex_parcours(request,idp):

    teacher = request.user.teacher
    parcours = Parcours.objects.get(id=idp)
    bibliotexs = Bibliotex.objects.filter(parcours=parcours)


    context = {'parcours': parcours, 'teacher': teacher , 'bibliotexs' : bibliotexs , 'type_of_document' : 5 }

    return render(request, 'bibliotex/form_peuplate_bibliotex_parcours.html', context)











def delete_bibliotex(request, id):
    bibliotex = Bibliotex.objects.get(id=id)
    if request.user == bibliotex.author.user :
        bibliotex.delete()

    return redirect('bibliotexs')



def show_bibliotex(request, id):

    bibliotex = Bibliotex.objects.get(id=id)
    relationtexs = Relationtex.objects.filter(bibliotex_id=id).order_by("ranking")

    context = { 'bibliotex': bibliotex, 'relationtexs': relationtexs, }

    return render(request, 'bibliotex/show_bibliotex.html', context )




def actioner(request):

    teacher = request.user.teacher 
    idbs = request.POST.getlist("selected_bibliotexs")
    if  request.POST.get("action") == "deleter" :  
        for idb in idbs :
            bibliotex = Bibliotex.objects.get(id=idb) 
            bibliotex.coteachers.clear()
            bibliotex.folders.clear()
            bibliotex.groups.clear()
            bibliotex.parcours.clear()
            bibliotex.exotexs.clear()
            bibliotex.students.clear()
            bibliotex.levels.clear()
            bibliotex.subjects.clear() 
            bibliotex.delete()

    elif  request.POST.get("action") == "archiver" :  
        for idb in idbs :
            bibliotex = Bibliotex.objects.get(id=idb) 
            bibliotex.is_archive = 1
            bibliotex.is_favorite = 0
            bibliotex.save()

 
  
    else : 
        for idb in idbs :
            bibliotex = Bibliotex.objects.get(id=idb) 
            bibliotex.is_archive = 0
            bibliotex.is_favorite = 0
            bibliotex.save()
     
    return redirect('my_bibliotexs')



def ajax_publish_bibliotex(request):

    data = {} 
    bibliotex_id = request.POST.get('bibliotex_id', None)
    statut = request.POST.get("statut")


    if statut == "True":
        data["statut"] = "False"
        data["publish"] = " n'est pas "
        data["class"] = "legend-btn-danger"
        data["noclass"] = "legend-btn-success"
        data["legendclass"] = "text-danger"
        data["nolegendclass"] = "text-success"
        data["color"] = "background-color:#dd4b39"
        data["removedisc"] = "disc"
        data["adddisc"] = "disc_persistant"
        data["noget"] = ""
        data["get"] = "noget"
        status = 0

    else:
        data["statut"] = "True"
        data["publish"] = "est"
        data["class"] = "legend-btn-success"
        data["noclass"] = "legend-btn-danger"
        data["legendclass"] = "text-success"        
        data["nolegendclass"] = "text-danger"
        data["color"] = "background-color:#00a65a"
        data["removedisc"] = "disc_persistant"
        data["adddisc"] = "disc"
        data["get"] = "get"
        data["noget"] = ""
        status = 1
   
    Bibliotex.objects.filter(pk = int(bibliotex_id)).update(is_publish = status)    
    return JsonResponse(data) 




def exercise_bibliotex_results(request, id):

    bibliotex    = Bibliotex.objects.get(id=id)
    relationtexs = Relationtex.objects.filter(bibliotex_id=id)
    students     = bibliotex.students.exclude(user__username__contains="_e-test").order_by('user__last_name')
 
    context = { 'bibliotex': bibliotex, 'relationtexs': relationtexs, 'students' : students  }

    return render(request, 'bibliotex/bibliotex_results.html', context )




def exercise_bibliotex_peuplate(request, id):

    teacher   = request.user.teacher
    bibliotex = Bibliotex.objects.get(id=id)
    skills    = Skill.objects.filter(subject__in=teacher.subjects.all())
    relationtexs = bibliotex.relationtexs.order_by("ranking")

 
    context   = { 'bibliotex': bibliotex, 'relationtexs': relationtexs , 'teacher': teacher, 'skills' : skills  }

    return render(request, 'bibliotex/form_peuplate_bibliotex.html', context )
 
 

def  exercise_bibliotex_individualise(request, id):

    teacher   = request.user.teacher
    bibliotex = Bibliotex.objects.get(id=id)

    context   = { 'bibliotex': bibliotex,    'group':None }

    return render(request, 'bibliotex/form_individualise_bibliotex.html', context )
 


def real_time_bibliotex(request, id):
    pass
 


def  ajax_chargethemes(request):
    level_id =  request.POST.get("id_level")
    id_subject =  request.POST.get("id_subject")
    teacher = request.user.teacher

    teacher_id = get_teacher_id_by_subject_id(id_subject)

    data = {}
    level =  Level.objects.get(pk = level_id)

    thms = level.themes.values_list('id', 'name').filter(subject_id=id_subject).order_by("name")
    data['themes'] = list(thms)
    exotexs = Exotex.objects.filter(Q(author__user__school = teacher.user.school)| Q(author__user_id=teacher_id),  level_id = level_id ).order_by('author').distinct()

    data['html'] = render_to_string('qcm/ajax_list_parcours.html', {'exotexs' : exotexs , })

    return JsonResponse(data)



def ajax_level_exotex(request):

    data = {} 
 
    theme_ids    = request.POST.getlist('theme_id', None)
    level_id     = request.POST.get("level_id",None)
    subject_id   = request.POST.get("subject_id",None)
    skill_id     = request.POST.get("skill_id",None)
    keyword      = request.POST.get("keyword",None)
    bibliotex_id = request.POST.get("bibliotex_id",None)
    is_annale    = request.POST.get("is_annale",None)

    teacher = request.user.teacher 

    if int(level_id) > 0 and subject_id :
        level = Level.objects.get(pk=int(level_id))
        subject = Subject.objects.get(pk=int(subject_id))
        thms  = level.themes.values_list('id', 'name').filter(subject_id=subject_id).order_by("name")
        data['themes'] = list(thms) 


    if bibliotex_id :

        bibliotex = Bibliotex.objects.get(pk=bibliotex_id)
        teacher = request.user.teacher 
 
        data['knowledges']       =  None
        data['knowledges_level'] =  None

        base = Exotex.objects.filter(theme__subject_id = subject_id).exclude(bibliotexs=bibliotex)
        if is_annale == 'yes' : 
            base = base.filter(is_annals=1)


        if level_id  : 
            base = base.filter( level_id = level_id).order_by("theme","knowledge__waiting","knowledge","ranking")
        
        if skill_id  : 
            skill = Skill.objects.get(pk=skill_id)
            base = base.filter( skills = skill ).order_by("theme","knowledge__waiting","knowledge","ranking")


        if theme_ids : 
            knowledges = set()
            for theme_id in theme_ids :
                try :
                    theme = Theme.objects.get(pk=int(theme_id))
                    knowledges.update( theme.knowledges.values_list('id', 'name').filter(level_id = level_id ) )
                except :
                    knowledges = []
            data['knowledges']  =  list(knowledges)

            if theme_ids[0] != "" : 
                base = base.filter( theme_id__in= theme_ids ).order_by("theme","knowledge__waiting","knowledge","ranking")

        if keyword  : 
            base = base.filter(Q(title__icontains=keyword)| Q(content_html__icontains=keyword)).order_by("theme","knowledge__waiting","knowledge","ranking")

        exotexs = base

        data['html'] = render_to_string('bibliotex/ajax_list_exercises.html', { 'bibliotex_id': bibliotex_id , 'exotexs': exotexs , "teacher" : teacher  })
    

    else :
        knowledges = Knowledge.objects.values_list("id","name").filter(theme_id__in=theme_ids, level_id = level_id  ) 
        knowledges_level = Knowledge.objects.values_list("id","name").filter(theme__subject__id = subject_id,  level_id = level_id  ) 
        data['knowledges']       =  list( knowledges )
        data['knowledges_level'] =  list( knowledges_level )
    return JsonResponse(data)

 
 
def ajax_charge_folders(request):  

    teacher = request.user.teacher
    data = {} 
    group_ids = request.POST.getlist('group_ids', None)

    if len(group_ids) :
        fldrs = set()
        prcs  = set()
        for group_id in group_ids :
            group = Group.objects.get(pk=group_id)
            fldrs.update(group.group_folders.values_list("id","title").filter(is_trash=0))
            prcs.update(group.group_parcours.values_list("id","title").filter(is_trash=0,folders=None))
        data['folders'] =  list( fldrs )
        data['parcours'] =  list( prcs )
    else :
        data['folders'] =  []
        data['parcours'] =  []
    return JsonResponse(data)



def ajax_charge_parcours(request):

    teacher = request.user.teacher
    data = {} 
    folder_ids = request.POST.getlist('folder_ids', None)

    if len(folder_ids) :
        parcourses = set()
        for folder_id in folder_ids :
            folder = Folder.objects.get(pk=folder_id)
            parcourses.update(folder.parcours.values_list("id","title").filter(is_trash=0))

        data['parcours'] =  list( parcourses )
    else :
        data['parcours'] =  []

    return JsonResponse(data)






def ajax_set_exotex_in_bibliotex(request):

    data = {} 
    exotex_id    = request.POST.get('exotex_id', None)
    bibliotex_id = request.POST.get('bibliotex_id', None)

    bibliotex   = Bibliotex.objects.get(pk = bibliotex_id) 
    exotex      = Exotex.objects.get(pk = exotex_id)
    skills      = exotex.skills.all()
    knowledges  = exotex.knowledges.all()

    statut = request.POST.get("statut") 

    data = {}    
    stds     = bibliotex.students.all()

    if statut=="true" or statut == "True":

        r = Relationtex.objects.get(bibliotex_id=bibliotex_id , exotex_id = exotex_id )  
        students = list(stds)
        r.students.remove(*students)

        data["statut"] = "False"
        data["class"] = "btn btn-danger"
        data["noclass"] = "btn btn-success"


    else:
        try :
            relationtex = Relationtex.objects.create(   bibliotex_id=bibliotex_id, exotex_id = exotex_id, ranking = 100,  
                                                        teacher = request.user.teacher, calculator = exotex.calculator,  duration =exotex.duration , 
                                                        is_python = exotex.is_python,is_scratch =exotex.is_scratch,is_tableur =exotex.is_tableur,is_print = 0,
                                                        is_publish = 1,  correction=exotex.correction ,is_publish_cor = 0 )
            relationtex.skills.set(skills)
            relationtex.knowledges.set(knowledges)
            relationtex.students.set(stds)


            data["statut"]  = "True"
            data["class"]   = "btn btn-success"
            data["noclass"] = "btn btn-danger"
        except :
            data["statut"] = "False"
            data["class"] = "btn btn-danger"
            data["noclass"] = "btn btn-success"


    data["nb"] = bibliotex.exotexs.count()


    return JsonResponse(data)



def unset_exotex_in_bibliotex(request,idr):
    bibliotex_id = Relationtex.objects.get(pk = idr).bibliotex.id
    Relationtex.objects.filter(pk = idr).delete()
    return redirect("show_bibliotex" , bibliotex_id)


@csrf_exempt # PublieDépublie un exercice depuis organize_parcours
def ajax_is_favorite(request):  

    target_id = int(request.POST.get("target_id",None))
    statut = int(request.POST.get("statut"))
    status = request.POST.get("status") 
    data = {}
 
    if statut :
        Bibliotex.objects.filter(pk = target_id).update(is_favorite = 0)
        data["statut"] = "<i class='fa fa-star text-default' ></i>"
        data["fav"] = 0
    else :
        Bibliotex.objects.filter(pk = target_id).update(is_favorite = 1)  
        data["statut"] = "<i class='fa fa-star   text-is_favorite' ></i>"
        data["fav"] = 1     

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
 
    bibliotex   = Bibliotex.objects.get(pk=target_id)
    if checked == "false" :
        bibliotex.groups.remove(group)
    else :
        bibliotex.groups.add(group)
        groups = (group,)
        attribute_all_documents_of_groups_to_all_new_students(groups)
    for g in bibliotex.groups.all():
        html += "<small>"+g.name +" (<small>"+ str(g.just_students_count())+"</small>)</small> "
    change_link = "change"

    data['html']        = html
    data['change_link'] = change_link
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

    Bibliotex.objects.filter(pk = int(parcours_id)).update(is_share = statut)
 
    return JsonResponse(data) 



@csrf_exempt   # PublieDépublie un parcours depuis form_group et show_group
def ajax_publish_list_bibliotex(request):  

    bibliotex_id = request.POST.get("bibliotex_id")
    statut = request.POST.get("statut")
    data = {}
    if statut=="true" or statut == "True":
        statut = 0
        data["statut"] = "false"
        data["style"] = "#dd4b39"
        data["class"] = "legend-btn-danger"
        data["noclass"] = "legend-btn-success"
        data["label"] = "Non publié"
    else:
        statut = 1
        data["statut"] = "true"
        data["style"] = "#00a65a"
        data["class"] = "legend-btn-success"
        data["noclass"] = "legend-btn-danger"
        data["label"] = "Publié"
 
    Bibliotex.objects.filter(pk = int(bibliotex_id)).update(is_publish = statut)

    return JsonResponse(data) 



############################################################################################################
############################################################################################################
#################  Résultats
############################################################################################################
############################################################################################################

def ajax_sort_exotexs_in_bibliotex(request):

    data = {}
    bibliotex_id = request.POST.get('bibliotex_id', None)
    relationtexs = request.POST.getlist('relationtexs', None)
    i=0
    for relationtex in relationtexs :
        Relationtex.objects.filter(pk = relationtex ).update(ranking=i)
        i+=1
    return JsonResponse(data)





############################################################################################################
############################################################################################################
#################  Résultats
############################################################################################################
############################################################################################################

def ajax_results_exotex(request):

    data = {}
    relationtex_id = request.POST.get('relationtex_id', None)
    relationtex = Relationtex.objects.get(pk=relationtex_id)
    students = relationtex.bibliotex.students.exclude(user__username__contains="_e-test").order_by("user__last_name")
    std_r = relationtex.students.order_by("user__last_name")
    if std_r.count() :
        students = [ s for s in std_r if s in students]



    context = { 'students': students , 'bibliotex': relationtex.bibliotex , "exotex" : relationtex.exotex  }
    data["html"] = render_to_string('bibliotex/ajax_results_exercise.html', context )
    data["title"] = "Résultats de l'exercice "+relationtex.exotex.title

    return JsonResponse(data)


############################################################################################################
############################################################################################################
#################  Individualisation
############################################################################################################
############################################################################################################


def ajax_individualise(request):
    """ A partir d'une bibliotex """    
    data = {}
    relationtex_id = request.POST.get('relationtex_id', None)
    student_id     = request.POST.get('student_id', None)
    statut         = request.POST.get('statut', None)
    is_checked     = request.POST.get('is_checked', None)

    relationtex    = Relationtex.objects.get(pk=relationtex_id)

    if is_checked == "true" : # Pour tous lex exercices à partir du premier
        for relationtex in relationtex.relationtexs.filter(is_publish=1 ) : 
            if student_id ==  "0"  :
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

                    if Studentanswer.objects.filter(student = student , relationtex = relationtex ).count() == 0 :
                        relationship.students.remove(student)
                        Blacklist.objects.get_or_create(relationtex=relationtex, student = student  )
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
                    if Blacklist.objects.filter(relationtex=relationtex, student = student  ).count()  > 0 :
                        Blacklist.objects.get(relationtex=relationtex, student = student ).delete()
                    data["statut"] = "True"
                    data["class"] = "btn btn-success"
                    data["noclass"] = "btn btn-default"
                    data["alert"] = False
    else :
        if student_id ==  "0"  :
            if statut=="true" or statut == "True" :
                somme = 0
                try :
                    for s in relationtex.students.all() :
                        Blacklistex.objects.get_or_create(student = s , relationtex = relationtex   )
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
                relationtex.students.set(relationtex.bibliotex.students.all())
                for s in relationtex.bibliotex.students.all():
                    if Blacklistex.objects.filter(relationtex=relationtex, student = s ).count() > 0 :
                        Blacklistex.objects.get(relationtex=relationtex, student = s ).delete()   
                data["statut"] = "True"
                data["class"] = "btn btn-success"
                data["noclass"] = "btn btn-default"
                data["alert"] = False

        else :
            student = Student.objects.get(pk = student_id)  

            if statut=="true" or statut == "True":

                relationtex.students.remove(student)
                Blacklistex.objects.get_or_create(relationtex=relationtex, student = student  )
                data["statut"] = "False"
                data["class"] = "btn btn-default"
                data["noclass"] = "btn btn-success"
                data["alert"] = False
 

            else:
                relationtex.students.add(student)
                if Blacklistex.objects.filter(relationtex=relationtex, student = student ).count()  > 0 :
                    Blacklistex.objects.get(relationtex=relationtex, student = student  ).delete()
                data["statut"] = "True"
                data["class"] = "btn btn-success"
                data["noclass"] = "btn btn-default"
                data["alert"] = False
 

    return JsonResponse(data)


        



def ajax_individualise_exotex(request):
    """ A partir d'un exotex """
    data = {}
    relationtex_id = request.POST.get('relationtex_id', None)
    relationtex = Relationtex.objects.get(pk=relationtex_id)
    students = relationtex.bibliotex.students.exclude(user__username__contains="_e-test").order_by("user__last_name")
    std_r = relationtex.students.all()
    if std_r.count() :
        students = std_b.intersection(std_r).order_by("user__last_name")
    context = { 'students': students ,  "relationtex" : relationtex }
    data["html"] = render_to_string('bibliotex/ajax_individualise_exercise.html',context)
    data["title"] = "Individualiser l'exercice "+relationtex.exotex.title

    return JsonResponse(data)
############################################################################################################
############################################################################################################
#################   IMPRESSION
############################################################################################################
############################################################################################################

def ajax_print_exotex(request):

    data = {}
    relationtex_id = request.POST.get('relationtex_id', None)
    relationtex = Relationtex.objects.get(pk=relationtex_id)
    context = { 'bibliotex': relationtex.bibliotex , "exotex" : relationtex.exotex  }
    data["html"] = render_to_string('bibliotex/ajax_print_exercise.html', context)
    data["title"] = "Imprimer l'exercice "+relationtex.exotex.title

    return JsonResponse(data)

def ajax_print_bibliotex(request):

    data = {}
    relationtex_id = request.POST.get('relationtex_id', None)
    bibliotex = Bibliotex.objects.get(pk=relationtex_id)
    students =  bibliotex.students.exclude(user__username__contains="_e-test").order_by("user__last_name")
    context = { 'students': students , 'bibliotex':  bibliotex   }
    data["html"] = render_to_string('bibliotex/ajax_print_bibliotex.html', context)
    data["title"] = "Imprimer la Bibliotex "+bibliotex.title

    return JsonResponse(data)





 

def print_bibliotex(request ):

    return printer(request,0, True,"pdf")


def print_exotex(request):

    return printer(request,0, False,"pdf")



def print_bibliotex_by_student(request,id):

    data = {}
    bibliotex = Bibliotex.objects.get(pk=id)
    return printer_bibliotex_by_student(bibliotex) 

 
