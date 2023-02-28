from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core import serializers
from django.template.loader import render_to_string
from django.contrib import messages
from django.core.mail import send_mail

from flashcard.models import Flashcard, Flashpack , Answercard , Madeflashpack
from flashcard.forms import FlashcardForm ,  FlashpackForm , CommentflashcardForm , FlashpackAcademyForm
from qcm.models import  Parcours, Exercise , Folder , Relationship
from account.models import Student , Teacher
from account.decorators import  user_is_testeur
from sacado.settings import MEDIA_ROOT
from qcm.views import  get_teacher_id_by_subject_id
from group.models import Group 
from socle.models import Level, Waiting , Knowledge , Theme
from django.views.decorators.csrf import csrf_exempt
from django.forms import inlineformset_factory
from templated_email import send_templated_mail
from django.db.models import Q
from random import  randint, shuffle
import math
import json
import time
############### bibliothèques pour les impressions pdf  #########################
import os
import csv
#################################################################################
import re
import pytz
from datetime import datetime , timedelta
from general_fonctions import *
 

 

def list_flashpacks(request):

    request.session["tdb"] = "Flashpack" # permet l'activation du surlignage de l'icone dans le menu gauche
    request.session["subtdb"] = ""

    if request.user.is_authenticated :
        if request.user.is_teacher :
            teacher = request.user.teacher
            flashpacks = Flashpack.objects.filter(teacher__user = request.user)
            return render(request, 'flashcard/all_flashpacks.html', {'flashpacks': flashpacks, 'teacher' : teacher })
        else :
            student = request.user.student
            today = time_zone_user(request.user)
            fpacks_base = Flashpack.objects.filter(students=student)
            fpacks = fpacks_base.exclude(is_global=1)
            flashpacks = fpacks_base.filter(is_global=1)
            return render(request, 'flashcard/list_flashpacks_student.html', {'flashpacks': flashpacks, 'fpacks': fpacks, 'student' : student , 'today' : today })
    else :
        return redirect('index')








 
def list_my_flashpacks(request):

    request.session["tdb"] = "Flashpack" # permet l'activation du surlignage de l'icone dans le menu gauche
    request.session["subtdb"] = ""
    teacher            = request.user.teacher
    dataset_user       = teacher.flashpacks
    dataset            = dataset_user.filter(is_archive=0)
    flashpacks         = dataset.filter(folders=None)
    flashpacks_folders = dataset.values_list("folders", flat=True).exclude(folders=None).distinct().order_by("folders")

    list_folders = list()
    for folder in flashpacks_folders :
        flash_folders = dict()
        flash_folders["folder"] = Folder.objects.get(pk=folder)
        teacher_flash_folders = dataset.filter(is_archive=0 , folders=folder)
        flash_folders["flashpacks"] = teacher_flash_folders  
        list_folders.append(flash_folders)

    ########################################################################
    # insere les cartes d'un flashpack de parcours dans les flashpack annuel
    ########################################################################
    for level in teacher.levels.all() :
        dataset_include_cards  = dataset_user.filter(is_global=1,is_inclusion=1,levels=level)
        dataset_parcourses     = dataset_user.filter(is_global=0,levels=level)
        for dataset_include_card in dataset_include_cards :
            cards = set()
            for flashpack in dataset_parcourses :
                cards.update(flashpack.flashcards.filter( is_globalset = 1,levels=level ))
            dataset_include_card.flashcards.set(cards)
    ########################################################################
    ########################################################################
    ########################################################################

    groups     = teacher.has_groups() # pour ouvrir le choix de la fenetre modale pop-up
    nb_archive = dataset_user.filter(is_archive=1).count()
    return render(request, 'flashcard/list_flashpacks.html', {'flashpacks': flashpacks, 'list_folders' : list_folders , 'groups' : groups , 'nba' : nb_archive , 'is_archive' : False })

 


def my_flashpack_archives(request):

    request.session["tdb"] = "Flashpack" # permet l'activation du surlignage de l'icone dans le menu gauche
    request.session["subtdb"] = ""
    teacher = request.user.teacher

    dataset = teacher.flashpacks.filter(is_archive=1)
    flashpacks = dataset.filter(folders=None)
    flashpacks_folders = dataset.values_list("folders", flat=True).exclude(folders=None).distinct().order_by("folders")

    list_folders = list()
    for folder in flashpacks_folders :
        flash_folders = dict()
        flash_folders["folder"] = Folder.objects.get(pk=folder)
        teacher_flash_folders = dataset.filter(is_archive=1 , folders=folder)
        flash_folders["flashpacks"] = teacher_flash_folders  
        list_folders.append(flash_folders)

    groups = teacher.has_groups() # pour ouvrir le choix de la fenetre modale pop-up
 
    return render(request, 'flashcard/list_flashpacks.html', {'flashpacks': flashpacks, 'list_folders' : list_folders , 'groups' : groups, 'is_archive' : True  })



def create_flashpack(request, idf=0):

    request.session["tdb"] = "Flashpack" # permet l'activation du surlignage de l'icone dans le menu gauche
    request.session["subtdb"] = ""

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

    form = FlashpackForm(request.POST or None,request.FILES or None, teacher = teacher, group = group, folder = folder, initial = { 'folders'  : [folder] ,  'groups'  : [group] } )

    if form.is_valid():
        nf = form.save(commit=False)
        nf.teacher  = teacher
        nf.save()
        form.save_m2m()

        group_students = set()
        for group_id in request.POST.getlist("groups") :
            group = Group.objects.get(pk = group_id)
            nf.levels.add(group.level)
            group_students.update(group.students.all())
        nf.students.set(group_students)

        if nf.is_global :
            messages.success(request, 'Le flashpack annuel est créé avec succès !')
            return redirect('my_flashpacks')
        else :
            messages.success(request, 'Le flashpack est créé avec succès !')
            return redirect('set_flashcards_to_flashpack' , nf.id)
    else:
        print(form.errors)

    context = {'form': form, 'communications' : [] , 'flashpack': None , 'parcours': None ,  'folder': folder  , 'group': group   }

    return render(request, 'flashcard/form_flashpack.html', context)


