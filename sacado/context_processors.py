import pytz
from django.utils import timezone
from account.models import Teacher, Student, User
from qcm.models import Parcours, Studentanswer, Exercise, Demand
from school.models import School
from association.models import Accounting , Rate , Abonnement
from sendmail.models import Email, Message
from socle.models import Level
from school.models import School
from group.models import Group
from tool.models import Tool
from datetime import datetime 

##############################################################################################################################################
##############################################################################################################################################
###              L'établissement est-t-il membre sacado 
##############################################################################################################################################
##############################################################################################################################################


def is_sacado_asso(this_user, today):
    last_adhesion = this_user.student.adhesions.last()
    is_sacado = False
    is_active = False
    if last_adhesion.stop > today :
        is_sacado = True
        is_active = True
    return is_sacado, is_active

##############################################################################################################################################
##############################################################################################################################################
##############################################################################################################################################
##############################################################################################################################################


def menu(request):

    if request.user.is_authenticated:

 
        is_gar_check = None
        if request.user.time_zone:
            time_zome = request.user.time_zone
            timezone.activate(pytz.timezone(time_zome))
            today = timezone.localtime(timezone.now())
        else:
            today = timezone.now()

        if request.user.is_teacher:
            teacher = request.user.teacher
            #nbs = Studentanswer.objects.filter(parcours__teacher=teacher, date=today).count()
            nbe = Email.objects.values_list("id").distinct().filter(receivers=request.user, today=today).count()
            #nb_not = nbs + nbe
            levels = Level.objects.exclude(pk=13).order_by("ranking")
            nb_demand = Demand.objects.filter(done=0).count()

            mytools = Tool.objects.filter(is_publish=1, teachers = teacher).order_by("title")

            ### Exercice traités non vus par l'enseignant -> un point orange dans la barre de menu sur message
            is_pending_studentanswers = False
            pending_s = Studentanswer.objects.filter(parcours__teacher = teacher, is_reading = 0)
            if pending_s  :
                is_pending_studentanswers = True
 
            ### Permet de vérifier qu'un enseignant est dans un établissement sacado
            sacado_asso, sacado_is_active = is_sacado_asso(teacher.user,today)
 
            ### Rapelle le renouvellement de la cotisation
            renew_hidden = request.session.get("renewal", False)
            if not renew_hidden :
                rates = Rate.objects.all() #tarifs en vigueur 
                today = datetime.now()

                if Abonnement.objects.filter(school = teacher.user.school,   date_stop__gte=today, date_start__lte=today,is_active = 1 ).count() == 1:
                    renew_hidden = True
                    request.session["renewal"] = renew_hidden
 
            return { 'is_gar_check' : is_gar_check,'today': today, 'index_tdb' : False , 'nbe': nbe, 'levels': levels, 'renew_propose' : renew_hidden ,  'nb_demand' : nb_demand , 'mytools' : mytools , 'sacado_asso' : sacado_asso , "is_pending_studentanswers" : is_pending_studentanswers  }

        elif request.user.is_student:
            
            student = Student.objects.get(user=request.user)
            groups = student.students_to_group.all()

            teacher_to_student = False
            if "_e-test" in student.user.username :
                teacher_to_student = True


            sacado_asso, sacado_is_active = is_sacado_asso(student.user,today)

            group_id = request.session.get("group_id",None)

            if group_id :
                group = Group.objects.get(pk=group_id)
            else :
                group = None
                
            return {
                'is_gar_check' : is_gar_check,
                'student': student,
                'sacado_asso' : sacado_asso , 
                'group' : group ,
                'groups' : groups,
                'teacher_to_student' : teacher_to_student ,   
                'index_tdb' : False ,              
            }

        elif request.user.is_parent:
            this_user = User.objects.get(pk=request.user.id)
            students = this_user.parent.students.all()
            sacado_asso, sacado_is_active = is_sacado_asso(this_user, today)
            return {
                'this_user': this_user,
                'sacado_asso' : sacado_asso , 
                 'sacado_asso' : False , 
                 'index_tdb' : False ,
                 'is_gar_check' : None,
            }


    else:
 
 
 
        contributeurs = User.objects.filter(is_superuser=1)
 
 
        return {
 
            'contributeurs': contributeurs,
  
        }
