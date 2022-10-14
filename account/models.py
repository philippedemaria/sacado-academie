import uuid

import pytz
from django.apps import apps
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.db import models
from django.db.models import  Q, Avg, Sum
from socle.models import Level, Knowledge, Skill, Subject
from school.models import School, Country

from templated_email import send_templated_mail
#from general_fonctions import *

from django.conf import settings # récupération de variables globales du settings.py
from general_fonctions import *
from datetime import datetime 
# Pour créer un superuser, il faut depuis le shell taper :
# from account.models import User
# User.objects.create_superuser("admin","admin@gmail.com","motdepasse", user_type=0).save()

def file_directory_path(instance, filename):
    return "factures/{}/{}".format(instance.user.id, filename)

def avatar_directory_path(instance,filename):
    return "avatar/{}".format(filename)    

def background_directory_path(instance,filename):
    return "background/{}".format(filename)    


def generate_code():
    '''
    Fonction qui génère un code pour les modèles suivantes :
    - Parcours
    - Group
    - Student
    - Supportfile
    '''
    return str(uuid.uuid4())[:8]


class ModelWithCode(models.Model):
    '''
    Ajoute un champ code à un modèle
    '''
    code = models.CharField(max_length=100, unique=True, blank=True, default=generate_code, verbose_name="Code")

    class Meta:
        abstract = True




class Avatar(models.Model):

    LEVELS = (
        (50, "moins de 50%"),
        (70, "moins de 70%"),
        (85, "moins de 85%"),
    )
    image = models.ImageField(upload_to=avatar_directory_path,verbose_name="avatar")
    level = models.PositiveSmallIntegerField(choices=LEVELS)
    adult = models.BooleanField(default=1)

    def __str__(self):
        image = self.image
        return "{}".format(image )



class Background(models.Model):

    image    = models.ImageField(upload_to=background_directory_path,verbose_name="background")
    is_title = models.BooleanField(default=0)



    def __str__(self):
        image = self.image
        return "{}".format(image)