def update_flashpack(request, id):

    request.session["tdb"] = "Flashpack" # permet l'activation du surlignage de l'icone dans le menu gauche
    request.session["subtdb"] = ""

    teacher = request.user.teacher
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

    flashpack = Flashpack.objects.get(id=id)

    form = FlashpackForm(request.POST or None, instance=flashpack, teacher = teacher , group = group, folder = folder,    )
    if request.method == "POST" :
        if form.is_valid():
            nf = form.save(commit=False)
            nf.teacher  = teacher
            nf.save()
            form.save_m2m()

            group_students = set()
            for group_id in request.POST.getlist("groups") :
                group = Group.objects.get(pk = group_id)
                nf.levels.add(group.level)
                group_students.update(group.students.all())

            nf.students.set(group_students)
            
            messages.success(request, 'Le flashpack a été modifié avec succès !')
            return redirect('set_flashcards_to_flashpack' , nf.id)


        else:
            print(form.errors)

    context = {'form': form, 'communications' : [] , 'flashpack': flashpack, 'parcours': None ,  'folder': folder  , 'group': group }

    return render(request, 'flashcard/form_flashpack.html', context )


def create_flashpack_from_parcours(request, idp=0):

    request.session["tdb"] = "Flashpack" # permet l'activation du surlignage de l'icone dans le menu gauche
    request.session["subtdb"] = ""

    teacher = request.user.teacher
    folder_id = request.session.get("folder_id",None)
    group_id = request.session.get("group_id",None)
    if group_id :group = Group.objects.get(id=group_id)
    else : group = None
    if folder_id : folder = Folder.objects.get(id=folder_id)
    else : folder = None

    parcours = Parcours.objects.get(id=idp)

    form = FlashpackForm(request.POST or None,request.FILES or None, teacher = teacher, group = group, folder = folder,  initial = { 'folders'  : [folder] ,  'groups'  : [group] ,  'parcours'  : [parcours]  } )

    if form.is_valid():
        nf = form.save(commit=False)
        nf.teacher  = teacher
        nf.save()
        form.save_m2m()
 
        group_students = set()
        for group_id in request.POST.getlist("groups") :
            group = Group.objects.get(pk = group_id)
            nf.levels.add(group.level)
            group_students.update(group.students.all())

        nf.students.set(group_students)
        
        messages.success(request, 'Le flashpack a été créé avec succès !')
        return redirect('set_flashcards_to_flashpack' , nf.id)
    else:
        print(form.errors)

    context = {'form': form, 'communications' : [] , 'flashpack': None , 'parcours': parcours , 'group': group  , 'folder': folder  }

    return render(request, 'flashcard/form_flashpack.html', context)





def create_flashpack_sequence(request, id):

    request.session["tdb"] = "Flashpack" # permet l'activation du surlignage de l'icone dans le menu gauche
    request.session["subtdb"] = ""
    teacher = request.user.teacher
    folder_id = request.session.get("folder_id",None)
    group_id = request.session.get("group_id",None)
    if group_id :group = Group.objects.get(id=group_id)
    else : group = None
    if folder_id : folder = Folder.objects.get(id=folder_id)
    else : folder = None

    parcours = Parcours.objects.get(id=id)

    form = FlashpackForm(request.POST or None,request.FILES or None, teacher = teacher, group = group, folder = folder,  initial = { 'folders'  : [folder] ,  'groups'  : [group] ,  'parcours'  : [parcours]  } )

    if form.is_valid():
        nf = form.save(commit=False)
        nf.teacher  = teacher
        nf.save()
        form.save_m2m()

        group_students = set()
        for group_id in request.POST.getlist("groups") :
            group = Group.objects.get(pk = group_id)
            nf.levels.add(group.level)
            group_students.update(group.students.all())

        nf.students.set(group_students)
        relation = Relationship.objects.create(parcours = parcours , exercise_id = None , document_id = nf.id  , type_id =  4 , ranking =  200 , is_publish= 1 , start= None , date_limit= None, duration= 10, situation= 0 ) 
        students = parcours.students.all()
        relation.students.set(students)

        messages.success(request, 'Le flashpack a été créé avec succès !')
        return redirect('set_flashcards_to_flashpack' , nf.id)
    else:
        print(form.errors)

    context = {'form': form, 'communications' : [] , 'flashpack': None , 'parcours': parcours , 'group': group  , 'folder': folder  }

    return render(request, 'flashcard/form_flashpack.html', context)



def peuplate_flashpack_parcours(request,idp):

    request.session["tdb"] = "Flashpack" # permet l'activation du surlignage de l'icone dans le menu gauche
    request.session["subtdb"] = ""

    teacher = request.user.teacher
    parcours = Parcours.objects.get(id=idp)

    flashpacks = Flashpack.objects.filter(parcours=parcours)


    context = {'parcours': parcours, 'teacher': teacher , 'flashpacks' : flashpacks , 'type_of_document' : 4 }

    return render(request, 'flashcard/form_peuplate_flashpack_parcours.html', context)





