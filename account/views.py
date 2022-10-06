#################################
#### Auteur : philipe Demaria 
#### pour SACADO
#################################
import html
import random
import json
import re
from django.conf import settings # récupération de variables globales du settings.py
from statistics import median, StatisticsError
import csv
import pytz
from datetime import datetime , timedelta
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.db.models import Q, Avg, Sum
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, reverse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.contrib.auth import   logout
from account.decorators import user_can_read_details, who_can_read_details, can_register, is_manager_of_this_school
from account.models import User, Teacher, Student, Resultknowledge, Parent , Response , Newpassword , Avatar , Background
from group.models import Group, Sharing_group
from qcm.models import Exercise, Parcours, Relationship, Resultexercise, Studentanswer
from sendmail.models import Communication
from socle.models import Level
from socle.models import Theme
from sendmail.forms import EmailForm
from .forms import UserForm, UserUpdateForm, StudentForm, TeacherForm, ParentForm, ParentUpdateForm, ManagerUpdateForm, NewUserTForm,ManagerForm , ResponseForm , NewpasswordForm , SetnewpasswordForm , AvatarForm , AvatarUserForm, BackgroundForm , BackgroundUserForm
from templated_email import send_templated_mail
from general_fonctions import *
from school.views import this_school_in_session
from qcm.views import tracker_execute_exercise
import uuid



def creation_auto(request):# user et parent du parent
    students = Student.objects.filter(user__username__contains="ProfSacAdo",user__user_type=0).exclude(level=6)
     
    for student in students :
        group = student.students_to_group.first()
        user.student.username = "Eleve_test_"+str(student.level)+"_"+group.name.split(" ")[0]
        user.save()
        messages.success(request, student )
        groups = [group]
        attribute_all_documents_of_groups_to_a_new_student(groups, student)

    return redirect('index')




def logout_view(request):
    tracker_execute_exercise(False,request.user)
    logout(request)
    return redirect('index')

                 

def list_teacher(request):
    teachers = User.objects.filter(user_type=User.TEACHER).exclude(pk__lte=131100)
    return render(request, 'account/list_teacher.html', {'teachers': teachers})


def navigation(group, id):
    students_ids = group.students.values_list('user__id', flat=True).order_by("user__last_name")
    index = list(students_ids).index(id)

    if len(students_ids) > 1:
        if index == 0:
            sprev_id = False
            snext_id = students_ids[1]
        elif index == len(students_ids) - 1:
            sprev_id = students_ids[index - 1]
            snext_id = False
        else:
            sprev_id = students_ids[index - 1]
            snext_id = students_ids[index + 1]
    else:
        sprev_id = False
        snext_id = False

    return sprev_id, snext_id


class DashboardView(TemplateView): # lorsque l'utilisateur vient de se connecter.
    template_name = "dashboard.html"

    # Lors de la connexion, analyse les exercices de tous les parcours qui doivent être visible à partir de cette date

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)

        if self.request.user.is_authenticated:

            this_user = User.objects.get(pk=self.request.user.id)
            
            today = time_zone_user(this_user)
            relationships = Relationship.objects.filter(is_publish = 0,start__lte=today,exercise__supportfile__is_title=0)
            for r in relationships :
                Relationship.objects.filter(id=r.id).update(is_publish = 1)

            if self.request.user.is_teacher:  # Teacher

                teacher = Teacher.objects.get(user=self.request.user.id)

                groups = Group.objects.filter(teacher = teacher)

                relationships = Relationship.objects.filter(Q(is_publish = 1)|Q(start__lte=today), parcours__teacher=teacher, date_limit__gte=today,exercise__supportfile__is_title=0).order_by("parcours")
                parcourses = Parcours.objects.filter(teacher=teacher,is_trash=0) # parcours non liés à un groupe

                communications = Communication.objects.filter(active=1)
                parcours_tab = Parcours.objects.filter(students=None, teacher=teacher)

                context = {'this_user': this_user, 'teacher': teacher, 'relationships': relationships,
                           'parcourses': parcourses, 'groups': groups, 'parcours_tab': parcours_tab, 'today' : today , 
                           'communications': communications, }
            elif self.request.user.is_student:  # Student
                student = Student.objects.get(user=self.request.user.id)

                parcourses = Parcours.objects.filter(students=student, linked=0, is_evaluation=0, is_publish=1,is_trash=0)
                groups = student.students_to_group.all()

                parcours = []
                for p in parcourses:
                    parcours.append(p)
 

                relationships = Relationship.objects.filter(Q(is_publish=1) | Q(start__lte=today), parcours__in=parcours, is_evaluation=0, date_limit__gte=today,exercise__supportfile__is_title=0).order_by("date_limit")
                exercise_tab = []
                for r in relationships:
                    if r not in exercise_tab:
                        exercise_tab.append(r.exercise)

                num = 0
                for e in exercise_tab:
                    if Studentanswer.objects.filter(student=student, exercise=e).count() > 0:
                        num += 1

                nb_relationships = Relationship.objects.filter(Q(is_publish = 1)|Q(start__lte=today), parcours__in=parcours, date_limit__gte=today,exercise__supportfile__is_title=0).count()
                try:
                    ratio = int(num / nb_relationships * 100)
                except:
                    ratio = 0

                ratiowidth = int(0.9*ratio)

                evaluations = Parcours.objects.filter(start__lte=today, stop__gte=today, students=student, is_evaluation=1,is_trash=0)
                studentanswers = Studentanswer.objects.filter(student=student)

                exercises = []
                for studentanswer in studentanswers:
                    if not studentanswer.exercise in exercises:
                        exercises.append(studentanswer.exercise)

                relationships_in_late = Relationship.objects.filter(Q(is_publish=1) | Q(start__lte=today),
                                                                    parcours__in=parcours, is_evaluation=0,
                                                                    date_limit__lt=today).exclude(exercise__in=exercises).order_by("date_limit")

                context = {'student_id': student.user.id, 'student': student, 'relationships': relationships,
                           'ratio': ratio, 'evaluations': evaluations, 'ratiowidth': ratiowidth, 'today' : today , 
                           'relationships_in_late': relationships_in_late}
            elif self.request.user.is_parent:  # Parent

                parent = Parent.objects.get(user=self.request.user)
                students = parent.students.order_by("user__first_name")
                context = {'parent': parent, 'students': students, 'today' : today ,  }

        else: ## Anonymous

            form = AuthenticationForm()
            u_form = UserForm()
            t_form = TeacherForm()
            s_form = StudentForm()
            levels = Level.objects.all()
            exercise_nb = Exercise.objects.filter(supportfile__is_title=0).count()

            exercises = Exercise.objects.filter(supportfile__is_title=0)

            i = random.randrange(0, len(exercises))
            exercise = exercises[i]

            context = {'form': form, 'u_form': u_form, 't_form': t_form, 's_form': s_form,
                       'levels': levels, 'exercise_nb': exercise_nb, 'exercise': exercise }
 
        return context




########################################            MON COMPTE               #########################################

def myaccount(request):
 
    if request.user.is_teacher:
        teacher = Teacher.objects.get(user_id=request.session.get('user_id'))
        context = {'teacher': teacher, }
        return render(request, 'account/teacher_account.html', context)
    else:
        student = Student.objects.get(user_id=request.session.get('user_id'))
        context = {'student': student, }

        return render(request, 'account/student_account.html', context)







########################################            AVATAR                   #########################################

#@user_is_parcours_teacher
def create_avatar(request, id ):
 
    if not request.user.is_superuser : 
        return redirect('index')

    form = AvatarForm(request.POST or None ,  request.FILES or None, )
    if form.is_valid():
        form.save()
        return redirect('list_avatars')
    else:
        print(form.errors)

    context = {'form': form }

    return render(request, 'account/avatar_admin_form.html', context)



 

def delete_avatar(request,id  ):
    if not request.user.is_superuser : 
        return redirect('index')

    avatar = Avatar.objects.get(pk=id)
    avatar.delete()
    return redirect('list_avatars') 



def list_avatars(request) :
    
    if not request.user.is_superuser : 
        return redirect('index')
    
    avatars = Avatar.objects.all()
    
    context = {  'avatars': avatars,   }
    return render(request, 'account/list_avatars.html', context)

 


def avatar(request) :

    user = User.objects.get(pk = request.user.id )
    avatar_form = AvatarUserForm(request.POST or None, request.FILES or None, instance = user  ) 


    if request.method == 'POST':
        if avatar_form.is_valid():
            user.avatar = request.POST.get("avatar")
            user.save()
            return redirect('profile')
        else:
            messages.error(request, user_form.errors)

    if request.user.user_type == 0 : adult = 0
    else : adult = 1

    avatars = Avatar.objects.filter(adult=adult)

    context = {'avatar_form': avatar_form, 'avatars' : avatars}
    return render(request, 'account/avatar_form.html', context)