class User(AbstractUser):
    """
    Modèle représentant un utilisateur. Possède les champs suivants hérités de la classe AbstractUser :

    first_name : Optional (blank=True). 100 characters or fewer.
    last_name : Optional (blank=True). 150 characters or fewer.
    email : Optional (blank=True). Email address.
    password : Required. A hash of, and metadata about, the password. (Django doesn’t store the raw password.)
    groups : Many-to-many relationship to Group
    user_permissions : Many-to-many relationship to Permission
    is_staff : Boolean. Designates whether this user can access the admin site.
    is_active : Boolean. Designates whether this user account should be considered active.
    is_superuser : Boolean. Designates that this user has all permissions without explicitly assigning them.
    last_login : A datetime of the user’s last login.
    date_joined : A datetime designating when the account was created. Is set to the current date/time by default when the account is created.

    """
 
    #### user_type = 0 for student, 2 for teacher, 2 + is_superuser for admin,  5 for superuser

    STUDENT, PARENT, TEACHER = 0, 1, 2
    USER_TYPES = (
        (STUDENT, "Élève"),
        (PARENT, "Parent"),
        (TEACHER, "Enseignant"),
    )

    CIVILITIES = (
        ('Mme', 'Mme'),
        ('M.', 'M.'),
    )

    TZ_SET = []
    for tz in pytz.common_timezones:
        TZ_SET.append((tz,tz))

    user_type  = models.PositiveSmallIntegerField(editable=False, null=True, choices=USER_TYPES)
    civilite   = models.CharField(max_length=10, default='Mme', blank=True, choices=CIVILITIES, verbose_name="Civilité")
    time_zone  = models.CharField(max_length=100, null=True, blank=True, choices=TZ_SET, verbose_name="Fuseau horaire")
    is_extra   = models.BooleanField(default=0)
    is_manager = models.BooleanField(default=0)
    school     = models.ForeignKey(School, blank=True, null=True, related_name="users", default=None, on_delete = models.SET_NULL)
    schools    = models.ManyToManyField(School, related_name="schools_to_users", blank=True,  verbose_name="Autres établissement à administrer")
    cgu        = models.BooleanField(default=1)
    closure    = models.DateTimeField(blank=True, null=True, default = None ,  verbose_name="Date de fin d'adhésion")
    is_testeur = models.BooleanField(default=0)
    country    = models.ForeignKey(Country, blank=True, null=True, related_name="countries", default=None, on_delete = models.SET_NULL)
    is_board   = models.BooleanField(default=0)
    avatar     = models.ImageField(upload_to=avatar_directory_path,verbose_name="avatar", blank=True, null= True, default ="" )
    background = models.ImageField(upload_to=background_directory_path,verbose_name="background", blank=True, null= True, default ="" )
    backtitle  = models.ImageField(upload_to=background_directory_path,verbose_name="back title", blank=True, null= True, default ="" )

    def __str__(self):
        return "{} {}".format(self.last_name, self.first_name)

    @property
    def is_student(self):
        return self.user_type == self.STUDENT

    @property
    def is_parent(self):
        return self.user_type == self.PARENT

    @property
    def is_teacher(self):
        return self.user_type == self.TEACHER

    @property
    def is_creator(self):
        return self.is_staff == True

    @property
    def sacado(self):
        """
        L'enseignant est un membre bénéficiaire de sacado
        """
        sacado_asso = False
        if self.school  :
            sacado_asso = True
        return sacado_asso

    @property
    def is_sacado_member(self):
        is_sacado = False
        today = time_zone_user(self)
        try :
            abonnement = self.school.abonnement.last()
            if today < abonnement.date_stop and abonnement.is_active :
                is_sacado = True
        except :
            pass
        return is_sacado 


 
    def permit_access(self, model ):
        is_sacado = False
        today = time_zone_user(self)
        try :
            abonnement = self.school.abonnement.last()
            if (today < abonnement.date_stop and abonnement.is_active) or model.author.user == self :
                is_sacado = True
        except :
            if model.author.user == self :
                is_sacado = True
        return is_sacado 




    def my_groups(self):
        group_string = ""
        try :
            groups = self.student.students_to_group.all()
            n , i = groups.count() , 1
            sep = ""
            for g in self.student.students_to_group.all():
                if n == i :
                    sep = "<br/>"
                group_string += g.name+" (<small>"+g.teacher.user.last_name +" "+g.teacher.user.first_name+"</small>)"+sep
                i+=1
        except : 
            pass   

        return group_string


    @property
    def is_in_academy(self):
        is_sacado = False
        today = time_zone_user(self) 

        if self.school_id == 50 :
            if self.is_parent  :
                try :
                    facture = self.factures.order_by("chrono").last()
                    adhesions = facture.adhesions.all()
                    for adhesion in adhesions :
                        if today > adhesion.start and  today < adhesion.stop :
                            is_sacado = True
                            break
                except :
                    is_sacado = False
                if self.closure > today :
                    is_sacado = True
            elif self.is_student : 
                try :
                    adhesion = self.student.adhesions.order_by("stop").last()
                    if today > adhesion.start and  today < adhesion.stop :
                        is_sacado = True
                except:    
                    is_sacado = False
        
        return is_sacado 