def ajax_find_peuplate_sequence(request):

    id_parcours = request.POST.get("id_parcours",0)
    subject_id  = request.POST.get("id_subject",0)
    keyword     = request.POST.get("keyword",None)  
    level_id    = request.POST.get("id_level",None) 
 

    if keyword and level_id :
        level = Level.objects.get(pk=level_id)
        flashpacks = Flashpack.objects.filter( title__icontains=keyword, teacher__user__school = request.user.school , subject_id=subject_id,levels=level  )
    elif keyword :
        flashpacks = Flashpack.objects.filter( title__icontains=keyword, teacher__user__school = request.user.school , subject_id=subject_id  )
    else :        
        level = Level.objects.get(pk=level_id)
        flashpacks = Flashpack.objects.filter(teacher__user__school = request.user.school , subject_id=subject_id,levels=level )

    context = { "flashpacks" : flashpacks }


    data = {}
    data['html']    = render_to_string( 'flashcard/ajax_flashpack_peuplate_sequence.html' , context)

    return JsonResponse(data)  


def clone_flashpack_sequence(request, idf):

    """ cloner un parcours """
    request.session["tdb"] = "Flashpack" # permet l'activation du surlignage de l'icone dans le menu gauche
    request.session["subtdb"] = ""

    teacher = request.user.teacher
    flashpack = Flashpack.objects.get(pk=idf) # parcours à cloner.pk = None
    flashcards = flashpack.flashcards.all()
    flashpack.pk = None
    flashpack.teacher = teacher
    flashpack.save()
    flashpack.flashcards.set(flashcards)

    parcours_id = request.session.get("parcours_id",None)  
    if parcours_id :
        parcours = Parcours.objects.get(pk = parcours_id)
        relation = Relationship.objects.create(parcours = parcours , exercise_id = None , document_id = flashpack.id  , type_id = 4 , ranking =  200 , is_publish= 1 , start= None , date_limit= None, duration= 10, situation= 0 ) 
        students = parcours.students.all()
        relation.students.set(students)
        flashpack.students.set(students)

        return redirect('show_parcours' , 0, parcours_id )
    else :
        return redirect('list_quizzes')
 




def delete_flashpack(request, id):
    flashpack = Flashpack.objects.get(id=id)
    levels = Level.objects.filter(flashpacks=flashpack)
    for l in levels :
        l.flashpacks.remove(flashpack)
    flashpack.delete()

    return redirect('my_flashpacks')


def create_flashpack_academy(request, id):

    request.session["tdb"] = "Flashpack" # permet l'activation du surlignage de l'icone dans le menu gauche
    request.session["subtdb"] = ""

    form = FlashpackAcademyForm(request.POST or None,request.FILES or None )
    teacher = Teacher.objects.get(user_id=2480)
    if form.is_valid():
        nf = form.save(commit=False)
        nf.teacher     = teacher
        nf.is_creative = True
        nf.subject_id  = 1
        nf.save()
        form.save_m2m()

        nf.students.add(request.user.student)


        messages.success(request, 'Le flashpack est créé avec succès !')
        return redirect('flashpacks' )
    else:
        print(form.errors)

    context = {'form': form, 'communications' : [] , 'flashpack': None  }

    return render(request, 'flashcard/form_flashpack_academy.html', context)



 
def update_flashpack_academy(request, id):

    request.session["tdb"] = "Flashpack" # permet l'activation du surlignage de l'icone dans le menu gauche
    request.session["subtdb"] = ""

    flashpack = Flashpack.objects.get(pk=id)
    form = FlashpackAcademyForm(request.POST or None,request.FILES or None, instance = flashpack )
    teacher = Teacher.objects.get(user_id=2480)
    if form.is_valid():
        nf = form.save(commit=False)
        nf.teacher     = teacher
        nf.is_creative = True
        nf.subject_id  = 1
        nf.save()
        form.save_m2m()
        nf.students.add(request.user.student)
        messages.success(request, 'Le flashpack est modifié avec succès !')
        return redirect('flashpacks' )
    else:
        print(form.errors)

    context = {'form': form, 'communications' : [] , 'flashpack': None  }

    return render(request, 'flashcard/form_flashpack_academy.html', context)


def delete_flashpack_academy(request, id):
    flashpack = Flashpack.objects.get(id=id)
    flashpack.delete()

    return redirect('flashpacks')



 
def show_flashpack(request, id):

    if request.user.is_authenticated:
        flashpack  = Flashpack.objects.get(id=id)
        if request.user.is_student :
            today = time_zone_user(request.user)
            template = 'flashcard/show_flashpack_student.html'
            context = {'flashpack': flashpack, 'today' : today }
        else :
            flashcards =  flashpack.flashcards.filter(is_validate=1) 
            template = 'flashcard/show_flashpack.html'
            context = {'flashpack': flashpack, 'flashcards' : flashcards  }

        return render(request,template, context )
    else :
        return redirect('index')


def revise_flashpack(request, id):


    flashpack  = Flashpack.objects.get(id=id)
    flashcards =  flashpack.flashcards.filter(is_validate=1) 
    template = 'flashcard/show_flashpack_student.html'
    context = {'flashpack': flashpack, 'flashcards' : flashcards  }

    return render(request,template, context )




def flashpack_peuplate(request, id):

    teacher   = request.user.teacher
    flashpack = Flashpack.objects.get(id=id)
    themes    = flashpack.themes.all()
    waitings  = set()
    for t in themes :
    	waitings.update(t.waitings.all())

    flashcards = flashpack.flashcards.all()

    context   = { 'flashpack': flashpack, 'flashcards': flashcards , 'teacher': teacher , 'waitings': waitings   }

    return render(request, 'flashcard/form_peuplate_flashcard.html', context )
 