#####################################
########################################            BACKGROUND                   #########################################

#@user_is_parcours_teacher
def create_background(request, id ):
 
    if not request.user.is_superuser : 
        return redirect('index')

    form = BackgroundForm(request.POST or None ,  request.FILES or None, )
    if form.is_valid():
        form.save()
        return redirect('list_backgrounds')
    else:
        print(form.errors)

    context = {'form': form }

    return render(request, 'account/background_admin_form.html', context)


def delete_background(request,id  ):
    if not request.user.is_superuser : 
        return redirect('index')

    background = Background.objects.get(pk=id)
    background.delete()
    return redirect('list_backgrounds') 



def list_backgrounds(request) :
    
    if not request.user.is_superuser : 
        return redirect('index')
    
    backgrounds = Background.objects.all()
    
    context = {  'backgrounds': backgrounds,   }
    return render(request, 'account/list_backgrounds.html', context)

 


def background(request) :

    user = User.objects.get(pk = request.user.id )
    background_form = BackgroundUserForm(request.POST or None, request.FILES or None, instance = user  ) 


    if request.method == 'POST':
        if background_form.is_valid():
            user.background = request.POST.get("background")
            print(request.POST.get("background"))
            user.save()
            return redirect('index')
        else:
            messages.error(request, user_form.errors)

    backgrounds = Background.objects.all()

    context = {'background_form': background_form, 'backgrounds' : backgrounds}
    return render(request, 'account/background_form.html', context)




#####################################

 
def send_to_teachers(request):
    users = User.objects.filter(user_type=2)
    context = {"users" : users, }
    return render(request,'account/send_message_to_teachers.html', context)




def message_to_teachers_sent(request):
    subject = request.POST.get("subject")
    message = request.POST.get("message")
    users = request.POST.getlist("users")

    rcv = []
    for u_id in users:
        u = User.objects.get(pk=u_id)
        if u.email:
            rcv.append(u.email)

    sending_mail(subject, cleanhtml(unescape_html(message)),  settings.DEFAULT_FROM_EMAIL , rcv)
 
    messages.success(request, 'message envoyé')

    return redirect("dashboard")  


#########################################Student #####################################################################


#@can_register
#@is_manager_of_this_school
def register_student_from_admin(request):
    """"
    Enregistre un enseignant depuis la console admin d'un établissement
    """
    group_id = request.POST.get("group")
    group = Group.objects.get(pk=group_id)

    user_form = NewUserTForm(request.POST or None) 
    if request.method == 'POST':
        if user_form.is_valid():
            u_form = user_form.save(commit=False)
            u_form.password = make_password("sacado2020")
            u_form.user_type = User.STUDENT
            u_form.school = this_school_in_session(request)
            u_form.username = get_username(request, u_form.last_name, u_form.first_name)
            u_form.save()

            # On récupère les parcours, exercices et cours du premier élève de ce groupe et on les attribue au nouvel élève.
            try :
                student = Student.objects.create(user=u_form, level=group.level, task_post=1)
                group.students.add(student)
                test = attribute_all_documents_of_groups_to_a_new_student([group], student)
                phrase = ""
                if test :
                    phrase = " Les documents du groupe lui ont été attribués."
                messages.success(request, 'Le profil a été changé avec succès !'+phrase)
            except :
                print("attribution et création non établies")

            send_templated_mail(
                template_name="student_registration",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[u_form.email, ],
                context={"student": u_form, }, )

            return redirect('school_groups')
        else:
            messages.error(request, user_form.errors)
 
    return redirect('index')





def register_student(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            username = user_form.cleaned_data['last_name'] + user_form.cleaned_data['first_name']
            user = user_form.save(commit=False)
            user.username = username
            user.user_type = User.STUDENT
            password = request.POST.get("password1")
            ######################### Choix du groupe  ###########################################
            if request.POST.get("choose_alone"):  # groupe sans prof
                # l'élève rejoint le groupe par défaut sur le niveau choisi
                teacher = request.user.teacher  
                group = Group.objects.get(teacher=teacher, level_id=int(request.POST.get("level_selector")), lock = 0 , formule_id=1)
                parcours = Parcours.objects.filter(teacher=teacher, level=group.level)

            else:  # groupe du prof  de l'élève
                code_group = request.POST.get("group")
                if Group.objects.filter(teacher=teacher, code=code_group, lock = 0 ).exists():
                    group = Group.objects.get(code=code_group)
                    parcours = Parcours.objects.filter(teacher=group.teacher, level=group.level,is_trash=0)
                else :
                    parcours = []
                    group = None
            #######################################################################################
            if group :
                user.save()
                student = Student.objects.create(user=user, level=group.level)
                try :
                    attribute_all_documents_of_groups_to_a_new_student([group], student)
                except :
                    print("Attribution et création non établies")

                user = authenticate(username=username, password=password)
                login(request, user,  backend='django.contrib.auth.backends.ModelBackend' )
                request.session["user_id"] = request.user.id
                messages.success(request, "Inscription réalisée avec succès !")               
                if user_form.cleaned_data['email']:
                    send_templated_mail(
                        template_name="student_registration",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user_form.cleaned_data['email'], ],
                        context={"student": user, }, )
            else:
                messages.error(request, "Erreur lors de l'enregistrement. Vous devez spécifier un groupe...")     

        else:
            messages.error(request, "Erreur lors de l'enregistrement. Reprendre l'inscription...")
    return redirect('index')


 



#@can_register
#@is_manager_of_this_school
def update_student(request, id,idg=0):  
    """
    Upadta par un admin d'un établissement
    """
    user = get_object_or_404(User, pk=id)
    today = time_zone_user(user)
    student = Student.objects.get(user=user)
    user_form = UserUpdateForm(request.POST or None, request.FILES or None, instance=user)
    student_form = StudentForm(request.POST or None, request.FILES or None, instance=student)
    if request.method == "POST":
        if all((user_form.is_valid(), student_form.is_valid())):
            user_form.save()
            student_f = student_form.save(commit=False)
            student_f.user = user
            student_f.save()
            messages.success(request, 'Le profil a été changé avec succès !')
        if idg == 0 :
            return redirect('school_students')
        else:
            group = Group.objects.get(pk=idg)
            test = attribute_all_documents_of_groups_to_a_new_student([group], student)
            phrase = ""
            if test :
                phrase = " Les documents du groupe lui ont été attribués."
            messages.success(request, 'Le profil a été changé avec succès !'+phrase)
            return redirect('school_groups')

    return render(request, 'account/student_form.html',
                  {'user_form': user_form, 'form': student_form, 'student': student, 'communications' : [],  'idg': idg  , 'today' : today })


def switch_teacher_student(request,idg): #idg = group_id  
    """
    Updete par un admin d'un établissement
    """
    user = request.user
    request.session["user_id_switch_student_teacher"] = request.user.id
    group = Group.objects.get(pk = idg)
    try :
        student  = group.students.filter(user__username__contains= "_e-test").last()
        user = authenticate(username=student.user.username, password = "sacado2020")
        login(request, user,  backend='django.contrib.auth.backends.ModelBackend' )
        request.session["user_id"] = request.user.id
        messages.success(request,"Vous êtes maintenant sur l'interface Elève de votre groupe.")
    except :
        messages.error(request,"Erreur sur la vue élève. Vue élève indisponible. Contacter l'équipe SACADO.")

    return redirect("index")


def switch_student_teacher(request): #idg = group_id  
    """
    Update par un admin d'un établissement
    """
    password = request.POST.get("password") 
    student  = request.user.student
    group    = student.students_to_group.last()
    user     = group.teacher.user
    try :
        user = authenticate(username= user.username, password = password)
        login(request, user,  backend='django.contrib.auth.backends.ModelBackend' )
        request.session["user_id"] = request.user.id
        messages.success(request,"Vous êtes revenu sur l'interface Enseignant.")
    except :
        messages.error(request,"Erreur de mot de passe.")
    return redirect("index")


