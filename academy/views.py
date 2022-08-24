#################################
#### Auteur : philipe Demaria 
#### pour SACADO
#################################

from django.conf import settings # récupération de variables globales du settings.py
from django.shortcuts import render, redirect
from django.forms.models import modelformset_factory
from django.forms import inlineformset_factory
from django.contrib.auth.decorators import  permission_required,user_passes_test, login_required
from django.http import JsonResponse 
from account.models import  Adhesion, Student, Resultknowledge , Parent , Teacher , User
from qcm.models import  Resultexercise, Studentanswer , Supportfile
from association.models import   Activeyear
from academy.models import  Autotest 
from academy.forms import  AutotestForm
from socle.models import  Level
from group.models import  Group
from qcm.models import  Studentanswer , Relationship , Parcours, Course, Folder , Mastering
from bibliotex.models import  Exotex
from django.template.loader import render_to_string
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from tool.consumers import *

import json
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



#---------------------------------------------------------------------------------------------------------
#   GESTION DE L'ACADEMIE 
#---------------------------------------------------------------------------------------------------------
def get_det():
    nbg = Group.objects.filter(subject_id=1).exclude(teacher__user_id=2480).exclude(teacher__user_id=2560).count()
    nbc = Course.objects.filter(subject_id=1).exclude(teacher__user_id=2480).exclude(teacher__user_id=2560).count()
    nbp = Parcours.objects.filter(subject_id=1).exclude(teacher__user_id=2480).exclude(teacher__user_id=2560).count()
    nbf = Folder.objects.filter(subject_id=1).exclude(teacher__user_id=2480).exclude(teacher__user_id=2560).count()

    nbr = Relationship.objects.exclude(parcours__teacher__user_id=2480).exclude(parcours__teacher__user_id=2560).count()

    nbgs = Group.objects.filter(subject_id=1).filter(teacher__user_id=2480).count()
    nbcs = Course.objects.filter(subject_id=1).filter(teacher__user_id=2480).count()
    nbps = Parcours.objects.filter(subject_id=1).filter(teacher__user_id=2480).count()
    nbfs = Folder.objects.filter(subject_id=1).filter(teacher__user_id=2480).count()
    nbrs = Relationship.objects.filter(parcours__teacher__user_id=2480).exclude(parcours__teacher__user_id=2560).count()

    return nbg, nbc , nbp , nbf , nbgs, nbcs , nbps , nbfs , nbr , nbrs




def gestion_academy_dashboard(request):
    teachers = Teacher.objects.order_by("user__last_name")
    nbt = teachers.count()
    nbu = User.objects.order_by("user__last_name").count()
    nbg, nbc , nbp , nbf , nbgs, nbcs , nbps , nbfs , nbr , nbrs = get_det()
    context = { 'nbg' : nbg ,  'nbc' :nbc , 'nbp' : nbp , 'nbf' : nbf , 'nbgs' : nbgs ,  'nbcs' : nbcs , 'nbps' : nbps , 'nbfs' : nbfs , 'nbr' : nbr , 'nbrs' : nbrs , 'teachers' : teachers, 'nbt' : nbt, 'nbu' : nbu }

    return render(request, "academy/dashboard_academy.html" , context)



def delete_groups(request):

    Group.objects.filter(subject_id=1).exclude(teacher__user_id=2480).delete()

    return redirect("gestion_academy_dashboard" )
 

def delete_parcours(request):

    parcourses = Parcours.objects.filter(subject_id=1).exclude(teacher__user_id=2480).exclude(teacher__user_id=2560)
    for p in parcourses :
        Mastering.objects.filter(relationship__parcours=p).delete()
        Relationship.objects.filter(parcours=p).delete()
        p.delete()
    return redirect("gestion_academy_dashboard" )


def delete_folders(request):

    Folder.objects.filter(subject_id=1).exclude(teacher__user_id=2480).delete()
    return redirect("gestion_academy_dashboard" )

def delete_courses(request):

    Course.objects.filter(subject_id=1).exclude(teacher__user_id=2480).delete()
    return redirect("gestion_academy_dashboard" )



def delete_teachers(request):
    Teacher.objects.exclude(user__is_superuser=1).delete()

    return redirect("gestion_academy_dashboard" )


def delete_users(request):
    User.objects.exclude(is_superuser=1).delete()
    return redirect("gestion_academy_dashboard" )

def delete_relations(request):
    parcourses = Parcours.objects.filter(subject_id=1).exclude(teacher__user_id=2480) 
    Relationship.objects.filter(parcours__in=parcourses).delete()
    return redirect("gestion_academy_dashboard" )
  
def create_academy(request):

 
    context = {   }
    return render(request, "academy/dashboard_academy.html" , context)