class Student(ModelWithCode):
    """
    Modèle représentant un élève.
    """
    user      = models.OneToOneField(User, blank=True, related_name="student", on_delete=models.CASCADE, primary_key=True)
    level     = models.ForeignKey(Level, blank=True, related_name="level_student", default='', on_delete=models.PROTECT, verbose_name="Niveau")
    task_post = models.BooleanField(default=True, verbose_name="Notification de tache ?")
    ebep      = models.BooleanField(default=False, editable=False)

    def __str__(self):
        lname = self.user.last_name.capitalize()
        fname = self.user.first_name.capitalize()

        return "{} {}".format(lname, fname)


    def nb_parcours(self):
        nb = self.students_to_parcours.filter(is_publish=1).count()
        return nb


    def resultexercises(self):
        ''' résultats de l'étudiant aux exercices '''
        return self.results_e.all().select_related('exercise__knowledge')


    def resultexercises_dict(self):
        ''' dictionnaire des résultats de l'étudiant aux exercices
        cle : exercise_id
        valeur : score de l'étudiant à cet exercice
        '''
        return {exercise_id: point for exercise_id, point in self.results_e.values_list('exercise_id', 'point')}


    def resultexercises_by_theme(self, theme):
        ''' résultats de l'étudiant pour les évaluations de savoirs-faire d'un thème donné'''
        return self.results_e.filter(exercise__theme=theme).select_related('exercise')


    def resultknowledge(self):
        ''' résultats de l'étudiant aux évaluations de savoirs-faire '''
        return self.results_k.all()


    def resultknowledge_dict(self):
        ''' dictionnaire des résultats de l'étudiant aux évaluations de savoirs-faire
        cle : knowledge_id
        valeur : score de l'étudiant pour ce savoir faire
        '''
        return {knowledge_id: point for knowledge_id, point in self.results_k.values_list('knowledge_id', 'point')}


    def resultknowledge_by_theme(self, theme):
        ''' résultats de l'étudiant pour les évaluations de savoirs-faire d'un thème donné'''
        return self.results_k.filter(knowledge__theme=theme)


    def result_skills(self, skill):
        ''' résultats de l'étudiant aux 3 derniers exercices de compétences de la compétence en paramètre'''
        n = 3
        relationships = self.students_relationship.filter(skills = skill).order_by("-id")[:n]
        results = self.results_s.filter(skill=skill).order_by("-id")[:n]

        relationships = list(relationships)
        if len(relationships) < n :
            for i in range( n - len(relationships)  ) :
                relationships.append("")

        results = list(results)
        if len(results) < n :
            for i in range( n - len(results)  ) :
                results.append("")

        data = {}
        data["relationships"] = relationships
        data["results"] = results

        return data





    def bilan_skills(self, skill):
        ''' résultats de l'étudiant aux 3 derniers exercices de compétences de la compétence en paramètre'''
        n = 3
        results = self.results_s.filter(skill=skill).order_by("-id")[:10] 
        nb = len(results) 
        somme , i , coef = 0 , 0, 0
        for r in results:
            coef += 2**(nb-i)
            somme += r.point*2**(nb-i)
            i +=1
        try :
            avg = int(somme/coef)
        except :
            avg = None
        return avg





    def result_waitings(self, waiting):
        ''' résultats de l'étudiant aux 3 derniers exercices '''
        results = self.results_k.filter(knowledge__waiting = waiting).order_by("-id") 
        nb = len(results) 
        somme = 0
        for r in results:
            somme += r.point
        try :
            avg = int(somme/nb)
        except :
            avg = None
        return avg


    def result_skills_custom(self, skill):
        data = {}
        n = 3
        customexercises = self.students_customexercises.filter(skills = skill).order_by("-id")[:n] 
        results = self.student_correctionskill.filter(skill=skill).order_by("-id")[:n] 

        customexercises = list(customexercises)
        if len(customexercises) < n :
            for i in range( n - len(customexercises)  ) :
                customexercises.append("")

        results = list(results)
        if len(results) < n :
            for i in range( n - len(results)  ) :
                results.append("")

        data = {}
        data["customexercises"] = customexercises
        data["results"] = results
        return data


    def knowledge_average(self, group):

        Resultknowledge = apps.get_model('account', 'Resultknowledge')
        knowledges = group.level.knowledges.all()
        resultknowledges = Resultknowledge.objects.filter(student = self, knowledge__in=knowledges) 
        nb = len(resultknowledges)
        somme = 0

        for r in resultknowledges:
            somme += r.point
        try :
            avg = int(somme/nb)
        except :
            avg = ""
        return avg


    def nb_knowledge_worked(self, group):

        Resultknowledge = apps.get_model('account', 'Resultknowledge')
        Relationship = apps.get_model('qcm', 'Relationship')

        relationships = Relationship.objects.filter(students = self).values_list("exercise__knowledge__id").order_by("exercise__knowledge__id").distinct()
            
        n = relationships.count()
        knowledges = group.level.knowledges.all()

        nb = Resultknowledge.objects.filter(student = self, knowledge__in=knowledges).count()

        return  str(nb)+"/"+str(n) 


    def is_in_parcours(self, parcours):
        if self in parcours.students.all() :
            test =  True
        else :
            test = False

        return test



    def percent_done(self, parcours):
        """ Pourcentage d'exercices faits dans un parcours par un élève donné """
        nb_total_relationships = self.students_relationship.filter(parcours = parcours,is_publish=1,exercise__supportfile__is_title=0).count()

        nb_sta    = self.answers.filter(parcours= parcours).values("exercise").distinct().count()
        nb_exo_ce = self.student_custom_answer.filter(parcours = parcours, customexercise__is_publish = 1 ).count()

        nb_exo  = nb_sta + nb_exo_ce
     
     
        try :
            percent = int((nb_exo/nb_total_relationships) *100)
        except :
            percent = 0 
        data = {}
        data["nb"] =  nb_exo
        data["percent"] =  percent
        return data





    def has_exercise(self, relationship):
        if self in relationship.students.all() :
            test =  True
        else :
            test = False
        return test
 

    def has_customexercise(self, customexercise):
        if self in customexercise.students.all() :
            test =  True
        else :
            test = False
        return test
 

    def suiviparent(self):
        test = False
        groups = self.students_to_group.all()
        for group in groups :
            if group.suiviparent :
                test = True
                break
        return test


    def last_exercise(self):
        studentanswer = self.students_relationship.order_by("id").last()
        return studentanswer


    def is_task_exists(self,parcours):

        relationships = self.students_relationship.filter(parcours = parcours).exclude(date_limit = None)

        if len(relationships) == 0 :
            test = False #Aucune tache créée.
        else :
            test =  True #Tache créée.
        som = 0
        for relationship in relationships :
            if self.answers.filter(exercise = relationship.exercise).count()> 0:#Tache effectuée.
                som  +=1
        if len(relationships) == som :
            test = False
 
        return test




    def nb_task(self):

        relationships = self.students_relationship.exclude(date_limit = None)
        som = 0
        for relationship in relationships :
            if self.answers.filter(exercise = relationship.exercise).count()> 0:#Tache effectuée.
                som  +=1
        return relationships.count() - som


    def this_exercise_is_locked(self,exercise, parcours , custom, today):
        
        tst = False 

        try :
            if parcours.stop < today :
                tst = True
            else :
                if int(custom) == 1 :
                    if self.student_exerciselocker.filter(customexercise = exercise, custom = 1, lock__lt= today ).exists() :
                        tst = True 

                    try :
                        if exercise.lock < today :
                            tst = True
                    except :   
                        pass 
                else :

                    if self.student_exerciselocker.filter(relationship = exercise, custom = 0, lock__lt= today ).exists() :
                        tst = True

                    try :
                        if exercise.is_lock :
                            tst = True       
                    except :   
                        pass


        except :

            if int(custom) == 1 :
                if self.student_exerciselocker.filter(customexercise = exercise, custom = 1, lock__lt= today ).exists() :
                    tst = True 
                try :
                    if exercise.lock < today :
                        tst = True
                except :   
                    pass 
            else :

                if self.student_exerciselocker.filter(relationship = exercise, custom = 0, lock__lt= today ).exists() :
                    tst = True

                try :
                    if exercise.is_lock :
                        tst = True       
                except :   
                    pass
        return tst
                

    def is_lock_this_parcours(self,parcours,today):

        
        booleen , test , teest , tst   = False , False , False  , False    

        if parcours.stop < today :
            tst = True 

        nbe = self.students_relationship.filter(parcours=parcours).count()

        nbc = self.students_customexercises.filter(parcourses = parcours).count()
 

        n = 0
        for el in  self.student_exerciselocker.filter(customexercise__parcourses = parcours, custom = 1, lock__gt= today ) :
            n +=1
        if n == nbe :
            teest = True  

        m = 0
        for exl in  self.student_exerciselocker.filter(relationship__parcours = parcours, custom = 0, lock__gt= today ) :
            m +=1
        if m == nbc :
            test = True 

        if tst and (teest or test)  :
            booleen = True
 
        return booleen



    def score_quizz_random(self, quizz) :

        data = {}
        qrs = quizz.generate_qr.all() # toutes les questions
        score = self.questions_player.filter(  qrandom__in= qrs, is_correct = 1).count()
        nbre_total = self.questions_player.filter( qrandom__in= qrs).count()
        try :
            percent = 100 * score/nbre_total
            data["score"] = score
        except :
            percent = "A"
            data["score"] = "A"
        return data


 

    def documents_counter_by_student(self,group):
        """
        Donne le nombre total de parcours/évaluations, le nombre de visibles et de publiés du groupe
        """
        today      = time_zone_user(self.user) 
        bases      = self.students_to_parcours.filter(Q(is_publish=1) | Q(start__lte=today, stop__gte=today), subject = group.subject, level = group.level ,    is_archive=0, is_trash=0) 
        nb_folders = self.folders.filter(Q(is_publish=1) | Q(start__lte=today, stop__gte=today), subject = group.subject, level = group.level ,  is_archive=0,  is_trash=0).count() 
        nb         = bases.filter( is_evaluation = 0).count() 
        nbe        = bases.filter( is_evaluation = 1).count() 

        nbb        = self.bibliotexs.filter(Q(is_publish=1) | Q(start__lte=today, stop__gte=today), subjects = group.subject, levels = group.level ,   is_archive=0 ).count() 
        nbc        = bases.exclude(course = None ).count() 
        nbf        = self.flashpacks.filter(Q(is_publish=1) | Q(start__lte=today, stop__gte=today), subject = group.subject, levels = group.level ,   is_archive=0 ).count() 
        nbq        = self.quizz.filter(Q(is_publish=1) | Q(start__lte=today, stop__gte=today), subject = group.subject, levels = group.level ,   is_archive=0 ).count() 

        a_new_c    = self.student_custom_answer.values("parcours").filter(parcours__subject = group.subject ,is_reading=0).first()
        if a_new_c :
            a_new_cop = a_new_c 
        else :
            a_new_cop = False


        data = {}
        data["nb_parcours"]     = nb
        data["nb_evaluations"]  = nbe 
        data["nb_folders"]      = nb_folders 
        data["nb_bibliotex"]    = nbb
        data["nb_cours"]        = nbc 
        data["nb_flashpacks"]   = nbf
        data["nb_quizz"]        = nbq 
        data["a_new_cop"]       = a_new_cop 
        return data



    def data_menu(self):
        today    = time_zone_user(self.user)
        adhesion = self.adhesions.filter(stop__gte=today).last()
        data     = {}
        Formule = apps.get_model('setup', 'Formule')
        try :
            formule      = Formule.objects.get(pk=adhesion.formule_id )
            data["name"] = formule.name 
            data["id"]   = adhesion.formule_id
            return data
        except :
            return None




    def runnning_adhesion(self):
        today    = time_zone_user(self.user)
        adhesion = self.adhesions.filter(stop__gte=today).last()
        return adhesion


    def nb_subjects(self):
        subjects = self.students_to_group.values_list("subject",flat=True)
        return  subjects.count()


    def is_lesson(self):
        adhesion = self.adhesions.last()
        test = False
        if adhesion.formule_id == 4:
            test = True
        return test


    def can_ask_lesson(self):
        Transaction = apps.get_model('lesson', 'Transaction')
        cd = Transaction.objects.filter(user__in=self.students_parent.values_list("user_id",flat=True) ).aggregate(Sum("amount"))
        test = False
        if cd["amount__sum"] and cd["amount__sum"]>0:
            test = True
        return test
        # else :
        #     cd = Credit.objects.filter(user = self).aggregate(Sum("amount"))
        #     test = False
        #     if cd["amount__sum"]>0:
        #         test = True
        #     return test