#@can_register
#@is_manager_of_this_school
def update_student_by_admin(request, id):  
    """
    Upadta par un admin d'un établissement
    """
    school = this_school_in_session(request)
    user = get_object_or_404(User, pk=id)
    today = time_zone_user(user)
    student = Student.objects.get(user=user)
    user_form = UserUpdateForm(request.POST or None, request.FILES or None, instance=user)
    student_form = StudentForm(request.POST or None, request.FILES or None, instance=student)
    groups = Group.objects.filter(teacher__user__school = school).order_by("name")


    if request.method == "POST":
        if all((user_form.is_valid(), student_form.is_valid())):
            user_form.save()
            student_f = student_form.save(commit=False)
            student_f.user = user
            student_f.save()
            messages.success(request, 'Le profil a été changé avec succès !')
            
            group_ids = request.POST.getlist("group_ids")
            these_groups = student.students_to_group.all()
            for g in these_groups:
                g.students.remove(student_f)
            for group_id in group_ids:
                group = Group.objects.get(pk = group_id)
                group.students.add(student_f)

            return redirect('school_students')

    return render(request, 'account/student_form_by_admin.html',
                  {'user_form': user_form, 'form': student_form, 'student': student, 'communications' : [],  'groups': groups  , 'today' : today })





@csrf_exempt
def update_student_by_ajax(request):
    student_id = int(request.POST.get("student_id"))
    is_name = int(request.POST.get("is_name"))
    value = request.POST.get("value")
    if is_name == 0:
        User.objects.filter(id=int(student_id)).update(first_name=value)
    elif is_name == 1:
        User.objects.filter(id=int(student_id)).update(last_name=value)
    elif is_name == 2:
        User.objects.filter(id=int(student_id)).update(email=value)
    else:
        User.objects.filter(id=int(student_id)).update(username=value)

    data = {'html': value}

    return JsonResponse(data)



def delete_student(request, id,idg):

    student = get_object_or_404(Student, user_id=id)
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
    return redirect('update_group', idg )


def newpassword_student(request, id,idg):

    student = get_object_or_404(Student, user_id=id)
    user = student.user
    user.set_password("sacado2020")
    user.save()

    sending_mail('Réinitialisation de mot de passe Sacado', "Bonjour, votre mot de passe est réinitialisé. Il est générique. Votre identifiant est : "+user.username+"\n\n Votre mot de passe est : sacado2020.\n\n  Pour plus de sécurité, vous devez le modifier dès votre connexion.\n\n Pour vous connecter, redirigez-vous vers https://sacado-academie.fr et cliquez sur le bouton bleu Se connecter.\n Ceci est un mail automatique. Ne pas répondre.", settings.DEFAULT_FROM_EMAIL, [user.email])
 
    if idg > 0 :
        return redirect('show_group', idg )
    else :
        return redirect('school_students')


def knowledges_of_a_student(student, theme):
    exercise_tab = []
    parcourses = student.students_to_parcours.all()

    for parcours in parcourses:
        exercises = parcours.exercises.filter(theme=theme)
        for exercise in exercises:
            if not exercise in exercise_tab:
                exercise_tab.append(exercise)

    knowledges = []
    for exercise in exercise_tab:
        if not exercise.knowledge in knowledges:
            knowledges.append(exercise.knowledge)

    return knowledges 


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
            sending_mail( cleanhtml(subject), cleanhtml(texte) , settings.DEFAULT_FROM_EMAIL , rcv)
 

        else :
            print(form.errors)
 


def logged_user_has_permission_to_this_student(user_reader, student) :

    test = False
    if user_reader.is_authenticated : 
        if user_reader.is_teacher :
            groups = Group.objects.filter(teacher__user = user_reader) # tous le groupes du prof
            for group in groups :
                if student in group.students.all() :
                    test = True
                    break

            sgroups = Sharing_group.objects.filter(teacher__user = user_reader) # tous le groupes partagés du prof
     
            for sgroup in sgroups :
                if student in sgroup.group.students.all() :
                    test = True
                    break

        elif user_reader.is_parent : 
            parent = Parent.objects.get(user = user_reader)
            if student in parent.students.all():
                test = True

        else : 
            if user_reader == student.user :
                test = True    
    return test

 

 
def detail_student(request, id):

    student = Student.objects.get(user_id=id)
    tracker_execute_exercise(False,student.user)

    if not logged_user_has_permission_to_this_student(request.user, student) :
        messages.error(request, "Erreur...Vous n'avez pas accès à ces résultats.")
        return redirect('index')

    today = time_zone_user(request.user) 
    parcourses_publish = Parcours.objects.filter(students=student,is_publish=1,is_trash=0)
    parcourses = Parcours.objects.filter(students=student)
    
    datas =[]
    themes = student.level.themes.all() # Tous les thèmes du niveau de l'élève
    for t in themes :
        theme={}
        theme["name"]= t
        relationships = Relationship.objects.filter( students=student,  exercise__theme = t,exercise__supportfile__is_title=0).order_by("exercise__knowledge") # Tous les exercices du niveau de l'élève, classé par thème

        exercises_tab = []
        for r in relationships:
            exo = {}
            exo["name"] = r.exercise
            exo["is_publish"] = r.is_publish
            stas = Studentanswer.objects.filter(exercise=r.exercise, student=student).order_by("date")
            scores_tab = []
            for sta in stas:
                scores_tab.append(sta)
            exo["scores"] = scores_tab
            exercises_tab.append(exo)
        theme["exercises"] = exercises_tab

        datas.append(theme)

    if request.user.is_teacher:
        students = []
        teacher = Teacher.objects.get(user=request.user)
        group = Group.objects.filter(students=student, teacher=teacher).last()
        groups =  student.students_to_group.filter(teacher=teacher)
        for g in groups :
            sts = g.students.all().order_by("user__last_name")
            for s in sts :
                students.append(s)

        if group :
            nav = navigation(group, id)
            context = {'datas': datas, 'parcourses': parcourses, 'group': group, 'sprev_id': nav[0], 'snext_id': nav[1], 'parcours' : None, 'students' : students ,  'today' : today ,  
                   'themes': themes, 'student': student , 'communications' : [], }
        else :
            messages.error(request, "Erreur...L'élève "+str(student.user.first_name)+" "+str(student.user.last_name)+" n'est pas associé à un groupe.")
            return redirect('index')

    else:
        group = Group.objects.filter(students=student).first()
        
        context = {'datas': datas, 'parcourses': parcourses, 'group': group, 'themes': themes, 'student': student , 'communications' : [] , 'parcours' : None,  'today' : today , 'students' : []  }

    return render(request, 'account/detail_student.html', context)



#@who_can_read_details
def detail_student_theme(request, id,idt):
    student = Student.objects.get(user_id=id)
    tracker_execute_exercise(False,student.user)

    if not logged_user_has_permission_to_this_student(request.user, student) :
        messages.error(request, "Erreur...Vous n'avez pas accès à ces résultats.")
        return redirect('index')

    parcourses = Parcours.objects.filter(students=student,is_trash=0)
    parcourses_publish = Parcours.objects.filter(students=student, is_publish=1,is_trash=0)
    today = time_zone_user(request.user)
    theme = Theme.objects.get(pk=idt)

    themes = student.level.themes.all()
    datas = []

    knowledges = knowledges_of_a_student(student, theme)

    for k in knowledges:
        knowledge_dict = {}
        relationships = Relationship.objects.filter(parcours__in = parcourses, exercise__knowledge = k, students= student,exercise__supportfile__is_title=0)
        if relationships.count() > 1 :
            knowledge_dict["name"] = k
            # liste des exercices du parcours qui correspondent aux savoir faire k mais un même exercice peut être donné sur deux parcours 
            # différents donc deux relationships pour un même exercice
            
            # merge les relationships identiques
            relations_tab, relations_tab_code = [], []
            for rel in relationships:
                if rel.exercise.supportfile.code not in relations_tab_code:
                    relations_tab_code.append(rel.exercise.supportfile.code)
                    relations_tab.append(rel)
            # merge les relationships identiques
            exercises_tab = []
            for relation in relations_tab:
                exo = {}
                exo["name"] = relation
                stas = Studentanswer.objects.filter( exercise= relation.exercise , student = student ).order_by("date")
                scores_tab = []
                for sta in stas:
                    scores_tab.append(sta) 
                exo["scores"] = scores_tab         
                exercises_tab.append(exo)
            knowledge_dict["exercises"] = exercises_tab
            datas.append(knowledge_dict)

    if request.user.is_teacher:
        students = []
        teacher = Teacher.objects.get(user=request.user)
        group = Group.objects.filter(students=student, teacher=teacher).last()
        groups =  student.students_to_group.filter(teacher=teacher)
        for g in groups :
            sts = g.students.all().order_by("user__last_name")
            for s in sts :
                students.append(s)

        if group :
            nav = navigation(group, id)
            context = {'datas': datas, 'student': student, 'theme': theme, 'group': group, 'parcours': None, 'students' : students ,  
                   'sprev_id': nav[0], 'snext_id': nav[1], 'communications': [], 'parcourses': parcourses, 'today' : today ,
                   'themes': themes}
        else :
            messages.error(request, "Erreur...L'élève "+str(student.user.first_name)+" "+str(student.user.last_name)+" n'est pas associé à un groupe.")
            return redirect('index') 

    else:
        group = Group.objects.filter(students=student).first()
        context = {'datas': datas, 'student': student, 'theme': theme, 'group': group, 'parcours': None,
                   'communications': [], 'parcourses': parcourses, 'themes': themes, 'sprev_id': None, 'today' : today ,
                   'snext_id': None, }

    return render(request, 'account/detail_student_theme.html', context)