def delete_and_erase():

    groups = Group.objects.filter(subject_id=1,teacher__user__is_superuser=1)
    for g in groups :

        password = make_password("sacado2020") 
        user     = User.objects.create(first_name= "Equipe " ,  last_name="Academie " + str(g.level_id) , username= "profil_e-test_" + str(g.level_id)+"_"+str(uuid.uuid4())[:2],  password = password ,  is_superuser=0, user_type=0,school_id=50, country_id=5)
        student  = Student.objects.create(user=user, level=g.level)
        g.students.add(student)
 

    """
    folders = Folder.objects.filter(subject_id=1,author__user_id=2480)



    for folder in folders :
        groups     = folder.groups.all()
        students   = folder.students.all()  
        parcourses = folder.parcours.all()
        for parcours in parcourses :

            groups   = parcours.groups.all()
            students = parcours.students.all() 
            teacher  = parcours.teacher

            relationships   = parcours.parcours_relationship.all()
            customexercises = parcours.parcours_customexercises.all()
            courses         = parcours.course.all()        
            quizzes         = parcours.quizz.all()
            flashpacks      = parcours.flashpacks.all()
            bibliotexs      = parcours.bibliotexs.all()

            # clone      
            parcours.pk = None
            parcours.teacher = teacher
            parcours.is_publish = 1
            parcours.is_archive = 0
            parcours.is_share = 0
            parcours.is_favorite = 1
            parcours.code = str(uuid.uuid4())[:8]
            parcours.is_sequence = 1
            parcours.save()
            # fin du clone

            for r  in relationships : 
                relations = Relationship.objects.create(parcours = parcours , exercise_id = r.exercise.id , document_id = r.exercise.id  , type_id = 0 , ranking =  2 , is_publish= r.is_publish  , start= None , date_limit= None, duration= r.duration, situation= r.situation ) 
                relations.students.set(students)

            for c  in customexercises : 
                relationc = Relationship.objects.create(parcours = parcours , exercise_id = None , document_id = c.id  , type_id = 1 , ranking =  3 , is_publish= c.is_publish  , start= None , date_limit= None, duration= c.duration, situation= 0 ) 
                relationc.students.set(students)

            for course in courses : 
                relation = Relationship.objects.create(parcours = parcours , exercise_id = None , document_id = course.id  , type_id = 2 , ranking =  1 , is_publish= course.is_publish  , start= None , date_limit= None, duration= course.duration, situation= 0 ) 
                relation.students.set(students)
            

            for quizz in quizzes : 
                relationq = Relationship.objects.create(parcours = parcours , exercise_id = None , document_id = quizz.id  , type_id = 3 , ranking =  4 , is_publish= quizz.is_publish , start= None , date_limit= None, duration= 10, situation= 0 ) 
                relationq.students.set(students)


            for flashpack in flashpacks : 
                relationf = Relationship.objects.create(parcours = parcours , exercise_id = None , document_id = flashpack.id  , type_id = 4 , ranking =  5 , is_publish= flashpack.is_publish  , start= None , date_limit= None, duration= 10, situation= 0 ) 
                relationf.students.set(students)

            for bibliotex in bibliotexs : 
                relationb = Relationship.objects.create(parcours = parcours , exercise_id = None , document_id = bibliotex.id  , type_id = 5 , ranking =  6 , is_publish= bibliotex.is_publish  , start= None , date_limit= None, duration= 10, situation= 0 ) 
                relationb.students.set(students)



    """





















def printer_bibliotex_by_student(exotexs):
    """affiche un exo ou une collection d'exercices, soit en pdf (output="pdf")
    soit en html (output="html") """

    # ouverture du texte dans le fichier tex

    preamb = settings.TEX_PREAMBULE_PDF_FILE

    entetes=open(preamb,"r")
    elements=entetes.read()
    entetes.close()

    elements +=r"\begin{document}"+"\n"   

    ## Création du texte dans le fichier tex   

 
 

    elements +=r"\titreFiche{Auto test"+r"}{SACADO"+r"}"

    today = datetime.now()
 
     
 

    j = 1
    for exotex in exotexs :
    
        skills_display = ""
        if exotex.skills.count():
            sks =  exotex.skills.all()
        else :
            sks =  exotex.exotex.skills.all()
        for s in sks :
            skills_display +=  s.name+". "
            

        elements += r"\exo {\bf " +   exotex.title  +  r" }    \competence{" +skills_display+r"}"
        
        j+=1

  
        k_display =  exotex.knowledge.name
        elements += r"\savoirs{  \item " +  k_display 


        if exotex.knowledges.count() : kws =  exotex.knowledges.all()
        else : kws = []
        
        for k in kws : 
            elements += r" \item " +  k.name  

        elements += r"}"
 
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

 








def academy_index(request):

	rq_user = request.user 

	if rq_user.is_board :
		levels = Level.objects.order_by("ranking")

		context = { 'levels' : levels   }

 
		return render(request, "academy/academy_index.html" , context)

	else:
		return redirect("index")