class Adhesion(models.Model):
    """docstring for Facture"""
    amount     = models.DecimalField(max_digits = 6,decimal_places=2,  verbose_name="Montant", editable= False)
    formule_id = models.PositiveIntegerField( null=True, blank=True, verbose_name="Formule", editable= False)

    start      = models.DateTimeField(null=True, blank=True, editable= False)
    stop       = models.DateTimeField(null=True, blank=True, editable= False)

    level      = models.ForeignKey(Level, related_name="adhesions", on_delete=models.CASCADE, null=True,blank=True, editable= False)
    student    = models.ForeignKey(Student, related_name="adhesions", on_delete=models.CASCADE,  null=True, blank=True, editable= False)
    year       = models.PositiveIntegerField( default=2021,  editable= False)

    def __str__(self):
        return "{} {} : {}€".format(self.student.user.last_name, self.student.user.first_name, self.amount)

    def formule(self):
        Formule = apps.get_model('setup', 'Formule')
        return Formule.objects.get(pk = int(self.formule_id))


class Facture(models.Model):
    """docstring for Facture"""
    chrono    = models.CharField(max_length=50,  verbose_name="Chrono", editable= False) # Insertion du code de la facture.
    user      = models.ForeignKey(User, blank=True,  null=True, related_name="factures", on_delete=models.CASCADE, editable= False)
    file      = models.FileField(upload_to=file_directory_path,verbose_name="fichier", blank=True, null= True, default ="", editable= False)
    adhesions = models.ManyToManyField(Adhesion, related_name="factures", blank=True, editable= False)
    date      = models.DateTimeField(null=True, blank=True, editable= False)
    orderID   = models.CharField(max_length=25, verbose_name="Numéro de paiement donné par Paypal", blank=True, default="") 
    is_lesson = models.BooleanField(default=0, editable= False)

    def __str__(self):
        return "{} {}".format(self.user, self.file)