def set_flashcards_to_flashpack(request, id):

 
    flashpack = Flashpack.objects.get(id=id)
    request.session["flashpack_id"] = id

    if not flashpack.is_creative and flashpack.teacher != request.user.teacher :
        messages.error(request,"Vous tentez d'ouvrir un flashpack illégalement. Vous êtes donc redirigé.")
        return redirect('index')


    form = FlashcardForm(request.POST or None , flashpack = flashpack  )

    if request.method == "POST" :
        if form.is_valid():
            nf = form.save(commit=False)
            nf.theme = flashpack.themes.first()
            nf.subject = flashpack.subject
            nf.is_validate = 1
            if request.user.is_student :
                nf.is_validate = 0
            nf.save()
            form.save_m2m()
            nf.levels.set(flashpack.levels.all())
            nf.authors.add(request.user)
            flashpack.flashcards.add(nf)

            if request.user.is_student :
                if flashpack.teacher.notification :
                    msg = "Une flashcard du flashpack "+ flashpack.title +" vient d'être créé/modifiée par " + request.user.first_name+ " " + request.user.last_name
                    sending_mail("Avertissement flashcard " ,  msg  , settings.DEFAULT_FROM_EMAIL , [flashpack.teacher.user.email])


            messages.success(request, 'La flashcard a été ajoutée avec succès !')
            return redirect('set_flashcards_to_flashpack' ,  id)

        else:
            print(form.errors)

    flashcards = flashpack.flashcards.all() 

    context    = { 'flashpack': flashpack, 'flashcards': flashcards ,   'form': form   }

    return render(request, 'flashcard/set_flashcards_to_flashpack.html', context )
 



def validate_flashcards_to_flashpack(request, id):

    flashpack = Flashpack.objects.get(id=id)
    flashcards = flashpack.flashcards.order_by("is_validate")

    request.session["flashpack_id"]=flashpack.id

    teacher = request.user.teacher
    form = CommentflashcardForm(request.POST or None, initial ={ 'teacher' : teacher , 'flashpack' : flashpack } )

    if request.method == "POST" :
        id_flashcards = request.POST.getlist('id_flashcard')


        for flashcard in flashpack.flashcards.all() :
            flashcard.is_validate = 0
            flashcard.save()

        for id_flashcard in id_flashcards :
            Flashcard.objects.filter(pk=id_flashcard).update(is_validate=1)
         
        messages.success(request, 'Validation réalisée avec succès !')
        return redirect('validate_flashcards_to_flashpack', id )

    context    = { 'flashpack': flashpack, 'flashcards': flashcards , 'form' : form }

    return render(request, 'flashcard/validate_flashcards_to_flashpack.html', context )

 


def import_flashcards_to_flashpack(request, id):

    teacher   = request.user.teacher
    flashpack = Flashpack.objects.get(id=id)
 
    if request.method == "POST":
        # try:
        csv_file = request.FILES["csv_file"]
        if not csv_file.name.endswith('.csv'):
            messages.error(request, "Le fichier n'est pas format CSV")
            return HttpResponseRedirect(reverse("import_flashcards_to_flashpack", args=[id]))
        # if file is too large, return
        if csv_file.multiple_chunks():
            messages.error(request, "Le fichier est trop lourd (%.2f MB)." % (csv_file.size / (1000 * 1000),))
            return HttpResponseRedirect(reverse("import_flashcards_to_flashpack", args=[id]))
        try:
            file_data = csv_file.read().decode("utf-8")
        except UnicodeDecodeError:
            messages.error(request, 'Erreur..... Votre fichier contient des caractères spéciaux qui ne peuvent pas être décodés. Merci de vérifier que votre fichier .csv est bien encodé au format UTF-8.')
            return HttpResponseRedirect(reverse("import_flashcards_to_flashpack", args=[id]))

        lines = file_data.split("\r\n")
        # loop over the lines and save them in db. If error , store as string and then display = []
 
        for line in lines:
 
            if ";" in line:
                fields = line.split(";")
            elif "," in line:
                fields = line.split(",")

            new_flashcard , is_new = Flashcard.objects.get_or_create(question = fields[1] , defaults = {'title' : fields[0]  , 'calculator' : fields[2], 'answer' : fields[3], 'helper' : fields[4], 'subject' : flashpack.subject, 'theme': flashpack.themes.first() , 'waiting' : None } )
            if is_new : 
                new_flashcard.levels.set(flashpack.levels.all())  
                flashpack.flashcards.add(new_flashcard) 
                new_flashcard.authors.add(request.user)
 
        messages.success(request,"importation réussie.")


    context = { 'flashpack': flashpack,  'teacher': teacher   }
    return render(request, 'flashcard/import_flashcard_in_flashpack.html', context )  
 


def clone_flashpack(request, id):

    flashpack = Flashpack.objects.get(id=id)
    request.session["tdb"] = False # permet l'activation du surlignage de l'icone dans le menu gauche 

    flashpack.pk = None
    flashpack.save()

    return redirect('set_flashcards_to_flashpack' , id)





def flashpack_results(request, idf,idp=0):

    flashpack = Flashpack.objects.get(id=idf)
    request.session["tdb"] = False # permet l'activation du surlignage de l'icone dans le menu gauche

    parcours = None
    if idp > 0 :
        parcours = Parcours.objects.get(pk=idp)    

    if request.user.is_teacher :
        answercards = flashpack.answercards.all()
        students = flashpack.students.exclude(user__username__contains="_e-test").order_by("user__last_name")
        template = 'flashcard/flashpack_results.html'
        context = { 'flashpack': flashpack,  'answercards': answercards ,'parcours' : parcours , 'students' : students }
    else :
        answercards = flashpack.answercards.filter(student = request.user.student) 
        template = 'flashcard/flashpack_results_student.html'
        context = { 'flashpack': flashpack,  'answercards': answercards ,'parcours' : parcours   }

    return render(request, template , context )  





def ajax_results_flashpack(request):

    flashpack_id = request.POST.get("flashpack_id")
    flashpack    = Flashpack.objects.get(pk=flashpack_id)
    student_id   = request.POST.get("student_id")
    student      = Student.objects.get(pk=student_id)
    data = {}


    data['html'] = render_to_string('flashcard/ajax_results_flashpack.html', { 'flashpack': flashpack , 'student': student ,  } )

    return JsonResponse(data)