def details_adhesion(request,level_id):

    rq_user = request.user

 

    if rq_user.is_board :

        level = Level.objects.get(pk=level_id)
        ay    = Activeyear.objects.get(is_active=1).year

        adhesions = Adhesion.objects.filter(level= level,  year = ay ).order_by("-start")
 

        context = { 'adhesions' : adhesions ,  'level' : level,   'historic' : False }

        return render(request, "academy/adhesions.html" , context)

    else:
        return redirect("index")



def historic_adhesions(request,level_id):

    rq_user = request.user 
    level = Level.objects.get(pk=level_id)
    if rq_user.is_board :
        adhesions = Adhesion.objects.filter(level= level ).order_by("-start")
        context = { 'adhesions' : adhesions ,  'level' : level ,  'historic' : True   }
        return render(request, "academy/adhesions.html" , context)

    else:
        return redirect("index")




def academy_list_adhesions(request):

    adhesions = Adhesion.objects.filter(student__user__school_id = 50)
    context   = { 'adhesions' : adhesions , }
    return render(request, "academy/academy_list_adhesions.html" , context)


def academy_list_parents(request):

    parents = Parent.objects.filter(user__school_id = 50) 
    context = { 'parents' : parents ,   }
    return render(request, "academy/academy_list_parents.html" , context)



def academy_delete_parent(request,user_id):

    parent = Parent.objects.get(user_id = user_id) 
    parent.delete()
    return redirect("academy_list_parents")




def delete_adhesion(request,ida):

    adhesion = Adhesion.objects.get(pk=ida)
    rq_user = request.user 
    if rq_user.is_board :
        level =  adhesion.level 
        adhesion.delete()
        today = time_zone_user(rq_user)
        adhesions = Adhesion.objects.filter(start__lte=today ,  level=level)
        return redirect("academy_list_adhesions" )

    else:
        return redirect("index")


def delete_student_academy(request, ids, level_id ):

    rq_user = request.user 
    if rq_user.is_board :
        level = Level.objects.get(pk=level_id) 
        today = time_zone_user(rq_user)
        adhesions = Adhesion.objects.filter(start__lte=today , stop__gte=today  , level=level)
 

        student = Student.objects.get(user_id=ids)
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
        context = { 'adhesions' : adhesions ,  'level' : level ,  'historic' : False   }

        return render(request, "academy/adhesions.html" , context)

    else:
        return redirect("index")


def autotests(request) :

	student   = request.user.student 
	autotests = Autotest.objects.filter(student=student )
	context   = { 'autotests' : autotests }

	return render(request, "academy/auto_tests.html" , context)




def create_autotest(request) :

	student  = request.user.student 
	form     = AutotestForm(request.POST or None, request.FILES or None )


	if request.method == "POST" :
		if form.is_valid():
			date = request.POST.get("date")

			studentanswers = Studentanswer.objects.filter(student=student, date__gte=date )

			knowledges , exotexs_exam = [] , []

			for studentanswer in studentanswers :
				if studentanswer.exercise.knowledge not in knowledges :
					knowledges.append(studentanswer.exercise.knowledge)

			exotexs = list( Exotex.objects.filter(knowledge__in=knowledges) )

			for i in range (5) :
				ind = random.randint(0,len(exotexs)-1)
				exotexs_exam.append(exotexs[ind])
				exotexs.remove(exotexs[ind])
 

			nf = form.save(commit=False)
			nf.file = printer_bibliotex_by_student(exotexs)
			nf.save()

	context   = { 'form' : form }
	return render(request, "academy/form_autotest.html" , context)





def delete_autotest(request,test_id) :

	student   = request.user.student 
	autotests = Autotest.objects.filter(student=student )
	context   = { 'autotests' : autotests }

	return render(request, "academy/auto_tests.html" , context)





def exemple_json(request):
    data = {}
    custom = request.POST.get("custom")
    image_id = request.POST.get("image_id")
    Customanswerimage.objects.get(pk = int(image_id)).delete()
    return JsonResponse(data)  






def synthese_parcours(request,user_id) :

	student   = request.user.student 
	parcourses = student.students_to_parcours.filter(is_evaluation=0, is_publish=1,is_trash=0).order_by("ranking").distinct()
	context   = { 'parcourses' : parcourses }

	return render(request, "academy/synthese_parcours.html" , context)


 
 
 
 
 ###################################################################
 ##       creation des graphiques et pdf
 ####################################################################
 
 
def radar(L):

    """dessine le radar d'une liste de listes [intitulé, note/100]
    valeur de retour : une "shape" de type Drawing
    """
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
    d.setFont("Times-Roman", 24)
    d.add(String(larg/2,haut-0.5*cm,"Graphique des attendus", textAnchor="middle"))
    #d.add(Rect(0,0,larg,haut,fillColor=cfond))
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
        r1=L[i-1][1]
        r2=L[i % n][1]
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
  


def contact_academy(request):


    context = {  }
    return render(request, 'academy/contact.html', context)