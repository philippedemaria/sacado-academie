from django.shortcuts import render
from django.forms import formset_factory
from django.contrib.auth.decorators import  permission_required,user_passes_test
from django.contrib.auth.forms import    AuthenticationForm
from django.db.models import Q 
from django.utils import formats, timezone
from account.decorators import user_is_board
from account.models import User,Parent, Student , Adhesion , Facture
from .models import *
from group.models import Group
from setup.models import Formule  
from qcm.models import Parcours, Exercise
from account.forms import  UserForm,  NewpasswordForm, BaseUserFormSet 
from datetime import datetime , timedelta
from setup.views import cmd_abonnement , champs_briqueCA
from general_fonctions import * 


def holidaybooks(request):

	form = AuthenticationForm()
	np_form = NewpasswordForm()

	hbooks = Holidaybook.objects.order_by("level__ranking")
	return render(request, 'holidaybook/holidaybooks.html', {'hbooks': hbooks ,  'form' : form ,  'np_form' : np_form    })



def try_it(request,idg):


    form = AuthenticationForm()
    np_form = NewpasswordForm()

    group = Group.objects.get(pk = idg)
    hbook = group.holidaybook
    parcours = group.group_parcours.first()
    relationships = parcours.parcours_relationship.filter(is_publish=1).order_by("ranking")

    return render(request, 'holidaybook/try_it_book.html', {'parcours': parcours , 'relationships': relationships ,  'hbook' : hbook ,  'form' : form ,  'np_form' : np_form })





def buy_it(request,idg):

    userFormset = formset_factory(UserForm, extra = 2,  formset=BaseUserFormSet)

    group = Group.objects.get(pk = idg)
    hbook = group.holidaybook

    level    = hbook.level 
    parcours = group.group_parcours.filter(ranking=1).first()

    form = AuthenticationForm()
    np_form = NewpasswordForm()
    today = datetime.now().replace(tzinfo=timezone.utc)

    formset     = userFormset(request.POST or None)
    if formset.is_valid():
        i = 0
        for form in formset :

            last_name  = form.cleaned_data["last_name"]
            first_name = form.cleaned_data["first_name"]
            username   = form.cleaned_data["username"]
            password_no_crypted = form.cleaned_data["password1"] 
            password  =  make_password(form.cleaned_data["password1"])
            email     =  form.cleaned_data["email"]  

            this_year  = today.year
            amount     = 5.00
            stop       = datetime(this_year,9,1).replace(tzinfo=timezone.utc)

            students_in = list()
            adhesion_in = list()
            if i ==0 :

                user_parent, created = User.objects.update_or_create(username = username, password = password ,  user_type = 1 , defaults = { "last_name" :  last_name  , "first_name" :  first_name  , "email" :  email  , "country_id" : 5 ,  "school_id" : 50 ,  "closure" : None })
                parent,create = Parent.objects.update_or_create(user = user_parent, defaults = { "task_post" : 1 })

                facture = Facture.objects.create(chrono = "BL_" +  user_parent.last_name +"_"+str(today) ,  user_id = user_parent.id , file = "" , date = today , orderID = "" , is_lesson = 1  ) #orderID = Numéro de paiement donné par la banque"


            else :

                user, created = User.objects.update_or_create(username = username, password = password , user_type = 0 , defaults = { "last_name" :last_name , "first_name" : first_name  , "email" : email , "country_id" : 5 ,  "school_id" : 50 , "closure" : stop })
                student,created_s = Student.objects.update_or_create(user = user, defaults = { "task_post" : 1 , "level" : level })

                if created_s : 
                    students_in.append(student) # pour associer les enfants aux parents 
                    group.students.add(student)
                    adhesion = Adhesion.objects.create( student = student , level = level , start = today , amount = amount , stop = stop , formule_id  = 5 , year  = today.year , is_active = 0)
                    test = attribute_all_documents_of_groups_to_a_new_student([group], student)


            i+=1

        facture.adhesions.add(adhesion)
        parent.students.set(students_in)
        formule = Formule.objects.get(pk=5)

        cmd = cmd_abonnement(formule,facture.id)
        try :
            sacado_msg = "Achat d'un cahier Vacances"
            send_mail("Inscription Cahier Vacances SACADO ACADÉMIE", sacado_msg, settings.DEFAULT_FROM_EMAIL, [facture.user.email,"sacado.academie@gmail.com"]) 
        except :
            pass
        billing='<?xml version="1.0" encoding="utf-8" ?><Billing><Address><FirstName>{}</FirstName><LastName>{}</LastName><Address1>Sarlat</Address1><ZipCode>24200</ZipCode><City>Sarlat</City><CountryCode>250</CountryCode></Address></Billing>'.format("Académie","SACADO ACADÉMIE")
        try : y,m,d = stop.split("T")[0].split("-")
        except : y,m,d = str(stop).split(" ")[0].split("-")
        end_day = d+"-"+m+"-"+y
        champs_val=champs_briqueCA(amount,cmd,user_parent.email,1,billing)

        context={ 'formule' : formule , 'level' : level , 'parent' : parent ,   'amount' : amount , 'end_day' : end_day , 'champs_val':champs_val , 'hbook': hbook ,  }
        return render(request, 'setup/brique_credit_agricole.html', context) 


    else :
        print("erreurs => ", formset.errors)

    hbooks = Holidaybook.objects.filter(is_publish = 1).order_by("level__ranking")

    clas_sups = ["CE1","CE2","CM1","CM2","6ème","5ème","4ème","3ème","2nde","1 es","1 spé"]
    try : classe_sup = clas_sups[hbook.group.level.id-1]
    except : classe_sup = clas_sups[hbook.group.level.id]

    return render(request, 'holidaybook/buy_it_book.html', {'hbooks': hbooks , 'hbook': hbook , 'userFormset' : userFormset, 'group' : group , 'classe_sup' : classe_sup , 'level' : level, 
    'form' : form ,  'np_form' : np_form     })

 


@user_passes_test(user_is_board) 
def create_holidaybook(request):
 
    form = RateForm(request.POST or None )

    if form.is_valid():
        nf = form.save(commit = False)
        nf.author = request.user
        nf.save()

        messages.success(request,"Création des groupes et séquences effectuée avec succès.")
        return redirect('list_rates')

    else:
        
        print(form.errors)

    
    context = {'form': form, }

    return render(request, 'association/form_holidaybook.html', context)

 

def show_this_hbook_exercise(request,ide):

    exercise  = Exercise.objects.get(pk = ide)
    context = {'exercise': exercise, }

    return render(request, "holidaybook/show_this_exercise.html", context)




def engage_holidaybooks(request):

    form = AuthenticationForm()
    np_form = NewpasswordForm()

    hbooks = Holidaybook.objects.order_by("level__ranking")
    
    if request.method == "POST" :
        engage_books = request.POST.getlist("engage_books")

        for eb in engage_books :
            hb = Holidaybook.objects.get(pk=eb)
            if hb.is_publish : hb.is_publish = 0
            else : hb.is_publish = 1
            hb.save() 


    return render(request, 'holidaybook/engage_holidaybooks.html', {'hbooks': hbooks ,  'form' : form ,  'np_form' : np_form    })



 

def dash_holidaybook_student(request):

    student = request.user.student
    group   = student.students_to_group.filter(name__startswith="Cahier", level=student.level).first()
    parcourses = group.group_parcours.all()

    context = {'parcourses': parcourses, 'student' : student }

    return render(request, "holidaybook/show_all_parcours_days.html", context)