def actioner(request):

    teacher = request.user.teacher 
    idbs = request.POST.getlist("selected_flashpacks")
    if  request.POST.get("action") == "deleter" :  
        for idb in idbs :
            flashpack = Flashpack.objects.get(id=idb) 
            flashpack.delete()

    elif  request.POST.get("action") == "archiver" :  
        for idb in idbs :
            flashpack = Flashpack.objects.get(id=idb) 
            flashpack.is_archive = 1
            flashpack.is_favorite = 0
            flashpack.save()
 
    else : 
        for idb in idbs :
            flashpack = Flashpack.objects.get(id=idb) 
            flashpack.is_archive = 0
            flashpack.is_favorite = 0
            flashpack.save()
     
    return redirect('my_flashpacks')    
######################################################################################
######################################################################################
#           Flashcard
######################################################################################
######################################################################################
 
def clone_flashcard(request, idf, id):

    flashpack = Flashpack.objects.get(id=idf)
    flashcard = Flashcard.objects.get(id=id)
    request.session["tdb"] = False # permet l'activation du surlignage de l'icone dans le menu gauche 

    flashcard.pk = None
    flashcard.save()
    flashpack.flashcards.add(flashcard)

    return redirect('set_flashcards_to_flashpack' , idf)



def list_flashcards(request):
 
    flashcards = Flashcard.objects.all()
    return render(request, 'flashcard/list_flashcards.html', {'flashcards': flashcards, 'communications' : [] , })



 
def create_flashcard(request):

    form = FlashcardForm(request.POST or None  , flashpack = None )

    if form.is_valid():
        nf = form.save()
        for l_id in request.POST.getlist("levels") :
            level = Level.objects.get(pk=l_id)
            level.flashcards.add(nf)
        messages.success(request, 'La flashcard a été créée avec succès !')
        return redirect('flashcards')
    else:
        print(form.errors)

    context = {'form': form, 'communications' : [] , 'flashcard': None  }

    return render(request, 'flashcard/form_flashcard.html', context)



 
def update_flashcard(request, id):

    flashcard = Flashcard.objects.get(id=id)
    flashcard_form = FlashcardForm(request.POST or None, instance=flashcard , flashpack = None )

    if request.method == "POST" :
        if flashcard_form.is_valid():
            flashcard_form.save()
            for l_id in request.POST.getlist("levels") :
                level = Level.objects.get(pk=l_id)
                level.flashcards.add(flashcard)
            messages.success(request, 'La flashcard a été modifiée avec succès !')
            fp_id = request.session.get("flashpack_id",None)

            if fp_id : return redirect('set_flashcards_to_flashpack',fp_id)
            else : return redirect('my_flashpacks')

        else:
            print(flashcard_form.errors)

    context = {'form': flashcard_form, 'communications' : [] , 'flashcard': flashcard,   }

    return render(request, 'flashcard/form_flashcard.html', context )


 
def delete_flashcard(request, idf , id):

	flashcard = Flashcard.objects.get(id=id)

	flashcard.delete()
	if idf :
		return redirect('set_flashcards_to_flashpack' , idf)
	else :
		return redirect('my_flashpacks')


def ajax_delete_flashcard(request):

    flashcard_id = request.POST.get("flashcard_id")
    flashcard = Flashcard.objects.get(id=flashcard_id)
    flashcard.delete()
    data = {}

    return JsonResponse(data) 



 
def show_flashcard(request, id):
    flashcard = Flashcard.objects.get(id=id)
    context = {'flashcard': flashcard,   }
    return render(request, 'flashcard/show_flashcard.html', context )


def ajax_level_flashcard(request):

    data = {} 
 
    theme_ids    = request.POST.getlist('theme_id', None)
    level_id     = request.POST.get("level_id",None)
    subject_id   = request.POST.get("subject_id",None)
    waiting_id     = request.POST.get("waiting_id",None)
    keyword      = request.POST.get("keyword",None)
    flashpack_id = request.POST.get("flashpack_id",None)

    flashpack = Flashpack.objects.get(pk=flashpack_id)
    teacher = request.user.teacher 
    data = {}

    base = Flashcard.objects.filter(subject_id= subject_id).exclude(flashpacks=flashpack)

    if theme_ids :  

        if (level_id != " " or level_id) and theme_ids[0] != "" and waiting_id and not keyword : 
            waiting = Waiting.objects.get(pk=waiting_id)
            level   = Level.objects.get(pk=level_id)
            flashcards = base.filter( levels = level , theme__in= theme_ids, waiting = waiting ).order_by("theme","waiting" )

        elif (level_id != " " or level_id)  and waiting_id and not keyword  : 
            waiting = Waiting.objects.get(pk=waiting_id)
            level   = Level.objects.get(pk=level_id)
            flashcards = base.filter( levels = level ,  waiting = waiting, ).order_by("theme","waiting" )

        elif (level_id != " " or level_id) and theme_ids[0] != "" and not keyword  : 
            level   = Level.objects.get(pk=level_id)
            flashcards = base.filter( levels = level , theme__in= theme_ids ).order_by("theme","waiting" )

        elif theme_ids[0] != ""  and not keyword   : 
            flashcards = base.filter(  theme__in= theme_ids).order_by("theme","waiting" )

        elif keyword and theme_ids[0] != ""   : 
            flashcards =  base.filter(Q(title__contains= keyword )|Q(question__contains= keyword ),  theme__in= theme_ids ).order_by("theme","waiting" )

        elif keyword : 
            flashcards =  base.filter(Q(title__contains= keyword )|Q(question__contains= keyword )  ).order_by("theme","waiting" )

        else :
            flashcards = base

    else :
        if level_id != " " and  waiting_id  : 
            waiting = Waiting.objects.get(pk=waiting_id)
            level   = Level.objects.get(pk=level_id)
            flashcards = base.filter(levels = level ,  waiting = waiting ).order_by("theme","waiting" )

        elif level_id != " " and keyword  : 
            level   = Level.objects.get(pk=level_id)
            flashcards = base.filter(Q(title__contains= keyword )|Q(question__contains= keyword ), levels = level  ).order_by("theme","waiting" )

        elif keyword and waiting_id  : 
            waiting = Waiting.objects.get(pk=waiting_id)
            flashcards =  base.filter(Q(title__contains= keyword)|Q(question__contains= keyword),waiting = waiting ).order_by("theme","waiting" )

        else :
            flashcards = base

    data['html'] = render_to_string('flashcard/ajax_list_flashcards.html', { 'flashpack_id': flashpack_id , 'flashcards': flashcards , "teacher" : teacher, "get_flashcard" : True})

    return JsonResponse(data)


