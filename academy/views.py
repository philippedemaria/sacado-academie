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
    nbt      = teachers.count()
    nbu      = User.objects.order_by("user__last_name").count()

    ids      = [14,1,2,3,4,5,6,7,8,9,10,11,12]
    suffixes = ["Maternelle","CP" , "CE1", "CE2", "CM1", "CM2", "Sxième", "Cinquième", "Quatrième", "Troisième", "Seconde", "Première", "Terminale"]
    dataset = []
    for i in range(len(ids)) :
        data= dict()
        data["id"]    = ids[i]
        data["level"] = suffixes[i] 
        dataset.append(data)

    accept = request.user.id == 1    
    nbg, nbc , nbp , nbf , nbgs, nbcs , nbps , nbfs , nbr , nbrs = get_det()
    context = { 'accept' : accept ,  'dataset' : dataset ,  'nbg' : nbg ,  'nbc' :nbc , 'nbp' : nbp , 'nbf' : nbf , 'nbgs' : nbgs ,  'nbcs' : nbcs , 'nbps' : nbps , 'nbfs' : nbfs , 'nbr' : nbr , 'nbrs' : nbrs , 'teachers' : teachers, 'nbt' : nbt, 'nbu' : nbu }

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
  

def create_academy(request,idl):

    # if Group.objects.filter(level_id=idl).count()>3:
    #     messages.error(request,"Vous avez sans doute dejà restauré ce niveau.")
    #     return redirect( "gestion_academy_dashboard" )

    names    = ["Autonomie " , "Adaptatif ", "Perso "]
    suffixes = ["0","CP" , "CE1", "CE2", "CM1", "CM2", "6", "5", "4", "3", "2", "1", "T","", "Mater"]
    u_suff   = ["0","CP" , "CE1", "CE2", "CM1", "CM2", "6.6", "5.5", "4.4", "3.3", "2.2", "1.1", "T.t","", "Mater"]
    teacher  = Teacher.objects.get(user__username = "ProfSacAdo"+u_suff[idl] )
    i = 1 # formule_id
    colors = ["0", "#605ca8" , '#ff9900' , '#e00a72' ]
    for name in names :
        if i == 1 : is_sequence = 0
        else : is_sequence = 1
        if idl == 11 :
            group = Group.objects.get(pk= 198) # group de référence à cloner
        elif idl == 12 :
            group = Group.objects.get(pk=538) # group de référence à cloner
        else : 
            group = Group.objects.get(teacher_id=2480,level_id=idl) # group de référence à cloner
        folders = group.group_folders.all() # récupération des dossiers du groupe

        group.pk = None
        group.color = colors[i]
        group.name= name + suffixes[idl]
        group.formule_id = i
        group.code = str(uuid.uuid4())[:8]
        group.teacher = teacher 
        group.save()
        # Création d'un élève du groupe profil élève de l'enseignant
        password = make_password("sacado2020") 
        user     = User.objects.create(first_name= "Equipe " ,  last_name="Académie " + suffixes[idl] , username= "ProfSacAdo"+u_suff[idl]+"_e-test_" + suffixes[idl]+"_"+str(uuid.uuid4())[:2],  password = password ,  is_superuser=0, user_type=0,school_id=50, country_id=5)
        student  = Student.objects.create(user=user, level_id=idl)
        group.students.add(student)
        # Clone des dossiers du groupe
        for folder in folders :
            parcourses = folder.parcours.all() # récupération des parcours
            #clone du dossier
            folder.pk = None
            folder.teacher = teacher
            folder.save()
            folder.groups.add(group)
            folder.students.add(student)
            for parcours in parcourses :
                relationships   = parcours.parcours_relationship.all() # récupération des relations
                courses         = parcours.course.all() # récupération des relations
                customexercises = parcours.parcours_customexercises.all() # récupération des customexercises
                quizzes         = parcours.quizz.all() # récupération des quizzes
                flashpacks      = parcours.flashpacks.all() # récupération des flashpacks
                bibliotexs      = parcours.bibliotexs.all() # récupération des bibliotexs

                #clone du parcours
                parcours.pk = None
                parcours.teacher = teacher
                parcours.is_publish = 1
                parcours.is_archive = 0
                parcours.is_share = 0
                parcours.is_favorite = 1
                parcours.is_sequence = is_sequence
                parcours.code = str(uuid.uuid4())[:8]
                parcours.save()
                parcours.students.add(student)
                folder.parcours.add(parcours)
                # fin du clone

                if is_sequence :
                    for r  in relationships : 
                        skills = r.skills.all() 
                        r.pk = None
                        r.save()                        
                        r.skills.set(skills)
                        r.students.add(student)

                else :

                    for c  in customexercises : 
                        skills     = c.skills.all() 
                        knowledges = c.knowledges.all() 
                        c.pk       = None
                        c.teacher  = teacher
                        c.save()
                        c.students.add(student)
                        c.skills.set(skills)
                        c.knowledges.set(knowledges)
                        c.parcourses.add(parcours)

                    n_r = []
                    for course in courses : 
                        relationships_c  = course.relationships.all() 
                        course.pk      = None
                        course.parcours = parcours
                        course.teacher = teacher
                        course.save()
                        
                        for r in relationships_c :
                            try :
                                skills = r.skills.all() 
                                r.pk       = None
                                r.parcours = parcours
                                r.save()
                                r.students.add(student)
                                r.skills.set(skills)
                                course.relationships.add(r)
                            except :
                                pass
                            n_r.append(r.id)

                    for r in relationships.exclude(pk__in=n_r) :
                        try :
                            skills = r.skills.all() 
                            r.pk       = None
                            r.parcours = parcours
                            r.save()
                            r.students.add(student)
                            r.skills.set(skills)
                        except :
                            pass


                    for quizz in quizzes :  
                        questions = quizz.questions.all()    
                        themes    = quizz.themes.all()  
                        levels    = quizz.levels.all()  

                        quizz.pk      = None
                        quizz.teacher = teacher
                        quizz.save()

                        for question in questions :
                            choices = question.choices.all()
                            question.pk = None
                            question.save()
                            question.students.add(student)
                            for choice in choices :
                                choice.pk= None
                                choice.question = question
                                choice.save()

                        quizz.groups.add(group)
                        quizz.parcours.add(parcours)
                        quizz.folders.add(folder)
                        quizz.levels.set(levels)
                        quizz.themes.set(themes)
                        quizz.students.add(student)


        #formule_id
        i+=1
    
    return redirect("gestion_academy_dashboard" )