#@who_can_read_details
def detail_student_parcours(request, id,idp):

    student = Student.objects.get(user_id=id)
    tracker_execute_exercise(False,student.user)

    if not logged_user_has_permission_to_this_student(request.user, student) :
        messages.error(request, "Erreur...Vous n'avez pas accès à ces résultats.")
        return redirect('index')

    parcours = Parcours.objects.get(pk=idp)
    # Affichage dans le menu
    parcourses = student.students_to_parcours.all()
    themes = student.level.themes.all()
    ########################################

    relationships = parcours.parcours_relationship.filter( students = student, is_publish = 1).order_by("ranking")
    today = time_zone_user(request.user)
    if request.user.is_teacher:
        students = []
        teacher = Teacher.objects.get(user=request.user)
        groups =  student.students_to_group.filter(Q(teacher=teacher)|Q(teachers=teacher))        
        group =  groups.last()
        for g in groups :
            sts = g.students.all().order_by("user__last_name")
            for s in sts :
                students.append(s)

 
        if group :
            nav = navigation(group, id)
            context = {'relationships': relationships, 'parcours': parcours, 'themes': themes, 'teacher' : teacher , 'sprev_id': nav[0], 'students' : students , 'group' : group , 'communications' : [], 
                   'snext_id': nav[1], 'parcourses': parcourses, 'student': student}
        else :
            messages.error(request, "Erreur...L'élève "+str(student.user.first_name)+" "+str(student.user.last_name)+" n'est pas associé à un groupe.")
            return redirect('index') 

    else:
        group = parcours.groups.filter(students=student).last()
        context = {'relationships': relationships, 'parcours': parcours, 'themes': themes, 'parcourses': parcourses,  'sprev_id': None , 'group' : group , 'communications' : [], 'today' : today ,
                   'snext_id': None, 'student': student}

    return render(request, 'account/detail_student_parcours.html', context)



#@user_can_read_details
def detail_student_all_views(request, id):

    user = User.objects.get(pk=id)
    student = user.student
    tracker_execute_exercise(False,user)

    studentanswers = student.answers.all()
    today = time_zone_user(user)
    parcourses_tab, parcourses_set = [] , set()
    exercise_tab = []
    prcrs = student.students_to_parcours.filter(is_publish=1)

    parcourses_set.update(set(prcrs))

    relations = student.students_relationship.filter(parcours__in=parcourses_set,is_publish=1,exercise__supportfile__is_title=0).order_by("exercise__theme")

    exercises = []
    for relation in relations:
        if relation.exercise not in exercises:
            exercises.append(relation.exercise)
 

    knowledges = []
    for relation in relations:
        if relation.exercise.knowledge not in knowledges:
            knowledges.append(relation.exercise.knowledge)

    months = []
    score_bool = False
    if request.user.is_teacher:
        students = []
        teacher = Teacher.objects.get(user=request.user)
        group = student.students_to_group.filter( Q(teacher=teacher)| Q(teachers=teacher)).last()
        groups =  student.students_to_group.filter(Q(teacher=teacher)| Q(teachers=teacher))

        themes = set()
        for g in groups :            
            themes.update(student.level.themes.filter(subject=g.subject)) 
            sts = g.students.all().order_by("user__last_name")
            for s in sts :
                students.append(s)

        form = EmailForm(request.POST or None)       
        sender_mail(request,form)
        if group :
            nav = navigation(group, id)
            context = {'exercises': exercises, 'knowledges': knowledges,    'themes': themes, 'students' : students ,  'group' : group , 'communications' : [], 'today' : today , 'form' : form ,  'groups' : groups ,
                   'student': student, 'parcours': None, 'sprev_id': nav[0], 'snext_id': nav[1] , 'teacher' : teacher,'months':months }
        else :
            messages.error(request, "Erreur...L'élève "+str(student.user.first_name)+" "+str(student.user.last_name)+" n'est pas associé à un groupe.")
            context = {'exercises': exercises, 'knowledges': knowledges,    'themes': themes, 'students' : students ,  'group' : None , 'communications' : [], 'today' : today , 'form' : form ,  'groups' : groups ,
                   'student': student, 'parcours': None,  'teacher' : teacher,'months':months }
 
    else :
        group = Group.objects.filter(students=student).last()
        groups = student.students_to_group.all()
        themes = set()
        for g in groups :
            themes.update(student.level.themes.filter(subject=g.subject)) 

        ###################
        #### Suivi si academie
        i = 1

 
        today   = time_zone_user(request.user) 
        year  = int(today.strftime("%Y"))
        month = int( today.strftime("%m"))
        


        nxt_mnth = today.replace(day=28) +  timedelta(days=4)
        res = nxt_mnth -  timedelta(days=nxt_mnth.day) 

        maxiset = []
        for j in range(3):
            upper_set = dict()
            dataset = []
            max_student_answers_nb = 1
            step = 0
            init , end = 1 + 10*j, 11+10*j
            real_month = [0,31,28,31,30,31,30,31,31,30,31,30,31]
            end = min(real_month[month],end )

            begin   = datetime( year , month , init)
            last_d  = datetime( year , month , end)

            if j == 2 :
                end = min(  end,res.day+1)
                last_d = datetime( year , month+1 , 1)


            student_answers_global = Studentanswer.objects.filter( student  = student , date__gte  = begin , date__lte  = last_d )
            nb_exo_count_g = student_answers_global.count()
            data_g = student_answers_global.aggregate( duration = Sum("secondes"), average_score_g=Avg('point'))
            if data_g["average_score_g"] : average_score_g = int(data_g["average_score_g"]) 
            else : average_score_g = 0
            if data_g["duration"] : duration_g = data_g["duration"] 
            else : duration_g = 0
            e_k_count_g = Studentanswer.objects.values_list("exercise__knowledge" ,flat =True).filter( student  = student , date__gte  = begin , date__lte  = last_d ).distinct().count()

            for i in range(init,end):
                datas = {}
                test_date = datetime( year , month , i)
                if i == res.day: 
                    mnth = month + 1
                    test_date_last = datetime( year , mnth , 1)
                else : test_date_last = datetime( year , month , i+1)

                student_answers    = Studentanswer.objects.filter( student  = student , date__gte  = test_date , date__lte  = test_date_last)
                student_answers_nb = student_answers.count()
                average            = student_answers.aggregate( duration = Sum("secondes"), average_score=Avg('point'))

                if not average["average_score"] : average["average_score"] = 0

                datas["date"] = test_date
                datas["hn"]   = 0
                datas["h"]    = student_answers_nb
                datas["a"]    = int(average["average_score"])
                datas["n"]    = student_answers_nb
                datas["l"]    = 9*step
                datas["le"]   = student_answers  
                datas["m"]    = month

                if int(average["average_score"]) < 50 :
                    datas["c"] = "red" 
                elif int(average["average_score"]) < 70 :
                    datas["c"] = "orange" 
                elif int(average["average_score"]) < 85 :
                    datas["c"] = "green"
                else :
                    datas["c"] = "darkgreen"
                step +=1

                dataset.append(datas)
     
                if max_student_answers_nb < student_answers_nb :
                    max_student_answers_nb = student_answers_nb
            
            for d in dataset :
                d["h"]  = int((d["h"]/max_student_answers_nb)*300)
                d["hn"] = d["h"]+20

            upper_set['datas']           = dataset 
            upper_set['nb_exo_g']        = nb_exo_count_g
            upper_set['average_score_g'] = average_score_g
            upper_set['duration_g']      = duration_g
            upper_set['k_count_g']       = e_k_count_g


            if nb_exo_count_g : is_display = True
            else : is_display = False 
            upper_set['is_display']      = is_display

            maxiset.append(upper_set)


 
        context = {'exercises': exercises, 'knowledges': knowledges,   'themes': themes, 'communications' : [], 'group' : group ,  'today' : today  , 'teacher' : None , 'groups' : groups ,
                   'student': student, 'parcours': None, 'sprev_id': None, 'snext_id': None, 'score_bool' : score_bool  ,  'maxiset' : maxiset  }


    return render(request, 'account/detail_student_all_views.html', context)