def ajax_search_flashpack(request):

    teacher = request.user.teacher
    data = {}

    level_id = request.POST.get('level_id',0)
    subject_id = request.POST.get('subject_id',None)

    teacher_id = get_teacher_id_by_subject_id(subject_id)

    if request.user.is_superuser :
        #flashpacks_ids = Flashpack.objects.values_list("id",flat=True).distinct().filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id),is_share = 1).order_by('level','ranking')
        flashpacks_ids = Flashpack.objects.values_list("id",flat=True).distinct().filter(is_share = 1).order_by('level','ranking')
    else :
        #flashpacks_ids = Flashpack.objects.values_list("id",flat=True).distinct().filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id),is_share = 1).exclude(flashcards = None ,teacher=teacher).order_by('level','ranking')
        flashpacks_ids = Flashpack.objects.values_list("id",flat=True).distinct().filter(is_share = 1).exclude(flashcards = None ,teacher=teacher).order_by('level','ranking')

    keywords = request.POST.get('keywords',None)

    if int(level_id) > 0 :
        level = Level.objects.get(pk=int(level_id))
        theme_ids = request.POST.getlist('theme_id',[])

        if len(theme_ids) > 0 :

            if theme_ids[0] != '' :
                flashpacks = set()
                if keywords :
                    for theme_id in theme_ids :
                        theme = Theme.objects.get(pk = theme_id)
                        #fs = Flashpack.objects.filter( Q(teacher__user_id=teacher_id)|Q(teacher__user__school = teacher.user.school) |Q(teacher__user__first_name__icontains = keywords) |Q(teacher__user__last_name__icontains = keywords)  ,is_share = 1, teacher__user__school = teacher.user.school,  levels = level,  themes = theme  ).exclude(teacher=teacher).order_by('teacher').distinct() 
                        fs = Flashpack.objects.filter(is_share = 1,   levels = level,  themes = theme  ).exclude(teacher=teacher).order_by('teacher').distinct() 

                        flashpacks.update(fs)

                else :
                    for theme_id in theme_ids :
                        theme = Theme.objects.get(pk = theme_id)
                        #fs =  Flashpack.objects.filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id),is_share = 1, themes = theme ,  levels = level ).exclude(teacher=teacher).order_by('teacher').distinct() 
                        fs =  Flashpack.objects.filter(is_share = 1, themes = theme ,  levels = level ).exclude(teacher=teacher).order_by('teacher').distinct() 
                        flashpacks.update(fs)

                    
            else :
                if keywords :            
                    #flashpacks = Flashpack.objects.filter(Q(teacher__user_id=teacher_id)|Q(teacher__user__first_name__icontains= keywords) |Q(teacher__user__last_name__icontains = keywords)    ,is_share = 1,  teacher__user__school = teacher.user.school ,  levels = level  ).exclude(teacher=teacher).order_by('teacher').distinct() 
                    flashpacks = Flashpack.objects.filter(is_share = 1,  teacher__user__school = teacher.user.school ,  levels = level  ).exclude(teacher=teacher).order_by('teacher').distinct() 

                else :
                    #flashpacks = Flashpack.objects.filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id),is_share = 1, levels = level ).exclude(teacher=teacher).order_by('teacher').distinct() 
                    flashpacks = Flashpack.objects.filter(is_share = 1, levels = level ).exclude(teacher=teacher).order_by('teacher').distinct() 

        else :
            if keywords:
                #flashpacks = Flashpack.objects.filter( Q(teacher__user_id=teacher_id)|Q(teacher__user__first_name__icontains = keywords) |Q(teacher__user__last_name__icontains = keywords)   ,teacher__user__school = teacher.user.school,is_share = 1,levels = level ).exclude(teacher=teacher).order_by('teacher').distinct() 
                flashpacks = Flashpack.objects.filter(  is_share = 1,levels = level ).exclude(teacher=teacher).order_by('teacher').distinct() 
            
            else :
                #flashpacks = Flashpack.objects.filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id),is_share = 1, levels = level ).exclude(teacher=teacher).order_by('teacher').distinct() 
                flashpacks = Flashpack.objects.filter(is_share = 1, levels = level ).exclude(teacher=teacher).order_by('teacher').distinct() 
    
    else :
        if keywords:
            #flashpacks = Flashpack.objects.filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id)|Q(teacher__user__first_name__icontains = keywords) |Q(teacher__user__last_name__icontains = keywords)  , is_share = 1  ).exclude(teacher=teacher).order_by('author','ranking').distinct()
            flashpacks = Flashpack.objects.filter(is_share = 1  ).exclude(teacher=teacher).order_by('author','ranking').distinct()
        
        else :
            #flashpacks = Flashpack.objects.filter(Q(teacher__user__school = teacher.user.school)| Q(teacher__user_id=teacher_id),is_share = 1 ).exclude(teacher=teacher).order_by('teacher').distinct()
            flashpacks = Flashpack.objects.filter(is_share = 1 ).exclude(teacher=teacher).order_by('teacher').distinct()

    data['html'] = render_to_string('flashcard/ajax_list_flashpacks.html', {'flashpacks' : flashpacks, 'teacher' : teacher ,  })
 
    return JsonResponse(data)