def associate_student_docs(request) :

    teachers = Teacher.objects.filter(user__is_superuser = 1 , user__is_staff = 0 )
    password = make_password("sacado2020") 
    for teacher in teachers :
        # Création d'un élève du groupe profil élève de l'enseignant
        user     = User.objects.create(first_name= "Elève " ,  last_name="Académie "  , username= teacher.user.username+"_e-test_"+str(uuid.uuid4())[:2],  password = password ,  is_superuser=0, user_type=0,school_id=50, country_id=5)
        for group in teacher.groups.all():
            student  = Student.objects.create(user=user, level_id=group.level.id)
            group.students.add(student)

            folders = group.group_folders.all() # récupération des dossiers du groupe
            for folder in folders :
                folder.students.add(student)
                for parcours in parcourses :
                    relationships   = parcours.parcours_relationship.all() # récupération des relations
                    courses         = parcours.course.all() # récupération des relations
                    customexercises = parcours.parcours_customexercises.all() # récupération des customexercises
                    quizzes         = parcours.quizz.all() # récupération des quizzes
                    flashpacks      = parcours.flashpacks.all() # récupération des flashpacks
                    bibliotexs      = parcours.bibliotexs.all() # récupération des bibliotexs

                    parcours.students.add(student)


                    if is_sequence :
                        for r  in relationships : 
                            r.students.add(student)

                        for c  in customexercises : 
                            c.students.add(student)

                        for course in courses : 
                            course.students.add(student)
                        

                        for quizz in quizzes : 
                            quizz.students.add(student)


                        for flashpack in flashpacks : 
                            flashpack.students.add(student)

                        for bibliotex in bibliotexs : 
                            relationb.students.add(student)
                    
                    else :

                        for c  in customexercises : 
                            c.students.add(student)


                        n_r = []
                        for course in courses : 
                            relationships_c  = course.relationships.all() 
        
                            for r in relationships_c :
                                r.students.add(student)
                                n_r.append(r.id)

                        for r in relationships.exclude(pk__in=n_r) :
                            r.students.add(student)


                        for quizz in quizzes :  
                            questions = quizz.questions.all()    
                            themes    = quizz.themes.all()  
                            levels    = quizz.levels.all()  

                            for question in questions :
                                question.students.add(student)
                            quizz.students.add(student)

    
    return redirect("gestion_academy_dashboard" )


 
def add_presentation(request,idl):


    sequences  = Parcours.objects.filter(subject_id=1,level_id=idl,is_sequence=1)
    for sequence in sequences :
        try :
            Relationship.objects.create(exercise_id=10155, parcours = sequence,ranking=0,situation=5)
        except :
            pass
        try :
            Relationship.objects.create(exercise_id=10154, parcours = sequence,ranking=0,situation=5)
        except :
            pass
    
    return redirect("gestion_academy_dashboard" )



#---------------------------------------------------------------------------------------------------------
#   FIN GESTION DE L'ACADEMIE 
#---------------------------------------------------------------------------------------------------------










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