#@user_can_read_details
def detail_student_academy(request, id):

    user = User.objects.get(pk=id)
    student = user.student
    tracker_execute_exercise(False,user)

    studentanswers = student.answers.all()
    today = time_zone_user(user)
    parcourses_tab, parcourses_set = [] , set()
    exercise_tab = []
    prcrs = student.students_to_parcours.filter(is_publish=1)

    parcourses_set.update(set(prcrs))

    relations = student.students_relationship.filter(parcours__in=parcourses_set,is_publish=1,exercise__supportfile__is_title=0).order_by("exercise__theme")

    exercises = []
    for relation in relations:
        if relation.exercise not in exercises:
            exercises.append(relation.exercise)
 

    knowledges = []
    for relation in relations:
        if relation.exercise.knowledge not in knowledges:
            knowledges.append(relation.exercise.knowledge)


    group = Group.objects.filter(students=student).last()
    groups = student.students_to_group.all()
    themes = set()
    for g in groups :
        themes.update(student.level.themes.filter(subject=g.subject)) 

    i = 1

    today   = time_zone_user(request.user) 
    year  = int(today.strftime("%Y"))
    month = int( today.strftime("%m"))
    

    nxt_mnth = today.replace(day=28) +  timedelta(days=4)
    res = nxt_mnth -  timedelta(days=nxt_mnth.day) 

    maxiset = []
    for j in range(3):
        upper_set = dict()
        dataset = []
        max_student_answers_nb = 1
        step = 0
        init , end = 1 + 10*j, 11+10*j
        real_month = [0,31,28,31,30,31,30,31,31,30,31,30,31]
        end = min(real_month[month],end )

        begin   = datetime( year , month , init)
        last_d  = datetime( year , month , end)

        if j == 2 :
            end += 1
            last_d = datetime( year , month+1 , 1)

        student_answers_global = Studentanswer.objects.filter( student  = student , date__gte  = begin , date__lte  = last_d )
        nb_exo_count_g = student_answers_global.count()
        data_g = student_answers_global.aggregate( duration = Sum("secondes"), average_score_g=Avg('point'))
        if data_g["average_score_g"] : average_score_g = int(data_g["average_score_g"]) 
        else : average_score_g = 0
        if data_g["duration"] : duration_g = data_g["duration"] 
        else : duration_g = 0
        e_k_count_g = Studentanswer.objects.values_list("exercise__knowledge" ,flat =True).filter( student  = student , date__gte  = begin , date__lte  = last_d ).distinct().count()

        for i in range(init,end):
            datas = {}
            test_date = datetime( year , month , i)
            if i == res.day: 
                mnth = month + 1
                test_date_last = datetime( year , mnth , 1)
            else : test_date_last = datetime( year , month , i+1)

            student_answers    = Studentanswer.objects.filter( student  = student , date__gte  = test_date , date__lte  = test_date_last)
            student_answers_nb = student_answers.count()
            average            = student_answers.aggregate( duration = Sum("secondes"), average_score=Avg('point'))

            if not average["average_score"] : average["average_score"] = 0

            datas["date"] = test_date
            datas["hn"]   = 0
            datas["h"]    = student_answers_nb
            datas["a"]    = int(average["average_score"])
            datas["n"]    = student_answers_nb
            datas["l"]    = 9*step
            datas["le"]   = student_answers  
            datas["m"]    = month

            if int(average["average_score"]) < 50 :
                datas["c"] = "red" 
            elif int(average["average_score"]) < 70 :
                datas["c"] = "orange" 
            elif int(average["average_score"]) < 85 :
                datas["c"] = "green"
            else :
                datas["c"] = "darkgreen"
            step +=1

            dataset.append(datas)
 
            if max_student_answers_nb < student_answers_nb :
                max_student_answers_nb = student_answers_nb
        
        for d in dataset :
            d["h"]  = int((d["h"]/max_student_answers_nb)*300)
            d["hn"] = d["h"]+20

        upper_set['datas']           = dataset 
        upper_set['nb_exo_g']        = nb_exo_count_g
        upper_set['average_score_g'] = average_score_g
        upper_set['duration_g']      = duration_g
        upper_set['k_count_g']       = e_k_count_g


        if nb_exo_count_g : is_display = True
        else : is_display = False 
        upper_set['is_display']      = is_display

        maxiset.append(upper_set)

        students = request.user.teacher.students.all()
 
        context = {'exercises': exercises, 'knowledges': knowledges,   'themes': themes, 'communications' : [], 'group' : None ,  'today' : today  , 'teacher' : None , 'groups' : groups ,
                   'student': student, 'parcours': None, 'sprev_id': None, 'snext_id': None,  'maxiset' : maxiset , 'students' : students  }


    return render(request, 'account/detail_student_academy.html', context)





def ajax_get_details_graph(request):
    student_id  = int(request.POST.get("student_id"))
    month       = int(request.POST.get("month"))
    date        = request.POST.get("date")
    d , m  , y , r = date.split(" ")

    date_f = datetime(int(y),month,int(d))
    date_e = date_f + timedelta(days=1)

    student = Student.objects.get(pk = student_id)
    student_answers    = Studentanswer.objects.filter( student  = student , date__gte  = date_f , date__lte  = date_e)
 

    context = {'student_answers': student_answers}

    data = {}

    data['this_date'] =  date_f.strftime("%d-%m-%Y") 
    data['html'] = render_to_string('account/ajax_get_details_graph.html', context)
 
    return JsonResponse(data)




def ebep(request,id,idg):
    student = Student.objects.get(user_id=id)
    if student.ebep :
        Student.objects.filter(user_id=id).update(ebep = False)
    else :
        Student.objects.filter(user_id=id).update(ebep = True)
    return redirect('show_group' , idg )




##############################################################################################################
##
##    Response from mail after exercise error
##
############################################################################################################## 



def response_from_mail(request,user_id):
 
    user = User.objects.get(pk=user_id)
    form = ResponseForm(request.POST or None)

    context = { 'user' : user , }

    if request.method == "POST" :
 
        message = request.POST.get("message",None)
        response = request.POST.get("response",None)
        msg = "Bonjour, \n vous venez d'envoyer le message suivant :\n\n" + message + " \n\n Voici notre réponse.\n\n " + response  + "\n\n Merci pour votre aide."
        if user.email :
 
            sending_mail("ERREUR SUR UN EXERCICE SACADO",  msg , settings.DEFAULT_FROM_EMAIL ,  [user.email] )
            sending_mail("ERREUR SUR UN EXERCICE SACADO",  msg , settings.DEFAULT_FROM_EMAIL , ["philippe.demaria-lgf@erlm.tn", "brunoserres33@gmail.com", "nicolas.villemain@claudel.org"])
 
        else :
            if form.is_valid():
                nf = form.save(commit=False)
                nf.admin = request.user
                nf.user = user
                nf.save()
 
        return redirect("index")

    else :

        return render(request, 'account/response_from_mail.html', context )




def check_response_from_mail(request):
 
    is_read = request.POST.get("is_read",None)
    response_id = request.POST.get("response_id",None)
    Response.objects.filter(pk= response_id).update(is_read = 1)

    return redirect("index")



##############################################################################################################
##
##    Close an account
##
############################################################################################################## 


def close_my_account(request):
    if request.method == 'POST':
        user = request.user
        try :
            user.delete()
        except :
            messages.error(request,"Vous avez crée des sections dans vos parcours qui bloquent votre désincription. Avant de supprimer votre compte, supprimez ces sections.")
        return redirect('index')
    else:
        user = request.user
        today = time_zone_user(user)
        return render(request, 'account/close_my_account.html', {'user': user, 'communications': [], 'today': today, })

#########################################Teacher #######################################################################
 
def register_teacher(request):


    user_form = UserForm(request.POST)

    if request.method == 'POST':
        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.user_type = User.TEACHER
            user.set_password(user_form.cleaned_data["password1"])
            user.save()
            username = user_form.cleaned_data['username']
            password = user_form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user,  backend='django.contrib.auth.backends.ModelBackend' )
            teacher = Teacher.objects.create(user=user)

            try :
                #teacher.notify_registration()
                teacher.notify_registration_to_admins()
                msg = "Bonjour "+ user.first_name +" " + user.last_name+",\n\n Votre compte Sacado est maintenant disponible.\n\nVotre identifiant est : "+user.username+".\n\nVotre mot de passe est : "+password+" \n\nPour vous connecter, redirigez-vous vers  https://sacado-academie.fr .\n\nCeci est un mail automatique. Merci de ne pas répondre."
                msg_ = "Bonjour,\n\n Un enseignant vient de rejoindre SacAdo : " + user.last_name + "  "+user.first_name 
                if user.email :
                    send_mail('INSCRIPTION SACADO', msg ,settings.DEFAULT_FROM_EMAIL,[user.email, ])
            except :
                pass

        else:
            messages.error(request, user_form.errors)

        return redirect("index")


    return render(request, 'account/teacher_form.html', {'user_form': user_form,  })