######################################################################################
######################################################################################
#           AJAX 
######################################################################################
######################################################################################

@csrf_exempt
def ajax_preview_flashcard(request):

    flashcard_id = request.POST.get("flashcard_id") 
    flashcard  = Flashcard.objects.get(id=flashcard_id)
    data = {}
    data['html'] = render_to_string('flashcard/ajax_preview_flashcard.html', {'flashcard' : flashcard,   })
    return JsonResponse(data)



def ajax_comment_flashcard(request):

    id_flashpack = request.POST.get('flashpack')
    id_flashcard = request.POST.get('flashcard')
    flashpack = Flashpack.objects.get(pk = id_flashpack )
    flashcard = Flashcard.objects.get(pk = id_flashcard )

    form = CommentflashcardForm(request.POST or None)
    if form.is_valid():
        nf = form.save(commit=False)
        nf.flashpack = flashpack
        nf.flashcard = flashcard
        nf.save()
    else :
        print(form.errors)

    return redirect( 'validate_flashcards_to_flashpack', id_flashpack )




def ajax_show_comments(request):

    flashcard_id = request.POST.get("flashcard_id") 
    flashcard  = Flashcard.objects.get(id=flashcard_id)

    data = {}
    data['html'] = render_to_string('flashcard/ajax_show_comments.html', {'flashcard' : flashcard,   })
    return JsonResponse(data)
 


def inter_days_repetition(n,inter_days,ef):
    if n == 1 :
        return int(8-(ef-1.3)/(2.5-1.3)*3)
    elif n == 2 :
        return int(13+(ef-1.3)/(2.5-1.3)*8)
    else :
        return int(inter_days*(ef-0.1))
 



@csrf_exempt
def ajax_store_score_flashcard(request):

    flashpack_id = request.POST.get("flashpack_id")
    flashcard_id = request.POST.get("flashcard_id") 
    value        = int(request.POST.get("value") )

    flashpack  = Flashpack.objects.get(id=flashpack_id)
    flashcard  = Flashcard.objects.get(id=flashcard_id)
    
    if request.user.user_type == 0 :

        mf, cr = Madeflashpack.objects.get_or_create( flashpack = flashpack, student = request.user.student  )
        
        if not cr :
            today = time_zone_user(request.user)
            Madeflashpack.objects.filter( flashpack = flashpack, student = request.user.student  ).update(date = today )

        answer, created = Answercard.objects.get_or_create( flashpack = flashpack, flashcard = flashcard , student = request.user.student )
        if answer.answers != "" : answers_str = answer.answers +"-"+str(value)
        else : answers_str =  str(value) 

        if not created :
            weight = answer.weight
        else :
            weight = 2.5
        weight += (0.1-(5-value)*(0.08+(5-value)*0.02))

        if flashpack.is_global :# flashpack annuel 
            try :
                inter_days = (answer.rappel - answer.date).days 
            except :
                inter_days = 0
            length_ans = len( answers_str.split("-") )
            this_inter_days = inter_days_repetition(length_ans,inter_days,weight)
 
        else : 
            this_inter_days = 100000 #si le flashpack n'est pas annuel alors il n'y a pas de répétitions espacées

        rappel = answer.date + timedelta(days = this_inter_days )
        if value :
            Answercard.objects.filter( flashpack = flashpack, flashcard = flashcard , student = request.user.student).update(  weight = weight ,  answers =  answers_str, rappel = rappel   )


    data = {}
    return JsonResponse(data)




@csrf_exempt   # PublieDépublie un parcours depuis form_group et show_group
def ajax_set_flashcard_in_flashpack(request):  
    
    flashpack_id = request.POST.get("flashpack_id")
    flashcard_id = request.POST.get("flashcard_id") 
    statut       = request.POST.get("statut") 
 
 
    flashpack = Flashpack.objects.get(pk = flashpack_id)
    flashcard = Flashcard.objects.get(pk = flashcard_id)
    data = {}

    if statut=="true" or statut == "True":
        flashpack.flashcards.remove(flashcard)
        data["statut"]  = "False"
        data["class"]   = "btn btn-danger"
        data["noclass"] = "btn btn-success"
    else:
        flashpack.flashcards.add(flashcard)
        data["statut"]  = "True"
        data["class"]   = "btn btn-success"
        data["noclass"] = "btn btn-danger"

    data["nb"] = flashpack.flashcards.count()
 


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

    Flashpack.objects.filter(pk = int(parcours_id)).update(is_share = statut)
 
    return JsonResponse(data) 

@csrf_exempt   # PublieDépublie un parcours depuis form_group et show_group
def ajax_publish_list_flashpack(request):  

    flashpack_id = request.POST.get("flashpack_id")
    statut = request.POST.get("statut")
    data = {}
    if statut=="true" or statut == "True":
        statut = 0
        data["statut"]  = "false"
        data["style"]   = "#dd4b39"
        data["class"]   = "legend-btn-danger"
        data["noclass"] = "legend-btn-success"
        data["label"]   = "Non publié"
    else:
        statut = 1
        data["statut"]  = "true"
        data["style"]   = "#00a65a"
        data["class"]   = "legend-btn-success"
        data["noclass"] = "legend-btn-danger"
        data["label"]   = "Publié"
 
    Flashpack.objects.filter(pk = int(flashpack_id)).update(is_publish = statut)

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
 
    flashpack   = Flashpack.objects.get(pk=target_id)
    if checked == "false" :
        flashpack.groups.remove(group)
    else :
        flashpack.groups.add(group)
        groups = (group,)
        attribute_all_documents_of_groups_to_all_new_students(groups)
    for g in flashpack.groups.all():
        html += "<small>"+g.name +" (<small>"+ str(g.just_students_count())+"</small>)</small> "
    change_link = "change"

    data['html']        = html
    data['change_link'] = change_link
    return JsonResponse(data)




