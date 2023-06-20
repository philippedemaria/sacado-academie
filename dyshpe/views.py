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
from qcm.models import Parcours
from account.forms import  UserForm,  NewpasswordForm, BaseUserFormSet 
from datetime import datetime , timedelta
from setup.views import cmd_abonnement , champs_briqueCA
from general_fonctions import * 


 

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
    
    else:  
         

        context = {   }
        response = render(request, 'dyshpe/home.html', context)
        return response




def try_it(request,idl):


	form = AuthenticationForm()
	np_form = NewpasswordForm()

	group =  Group.objects.filter(level_id = idl,formule_id=5).last()
	hbook = Holidaybook.objects.filter(level_id = idl, is_publish = 1).first()
	parcours = group.group_parcours.filter(ranking=0).first()
	relationships = parcours.parcours_relationship.filter(is_publish=1).order_by("ranking")

	return render(request, 'holidaybook/try_it_book.html', {'parcours': parcours , 'relationships': relationships ,  'hbook' : hbook ,  'form' : form ,  'np_form' : np_form })





def buy_it(request,idl):

    userFormset = formset_factory(UserForm, extra = 2,  formset=BaseUserFormSet)

    hbook = Holidaybook.objects.filter(level_id=idl).first()

    level   = Level.objects.get(pk=idl)
    group =  Group.objects.filter(level_id = idl,formule_id=5).last()
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
                student,created_s = Student.objects.update_or_create(user = user, defaults = { "task_post" : 1 , "level_id" : idl })

                if created_s : 
                    students_in.append(student) # pour associer les enfants aux parents 

                    adhesion = Adhesion.objects.create( student = student , level_id = idl , start = today , amount = amount , stop = stop , formule_id  = 5 , year  = today.year , is_active = 0)
                    test = attribute_all_documents_of_groups_to_a_new_student([group], student)

            i+=1

        facture.adhesions.add(adhesion)
        parent.students.set(students_in)
        formule = Formule.objects.get(pk=5)

        cmd = cmd_abonnement(formule,facture.id)
 
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

    clas_sups = ["CE1","CE2","CM1","CM2","6ème","5ème","4ème","3ème","2nde","1ère","Terminale"]
    classe_sup = clas_sups[idl-1]

    return render(request, 'holidaybook/buy_it_book.html', {'hbooks': hbooks , 'hbook': hbook ,    'userFormset' : userFormset, 'group' : group , 'classe_sup' : classe_sup , 'level' : level, 
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

    exercise  = Exercise.objects.get(pk = id)
    template = "holidaybook/show_this_exercise.html"
    context = {'exercise': exercise, }

    return render(request, template, context)