#@can_register
#@is_manager_of_this_school
def update_teacher(request, pk):

    user = get_object_or_404(User, pk=pk)
    teacher = get_object_or_404(Teacher, user=user)
    today = time_zone_user(user)
    user_form = ManagerUpdateForm(request.POST or None, instance=user)
    teacher_form = TeacherForm(request.POST or None, instance=teacher)
    new = False
    if all((user_form.is_valid(), teacher_form.is_valid())):
        user_form.save()
        teacher = teacher_form.save(commit=False)
        teacher.user = user
        teacher.save()
        teacher_form.save_m2m()
        messages.success(request, "Actualisation réussie !")

        test = request.POST.get("listing",None)
 
        if test :
            return redirect('list_teacher')
        elif request.user.is_manager :
            return redirect('school_teachers')
        else :
            return redirect('index') 

    return render(request, 'account/teacher_form.html',
                  {'user_form': user_form, 'new' : new , 'communications': [] , 'today' : today , 
                   'teacher_form': teacher_form,
                   'teacher': teacher})



#@can_register
#@is_manager_of_this_school
def delete_teacher(request, id):

    teacher = get_object_or_404(Teacher, user_id=id)

    supprime , sup  = False , False

    if request.user.is_manager and teacher.user.school == request.user.school : #Si l'enseignant est manager et administre le même étabissement que le prof à supprimer alors on supprime.
        supprime = True
        if teacher.groups.count() > 0 : # si le prof a déjà des groupes, seul lui peut se supprimer
            supprime = False

    if request.user.teacher == teacher or request.user.is_superuser   :
        sup = True
        
    if sup or supprime :
        teacher.user.delete()
        messages.success(request,"Le profil a été supprimé avec succès.")
    else :
        messages.error(request,"Permission refusée. Le profil n'a pas été supprimé. Des groupes sont attribués à cet enseignant. Il faut le dissocer de ses groupes.")

    if request.user.is_superuser :
        return redirect('list_teacher')
    elif request.user.is_manager :
        return redirect('school_teachers')
    else :
        return redirect('index') 


def dissociate_teacher(request, id):

    user = User.objects.get(pk=id)
    this_user = request.user

    if user == this_user or  this_user.is_manager :

        User.objects.filter(pk=id).update(school = None)
 

 
    msg = "Bonjour cher collègue, vous venez d'être dissocié de votre établissement d'affectation. Votre compte reste actif avec vos identifiants habituels. Vous pourrez utiliser Sacado dans votre prochaine affectation. Cordialement."

    if user.email :
        sending_mail('Disociation de compte à un établissement', msg ,
                      settings.DEFAULT_FROM_EMAIL,
                      [user.email, ])



    test = request.POST.get("listing",None)
    if test :
        return redirect('list_teacher')
    elif request.user.is_manager :
        return redirect('school_teachers')
    else :
        return redirect('index') 



#@can_register
#@is_manager_of_this_school
def register_teacher_from_admin(request):
    """"
    Enregistre un enseignant depuis la console admin d'un établissement
    """ 
    user_form = ManagerForm(request.POST or None,initial = {'time_zone': request.user.time_zone , 'country': request.user.country })
    teacher_form = TeacherForm(request.POST or None)
    new = False
    if request.method == 'POST':
        if all((user_form.is_valid(),teacher_form.is_valid())):
            u_form = user_form.save(commit=False)
            password = "sacado2020" #str(uuid.uuid4())[:8]
            u_form.password = make_password(password)
            u_form.user_type = User.TEACHER
            school = request.user.school
            u_form.school = school
            u_form.save()
            teacher = teacher_form.save(commit=False)
            teacher.user = u_form
            teacher.save()
            teacher_form.save_m2m()

            sending_mail('Création de compte sur Sacado',
                          f'Bonjour {teacher.user}, votre compte Sacado est maintenant disponible.\r\n\r\nVotre identifiant est {u_form.username} \r\n\r\nVotre mot de passe est : {password} \r\n\r\nVous pourrez le modifier une fois connecté à votre espace personnel.\r\n\r\nPour vous connecter, redirigez-vous vers https://sacado-academie.fr.\r\n\r\nCeci est un mail automatique. Ne pas répondre.',
                          settings.DEFAULT_FROM_EMAIL,
                          [u_form.email, ])
 
            return redirect('school_teachers')
        else:
            messages.error(request, user_form.errors)
    else:
        new = True

    return render(request, 'account/teacher_form.html',
                  {'user_form': user_form, 'communications': [] , 
                   'teacher_form': teacher_form,
                   'new': new, })

 
#@can_register
#@is_manager_of_this_school
def register_by_csv(request, key, idg=0):
    """
    Enregistrement par csv : key est le code du user_type : 0 pour student, 2 pour teacher
    """
    if idg > 0:
        group = Group.objects.get(pk=idg)
        is_teacher = False
    else :
        is_teacher = True
    if request.method == "POST":
        # try:
        csv_file = request.FILES["csv_file"]
        if not csv_file.name.endswith('.csv'):
            messages.error(request, "Le fichier n'est pas format CSV")
            return HttpResponseRedirect(reverse("register_teacher_csv", args=[key, idg]))
        # if file is too large, return
        if csv_file.multiple_chunks():
            messages.error(request, "Le fichier est trop lourd (%.2f MB)." % (csv_file.size / (1000 * 1000),))
            return HttpResponseRedirect(reverse("register_teacher_csv", args=[key, idg]))
        

        file_data = csv_file.readlines()

        #lines = file_data.split("\r\n")
        # loop over the lines and save them in db. If error , store as string and then display = []
        list_names = ""
        for line in file_data :
            try:
                line = line.decode("utf-8")
            except UnicodeDecodeError:
                messages.error(request, 'Erreur..... Votre fichier contient des caractères spéciaux qui ne peuvent pas être décodés. Merci de vérifier que votre fichier .csv est bien encodé au format UTF-8.')
                return HttpResponseRedirect(reverse("register_teacher_csv", args=[key, idg]))
            try : 
            # loop over the lines and save them in db. If error , store as string and then display
                simple = request.POST.get("simple",None)
                ln, fn, username , password , email , group_name , level , is_username_changed = separate_values(request, line, 2 , simple)   # 2 donne la forme du CSV

                if key == User.TEACHER:  # Enseignant
                    user, created = User.objects.get_or_create(last_name=ln, first_name=fn, email=email, user_type=2,
                                                      school=this_school_in_session(request), time_zone=request.user.time_zone,
                                                      is_manager=0,
                                                      defaults={'username': username, 'password': password,
                                                                'is_extra': 0})
                    Teacher.objects.get_or_create(user=user, notification=1, exercise_post=1)
                    group = None
                else:  # Student
                    user, created = User.objects.get_or_create(last_name=ln, first_name=fn, email=email, user_type=0,
                                                               school=this_school_in_session(request),
                                                               time_zone=request.user.time_zone, is_manager=0,
                                                               defaults={'username': username, 'password': password,
                                                                         'is_extra': 0})
                    student, creator = Student.objects.get_or_create(user=user, level=group.level, task_post=1)
                    if not creator : #Si l'élève n'est pas créé alors il existe dans des groupes. On l'efface de ses anciens groupes pour l'inscrire à nouveau !
                        for g in student.students_to_group.all():
                            g.students.remove(student)
                    group.students.add(student)

                if is_username_changed :
                    list_names += ln+" "+fn+" : "+username+"; "

                if email != "" :
                    sending_mail('Création de compte sur Sacado',
                      f'Bonjour {user}, votre compte Sacado est maintenant disponible.\r\n\r\nVotre identifiant est {user.username} \r\n\r\nVotre mot de passe est : sacado2020 \r\n\r\nVous pourrez le modifier une fois connecté à votre espace personnel.\r\n\r\nPour vous connecter, redirigez-vous vers https://sacado-academie.fr.\r\n\r\nCeci est un mail automatique. Ne pas répondre.',
                      settings.DEFAULT_FROM_EMAIL, [email,])
            except :
                pass

        if len(list_names) >  0 :
            if key == User.TEACHER:
                user_type = " enseignants "
            else :
                user_type = " élèves "
            messages.error(request,"Les identifiants des "+user_type+" suivants ont été modifiés lors de la création "+list_names)
 

        if key == User.TEACHER:
            return redirect('school_teachers')
        else:
            return redirect('school_groups')
    else:
        if key == User.TEACHER:
            group = None
        else:
            group = Group.objects.get(pk=idg)

        return render(request, 'account/csv_teachers_or_students.html', {'key': key, 'idg': idg, 'communications' : [],  'group': group ,  'is_teacher': is_teacher })