class Teacher(models.Model):
    """
    Modèle représentant un enseignant.
    """
    user          = models.OneToOneField(User, blank=True, related_name="teacher", on_delete=models.CASCADE, primary_key=True)
    levels        = models.ManyToManyField(Level, related_name="levels_to_group", blank=True, verbose_name="Niveaux préférés")
    notification  = models.BooleanField(default=0, verbose_name="Réception de notifications ?")
    exercise_post = models.BooleanField(default=0, verbose_name="Réception de notification de création d'exercice ?")
    subjects      = models.ManyToManyField(Subject, related_name="teacher", verbose_name="Enseignements")
    is_mailing    = models.BooleanField(default=0, verbose_name="Réception de messages ?")
    helping_right = models.BooleanField(default=0, verbose_name="Aide à distance ?")
    students      = models.ManyToManyField(Student, related_name="teachers", blank=True, editable= False)
    is_lesson     = models.BooleanField(default=0, verbose_name="Propose des cours ?")
    comment       = models.TextField( blank=True, null=True, verbose_name="Commentaire")
    tarif         = models.DecimalField(default=0, blank=True , max_digits=10, decimal_places=2)


    def __str__(self):
        return f"{self.user.last_name.capitalize()} {self.user.first_name.capitalize()}"





    def student_in_my_lesson(self,student):
        inside = False
        if student in self.students.all():
            inside = True
        return inside


    def notify_registration(self):
        """
        Envoie un email à l'enseignant l'informant de la réussite de son inscription
        """
        try :
            if self.user.email != '':
                send_templated_mail(
                    template_name="teacher_registration",
                    from_email= settings.DEFAULT_FROM_EMAIL ,
                    recipient_list=[self.user.email, ],
                    context={"teacher": self.user, }, )
        except :
            pass


    def notify_registration_to_admins(self):
        """
        Envoie un email aux administrateurs informant de l'inscription d'un nouvel enseignant
        """
        try :
            #admins = User.objects.filter(is_superuser=1)
            #admins_emails = list(admins.values_list('email', flat=True))
            admins_emails =["sacado.asso@gmail.com"]
            send_templated_mail(
                template_name="teacher_registration_notify_admins",
                from_email= settings.DEFAULT_FROM_EMAIL ,
                recipient_list=admins_emails,
                context={"teacher": self.user,}, )
        except :
            pass




    def sacado(self):
        """
        L'enseignant est un membre bénéficiaire de sacado
        """
        sacado_asso = False
        if self.user.school  :
            sacado_asso = True
        return sacado_asso


    def is_creator(self):
        """
        L'enseignant est un membre bénéficiaire de sacado
        """
        creator = False
        if self.user.is_creator  :
            creator = True
        return creator

 

    ################################################################################################
    # aefe
    ################################################################################################
    def historic_aefe(self,parcours):
        get = False
        if self.teacher_to_test.filter(origin = parcours).count()>0  :
            get = True
        return get



    def has_groups(self):
        return self.groups.all() | self.teacher_group.all()
        


    def nb_boolean_multi_subjects(self):
        nb = False
        if self.subjects.count() > 1 :
            nb = True
        return nb
        