@csrf_exempt # PublieDépublie un exercice depuis organize_parcours
def ajax_is_favorite(request):  

    target_id = int(request.POST.get("target_id",None))
    statut = int(request.POST.get("statut"))
    status = request.POST.get("status") 
    data = {}
 
    if statut :
        Flashpack.objects.filter(pk = target_id).update(is_favorite = 0)
        data["statut"] = "<i class='fa fa-star text-default' ></i>"
        data["fav"] = 0
    else :
        Flashpack.objects.filter(pk = target_id).update(is_favorite = 1)  
        data["statut"] = "<i class='fa fa-star   text-is_favorite' ></i>"
        data["fav"] = 1     

    return JsonResponse(data) 



def ajax_chargethemes(request):
    level_id =  request.POST.get("id_level")
    id_subject =  request.POST.get("id_subject")
    teacher = request.user.teacher

    teacher_id = get_teacher_id_by_subject_id(id_subject)

    data = {}
    level =  Level.objects.get(pk = level_id)

    thms = level.themes.values_list('id', 'name').filter(subject_id=id_subject).order_by("name")
    data['themes'] = list(thms)
    flashcards = Flashcard.objects.filter( levels = level  ).order_by('teacher').distinct()[:300]

    data['html'] = render_to_string('qcm/ajax_list_parcours.html', {'flashcards' : flashcards , })

    return JsonResponse(data)



@csrf_exempt 
def ajax_attribute_this_flashcard(request):  

    id_level =  request.POST.get("id_level")
    id_theme =  request.POST.get("id_theme")
    data = {}

    level =  Level.objects.get(pk = id_level)

    waitings = level.waitings.values_list('id', 'name').filter(theme_id=id_theme) 
    data['waitings'] = list(waitings)
 
    return JsonResponse(data)


@csrf_exempt 
def ajax_chargewaitings(request):  

    id_level =  request.POST.get("id_level")
    id_theme =  request.POST.get("id_theme")
    data = {}

    level =  Level.objects.get(pk = id_level)

    waitings = level.waitings.values_list('id', 'name').filter(theme_id=id_theme) 
    data['waitings'] = list(waitings)
 
    return JsonResponse(data)



@csrf_exempt 
def ajax_chargeknowledges(request): 

    id_waiting =  request.POST.get("id_waiting")

    data = {}
    waiting =  Waiting.objects.get(pk = id_waiting)

    knowledges = waiting.knowledges.values_list('id', 'name')
    data['knowledges'] = list(knowledges)
 
    return JsonResponse(data)



def ajax_charge_groups(request):  # utilisé par form_quizz et form_folder aussi

    teacher = request.user.teacher
    data = {} 
    subject_id = request.POST.get('id_subject', None)
    groups = Group.objects.values_list("id","name").filter(Q(teacher=teacher)|Q(teachers=teacher),subject_id =  subject_id)

    data["groups"] = list(groups)

    return JsonResponse(data)


def ajax_charge_groups_level(request):  # utilisé par form_folder aussi

    teacher = request.user.teacher
    data = {} 
    subject_id = request.POST.get('id_subject', None)
    level_id   = request.POST.get('id_level', None)
    groups     = Group.objects.values_list("id","name").filter(Q(teacher=teacher)|Q(teachers=teacher),subject_id =  subject_id, level_id =  level_id)

    data["groups"] = list(groups)

    # gère les propositions d'image d'accueil    
    level =  Level.objects.get(pk = level_id)
    data['imagefiles'] = None
    imagefiles = level.level_folders.values_list("vignette", flat = True).filter(subject_id=subject_id).exclude(vignette=" ").distinct()
    if imagefiles.count() > 0 :
        data['imagefiles'] = list(imagefiles)

    return JsonResponse(data)


def ajax_charge_folders(request):  

    teacher = request.user.teacher
    data = {} 
    group_ids = request.POST.getlist('group_ids', None)

    if len(group_ids) :
        fldrs = set()
        prcs  = set()
        thms  = set()
        lvls  = set()
        for group_id in group_ids :
            group = Group.objects.get(pk=group_id)
            fldrs.update(group.group_folders.values_list("id","title").filter(is_trash=0))
            prcs.update(group.group_parcours.values_list("id","title").filter(is_trash=0,folders=None))
            thms.update(group.level.themes.values_list('id', 'name').filter(subject =group.subject))
            lvls.update((group.level.id,))
        data['folders']  =  list( fldrs )
        data['parcours'] =  list( prcs )
        data['themes']   =  list( thms )
        data['lvls']     =  list( lvls )
        data['subject']  =  group.subject.id

    else :
        data['folders']  =  []
        data['parcours'] =  []
        data['themes']   =  []
        data['lvls']     =  []
        data['subject']  =  ""

    return JsonResponse(data)



def ajax_charge_parcours(request): # utilisé par form_quizz et form_folder aussi

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



def ajax_charge_parcours_without_folder(request): # utilisé que par form_folder mais placé ici pour homogénéiser la structure 

    teacher = request.user.teacher
    data = {} 
    groups_ids = request.POST.getlist('groups_ids', None)

    if len(groups_ids) :
        parcourses = set()
        for groups_id in groups_ids :
            group = Group.objects.get(pk=groups_id)
            parcourses.update(group.group_parcours.values_list("id","title").filter(is_trash=0))

        data['parcours'] =  list( parcourses )
    else :
        data['parcours'] =  []

    return JsonResponse(data)