#@can_register
#@is_manager_of_this_school
def register_users_by_csv(request,key):
    """
    Enregistrement par csv : key est le code du user_type : 0 pour student, 2 pour teacher
    """
    if request.method == "POST":
        # try:
        csv_file = request.FILES["csv_file"]
        if not csv_file.name.endswith('.csv'):
            messages.error(request, "Le fichier n'est pas format CSV")
            return HttpResponseRedirect(reverse("register_teacher_csv"))
        # if file is too large, return
        if csv_file.multiple_chunks():
            messages.error(request, "Le fichier est trop lourd (%.2f MB)." % (csv_file.size / (1000 * 1000),))
            return HttpResponseRedirect(reverse("register_teacher_csv"))
   

        file_data = csv_file.readlines()
        #lines = file_data.split("\r\n")
        # loop over the lines and save them in db. If error , store as string and then display = []
        list_names = ""
        for line in file_data :
            try:
                line = line.decode("utf-8")
            except UnicodeDecodeError:
                messages.error(request, 'Erreur..... Votre fichier contient des caractères spéciaux qui ne peuvent pas être décodés. Merci de vérifier que votre fichier .csv est bien encodé au format UTF-8.')
                return HttpResponseRedirect(reverse("register_teacher_csv", args=[key, idg]))
            try : 
                simple = request.POST.get("simple",None)
                ln, fn, username , password , email , group_name , level , is_username_changed = separate_values(request, line, 1 , simple) # 2 donne la forme du CSV

                if key == User.TEACHER:  # Enseignant
                    user, created = User.objects.get_or_create(last_name=ln, first_name=fn, email=email, user_type=2,
                                                      school=this_school_in_session(request), time_zone=request.user.time_zone,
                                                      is_manager=0,
                                                      defaults={'username': username, 'password': password,
                                                                'is_extra': 0})
                    Teacher.objects.get_or_create(user=user, notification=1, exercise_post=1)
                else:  # Student
                    user, created = User.objects.get_or_create(last_name=ln, first_name=fn, email=email, user_type=0,
                                                               school=this_school_in_session(request),
                                                               time_zone=request.user.time_zone, is_manager=0,
                                                               defaults={'username': username, 'password': password,
                                                                         'is_extra': 0})
                    student, creator = Student.objects.get_or_create(user=user, level_id=level, task_post=1)

                if is_username_changed :
                    list_names += ln+" "+fn+" : "+username+"; "

            except :
                pass
     
        if len(list_names) >  0 :
            if key == User.TEACHER:
                user_type = " enseignants "
            else :
                user_type = " élèves "
            messages.error(request,"Les identifiants des "+user_type+" suivants ont été modifiés lors de la création "+list_names)

        if key == User.TEACHER:
            return redirect('school_teachers')
        else:
            return redirect('school_students')

    else :

        return render(request, 'account/csv_all_teachers_or_students.html', {'key': key , 'communications' : [], })

  
#########################################Lost password #################################################################


def updatepassword(request):

    today = time_zone_user(request.user)
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            userport = form.save()
            update_session_auth_hash(request, userport) # Important!
            messages.success(request, 'Votre mot de passe a été modifié avec succès !')

            sending_mail('Changement de mot de passe sur sacAdo', 'Bonjour, votre nouveau mot de passe sacado est '+str(request.POST.get("new_password1"))+'. Pour vous connecter, redirigez-vous vers https://sacado-academie.fr .', settings.DEFAULT_FROM_EMAIL, [request.user.email])

            return redirect('logout')
        else :
            print(form.errors)  
    else:
        form = PasswordChangeForm(request.user)
 
    return render(request, 'account/password_form.html', { 'form': form, 'communications' : [], 'today' : today , })



##############################################################################################################
##############################################################################################################
#    PARENTS
##############################################################################################################
##############################################################################################################