class Resultknowledge(models.Model):
    student = models.ForeignKey(Student, related_name="results_k", default="", on_delete=models.CASCADE, editable=False)
    knowledge = models.ForeignKey(Knowledge, related_name="results_k", on_delete=models.CASCADE, editable=False)
    point = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "{}".format(self.point)

    class Meta:
        unique_together = ['student', 'knowledge']

class Resultskill(models.Model): # Pour récupérer tous les scores des compétences
    student = models.ForeignKey(Student, related_name="results_s", default="", on_delete=models.CASCADE, editable=False)
    skill = models.ForeignKey(Skill, related_name="results_s", on_delete=models.CASCADE, editable=False)
    point = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.skill} : {self.point}"

class Resultlastskill(models.Model): # Pour récupérer la moyenne des 10 derniers score des compétences
    student = models.ForeignKey(Student,   related_name = "student_resultskill", default="", on_delete=models.CASCADE, editable=False)
    skill = models.ForeignKey(Skill,   related_name = "student_resultskill", on_delete=models.CASCADE, editable=False)
    point  = models.PositiveIntegerField(default=0 ) 

    def __str__(self):
        return "{} : {}".format(self.skill, self.point)  

    class Meta:
        unique_together = ['student', 'skill']


class Parent(models.Model):
    """
    Modèle représentant un parent.
    """
    user        = models.OneToOneField(User, blank=True, related_name="parent", on_delete=models.CASCADE, primary_key=True)
    students    = models.ManyToManyField(Student, related_name="students_parent", editable=False)
    task_post   = models.BooleanField(default=1, verbose_name="Notification de tache ?")
    periodicity = models.PositiveIntegerField(default=14, verbose_name="Périodicité ? En nombre de jours")

    def __str__(self):
        lname = self.user.last_name.capitalize()
        fname = self.user.first_name.capitalize()

        child = ""
        for s in self.students.all():
            child += s.user.last_name + " " + s.user.first_name + "-"

        return "{} {} - {}".format(lname, fname, child)


    def is_lesson(self):
        test = False
        for student in self.students.all() :
            adhesion = student.adhesions.last()
            if adhesion.formule_id == 4:
                test = True
                break
        return test







class Response(models.Model):

    admin = models.ForeignKey(User, blank=True,  null=True, related_name="response", on_delete=models.CASCADE, editable= False)
    user = models.ForeignKey(User, blank=True,  null=True, related_name="user_response", on_delete=models.CASCADE, editable= False)
    response = models.TextField(blank=True,  null=True )
    message = models.TextField(blank=True,  null=True )
    date_created = models.DateTimeField(auto_now=True, editable= False)
    is_read = models.BooleanField(default=0, editable= False)

    def __str__(self):
        return f"{self.response}"



class Newpassword(ModelWithCode):
    """
    Modèle de ré initialisation de password.
    """
    email = models.CharField(max_length=255 )  
 

    def __str__(self):
        email = self.email
        return "{}".format(email )