def register_parent(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            code_student = request.POST.get("code_student")
            if Student.objects.filter(code=code_student).exists():
                username = user_form.cleaned_data['last_name'] + user_form.cleaned_data['first_name']
                user = user_form.save(commit=False)
                user.username = username
                user.user_type = User.PARENT
                password = request.POST.get("password1")
                user.set_password(password)
                user.save()
                parent, result = Parent.objects.get_or_create(user=user)
                student = Student.objects.get(code=code_student)
                parent.students.add(student)
            
                user = authenticate(username=username, password = password)
                login(request, user,  backend='django.contrib.auth.backends.ModelBackend' )
                messages.success(request, "Inscription réalisée avec succès !")            
                if user_form.cleaned_data['email'] :
                    sending_mail('Création de compte sur Sacado', 'Bonjour, votre compte SacAdo est maintenant disponible. \n\n Votre identifiant est '+str(username) +". \n\n votre mot de passe est "+str(password)+'.\n\n Pour vous connecter, redirigez-vous vers https://sacado-academie.fr.\n Ceci est un mail automatique. Ne pas répondre.', settings.DEFAULT_FROM_EMAIL, [request.POST.get("email")])
       
        else:
            messages.error(request, "Erreur lors de l'enregistrement. Reprendre l'inscription...")
    return redirect('index')



def update_parent(request, id):
    user = get_object_or_404(User, pk=id)
    parent = get_object_or_404(Parent, pk=id)
    user_form = UserUpdateForm(request.POST or None, instance=user)
    parent_form = ParentUpdateForm(request.POST or None, instance=student)
    if all((user_form.is_valid(), parent_form.is_valid())):
        user_form.save()
        parent_f = parent_form.save(commit=False)
        parent_f.user = user
        parent_f.save()
        return redirect('index')

    return render(request, 'account/parent_form.html',
                  {'user_form': user_form, 'parent_form': parent_form, 'parent': parent})


def delete_parent(request, id):
    parent = get_object_or_404(Parent, user_id=id)
    parent.delete()
    return redirect('index')




#####################################


def my_profile(request):

    if request.user.is_authenticated : 
        user = request.user
        is_manager = user.is_manager
        is_extra   = user.is_extra
        is_testeur = user.is_testeur
        today = time_zone_user(user)
        if user.is_superuser :
            user_form = ManagerUpdateForm(request.POST or None, request.FILES or None, instance=user)        
        else :
            user_form = UserUpdateForm(request.POST or None, request.FILES or None, instance=user)

        new = False

        if request.user.is_teacher:
            teacher = Teacher.objects.get(user=user)

            teacher_form = TeacherForm(request.POST or None, request.FILES or None, instance=teacher)
            if request.method == "POST":
                if all((user_form.is_valid(), teacher_form.is_valid())):
                    teacher       = teacher_form.save(commit=False)
                    teacher.user  = user
                    teacher.save()
                    teacher_form.save_m2m()
                    uf            = user_form.save(commit=False) 
                    uf.is_manager = is_manager
                    uf.is_extra   = is_extra
                    uf.is_testeur = is_testeur
                    uf.save()
                    messages.success(request, 'Votre profil a été changé avec succès !')
                    if teacher.groups.count() == 0:
                        return redirect('index')
                    else:
                        return redirect('profile')

            return render(request, 'account/teacher_form.html', 
                          {'teacher_form': teacher_form, 'user_form': user_form,'new' : new , 'communications': [] ,  'teacher': teacher, 'today' : today})

        elif request.user.is_student:

            student = Student.objects.get(user=user)
            form = StudentForm(request.POST or None, request.FILES or None, instance=student)
            if request.method == "POST":
                if all((user_form.is_valid(), form.is_valid())):
                    user_form.save()
                    student_f = form.save(commit=False)
                    student_f.user = user
                    student_f.save()
                    messages.success(request, 'Votre profil a été changé avec succès !')
                    return redirect('profile')

                else:
                    print(form.errors)
            return render(request, 'account/student_form.html',
                          {'form': form, 'user_form': user_form, 'communications' : [],  'student': student, 'idg' : None , 'today' : today })

        else:
            parent = Parent.objects.get(user=user)
            form = ParentForm(request.POST or None, request.FILES or None, instance=parent)
            if request.method == "POST":
                if all((user_form.is_valid(), form.is_valid())):
                    user_form.save()
                    parent_f = form.save(commit=False)
                    parent_f.user = user
                    parent_f.save()
                    messages.success(request, 'Votre profil a été changé avec succès !')
                    return redirect('profile')

                else:
                    print(form.errors)
            return render(request, 'account/parent_form.html', {'parent_form': form, 'communications' : [],  'user_form': user_form, 'parent': parent, 'today' : today })
    else :
        redirect("index")


@csrf_exempt
def ajax_userinfo(request):
    username = request.POST.get("username")

    data = {}
    nb_user = User.objects.filter(username=username).count()

    if nb_user > 0:
        data['html'] = "<br><i class='fa fa-times text-danger'></i> Identifiant déjà utilisé."
        data['test'] = False
    else:
        data['html'] = "<br><i class='fa fa-check text-success'></i>"
        data['test'] = True

    return JsonResponse(data)


@csrf_exempt
def ajax_userinfomail(request):
    email = request.POST.get("email")

    data = {}
    nb_user = User.objects.filter(email=email).count()

    if nb_user > 0:
        data['html'] = "<br><i class='fa fa-times text-danger'></i> Identifiant déjà utilisé."
        data['test'] = False
    else:
        data['html'] = "<br><i class='fa fa-check text-success'></i>"
        data['test'] = True

    return JsonResponse(data)




def ajax_courseinfo(request):
    groupe_code = request.POST.get("groupe_code")
    data = {}
    try:
        nb_group = Group.objects.filter(code=groupe_code,lock=0).count()
        if nb_group == 1:
            data['htmlg'] = "<br><i class='fa fa-check text-success'></i>"
        else:
            data['htmlg'] = "<br><i class='fa fa-times text-danger'></i> Groupe inconnu ou verrouillé."
    except:
        data['htmlg'] = "<br><i class='fa fa-times text-danger'></i> Groupe inconnu ou verrouillé."

    return JsonResponse(data)


def ajax_control_code_student(request):
    data = {}
    try:
        code_student = request.POST.get("code_student")
        nb_user = Student.objects.filter(code=code_student).count()

        if nb_user == 1:
            student = Student.objects.get(code=code_student)
            data[
                'html'] = "<br><i class='fa fa-check text-success'></i> Paire avec " + student.user.first_name + " en " + student.level.name
            data['test'] = True

        else:
            data['html'] = "<br><i class='fa fa-times text-danger'></i> Code inconnu."
            data['test'] = False

    except:
        data['html'] = "<br><i class='fa fa-times text-danger'></i> Code inconnu."
        data['test'] = False

    return JsonResponse(data)




def ajax_detail_student(request):
    student_id = int(request.POST.get("student_id"))
    theme_id = int(request.POST.get("theme_id"))
    group_id = int(request.POST.get("group_id"))

    user = User.objects.get(pk=student_id)
    group = Group.objects.get(pk=group_id)
    student = Student.objects.get(user=user)

    if theme_id > 0:
        theme = Theme.objects.get(pk=theme_id)
        knowledges = group.level.knowledges.filter(theme=theme)
        context = {'student': student, 'theme': theme, 'group': group, 'knowledges': knowledges}
    else:
        themes = group.level.themes.all()
        context = {'student': student, 'themes': themes, 'group': group}

    data = {}
    data['html'] = render_to_string('account/ajax_detail_student.html', context)
 
    return JsonResponse(data)



def ajax_detail_student_exercise(request):
    student_id = int(request.POST.get("student_id"))
    parcours_id = int(request.POST.get("parcours_id"))

    parcours = Parcours.objects.get(pk=parcours_id)
    student = Student.objects.get(user_id=student_id)

    relationships = Relationship.objects.filter(parcours=parcours, students=student,exercise__supportfile__is_title=0).order_by("ranking")
    studentanswers = Studentanswer.objects.filter(student=student, parcours=parcours).order_by("exercise")

    context = {'student': student, 'parcours': parcours, 'studentanswers': studentanswers, 'communications' : [], 
               'relationships': relationships}

    data = {}
    data['html'] = render_to_string('account/ajax_detail_student_exercise.html', context)

    return JsonResponse(data)



def ajax_detail_student_parcours(request):
    student_id = int(request.POST.get("student_id"))
    parcours_id = int(request.POST.get("parcours_id"))

    student = Student.objects.get(user_id=student_id)
    parcours = Parcours.objects.get(pk=parcours_id)

    if student.user.school :
        stage = Stage.objects.get(school = student.user.school)
    else :
        stage = { 'low' : 30, 'medium' : 60 , 'up' :80 }        


    relationships = Relationship.objects.filter(parcours=parcours,exercise__supportfile__is_title=0).order_by("ranking")

    context = {'student': student, 'relationships': relationships, 'stage' : stage}

    data = {}
    data['html'] = render_to_string('account/ajax_detail_student_parcours.html', context)

    return JsonResponse(data)


########## oauth social ###################

def ask_usertype(request):
    """
    Authentification avec google et social_django, demande d'informations complémentaires comme
    le type de l'utilisateur ou la classe afin de compléter le profil
    """
    levels = Level.objects.all()
    return render(request, 'account/oauth_usertype.html', {'levels': levels})


##########################################################################################################################
##
## password reset
##
##########################################################################################################################


def passwordResetView(request):

    if request.method == 'POST':
        form = NewpasswordForm(request.POST)
        if form.is_valid():
            this_form = form.save(commit=False)
            nb_user=User.objects.filter(email=this_form.email).count()
            if nb_user :
                link ="https://sacado-academie.fr/account/newpassword/"+this_form.code
                msg = "Bonjour, \nvous venez de demander la réinitialisation de votre mot de passe. Cliquez sur le lien suivant :\n"+ link +"\n\nMerci. \n\n Ceci est un mail automatique, ne pas répondre."

                send_mail('SacAdo : Ré-initialisation de mot de passe',msg ,settings.DEFAULT_FROM_EMAIL,[this_form.email])
                this_form=form.save()
                return redirect("password_reset_done")
            
            else :
                messages.error(request, "Adresse courriel inconnue. Contacter l'équipe SACADO.")
                return redirect('index')

    messages.error(request, "une erreur est survenue. Contacter l'équipe SACADO.")
    return redirect('index')



def passwordResetDoneView(request):
    return render(request, 'registration/password_reset_done.html', { })



def passwordResetConfirmView(request, code ):
    try :
        np = Newpassword.objects.get(code = code)
        validlink = True
        form = SetnewpasswordForm()
    except :
        validlink = False

    if request.method == 'POST':
        form = SetnewpasswordForm(request.POST)
        if form.is_valid():
            get_new_password = Newpassword.objects.get(code = code)
            users = User.objects.filter(email = get_new_password.email, user_type=2)
            cpt = 0
            for u in users :
                u.password = make_password(request.POST.get('password1'))
                u.save()
                cpt += 1
        if cpt > 1 :
            msg = "Bonjour, \n\n Plusieurs comptes sont associés à cette adresse email : "+ get_new_password.email +"\n\n Votre mot de passe " + request.POST.get('password1') + "\nest attribué à chaque compte associé à cette adresse mail.\n\n Ceci est un mail automatique, ne pas répondre."
        else :
            msg = "Bonjour, \n\n Votre mot de passe : " + request.POST.get('password1') + "\nest attribué.\n\n Ceci est un mail automatique, ne pas répondre."
 
        send_mail('SacAdo : Ré-initialisation de mot de passe', msg ,settings.DEFAULT_FROM_EMAIL,[get_new_password.email, ])
        return render(request, 'registration/password_reset_complete.html', { })


    return render(request, 'registration/password_reset_confirm.html', { 'validlink' : validlink , 'form' : form , 'code' : code , })



def init_password_teacher(request, id ):

    teacher = Teacher.objects.get(pk=id)
    password =  str(uuid.uuid4())[:8]
    password_hash = make_password(password)
    teacher.user.password = password_hash
    User.objects.filter(pk= teacher.user_id).update(password = password_hash)
 
    msg = "Bonjour, \n\n Votre nouveau mot de passe : " + password + "\nest attribué. Il est généré automatiquement.\n\n Vous pouvez le modifer via votre profil. Ceci est un mail automatique, ne pas répondre.\n\nL'équipe SACADO."
    
    if teacher.user.email :
        send_mail('SacAdo : Ré-initialisation de mot de passe', msg ,settings.DEFAULT_FROM_EMAIL,[teacher.user.email, ])


    return redirect('list_teacher') 





def aggregate_child(request):

    child_code = request.POST.get('child')
    parent     = request.user.parent

    try :
        child_user = User.object.get(code=child_code)
        parent.students.add(child_user)
    except :
        messages.error(request,"Echec de la paire. Le code de l'enfant est inconnu.")

 
    return redirect('index') 


