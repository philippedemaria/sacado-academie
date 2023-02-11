import uuid
from django.db import models
from datetime import date, datetime, timedelta

from group.models import  Group
from django.utils import timezone
from account.models import Student, Teacher, ModelWithCode, generate_code, User
from socle.models import  Knowledge, Level , Theme, Skill , Subject
from django.apps import apps
from ckeditor_uploader.fields import RichTextUploadingField
from django.db.models import Q, Min, Max ,Avg
import os.path
from django.utils import timezone
from general_fonctions import *
# Pour créer un superuser, il faut depuis le shell taper :
# from account.models import User 
# User.objects.create_superuser("admin","admin@gmail.com","motdepasse", user_type=0).save()
########################################################################################################
########################################################################################################
# cette parties sert à créer un répertoire par user pour sauvegarder les fichiers
 
 
def quiz_directory_path(instance, filename):
    return "ggbfiles/{}/{}".format(instance.level.id, filename)

def image_directory_path(instance, filename):
    return "ggbimages/{}/{}".format(instance.level.id, filename)

def vignette_directory_path(instance, filename):
    return "vignettes/{}/{}".format(instance.teacher.user.id, filename)


def file_directory_path(instance, filename):
    return "files/{}/{}".format(instance.relationship.parcours.teacher.user.id, filename)


def file_folder_path(instance, filename):
    return "files/{}/{}".format(instance.customexercise.teacher.user.id, filename)

def directory_path_mastering(instance, filename):
    return "mastering/{}/{}".format(instance.relationship.parcours.teacher.user.id, filename)
 
def directory_path(instance, filename):
    return "demandfiles/{}/{}".format(instance.level.id, filename)

def file_attach_path(instance, filename):
    return "attach_files/{}/{}".format(instance.level.id, filename)


def file_directory_student(instance, filename):
    return "files/{}/{}".format(instance.student.user.id, filename)

def file_directory_to_student(instance, filename):
    return "files/{}/{}".format(instance.customanswerbystudent.student.user.id, filename)


def audio_directory_path(instance,filename):
    return "audio/{}/{}".format(instance.id,filename)

def etype_directory_path(instance, filename):
    return "exercise/qtype/{}".format(filename)


def choice_directory_path(instance, filename):
    return "exercise/choices/{}".format(filename) 


def subchoice_directory_path(instance, filename):
    return "images_legendables/{}/{}".format(instance.supportchoice.id, filename)



def convert_time(duree) :
    try :
        d = int(duree)
        if d < 59 :
            return duree+"s"
        elif d < 3600:
            s = d%60        
            m = int((d-s)/60)
            return str(m)+"min "+str(s)+"s"
        else :
            return  "td" #temps dépassé
    except :
        return ""


########################################################################################################
########################################################################################################
########################################################################################################
########################################################################################################
class Criterion(models.Model):
    label     = models.TextField( verbose_name="Critère") 
    subject   = models.ForeignKey(Subject, related_name="criterions", on_delete=models.CASCADE, default='', blank=True, null=True, verbose_name="Enseignement")
    level     = models.ForeignKey(Level, related_name="criterions", default="", blank=True, null=True, on_delete=models.CASCADE, verbose_name="Niveau")
    knowledge = models.ForeignKey(Knowledge, related_name="criterions", on_delete=models.CASCADE, default='', blank=True, null=True, verbose_name="Thème")
    skill     = models.ForeignKey(Skill, related_name="criterions", default="", on_delete=models.CASCADE, blank=True, null=True, verbose_name="Compétences")
    def __str__(self):       
        return "{}".format(self.label)

    def results( self , customexercise, parcours , student):
        autoposition = self.autopositions.filter(customexercise = customexercise, parcours = parcours, student = student).last()
        return autoposition.position
########################################################################################################
########################################################################################################
class Supportfile(models.Model):


    title = models.CharField(max_length=255, null=True, blank=True,   verbose_name="Titre")
    knowledge = models.ForeignKey(Knowledge, on_delete=models.PROTECT,  related_name='supportfiles', verbose_name="Savoir faire associé")
    annoncement = models.TextField( default = "" , blank=True, verbose_name="Consigne")
    author = models.ForeignKey(Teacher, related_name="supportfiles", on_delete=models.PROTECT, editable=False)

    code = models.CharField(max_length=100, unique=True, blank=True, default='', verbose_name="Code*")
    #### pour validation si le qcm est noté

    situation = models.PositiveIntegerField(default=5, blank=True, verbose_name="Nombre minimal de situations", help_text="Pour valider le qcm")
    calculator = models.BooleanField(default=0, verbose_name="Calculatrice ?")
    #### 
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modified = models.DateTimeField(auto_now=True, verbose_name="Date de modification")

    level = models.ForeignKey(Level, related_name="supportfiles", on_delete=models.PROTECT, verbose_name="Niveau")
    theme = models.ForeignKey(Theme, related_name="supportfiles", on_delete=models.PROTECT, verbose_name="Thème")

    width = models.PositiveIntegerField(default=750,  blank=True,verbose_name="Largeur")
    height = models.PositiveIntegerField(default=550,  blank=True,verbose_name="Hauteur")
    ggbfile = models.FileField(upload_to=quiz_directory_path, verbose_name="Fichier ggb",blank=True, default="" )
    imagefile = models.ImageField(upload_to=image_directory_path, verbose_name="Vignette d'accueil", blank=True, default="qtype_img/underlayer.png")

    toolBar = models.BooleanField(default=0, verbose_name="Barre des outils ?")
    menuBar = models.BooleanField(default=0, verbose_name="Barre de menu ?")
    algebraInput = models.BooleanField(default=0, verbose_name="Multi-fenêtres ?")
    resetIcon = models.BooleanField(default=0, verbose_name="Bouton Reset ?")
    dragZoom = models.BooleanField(default=0, verbose_name="Zoom/déplacement ?")

    is_title = models.BooleanField(default=0, editable=False, verbose_name="titre pour l'organisation des parcours")
    is_subtitle = models.BooleanField(default=0 , verbose_name="sous-titre pour l'organisation des parcours")
    attach_file = models.FileField(upload_to=file_attach_path, blank=True,  verbose_name="Fichier pdf attaché", default="")

    duration = models.PositiveIntegerField(default=15, blank=True, verbose_name="Durée estimée")
    skills = models.ManyToManyField(Skill, blank=True, related_name='skills_supportfile', verbose_name="Compétences ciblées")

    is_ggbfile = models.BooleanField(default=1, verbose_name="Type de support")
    is_python  = models.BooleanField(default=0, verbose_name="Python ?")
    is_scratch = models.BooleanField(default=0, verbose_name="Scratch ?")
    is_file    = models.BooleanField(default=0, verbose_name="Fichier ?")
    is_image   = models.BooleanField(default=0, verbose_name="Iage/Scan ?")
    is_text    = models.BooleanField(default=0, verbose_name="Texte ?")

    ####  Notation
    is_mark = models.BooleanField(default=0,  verbose_name="Notation ?")
    mark    = models.PositiveIntegerField(default=0, blank=True,verbose_name="Sur ?")
    ####  Partage
    is_share    = models.BooleanField(default=1, verbose_name="Mutualisé ?")
    is_realtime = models.BooleanField(default=0, verbose_name="Temps réel ?")

    ranking = models.PositiveIntegerField(  default=0,  blank=True, null=True, editable=False)
    ####  Corrigé
    correction = models.TextField( blank=True, default="", null=True, verbose_name="Corrigé")
    is_display_correction = models.BooleanField(default=0, verbose_name="Afficher le corrigé ?") 
    criterions   = models.ManyToManyField(Criterion, blank=True, related_name='supportfiles' )
    ####################################################################################################################################
    #### Pour rattacher les exercices non GGB
    ####################################################################################################################################
    ####  Format de l'exercice
    qtype         = models.PositiveIntegerField(default=100)    
    nb_pseudo     = models.PositiveIntegerField(default=0, blank=True,  verbose_name="Nombre de pseudo situation")
    nb_subpseudo  = models.PositiveIntegerField(default=0, blank=True,  verbose_name="Nombre de pseudo proposition")      

    def __str__(self): 
        knowledge = self.knowledge.name[:20]       
        return "{} > {} > {}".format(self.level.name, self.theme.name, knowledge)


    def qtype_obj(self):        
        Qtype = apps.get_model('tool', 'Qtype')
        return Qtype.objects.get(pk=self.qtype)


    def qtype_title(self):
        Qtype = apps.get_model('tool', 'Qtype')
        qt = Qtype.objects.get(pk=self.qtype)
        return qt.title


    def qtype_logo(self):        
        Qtype = apps.get_model('tool', 'Qtype')
        logo = Qtype.objects.get(pk=self.qtype).imagefile
        return logo


    def this_template(self):
        Qtype = apps.get_model('tool', 'Qtype')
        qt = Qtype.objects.get(pk=self.qtype)
        return 'qcm/qtype/ans_'+qt.custom+'.html'


    def is_alea(self):
        test = False
        supportchoice = self.supportchoices.first()
        if supportchoice.precision : test = True
        return test






    def grid(self):

        support_choices = list()
        nb_pseudo = self.nb_pseudo
        supportchoices = self.supportchoices.all()
        if nb_pseudo :
            supportchoices = supportchoices[0,nb_pseudo]

        for choice in supportchoices :
            support_choices.append(choice.answer)
        return create_string_table(support_choices) 


    def element_is_display(self):
        data = dict()
        scores        = [0,True,True,True,True,False,False,True,False,True,False,False,True,True,True,False,False,False,False,False,False]
        visus         = [0,True,True,False,False,True,True,True,False,False,False,False,True,True,True,False,False,False,False,False,False]
        data["score"] = scores[self.qtype]
        data["visu"]  = visus[self.qtype] 
        return data 

    def levels_used(self):
        return self.exercises.select_related('level')


    def all_parcourses(self):
        exercises =  self.exercises.all()
        parcourses = Relationship.objects.values_list("parcours").filter(exercise__in=exercises)
        return parcourses



    def in_folder(self) :

        folder_path = "/home/c1398844c/sacado/media/"
        data = {}
        #folder_path  = "D:/uwamp/www/sacadogit/sacado/media/"
        
        if os.path.isfile(folder_path+str(self.ggbfile)):
            data["file_in_folder"] = True
        else:
            data["file_in_folder"] = False

        if os.path.isfile(folder_path+str(self.imagefile)):
            data["image_in_folder"] = True
        else:
            data["image_in_folder"] = False
        return data

    def used_in_parcours(self, teacher):
        exercises = self.exercises.all()
        parcours = Parcours.objects.filter(exercises__in= exercises, author=teacher)
        return parcours

class Supportvariable(models.Model):

    name       = models.CharField(max_length=50,  blank=True, verbose_name="variable")
    supporfile = models.ForeignKey(Supportfile, related_name="supportvariables", blank=True, null = True,  on_delete=models.CASCADE)
    ## Variable numérique
    is_integer = models.BooleanField(default=1, verbose_name="Valeur entière ?") 
    is_notnull = models.BooleanField(default=1, verbose_name="Exclure 0 ?")       
    maximum    = models.IntegerField(default=10)
    minimum    = models.IntegerField(default=0)
    ## Variable littérale
    words      = models.CharField(max_length=255,  blank=True, verbose_name="Liste de valeurs")

    def __str__(self):
        return self.name 
 

class SupportvariableImage(models.Model):

    variable = models.ForeignKey(Supportvariable, related_name="supportvariables_img", blank=True, null = True,  on_delete=models.CASCADE)
    image    = models.ImageField(upload_to=vignette_directory_path,   verbose_name="Image", default="")

    def __str__(self):
        return self.variable.name 


######################################################################
#####  type de réponse possible et choix pour les types de questions
######################################################################
class Supportchoice(models.Model):
    """
    Modèle représentant un associé.
    """
    imageanswer = models.ImageField(upload_to=choice_directory_path,  null=True,  blank=True, verbose_name="Image", default="")
    answer      = models.TextField(default='', null=True,  blank=True, verbose_name="Réponse écrite")
    retroaction = models.TextField(default='', null=True,  blank=True, verbose_name="Rétroaction")
    audioanswer = models.FileField(upload_to=choice_directory_path,  null=True,  blank=True, verbose_name="Audio", default="")

    imageanswerbis = models.ImageField(upload_to=choice_directory_path,  null=True,  blank=True, verbose_name="Image par paire", default="")
    answerbis      = models.TextField(max_length=255, default='', null=True,  blank=True, verbose_name="Réponse par paire")
    audioanswerbis = models.FileField(upload_to=choice_directory_path,  null=True,  blank=True, verbose_name="Audio", default="")

    is_correct  = models.BooleanField(default=0, blank=True, verbose_name="Réponse correcte ?")
    supportfile = models.ForeignKey(Supportfile, related_name="supportchoices", blank=True, null = True,  on_delete=models.CASCADE)

    ####  Cas spécifique axe gradué
    xmin       = models.FloatField( null = True,   blank=True, verbose_name="x min ")
    xmax       = models.FloatField( null = True,   blank=True, verbose_name="x max ")
    tick       = models.FloatField( null = True,   blank=True, verbose_name="Graduation principale")
    subtick    = models.FloatField( null = True,   blank=True, verbose_name="Graduation")
    precision  = models.FloatField( null = True,   blank=True, verbose_name="Précision") 
    ####  Cas spécifique texte à trous
    is_written = models.BooleanField(default=0, blank=True,  verbose_name="Mots à écrire ?") # ou à glisser déposer

    def __str__(self):
        return self.answer 



class Supportsubchoice(models.Model):
    """
    Modèle représentant un associé.
    """
    imageanswer   = models.ImageField(upload_to=subchoice_directory_path,  null=True,  blank=True, verbose_name="Image", default="")
    answer        = models.TextField(default='', null=True,  blank=True, verbose_name="Réponse écrite")
    retroaction   = models.TextField(default='', null=True,  blank=True, verbose_name="Rétroaction")
    label         = models.CharField(max_length=255, default='', null=True,  blank=True, verbose_name="Label")#pour les position sur images
    is_correct    = models.BooleanField(default=0, verbose_name="Réponse correcte ?")
    supportchoice = models.ForeignKey(Supportchoice, related_name="supportsubchoices", blank=True, null = True,  on_delete=models.CASCADE)
    def __str__(self):
        return self.answer 


class Exercise(models.Model):
    level       = models.ForeignKey(Level, related_name="exercises", on_delete=models.PROTECT, verbose_name="Niveau")
    theme       = models.ForeignKey(Theme, related_name="exercises", on_delete=models.PROTECT, verbose_name="Thème")
    knowledge   = models.ForeignKey(Knowledge, on_delete=models.PROTECT, related_name='exercises',
                                  verbose_name="Savoir faire associé - Titre")
    supportfile = models.ForeignKey(Supportfile, blank=True, default=1, related_name="exercises",
                                    on_delete=models.CASCADE, verbose_name="Fichier Géogebra")
    ranking     = models.PositiveIntegerField(  default=0,  blank=True, null=True, editable=False)
    audiofile   = models.FileField(upload_to=audio_directory_path, verbose_name="Fichier Audio", blank=True, default="" )


    def __str__(self):
        return "{}".format(self.knowledge.name)

    class Meta:
        unique_together = ('knowledge', 'supportfile')


    def send_score(self, student):
        try:
            r = Resultexercise.objects.get(student=student, exercise=self)
            return int(r.point)
        except:
            return ""

    #############################################
    # non utilisée ?????? 
    def send_scores(self, student_id):
        score = ""
        student = Student.objects.get(pk=student_id)
        if student.answers.filter(exercise=self.pk).exists():
            studentanswers = student.answers.filter(exercise=self.pk)
            for studentanswer in studentanswers:
                score = score + str(studentanswer.point) + " - "
        return score
    ############################################# 
    def is_exercise(self):
        return True


    def score_and_time(self, student_id):
        scores_times_tab = []
        student = Student.objects.get(pk=student_id)
        if student.answers.filter(exercise=self.pk).exists():
            studentanswers = student.answers.filter(exercise=self.pk)
            for studentanswer in studentanswers:
                scores_times = {}
                scores_times["score"] = studentanswer.point
                scores_times["time"] = convert_time(studentanswer.secondes)
                scores_times["numexo"] = studentanswer.numexo
                scores_times["date"] = studentanswer.date
                scores_times_tab.append(scores_times)
        return scores_times_tab

    def details(self, parcours):
        details, tab = {}, []
        somme = 0
        for student in parcours.students.all():
            try:
                studentanswer = student.answers.filter(exercise=self, parcours=parcours).last()
                somme += studentanswer.point
                tab.append(studentanswer.point)
            except:
                pass

        try:
            avg = somme / len(tab)
            tab.sort()
            details["min"] = tab[0]
            details["max"] = tab[-1]
            details["avg"] = int(avg)
        except:
            details["min"] = 0
            details["max"] = 0
            details["avg"] = 0

        return details



    def last_score_and_time(self, parcours, student_id):
        student = Student.objects.get(pk=student_id)
        scores_times = {}
        if student.answers.filter(exercise=self.pk, parcours=parcours).exists():
            studentanswer = student.answers.filter(exercise=self.pk, parcours=parcours).last()
            scores_times["score"] = studentanswer.point
            scores_times["time"] = convert_time(studentanswer.secondes)
        else :
            scores_times["score"] = None
            scores_times["time"] = None


        return scores_times

    def timer(self, parcours, student_id):
        reponse, datetime_object = "", ""
        student = Student.objects.get(pk=student_id)
        if student.answers.filter(exercise=self.pk, parcours=parcours).exists():
            studentanswer = student.answers.filter(exercise=self.pk).last()
            reponse = int(studentanswer.secondes)
            if reponse > 59:
                minutes = int(reponse / 60)
                scdes = reponse % 60

                datetime_object = str(minutes) + "min" + str(scdes) + "s"
            else:
                datetime_object = str(reponse) + " s"
        return datetime_object

    def is_selected(self, parcours):
        relationship = Relationship.objects.filter(parcours=parcours, exercise=self)
        return relationship.count() == 1


    def is_ranking(self, parcours):
        try :
            relationship = Relationship.objects.get(parcours=parcours, exercise=self)
            rk = relationship.ranking
        except :
            rk = ""
        return rk


    def is_relationship(self ,parcours):
        try:
            relationship = Relationship.objects.get(parcours=parcours, exercise=self)
        except:
            relationship = False
        return relationship

    def used_in_parcours(self, teacher):
        parcours = Parcours.objects.filter(exercises=self, author=teacher)
        return parcours

    def is_used(self):
        '''
        Vérifie si l'exercice a été associé à un parcours
        '''
        return Relationship.objects.filter(exercise=self).exists()

    def is_done(self,student):
        return student.answers.filter(exercise=self).exists()

    def nb_task_done(self, group):
        """
        group ou parcours car on s'en sert pour récupérer les élèves
        """
        try:
            studentanswer_tab = []
            for s in group.students.all():
                studentanswer = s.answers.filter(exercise=self).first()
                if studentanswer :
                    studentanswer_tab.append(studentanswer)
            nb_task_done = len(studentanswer_tab)
        except:
            nb_task_done = 0
        return nb_task_done

    def who_are_done(self, group):
        studentanswer_tab = []
        try:
            for s in group.students.all():
                studentanswer = Studentanswer.objects.filter(exercise=self, student=s).first()
                if studentanswer:
                    studentanswer_tab.append(studentanswer)
        except:
            pass
        return studentanswer_tab

    def nb_task_parcours_done(self, parcours):
        studentanswer_tab = []
        for s in parcours.students.all():
            studentanswer = Studentanswer.objects.filter(exercise=self, student=s).first()
            if studentanswer:
                studentanswer_tab.append(studentanswer)
        nb_task_done = len(studentanswer_tab)
        return nb_task_done

    def who_are_done_parcours(self,parcours):
        studentanswer_tab = []
        for s in parcours.students.all():
            studentanswer = Studentanswer.objects.filter(exercise = self, student = s).first()
            if studentanswer :
                studentanswer_tab.append(studentanswer)
        return studentanswer_tab

    def levels_used(self):

        exercises = Exercise.objects.filter(level=self.supportfile)
        return exercises

    def my_parcours_container(self, teacher):

        parcours = self.exercises_parcours.filter(teacher=teacher)
        return parcours


    def ebep(self):
        """l'exercice utilise des outils pour les EBEP"""
        ok = False
        if self.tools.count() > 0 :
            ok = True
        return ok


    def remediations():
        remediations = Remediation.objects.filter(relationship__exercise=self)
        return remediations


class Parcours(ModelWithCode):

    title = models.CharField(max_length=255, verbose_name="Titre")
    color = models.CharField(max_length=255, default='#5d4391', verbose_name="Couleur")
    author = models.ForeignKey(Teacher, related_name="author_parcours", on_delete=models.CASCADE, default='', blank=True, null=True, verbose_name="Auteur")
    teacher = models.ForeignKey(Teacher, related_name="teacher_parcours", on_delete=models.CASCADE, default='', blank=True, editable=False)
    coteachers = models.ManyToManyField(Teacher, blank=True,  related_name="coteacher_parcours",  verbose_name="Enseignant en co-animation")
    subject = models.ForeignKey(Subject, related_name="subject_parcours", on_delete=models.CASCADE, default='', blank=True, null=True, verbose_name="Enseignement")
    
    groups = models.ManyToManyField(Group,  blank=True,  related_name="group_parcours" )

    exercises = models.ManyToManyField(Exercise, blank=True, through="Relationship", related_name="exercises_parcours")
    students = models.ManyToManyField(Student, blank=True, related_name='students_to_parcours', verbose_name="Elèves")
    is_share = models.BooleanField(default=0, verbose_name="Mutualisé ?")
    is_publish = models.BooleanField(default=0, verbose_name="Publié ?")
    is_archive = models.BooleanField(default=0, verbose_name="Archivé ?", editable=False)
    is_achievement = models.BooleanField(default=0, verbose_name="Avancement ?")

    level = models.ForeignKey(Level, related_name="level_parcours", on_delete=models.CASCADE, default='', blank=True, null=True)
    linked = models.BooleanField(default=0, editable=False)
    is_favorite = models.BooleanField(default=1, verbose_name="Favori ?")

    is_evaluation = models.BooleanField(default=0, editable=False)
    is_active = models.BooleanField( default=0,  verbose_name="Page d'accueil élève")  

    is_next = models.BooleanField(default=0, verbose_name="Suivant ?")
    is_exit = models.BooleanField(default=0, verbose_name="Retour aux exercices ?")
    is_stop = models.BooleanField(default=0, verbose_name="Limité ?")

    duration = models.PositiveIntegerField(default=2, blank=True, verbose_name="Temps de chargement (min.)")
    start = models.DateTimeField(null=True, blank=True, verbose_name="A partir de")
    stop = models.DateTimeField(null=True, blank=True, verbose_name="Date de verrouillage")

    zoom = models.BooleanField(default=1, verbose_name="Zoom ?")

    maxexo = models.IntegerField(  default=-1,  blank=True, null=True,  verbose_name="Tentatives")

    vignette = models.ImageField(upload_to=vignette_directory_path, verbose_name="Vignette d'accueil", blank=True, default ="")
    ranking = models.PositiveIntegerField(  default=0,  blank=True, null=True, editable=False)
    
    is_trash = models.BooleanField(default=0, verbose_name="Poubelle ?", editable=False)

    is_sequence = models.BooleanField(default=0, verbose_name="Séquence d'apprentissage ?", editable=False)

    def __str__(self):
        flds = ""
        for f in self.folders.all():
            flds += f.title+" - "
 
        try :
            if self.coteachers.count() > 0 and flds != "" :
                return "{} > {} [CoA]".format(flds, self.title)
            elif self.coteachers.count() > 0 and flds == "" :
                return "{} [CoA]".format(self.title)
            else :
                return "{}".format(self.title)
        except :
            return "{}".format(self.title)

 
    def contains_exercises(self):
        contains = False
        if self.parcours_relationship.count() > 0 :
            contains = True
        return contains

 
    def contains_exo_perso(self):
        contains = False
        if self.parcours_customexercises.count() > 0 :
            contains = True
        return contains


    def contains_student(self):
        contains = False
        if self.students.count() > 0 :
            contains = True
        return contains


    def publish_parcours_inside_folder(self, folders, student) :
        """Détermine si un parcours est publié et s'il est dans un dossier publié """
        is_publish = self.is_publish
        nb_folders_published = self.folders.filter(students=student, is_publish=1).count()
        if nb_folders_published > 0 :
            is_publish = False
        return is_publish


    def isnot_shared(self) :
        test = False
        if self.groups.exclude(teacher_id=2480).count()>1:
            test = True
        return test

    def is_available(self,student,exercise) :
        data = {}
        is_ok = True
        nbs = Studentanswer.objects.filter(parcours=self , exercise= exercise,student = student ).count()

        try : 
            nbleft = self.maxexo - nbs
        except :
            nbleft = self.maxexo 

        if nbleft == 0  :
            is_ok = False
        if self.maxexo == -1   :
            is_ok = True

        data["is_ok"] = is_ok
        data["nbleft"] = nbleft

        return data


    def is_done(self,student):
        Studentanswer = apps.get_model('qcm', 'Studentanswer')
        studentanswers = Studentanswer.objects.filter(student=student, parcours=self).values_list("exercise",flat=True).order_by("exercise").distinct()
        n = len(studentanswers) 
        return n

    def is_affect(self, student):
        nb_relationships = Relationship.objects.filter(parcours=self, exercise__supportfile__is_title=0,
                                                       students=student, is_publish=1).count()
        return nb_relationships

    def is_lock(self,today):
        lock = False
        try :
            if self.stop < today :
                lock = True 
        except :
            pass
        return lock


    def get_themes(self):
        exercises = self.exercises.filter(supportfile__is_title=0)
        theme_tab, theme_tab_id  = [] , []
        for exercise in exercises :
            data = {}
            if not exercise.theme.id in theme_tab_id :
                data["theme"] = exercise.theme
                data["annoncement"] = exercise.supportfile.annoncement              
                theme_tab_id.append(exercise.theme.id)
                theme_tab.append(data)
        return theme_tab


    def nb_exercises(self):
        nb = self.parcours_relationship.filter(exercise__supportfile__is_title=0).count()
        nba = self.parcours_customexercises.all().count()     
        return nb + nba





    def exercises_only(self):
        exercises = self.exercises.filter(supportfile__is_title=0).prefetch_related('level')
        return exercises 

    def level_list(self):
        exercises_level_tab = self.exercises.values_list("level__name",flat=True).filter(supportfile__is_title=0).prefetch_related("level").order_by("level").distinct()
        return exercises_level_tab

        

    def duration_overall(self):
        som = self.duration
        for d in self.parcours_relationship.select_related('duration').values_list('duration',flat=True).filter(is_publish=1):
            som += d
        for e in self.parcours_customexercises.select_related('duration').values_list('duration',flat=True).filter(is_publish=1):
            som += e
        return som 

    def duration_reader_course(self):
        som = 0
        for c in self.course.select_related('duration').values_list('duration',flat=True).filter(is_publish=1):
            som += c
        return som 



    def level_by_exercises(self):
        
        exercises = self.exercises.filter(supportfile__is_title=0).prefetch_related("level").order_by("level")
        dct , tab =  {} , [] 
        for l in Level.objects.all():
            dct[l.shortname] = 0
        for e  in exercises :
            dct[e.level.shortname] +=1
        tab = []
        for k, v in sorted(dct.items(), key=lambda x: x[1]):
            name = k
        return name

    def group_list(self):
        groups = self.groups.all()
        return groups

    def shared_group_list(self):

        Sharing_group = apps.get_model('group', 'Sharing_group')
        group_tab = Sharing_group.objects.filter(teacher = self.teacher)
        return group_tab 



    def parcours_shared(self):

        students = self.students.all() #Elève d'un parcours
        shared = False
        for s  in students :
            if len(s.students_to_group.all()) > 1 :
                shared = True
                break
        return shared



    def parcours_group_students_count(self,group):

        data = {}
        group_students = group.students.all() #.exclude(user__username__contains="_e-test")
        parcours_students = self.students.exclude(user__username__contains="_e-test")
        intersection = list(set(group_students) & set(parcours_students))

        data["nb"]= len(intersection)
        data["students"] = intersection
        return data 
 

    def just_students(self):
        return self.students.exclude(user__username__contains="_e-test").order_by("user__last_name")



    def only_students(self,group):
        if group :
            return self.students.filter(students_to_group=group).exclude(user__username__contains="_e-test").order_by("user__last_name")            
        else :
            return self.students.exclude(user__username__contains="_e-test").order_by("user__last_name")


 
    def is_task_exists(self):
        today = timezone.now()
        test = False
        if Relationship.objects.filter(parcours= self,date_limit__gte = today).count() > 0 :
            test = True
        if Customexercise.objects.filter(parcourses = self, date_limit__gte = today).count() > 0 :
            test = True
        return test 



    def is_individualized(self):

        test = False
        students_parcours = self.students.all() # élève du parcours
        relation_ships = self.parcours_relationship.all()
        for r in relation_ships :
            if r.students.exclude(user__username__contains="_e-test").count() != self.students.exclude(user__username__contains="_e-test").count() :
                test = True
            break 
        return test 


    def is_courses_exists(self):

        test = False
        if self.course.count() > 0 :
            test = True
        return test 


    def is_sections_exists(self) :

        test = False
        if self.parcours_relationship.filter(exercise__supportfile__is_title = 1).count() > 0 :
            test = True
        return test 

    def nb_task(self):

        today = timezone.now()
        nb = self.parcours_relationship.filter(date_limit__gte = today).count()
        return nb

    def evaluation_duration(self):
        """
        Calcul de la durée d'une évaluation par somme des temps d'exercices choisis
        """
        relationships = self.parcours_relationship.all()
        som = self.duration
        for r in relationships : 
            som += r.duration

        customexercises = self.parcours_customexercises.all()
        for c in customexercises : 
            som += c.duration

        return som 


 

    def is_percent(self,student):
        ## Nombre de relationships dans le parcours => nbre  d'exercices
 
        nb_relationships =  self.parcours_relationship.filter(students = student, is_publish=1,  exercise__supportfile__is_title=0 ).count()
        nb_customs =  self.parcours_customexercises.filter(students = student, is_publish=1).count()

        ## Nombre de réponse avec exercice unique du parcours
        nb_studentanswers = Studentanswer.objects.filter(student=student, parcours=self).values_list("exercise",flat=True).order_by("exercise").distinct().count()
        nb_customanswerbystudent = Customanswerbystudent.objects.filter(student=student, customexercise__parcourses=self).values_list("customexercise",flat=True).order_by("customexercise").distinct().count()

 
        data = {}
        nb_exercise_done = nb_studentanswers + nb_customanswerbystudent
        data["nb"] = nb_exercise_done
        data["nb_total"] = nb_relationships + nb_customs
        try :
            maxi = int(nb_exercise_done * 100/(nb_relationships+nb_customs))
            if int(nb_exercise_done * 100/(nb_relationships+nb_customs)) > 100:
                maxi = 100
            data["pc"] = maxi
            data["opac"] = 0.3 + 0.7*maxi/100
        except :
            data["pc"] = 0
            data["opac"] = 1

        return data



    def get_details_for_min_score(self,student):
        ## Nombre de relationships dans le parcours => nbre  d'exercices
        relationships    =  self.parcours_relationship.filter(students = student, is_publish=1,  exercise__supportfile__is_title=0 ) 
        customs          =  self.parcours_customexercises.filter(students = student, is_publish=1) 
        nb_relationships =  relationships.count()
        nb_customs       =  customs.count()

        ## Nombre de réponse avec exercice unique du parcours
        answers                  = self.answers.filter(student=student).values_list("exercise",flat=True).order_by("exercise").distinct()
        nb_studentanswers        = answers.count()

        answers_c                = Customanswerbystudent.objects.filter(student=student, customexercise__parcourses=self).values_list("customexercise",flat=True).order_by("customexercise").distinct()
        nb_customanswerbystudent = answers_c.count()

        data = {}
        nb_exercise_done = nb_studentanswers + nb_customanswerbystudent
        data["nb"] = nb_exercise_done
        data["nb_total"] = nb_relationships + nb_customs
        try :
            maxi = int(nb_exercise_done * 100/(nb_relationships+nb_customs))
            if int(nb_exercise_done * 100/(nb_relationships+nb_customs)) > 100:
                maxi = 100
            data["pc"] = maxi
            data["opac"] = 0.3 + 0.7*maxi/100
        except :
            data["pc"] = 0
            data["opac"] = 1

        return data  ,  relationships , customs, answers ,  answers_c





    def min_score(self,student):
        """
        min score d'un parcours par élève
        """
        data  ,  relationships , custom_exercises, answers ,  answers_c = self.get_details_for_min_score(student)
        max_tab, max_tab_custom = [] , []
        nb_done = 0
        score_ggb, coeffs =  0 , 0
 
        for r in relationships :
            maxi = self.answers.filter(exercise = r.exercise, student = student)
            if maxi.count()>0 :
                maximum    = maxi.aggregate(Max('point'))
                point_max  = maximum["point__max"]
                score_ggb += point_max * r.coefficient
                coeffs    += r.coefficient
                nb_done +=1

        nb_exo_in_parcours = relationships.count()
        today = timezone.now()


        data["nb_cours"]     = self.course.filter( is_publish =1 ).count()
        data["nb_quizz"]     = self.quizz.filter( is_publish = 1 ).count()
        data["nb_exercise"]  = nb_exo_in_parcours
        data["nb_bibliotex"] = self.bibliotexs.filter( is_publish =1, students = student ).count()
        data["nb_flashpack"] = self.flashpacks.filter(Q(stop__gte=today)|Q(stop=None) ,  is_publish =1, students = student ).count()



        try :
            stage =  student.user.school.aptitude.first()
            up    = stage.up
            med   = stage.medium
            low   = stage.low
        except :
            up  = 85
            med = 65
            low = 35



        try :
            score_ggb = score_ggb / coeffs
            data["score_ggb"] = score_ggb
        except :
            score_ggb = None
            data["score_ggb"] = 0
 

        nb_exos = nb_exo_in_parcours // 2
        if nb_done > nb_exos :
            data["opacity"] = 0.95
        else :
            data["opacity"] = 0 


        if score_ggb :
            if score_ggb > up :
                data["colored"] = "darkgreen"
                data["label"] = "Expert"
                if student.user.civilite =="Mme": 
                    data["label"] = "Experte"
            elif score_ggb >  med :
                data["colored"] = "green"
                data["label"] = "Confirmé"
                if student.user.civilite =="Mme": 
                    data["label"] = "Confirmée"
            elif score_ggb > low :
                data["colored"] = "orange"
                data["label"] = "Amateur"
                if student.user.civilite =="Mme": 
                    data["label"] = "Amatrice"
            else :
                data["colored"] = "red"
                data["label"] = "Explorateur"
                if student.user.civilite =="Mme": 
                    data["label"] = "Exploratrice"
        else :
            data["boolean"] = True
            data["colored"] = "red"
            data["label"] = "Explorateur"
            if student.user.civilite =="Mme": 
                data["label"] = "Exploratrice"
 
        return data

 

    def is_pending_correction(self):
        """
        Correction en attente
        """
        submit = False
        customexercises = Customexercise.objects.filter(parcourses = self)
        for customexercise in customexercises :
            if customexercise.customexercise_custom_answer.exclude(is_corrected = 1).exists() :
                submit = True 
                break

        if not submit :
            if Writtenanswerbystudent.objects.filter(relationship__parcours  = self).exclude(is_corrected = 1).exists() : 
                submit = True 

        return submit


    def is_real_time(self):
        test = False
        if self.tracker.count() > 0 :
            test = True
        return test

 
    def nb_exercices_and_cours(self):

        data = {}
        today = timezone.now()
        if self.is_sequence :
            exercises  = self.parcours_relationship.filter(type_id=0,exercise__supportfile__is_title=0 ) 
            custom     = self.parcours_relationship.filter(type_id=1 ) 
            courses    = self.parcours_relationship.filter(type_id=2)
            bibliotex  = self.parcours_relationship.filter(type_id=5)
            quizz      = self.parcours_relationship.filter(type_id=3)
            flashpacks = self.parcours_relationship.filter( type_id=4 )

 
            nb_exercises_published = exercises.filter(is_publish = 1).count() + custom.filter(is_publish = 1).count()
            nb_cours_published     = courses.filter(is_publish = 1).count() 


            nb_exercises = exercises.count() + self.parcours_customexercises.count()
            nb_cours     = courses.count()

            nb_bibliotex_published = bibliotex.filter(is_publish = 1).count() 
            nb_quizz_published     = quizz.filter(is_publish = 1).count() 

            nb_bibliotex = bibliotex.count()  
            nb_quizz     = quizz.count()

            nb_flashpack           = flashpacks.count() 
            nb_flashpack_published = flashpacks.filter(is_publish = 1).count() 



        else :
            exercises  = self.parcours_relationship.filter( exercise__supportfile__is_title=0 ) 
            courses    = self.course.all()
            bibliotex  = self.bibliotexs.all() 
            quizz      = self.quizz.all()
            flashpacks = self.flashpacks.filter(Q(stop__gte=today)|Q(stop=None) )


            nb_exercises_published = exercises.filter(is_publish = 1).count() + self.parcours_customexercises.filter(is_publish = 1).count()
            nb_cours_published     = courses.filter(is_publish = 1).count() 

            nb_exercises = exercises.count() + self.parcours_customexercises.count()
            nb_cours     = courses.count()

            nb_bibliotex_published = bibliotex.filter(is_publish = 1).count() 
            nb_quizz_published     = quizz.filter(is_publish = 1).count() 

            nb_bibliotex = bibliotex.count() 
            nb_quizz     = quizz.count()

            nb_flashpack           = flashpacks.count() 
            nb_flashpack_published = flashpacks.filter(is_publish = 1).count() 


        nb_docs_published = nb_exercises_published + nb_cours_published + nb_quizz_published + nb_flashpack_published + nb_bibliotex_published 
        nb_docs = nb_exercises + nb_cours + nb_quizz + nb_flashpack + nb_bibliotex 


        data["nb_exercises"]            = nb_exercises
        data["nb_exercises_published"]  = nb_exercises_published
        data["exercises_care"]          = ( nb_exercises == nb_exercises_published)

        data["nb_cours"]                = nb_cours
        data["nb_cours_published"]      = nb_cours_published
        data["cours_care"]              = ( nb_cours == nb_cours_published )

        data["nb_quizz"]                = nb_quizz
        data["nb_quizz_published"]      = nb_quizz_published
        data["quizz_care"]              = ( nb_quizz == nb_quizz_published )        

        data["nb_flashpack"]            = nb_flashpack
        data["nb_flashpack_published"]  = nb_flashpack_published
        data["flashpack_care"]          = ( nb_flashpack == nb_flashpack_published)

        data["nb_bibliotex"]            = nb_bibliotex        
        data["nb_bibliotex_published"]  = nb_bibliotex_published
        data["bibliotex_care"]          = ( nb_bibliotex == nb_bibliotex_published)

        data["nb_docs"]                 = nb_docs        
        data["nb_docs_published"]       = nb_docs_published
        data["docs_care"]               = ( nb_docs == nb_docs)



        return data


 
    def is_percent_to_parcours(self,student):

        data = {}
        today = timezone.now()
        if self.is_sequence :        
            Quizz = apps.get_model('tool', 'Quizz')
            nb_exercises  = self.parcours_relationship.filter(type_id=0, students = student,is_publish = 1).count() 
            relationships = self.parcours_relationship.filter(type_id=3, students = student,is_publish = 1)
            nb_q = 0
            for relationship in relationships :
                quizz = Quizz.objects.get(pk=relationship.document_id)
                nb_q += quizz.questions.filter( students = student).values_list("id",flat=True).distinct().count() 



        else :
            nb_exercises  = self.parcours_relationship.filter( exercise__supportfile__is_title=0 , students = student,is_publish = 1).count()  
            quizzes       = self.quizz.filter( students = student)
            nb_q = 0
            for quizz in quizzes :
                nb_q += quizz.questions.filter( students = student).values_list("id",flat=True).distinct().count() 

        nb_answers   = self.answers.filter(student = student).values_list("exercise",flat=True).distinct().count() 
        nb_answers_q = student.questions_player.values_list("question",flat=True).distinct().count() 

        try :
            score = int( (nb_answers + nb_answers_q) / (nb_exercises + nb_q) * 100 )
            data["nb_total"] = score


            try :
                stage =  student.user.school.aptitude.first()
                up = stage.up
                med = stage.medium
                low = stage.low
            except :
                up = 85
                med = 65
                low = 35

            if score :
                if score > up :
                    data["colored"] = "text_darkgreen"
                elif score >  med :
                    data["colored"] = "text_green"
                elif score > low :
                    data["colored"] = "text_orange"
                else :
                    data["colored"] = "text_red"
            else :
                data["colored"] = "text_gray"

        except :
            data["nb_total"] = 0
            data["color"]    = "text_gray"

        return data


class Folder(models.Model):

    title = models.CharField(max_length=255, verbose_name="Titre")
    color = models.CharField(max_length=255, default='#00819F', verbose_name="Couleur")
    author = models.ForeignKey(Teacher, related_name="author_folders", on_delete=models.CASCADE, default='', blank=True, null=True, verbose_name="Auteur")
    teacher = models.ForeignKey(Teacher, related_name="teacher_folders", on_delete=models.CASCADE, default='', blank=True, editable=False)
    coteachers = models.ManyToManyField(Teacher, blank=True,  related_name="coteacher_folders",  verbose_name="Enseignant en co-animation")

    groups = models.ManyToManyField(Group,  blank=True, related_name="group_folders" )

    students = models.ManyToManyField(Student, blank=True, related_name='folders', editable=False)
    is_share = models.BooleanField(default=0, verbose_name="Mutualisé ?")
    is_publish = models.BooleanField(default=0, verbose_name="Publié ?")

    subject = models.ForeignKey(Subject, related_name="subject_folders", on_delete=models.CASCADE, default='', blank=True, null=True, verbose_name="Enseignement")
    level = models.ForeignKey(Level, related_name="level_folders", on_delete=models.CASCADE, default='', blank=True, null=True)

    is_favorite = models.BooleanField(default=1, verbose_name="Favori ?")
    is_archive = models.BooleanField(default=0, verbose_name="Archive ?")

    duration = models.PositiveIntegerField(default=2, blank=True, verbose_name="Temps de chargement (min.)")
    start = models.DateTimeField(null=True, blank=True, verbose_name="A partir de")
    stop = models.DateTimeField(null=True, blank=True, verbose_name="Date de verrouillage")

    vignette = models.ImageField(upload_to=vignette_directory_path, verbose_name="Vignette d'accueil", blank=True, default ="")
    ranking = models.PositiveIntegerField(  default=0,  blank=True, null=True, editable=False)

    parcours = models.ManyToManyField(Parcours ,  blank=True,  related_name="folders" )  
    
    is_trash = models.BooleanField(default=0, verbose_name="Poubelle ?", editable=False)

    old_id = models.PositiveIntegerField(  default=0,  blank=True, null=True, editable=False)


    def __str__(self):
        return "{}>{}".format( self.groups.last().name ,self.title)

 

    def isnot_shared(self) :
        test = False
        if self.groups.exclude(teacher_id=2480).count()>1:
            test = True
        return test

 

    def is_affect(self, student):
        nb_relationships = Relationship.objects.filter(parcours=self, exercise__supportfile__is_title=0,
                                                       students=student, is_publish=1).count()
        return nb_relationships


    def is_lock(self,today):
        lock = False
        try :
            if self.stop < today :
                lock = True 
        except :
            pass
        return lock



    def group_and_folder_only_students(self,group):

        data = {}
        group_students = group.students.all()
        #print(group, group_students)
        o_students = self.students.exclude(user__username__contains="_e-test")
        #print(self , o_students)
        only_students = [s for s in o_students if s in group_students]
        data["only_students"]= only_students
        data["nb"]= len(only_students)
        return data 

    def is_coanimation(self) :
        is_co = False 
        if self.coteachers.count() > 0 :
            is_co = True 

        for parcours in self.parcours.all() :
            if parcours.coteachers.count()>0 :
                is_co = True
                break
        return is_co

    def folder_only_students_count(self):

        data = {}
        only_students = self.students.exclude(user__username__contains="_e-test")

        data["only_students"]= only_students
        data["nb"]= only_students.count()
        return data 

  
    def only_students_folder(self):

 
        only_students = self.students.exclude(user__username__contains="_e-test").order_by("user__last_name")
 
        return only_students    
 


    def min_score(self,student):
        """
        min score d'un parcours par élève
        """
        data = {}
        max_tab = []
        nb_done = 0
        exercises = set()

        exs = set()
        nb_exo_in_parcours , nb_cours , nb_quizz = 0 , 0 , 0
        parcours_set = set()
        for p in self.parcours.filter(is_publish=1, students=student):
            exos = p.exercises.filter(supportfile__is_title=0, supportfile__is_ggbfile=1 )
            nb_cours += p.course.values_list("id").filter( is_publish=1 ).distinct().count()
            nb_quizz += p.quizz.values_list("id").filter( is_publish=1 ).distinct().count()

            if exos.count() > 0 : 
                exercises.update(exos)

            nb_exo_in_parcours +=  p.parcours_relationship.filter(is_publish=1,students=student ).count()
    
            for exercise in exercises :
                maxi = p.answers.filter(student=student, exercise = exercise )
                if maxi.count()>0 :
                    maximum = maxi.aggregate(Max('point'))
                    max_tab.append(maximum["point__max"])
                    nb_done +=1

        data["nb_parcours"]    = self.parcours.filter(is_evaluation = 0, is_publish=1, students=student).count()
        data["nb_evaluations"] = self.parcours.filter(is_evaluation = 1, is_publish=1, students=student).count()

        data["nb_cours"] = nb_cours
        data["nb_quizz"] = nb_quizz

        data["nb_flashpack"] = self.flashpacks.filter(is_publish=1, students=student).count()
        data["nb_bibliotex"] = self.bibliotexs.filter(is_publish=1, students=student).count()



        try :
            stage =  student.user.school.aptitude.first()
            up = stage.up
            med = stage.medium
            low = stage.low
        except :
            up = 85
            med = 65
            low = 35

        ### Si l'elève a fait tous les exercices du parcours
        suff = ""
        if student.user.civilite =="Mme":
            suff = "e"

        data["colored"] = "red"
        data["label"] = ""

        if nb_done == nb_exo_in_parcours :
            data["size"] = "40px"
          
            max_tab.sort()
            try :
                score = max_tab[0]
            except :
                score = None

            data["boolean"] = True

            if score :
                if score > up :
                    data["colored"] = "darkgreen"
                elif score >  med :
                    data["colored"] = "green"
                elif score > low :
                    data["colored"] = "orange"
                else :
                    data["colored"] = "red"
            else :
                data["colored"] = "red"



        ### Si l'elève a fait plus de la moitié des exercices du parcours
        elif nb_done > nb_exo_in_parcours // 2 :
            data["size"] = "20px"

            max_tab.sort()

            if len(max_tab)>0 :
                score = max_tab[0]
            else :
                score = None

            data["boolean"] = True
            if score :
                if score > up :
                    data["colored"] = "darkgreen"
                    data["label"] = "Expert"+suff
                elif score >  med :
                    data["colored"] = "green"
                    data["label"] = "Confirmé"+suff
                elif score > low :
                    data["colored"] = "orange"
                    data["label"] = "Amateur"
                    if student.user.civilite =="Mme": 
                        data["label"] = "Amatrice"
                else :
                    data["colored"] = "red"
                    data["label"] = "Débutant"+suff
            else :
                data["boolean"] = True
                data["colored"] = "red"
                data["label"] = "Débutant"+suff
        else :
            data["boolean"] = False
  
        return data



    def nb_parcours_is_publish(self):
        return self.parcours.filter(is_evaluation=0, is_publish=1, is_trash=0).count()


    def parcours_is_not_archived(self):
        return self.parcours.filter(is_archive=0) 

    def parcours_is_archived(self):
        return self.parcours.filter(is_archive=1)  


    def data_parcours_evaluations(self):
        data = {}

        data["parcours_exists"] = False
        data["evaluations_exists"] = False
        data["is_students"] = False
        data["is_folder_courses_exists"] = False
        data["is_folder_task_exists"] = False


        parcours        = self.parcours.filter(is_evaluation=0, is_trash=0) 
        evaluations     = self.parcours.filter(is_evaluation=1, is_trash=0)
        nb_parcours     = parcours.count()
        nb_evaluations  = evaluations.count()

        data["parcours"]       = parcours 
        data["evaluations"]    = evaluations
        data["nb_parcours"]    = nb_parcours
        data["nb_evaluations"] = nb_evaluations


        if nb_parcours      :
            data["is_parcours_exists"]    = True
        if nb_evaluations   :
            data["is_evaluations_exists"] = True
        if self.students.exclude(user__username__contains= "_e-test") :
            data["is_students"]        = True 
 
        test = False
        for p in self.parcours.all() :
            if p.course.count() > 0 :
                test = True
                break
        data["is_folder_courses_exists"] = test


        today = timezone.now()
        tested = False
        if Relationship.objects.filter(parcours__in= self.parcours.filter(is_publish=1),date_limit__gte = today).count() > 0 :
            tested = True
        for p in self.parcours.filter(is_publish=1):
            if Customexercise.objects.filter(parcourses= p ,date_limit__gte = today).count() > 0 :
                tested = True
                break

        data["is_folder_task_exists"] = tested

        return data

 
    def is_pending_folder_correction(self):
        """
        Correction en attente deuis un folder de parcours
        """
        submit = False
        for p in self.parcours.filter(is_publish=1) :
            customexercises = Customexercise.objects.filter(parcourses  = p )
            for customexercise in customexercises :
                if customexercise.customexercise_custom_answer.exclude(is_corrected = 1).exists() :
                    submit = True 
                    break
 
        if not submit :
            if Writtenanswerbystudent.objects.filter(relationship__parcours__in = self.parcours.all(), is_corrected = 0).exists() : 
                submit = True 

        return submit


    def data_parcours_evaluations_from_group(self,group):

        data = {}

        data["parcours_exists"]          = False
        data["evaluations_exists"]       = False
        data["is_students"]              = False
        data["is_folder_courses_exists"] = False
        data["is_folder_task_exists"]    = False
        data["is_quizz_exists"]          = False
        data["is_bibliotex_exists"]      = False
        data["is_course_exists"]         = False
        data["is_flashpack_exists"]      = False


        group_students  = group.students.exclude(user__username__contains= "_e-test")
        folder_students = self.students.exclude(user__username__contains= "_e-test")
        all_students    = [s for s in folder_students if s in  group_students]


        parcours        = self.parcours.filter(is_evaluation=0, is_trash=0) 
        evaluations     = self.parcours.filter(is_evaluation=1, is_trash=0)

        nb_parcours_published    = parcours.filter(is_publish = 1).count() 
        nb_evaluations_published = evaluations.filter(is_publish = 1).count() 

        nb_parcours     = parcours.count()
        nb_evaluations  = evaluations.count()

        quizzes     = self.quizz.all()  
        bibliotexs  = self.bibliotexs.all()
        flashpacks  = self.flashpacks.all()

        nb_quizz     = quizzes.count() 
        nb_bibliotex = bibliotexs.count()
        nb_flashpack = flashpacks.count() 


        for p in parcours :
            if p.course.count():
                data["is_course_exists"] = True
                break


        data["parcours"]       = parcours 
        data["evaluations"]    = evaluations
        data["nb_parcours"]    = nb_parcours
        data["nb_evaluations"] = nb_evaluations
        data["nb_parcours_published"]    = nb_parcours_published
        data["nb_evaluations_published"] = nb_evaluations_published


        data["quizzes"]      = quizzes 
        data["bibliotexs"]   = bibliotexs
        data["flashpacks"]   = flashpacks
        data["nb_quizzes"]   = nb_quizz
        data["nb_bibliotex"] = nb_bibliotex
        data["nb_flashpack"] = nb_flashpack



        if nb_parcours      :
            data["is_parcours_exists"]    = True
        if nb_evaluations   :
            data["is_evaluations_exists"] = True
        if len(all_students) > 0:
            data["is_students"]           = True 


        if nb_quizz      :
            data["is_quizz_exists"]     = True
        if nb_bibliotex   :
            data["is_bibliotex_exists"] = True
        if nb_flashpack   :
            data["is_flashpack_exists"] = True

        to_validate = False
        flashpacks_to_validate = self.flashpacks.filter(is_creative = 1)
        nb_flashcards_to_validate = 0
        for ftv in flashpacks_to_validate:
            nb_flashcards_to_validate += ftv.flashcards.filter(is_validate=0).count()
            if nb_flashcards_to_validate > 0 :
                to_validate = True
                break
 
        data["flashpack_to_validate"] = to_validate
 
        test = False
        for p in self.parcours.all() :
            if p.course.count() > 0 :
                test = True
                break
        data["is_folder_courses_exists"] = test


        data["parcours_care"]    = ( nb_parcours == nb_parcours_published)
        data["evaluations_care"] =  ( nb_evaluations == nb_evaluations_published )



        today = timezone.now()
        tested = False
        if Relationship.objects.filter(parcours__in= self.parcours.filter(is_publish=1),date_limit__gte = today).count() > 0 :
            tested = True
        for p in self.parcours.filter(is_publish=1):
            if Customexercise.objects.filter(parcourses= p ,date_limit__gte = today).count() > 0 :
                tested = True
                break

        data["is_folder_task_exists"] = tested

        return data
 

class Relationship(models.Model):
    exercise = models.ForeignKey(Exercise,  null=True, blank=True,   related_name='exercise_relationship', on_delete=models.CASCADE,  editable= False)
    parcours = models.ForeignKey(Parcours, on_delete=models.CASCADE,  related_name='parcours_relationship',  editable= False)
    ranking = models.PositiveIntegerField(default=0, editable=False)
    is_publish = models.BooleanField(default=1)
    start = models.DateTimeField(null=True, blank=True, verbose_name="A partir de")
    date_limit = models.DateTimeField(null=True, blank=True, verbose_name="Date limite du rendu")
    is_evaluation = models.BooleanField(default=0)
    duration = models.PositiveIntegerField(default=15, verbose_name="Durée estimée en minutes")
    situation = models.PositiveIntegerField(default=10, verbose_name="Nombre minimal de situations", help_text="Pour valider le qcm")
    beginner = models.TimeField(null=True, blank=True, verbose_name="Heure du début")
    skills = models.ManyToManyField(Skill, blank=True, related_name='skills_relationship', editable=False)
    students = models.ManyToManyField(Student, blank=True, related_name='students_relationship', editable=False)
    instruction = models.TextField(blank=True,  null=True,  editable=False)

    maxexo = models.IntegerField(  default=-1,  blank=True, null=True,  verbose_name="Nombre max de réalisation par exercice")

    is_lock = models.BooleanField(default=0, verbose_name="Exercice cloturé ?")
    is_mark = models.BooleanField(default=0, verbose_name="Notation ?")
    mark = models.CharField(max_length=3, default="", verbose_name="Sur ?")
    is_correction_visible = models.BooleanField(default=0, editable=False  )
    
    coefficient = models.DecimalField(default=1,  max_digits=4, decimal_places=2, verbose_name="Coefficient")

    # document : type du doc et id du doc ( exercice = 0 , custom = 1 , cours = 2 , quizz= 3 , biblio = 4 , flash = 5)
    document_id = models.IntegerField(  default=0,  blank=True, null=True, editable=False)    
    type_id = models.IntegerField(  default=0,  blank=True, null=True, editable=False)

    is_in_average = models.BooleanField(default=0,  blank=True, editable=False)
    
    def __str__(self):

        try :
            return "{} : {}".format(self.parcours, cleanhtml(unescape_html(self.exercise.supportfile.annoncement)))
        except :
            return "{}".format(self.parcours)  

    class Meta:
        unique_together = ('exercise', 'parcours')





    def type_of_document(self):
        Quizz = apps.get_model('tool', 'Quizz')
        Flashpack = apps.get_model('flashcard', 'Flashpack')
        Bibliotex = apps.get_model('bibliotex', 'Bibliotex')
        if self.type_id == 0 :
            document = Exercise.objects.get(pk=self.exercise.id)
        if self.type_id == 1 :
            document = Customexercise.objects.get(pk=self.document_id)
        elif self.type_id == 2 :
            document = Course.objects.get(pk=self.document_id)     
        elif self.type_id == 3 :
            document = Quizz.objects.get(pk=self.document_id)
        elif self.type_id == 4 :
            document = Flashpack.objects.get(pk=self.document_id)
        elif self.type_id == 5 :
            document = Bibliotex.objects.get(pk=self.document_id)
        return document


    def is_mastering(self):
        test = False
        if self.relationship_mastering.count() :
            test = True
        return test




    def score_student_for_this(self,student):
        studentanswer = Studentanswer.objects.filter(student=student, parcours= self.parcours , exercise = self.exercise ).last()
        return studentanswer

    def is_done(self,student):
        done = False
        sta = Studentanswer.objects.filter(student=student, exercise = self.exercise, parcours= self.parcours ).exists()
        stw = self.relationship_written_answer.filter(student=student).exists()
        if sta or stw :
            done = True
        return done

    def is_task(self):
        task = False
        today = timezone.now() 
        try :
            if self.date_limit >= today:
                task = True
        except :
            task = False
        return task


    def score_and_time(self, student):
        scores_times_tab = []
        if student.answers.filter(exercise=self.exercise,parcours=self.parcours ).exists():
            studentanswers = student.answers.filter(exercise=self.exercise,parcours=self.parcours)
            for studentanswer in studentanswers:
                scores_times = {}
                scores_times["score"] = studentanswer.point
                scores_times["time"] = convert_time(studentanswer.secondes)
                scores_times["numexo"] = studentanswer.numexo
                scores_times["date"] = studentanswer.date
                scores_times_tab.append(scores_times)
        return scores_times_tab



    def constraint_to_this_relationship(self,student): # Contrainte. 

        data = {}
        under_score = True # On suppose que l'élève n'a pas obtenu le score minimum dans les exercices puisqu'il ne les a pas fait. 
        constraints = self.relationship_constraint.all()
        block = []
        for constraint in constraints : # On étudie si les contraignants ont un score supérieur à score Min
            if not student.answers.filter(exercise__supportfile__code = constraint.code, parcours= self.parcours  ).exists() or student.answers.filter(exercise__supportfile__code = constraint.code, parcours= self.parcours, point__lt= constraint.scoremin ).exists():
                block.append(constraint)
        if len(block) == 0: # Si l'élève a obtenu les minima à chaque exercice
            under_score = False # under_score devient False
        data["under_score"]     = under_score
        data["constraint_list"] = block[:5]
        return data  

    def is_header_of_section(self): # Contrainte. 
    
        header = False # On suppose que l'élève n'a pas obtenu le score minimum dans les exercices puisqu'il ne les a pas fait. 
        courses = Course.objects.filter(relationships = self).order_by("ranking") 
        data = {}
        if courses.count() > 0 : 
            header = True  
        
        data["header"] = header

        return header 




    def percent_student_done_parcours_exercice_group(self,parcours,group):

        students          = self.students.filter( students_to_group = group).exclude(user__username__contains="_e-test")
        nb_student        = len(students)

        if self.exercise.supportfile.is_ggbfile :
            nb_exercise_done = Studentanswer.objects.filter(student__in= students, parcours= parcours, exercise = self.exercise).values_list("student",flat= True).order_by("student").distinct().count()
        else :
            nb_exercise_done = Writtenanswerbystudent.objects.filter(relationship= self, student__in= students ).values_list("student",flat= True).order_by("student").distinct().count()        
 
        try :
            percent = int(nb_exercise_done * 100/nb_student)
        except : 
            percent = 0
        data = {}
        data["nb"] = nb_student
        data["percent"] = percent
        data["nb_done"] = nb_exercise_done
        return data


    def is_submit(self,student):
        submit = False
        if self.relationship_written_answer.filter(student = student).exclude(is_corrected = 1).exists() :
            submit = True          
        return submit

    def noggb_data(self,student):
        try :
            data =  self.relationship_written_answer.get(student = student)   
        except :
            data = {'is_corrected' : False , 'skills' : [] , 'comment' : "" , }     
        return data

    def is_pending_correction(self):
        submit = False
        if self.relationship_written_answer.exclude(is_corrected = 1).exists() :
            submit = True          
        return submit

    def code_student_for_this(self,student):
        Stage = apps.get_model('school', 'Stage')
        studentanswer = Studentanswer.objects.filter(student=student, parcours= self.parcours , exercise = self.exercise ).last()
        try :
            point = studentanswer.point
        except :
            point = -1
 
        if student.user.school :

            try :
                school = student.user.school
                stage = Stage.objects.get(school = school)
                if point > stage.up :
                    level = 4
                elif point > stage.medium :
                    level = 3
                elif point > stage.low :
                    level = 2
                elif point > -1 :
                    level = 1
                else :
                    level = 0
            except :
                stage = { "low" : 50 ,  "medium" : 70 ,  "up" : 85  }
                if point > stage["up"] :
                    level = 4
                elif point > stage["medium"] :
                    level = 3
                elif point > stage["low"] :
                    level = 2
                elif point > -1 :
                    level = 1
                else :
                    level = 0
        else : 
            stage = { "low" : 50 ,  "medium" : 70 ,  "up" : 85  }
 
            if point > stage["up"] :
                level = 4
            elif point > stage["medium"] :
                level = 3
            elif point > stage["low"] :
                level = 2
            elif point > -1 :
                level = 1
            else :
                level = 0

        return level

    def result_skill(self,skill,student):
        Stage = apps.get_model('school', 'Stage')
        try :
            studentanswer = Resultggbskill.objects.get(student=student, relationship= self,skill = skill )
            point = studentanswer.point
            if student.user.school :
                try :
                    school = student.user.school
                    stage = Stage.objects.get(school = school)
                    if point > stage.up :
                        level = 4
                    elif point > stage.medium :
                        level = 3
                    elif point > stage.low :
                        level = 2
                    elif point > -1 :
                        level = 1
                    else :
                        level = 0
                except :
                    stage = { "low" : 50 ,  "medium" : 70 ,  "up" : 85  }
                    if point > stage["up"] :
                        level = 4
                    elif point > stage["medium"] :
                        level = 3
                    elif point > stage["low"] :
                        level = 2
                    elif point > -1 :
                        level = 1
                    else :
                        level = 0
            else : 
                stage = { "low" : 50 ,  "medium" : 70 ,  "up" : 85  }
 
                if point > stage["up"] :
                    level = 4
                elif point > stage["medium"] :
                    level = 3
                elif point > stage["low"] :
                    level = 2
                elif point > -1 :
                    level = 1
                else :
                    level = 0
        except :
            level = 0
        return level

    def mark_to_this(self,student,parcours_id): # parcours_id n'est pas utilisé mais on le garde pour utiliser la fontion exostante dans item_tags
        data = {}
 
        if Writtenanswerbystudent.objects.filter(relationship = self,  student = student,is_corrected=1).exists() :
            wa = Writtenanswerbystudent.objects.get(relationship = self,   student = student,is_corrected=1)
            data["is_marked"] = True
            data["marked"] = wa.point
        else :
            data["is_marked"] = False
            data["marked"] = ""            

        return data


    def is_available(self,student) :
        data = {}
        is_ok = True
        nbs = Studentanswer.objects.filter(parcours=self.parcours , exercise= self.exercise,student = student ).count()
        
        try : 
            nbleft = self.maxexo - nbs
        except :
            nbleft = self.maxexo 

        if nbleft == 0  :
            is_ok = False
        if self.maxexo == -1   :
            is_ok = True
          
        data["is_ok"] = is_ok
        data["nbleft"] = nbleft

        return data


    def is_locker(self,student) :  
        test = False 
        if self.relationship_exerciselocker.filter(student= student).count()>0:
            test = True
        return test



    def just_students(self) :  
        return self.students.exclude(user__username__contains= "_e-test").order_by("user__last_name")


    def group_and_rc_only_students(self,group):

        data = {}
        try :
            group_students = group.students.all()
            o_students = self.students.exclude(user__username__contains="_e-test")
            only_students = [s for s in o_students if s in group_students]
            data["only_students"]= only_students
            data["nb"]= len(only_students)
        except :
            pass

        return data 

    def all_results_custom(self,student,parcours): # résultats vue élève
        data = {}

        if self.relationship_written_answer.filter(student = student) :
            c_image =  self.relationship_written_answer.filter(student = student).last()
            canvas_img = c_image.imagefile
        else :
            canvas_img = None
        data["canvas_img"] = canvas_img   

        if self.relationship_written_answer.filter(student = student,is_corrected=1).exists() :
            c = self.relationship_written_answer.filter(student = student,   is_corrected=1).last()
            data["is_corrected"] = True            
            data["comment"] = c.comment
            data["audio"] =  c.audio
            data["point"] = c.point
            c_skills = student.results_s.last()
            c_knowledges = student.results_k.last()
            data["skills"] = c_skills
            data["knowledges"] = c_knowledges
        else :
            data["is_corrected"] = False
            data["comment"] = False           
            data["skills"] = []
            data["knowledges"] = []
            data["point"] = False
            data["audio"] = False
        return data


    def is_consigne_remediation():
        return self.relationship_remediation.filter(consigne = 1)

    def is_not_consigne_remediation():
        return self.relationship_remediation.filter(consigne = 0)


class Studentanswer(models.Model):

    parcours = models.ForeignKey(Parcours,  on_delete=models.CASCADE, blank=True, null=True,  related_name='answers', editable=False)
    exercise = models.ForeignKey(Exercise,  on_delete=models.CASCADE, blank=True,  related_name='ggbfile_studentanswer', editable=False) 
    student = models.ForeignKey(Student,  on_delete=models.CASCADE, blank=True,  related_name='answers', editable=False)
    point  = models.PositiveIntegerField(default=0 )  
    numexo  = models.PositiveIntegerField(default=10 )  
    date = models.DateTimeField(default=timezone.now)
    secondes = models.CharField(max_length=255, editable=False)
    is_reading = models.BooleanField( default=0, editable=False ) 

    def __str__(self):        
        return "{}".format(self.exercise.knowledge.name)


class Resultggbskill(models.Model): # Pour récupérer tous les scores des compétences d'une relationship
    student = models.ForeignKey(Student, related_name="student_resultggbskills", default="", on_delete=models.CASCADE, editable=False)
    skill = models.ForeignKey(Skill, related_name="skill_resultggbskills", on_delete=models.CASCADE, editable=False)
    point = models.PositiveIntegerField(default=0)
    relationship = models.ForeignKey(Relationship,  on_delete=models.CASCADE, blank=True, null=True,  related_name='relationship_resultggbskills', editable=False)

    def __str__(self):
        return f"{self.skill} : {self.point}"


class Resultexercise(models.Model):  # Last result

    student = models.ForeignKey(Student, related_name="results_e", default="",
                                on_delete=models.CASCADE, editable=False)
    exercise = models.ForeignKey(Exercise, related_name="results_e",
                                 on_delete=models.CASCADE, editable=False)
    point = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "{}".format(self.point)

    class Meta:
        unique_together = ['student', 'exercise']


class Writtenanswerbystudent(models.Model): # Commentaire pour les exercices non autocorrigé coté enseignant

    relationship = models.ForeignKey(Relationship,  on_delete=models.CASCADE,   related_name='relationship_written_answer', editable=False)
    student = models.ForeignKey(Student,  on_delete=models.CASCADE, blank=True,  related_name='student_written_answer', editable=False)
    date = models.DateTimeField(auto_now_add=True)
    # rendus
    imagefile = models.ImageField(upload_to= file_directory_student, blank = True, null=True,   verbose_name="Scan ou image ou Photo", default="")
    answer = RichTextUploadingField( default="", null=True,  blank=True, ) 
    comment = models.TextField( default="", null=True,   editable=False) # Commentaire de l'enseignant sur l'exercice
    audio = models.FileField(upload_to=file_directory_path,verbose_name="Commentaire audio", blank=True, null= True, default ="")
    point = models.CharField(default="", max_length=10, verbose_name="Note")
    is_corrected = models.BooleanField( default=0, editable=False ) 

    def __str__(self):        
        return "{}".format(self.relationship.exercise.knowledge.name)

########################################################################################################################################### 
########################################################################################################################################### 
############################################################ Exercice customisé ###########################################################
########################################################################################################################################### 
########################################################################################################################################### 
class Etype(models.Model):
    """
    Modèle représentant un associé.
    """
    title     = models.TextField(max_length=255, default='',  blank=True, verbose_name="Type")
    imagefile = models.ImageField(upload_to=etype_directory_path, blank=True, default="", verbose_name="Image")
    html      = models.TextField( default='',  blank=True, verbose_name="Html éventuel")
    url       = models.CharField(max_length=255,  blank=True, default='', verbose_name="url") 
    is_online = models.BooleanField(default=0, verbose_name="En ligne ?")
    template  = models.CharField(max_length=255,  blank=True, default='', verbose_name="template") 
    ranking   = models.PositiveIntegerField(default=0,   ) 

    def __str__(self):
        return self.title

class Customexercise(ModelWithCode):

    instruction  = RichTextUploadingField( verbose_name="Consigne*") 
    teacher      = models.ForeignKey(Teacher, related_name="teacher_customexercises", blank=True, on_delete=models.CASCADE)
    calculator   = models.BooleanField(default=0, verbose_name="Calculatrice ?")
 
    date_created  = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modified = models.DateTimeField(auto_now=True, verbose_name="Date de modification")
    #### pour donner une date de remise - Tache     
    start = models.DateTimeField(null=True, blank=True, verbose_name="A partir de")
    date_limit = models.DateTimeField(null=True, blank=True, verbose_name="Date limite du rendu")
    lock = models.DateTimeField(null=True, blank=True, verbose_name="Verrouillé dès le")

    imagefile = models.ImageField(upload_to=vignette_directory_path, blank=True, verbose_name="Vignette d'accueil", default="")

    duration = models.PositiveIntegerField(default=15, blank=True, verbose_name="Durée (min.)")
    
    skills = models.ManyToManyField(Skill, blank=True, related_name='skill_customexercises', verbose_name="Compétences évaluées")
    knowledges = models.ManyToManyField(Knowledge, blank=True, related_name='knowledge_customexercises', verbose_name="Savoir faire évalués")
    parcourses = models.ManyToManyField(Parcours, blank=True, related_name='parcours_customexercises', verbose_name="Parcours attachés")
    students = models.ManyToManyField(Student, blank=True, related_name='students_customexercises' )   
    
    is_share = models.BooleanField(default=0, verbose_name="Mutualisé ?")
    is_realtime = models.BooleanField(default=0, verbose_name="Temps réel ?")

    is_python = models.BooleanField(default=0, verbose_name="Python ?")
    is_scratch = models.BooleanField(default=0, verbose_name="Scratch ?")
    is_file = models.BooleanField(default=0, verbose_name="Fichier ?")
    is_image = models.BooleanField(default=0, verbose_name="Image/Scan ?")
    is_text = models.BooleanField(default=0, verbose_name="Texte ?")
    is_mark = models.BooleanField(default=0, verbose_name="Notation ?")
    is_collaborative = models.BooleanField(default=0, verbose_name="Collaboratif ?")

    is_autocorrection = models.BooleanField(default=0, verbose_name="Autocorrection ?")
    criterions = models.ManyToManyField(Criterion, blank=True, related_name='customexercises' )    

    mark = models.PositiveIntegerField(default=0, verbose_name="Sur ?")
    is_publish = models.BooleanField(default=0, verbose_name="Publié ?")
    ranking = models.PositiveIntegerField(  default=0,  blank=True, null=True, editable=False)

    text_cor = RichTextUploadingField(  blank=True, null=True,  verbose_name="Correction écrite") 
    file_cor = models.ImageField(upload_to=vignette_directory_path, blank=True, verbose_name="Fichier de correction", default="")
    video_cor = models.CharField(max_length = 100, blank=True, verbose_name="Code de la vidéo Youtube", default="")
    is_publish_cor = models.BooleanField(default=0, verbose_name="Publié ?")    


    etype     = models.ForeignKey(Etype, related_name="customexercises", null=True, blank=True, on_delete=models.CASCADE)
    filltheblanks = RichTextUploadingField( default='',  blank=True, verbose_name="Texte à trous") 
    ####  Cas spécifique axe gradué qtype =18
    xmin       = models.FloatField( null = True,   blank=True, verbose_name="x min ")
    xmax       = models.FloatField( null = True,   blank=True, verbose_name="x max ")
    tick       = models.FloatField( null = True,   blank=True, verbose_name="Graduation")
    precision  = models.FloatField( null = True,   blank=True, verbose_name="Précision") 
    ####  Pseudo aléatoire
    pseudoalea_nb = models.PositiveIntegerField(default=0, blank=True, )



    def __str__(self):       
        return "{}".format(self.instruction)
 

    def subjects(self):
        subjects = []
        for k in self.knowledges.all() :
            if k.theme.subject  not in subjects :
                subjects.append(k.theme.subject)

        for s in self.skills.all() :
            if s.subject not in subjects :
                subjects.append(s.subject)

        if len(subjects) == 0 :
            for sb in self.teacher.subjects.all() :
                if sb  not in subjects :
                    subjects.append(sb)       
        return subjects

    def levels(self):
        levels = []
        for k in self.knowledges.all() :
            if k.level  not in levels :
                levels.append(k.level)

 
        if len(levels) == 0 :
            for sb in self.teacher.levels.all() :
                if sb  not in levels :
                    levels.append(sb)       
        return levels

    def percent_student_done_parcours_exercice_group(self, parcours,group):

        students = self.students.filter( students_to_group = group).exclude(user__username__contains="_e-test")
        nb_student = students.count()
        nb_exercise_done = Customanswerbystudent.objects.filter(student__in= students, customexercise__parcourses = parcours, customexercise = self).values_list("student",flat= True).order_by("student").distinct().count()
        
        try :
            percent = int(nb_exercise_done * 100/nb_student)
        except : 
            percent = 0
        data = {}
        data["nb"] = nb_student
        data["percent"] = percent
        data["nb_done"] = nb_exercise_done
        return data

    def type_of_document(self):
        return 1

    def is_done(self,student):
        done = False
        if student.student_custom_answer.filter( customexercise = self).exists():
            done = True
        elif student.user.tracker.filter(exercise_id = self.pk).exists():
            done = True
        return done


    def score_student_for_this(self,student):

        correction = Customanswerbystudent.objects.filter(student=student, customexercise = self ).exclude(is_corrected=1)

        if correction.exists() :
            cor = correction.last()
            try :
                score = int(cor.point)
            except:
                score = "C"
        else :
            score = False

        return score

    def is_corrected_for_this(self,student,parcours): # devoir corrigé
        correction = Customanswerbystudent.objects.filter(student=student, customexercise = self, parcours =parcours,is_corrected=1)
        is_corrected = False
        data = {}
        if correction.exists() :
            correction = Customanswerbystudent.objects.get(student=student, customexercise = self, parcours =parcours,is_corrected=1)
            answer = correction.answer
            is_corrected = True
        else :
            answer=None
        data["answer"] = answer
        data["is_corrected"] = is_corrected
        return data

    def is_lock(self,today):
        locker = False
        try :
            if self.lock < today :
                locker = True
        except :
            pass
        return locker


    def is_submit(self,parcours,student):
        submit = False
        if Customanswerbystudent.objects.filter(customexercise = self, parcours = parcours, student = student).exclude(is_corrected=1).exists() :
            submit = True          
        return submit

    def result_k_s(self,k_s, student, parcours_id,typ):
 
        if typ == 1 :
            if Correctionskillcustomexercise.objects.filter(customexercise = self, parcours_id = parcours_id, student = student, skill = k_s).exists() :
                c = Correctionskillcustomexercise.objects.get(customexercise = self, parcours_id = parcours_id, student = student, skill = k_s)    
                point = int(c.point)
            else :
                point = -1  
        else :
            if Correctionknowledgecustomexercise.objects.filter(customexercise = self, parcours_id = parcours_id, student = student, knowledge = k_s).exists() :
                c = Correctionknowledgecustomexercise.objects.get(customexercise = self, parcours_id = parcours_id, student = student, knowledge = k_s)    
                point = int(c.point)   
            else :
                point = -1  
 
        if student.user.school :

            school = student.user.school
            try :
                stage  = school.aptitude.first()
                stage = { "low" : stage.low ,  "medium" : stage.medium   ,  "up" : stage.up  }
            except :
                stage = { "low" : 50 ,  "medium" : 70 ,  "up" : 85  }

 
        else : 
            stage = { "low" : 50 ,  "medium" : 70 ,  "up" : 85  }
 
        if point > stage["up"]  :
            level = 4
        elif point > stage["medium"]  :
            level = 3
        elif point > stage["low"]  :
            level = 2
        elif point > -1 :
            level = 1
        else :
            level = 0
        return level

    def mark_to_this(self,student,parcours_id):
        data = {}
        if Customanswerbystudent.objects.filter(customexercise = self, parcours_id = parcours_id, student = student,is_corrected=1).exists() :
            c = Customanswerbystudent.objects.get(customexercise = self, parcours_id = parcours_id, student = student,is_corrected=1)
            data["is_marked"] = True
            data["marked"] = c.point
        else :
            data["is_marked"] = False
            data["marked"] = ""            

        return data

    def all_results_custom(self,student,parcours): # résultats vue élève
        data = {}
        if Customanswerimage.objects.filter(customanswerbystudent__customexercise = self, customanswerbystudent__parcours = parcours, customanswerbystudent__student = student) :
            c_image = Customanswerimage.objects.filter(customanswerbystudent__customexercise = self, customanswerbystudent__parcours = parcours, customanswerbystudent__student = student).last()
            canvas_img = c_image.imagecanvas
        else :
            canvas_img = None
        data["canvas_img"] = canvas_img  

        data["positionnement"] = False
        if Customanswerbystudent.objects.filter(customexercise = self, parcours = parcours, student = student,is_corrected=1).exists() :
            c = Customanswerbystudent.objects.get(customexercise = self, parcours = parcours, student = student,is_corrected=1)
            data["is_corrected"] = True            
            data["comment"] = c.comment
            data["audio"] =  c.audio
            data["point"] = c.point
            c_skills = Correctionskillcustomexercise.objects.filter(customexercise = self, parcours = parcours, student = student)
            c_knowledges = Correctionknowledgecustomexercise.objects.filter(customexercise = self, parcours = parcours, student = student)
            data["skills"] = c_skills
            data["knowledges"] = c_knowledges
        else :
            data["is_corrected"] = False
            data["comment"] = False           
            data["skills"] = []
            data["knowledges"] = []
            data["point"] = False
            data["audio"] = False
 
        if self.is_autocorrection and Customanswerbystudent.objects.filter(customexercise = self, parcours = parcours, student = student ).exists():
                data["positionnement"] = True
        return data


    def is_pending_correction(self):
        submit = False
        if self.customexercise_custom_answer.exclude(is_corrected = 1).exists() :
            submit = True      
        return submit

    def nb_task_parcours_done(self, parcours):
        studentanswer_tab = []
        for s in parcours.students.all():
            studentanswer = Studentanswer.objects.filter(exercise=self, student=s).first()
            if studentanswer:
                studentanswer_tab.append(studentanswer)
        nb_task_done = len(studentanswer_tab)
        return nb_task_done

    def nb_task_done(self, group):
        """
        group ou parcours car on s'en sert pour récupérer les élèves
        """
        try:
            custom_tab = []
            for s in group.students.all():
                custom_answer = Customanswerbystudent.objects.filter(customexercise=self, student=s).first()
                if custom_answer:
                    custom_tab.append(custom_answer)
            nb_task_done = len(custom_tab)
        except:
            nb_task_done = 0

        data = {}
        data["nb_task_done"] = nb_task_done
        data["custom_tab"] = custom_tab
        return data

    def is_locker(self,student) :  
        test = False 
        if self.customexercise_exerciselocker.filter(student = student).count()>0:
            test = True
        return test


    def just_students(self) :  
        return self.students.exclude(user__username__contains= "_e-test").order_by("user__last_name")


    def group_and_rc_only_students(self,group):

        data = {}
        group_students = group.students.all()
        o_students = self.students.exclude(user__username__contains="_e-test")
        only_students = [s for s in o_students if s in group_students]
        data["only_students"]= only_students
        data["nb"]= len(only_students)
        return data 


    def is_mastering(self):
        test = False
        if self.customexercise_mastering_custom.count() :
            test = True
        return test

######################################################################
#####  type de réponse possible et choix pour les types d'exercices
######################################################################
class Choice(models.Model):
    """
    Modèle représentant un associé.
    """

    imageanswer    = models.ImageField(upload_to=choice_directory_path,  null=True,  blank=True, verbose_name="Image", default="")
    answer         = models.TextField(max_length=255, default='', null=True,  blank=True, verbose_name="Réponse écrite")
    retroaction    = models.TextField(max_length=255, default='', null=True,  blank=True, verbose_name="Rétroaction")
    imageanswerbis = models.ImageField(upload_to=choice_directory_path,  null=True,  blank=True, verbose_name="Image par paire", default="")
    answerbis      = models.TextField(max_length=255, default='', null=True,  blank=True, verbose_name="Réponse par paire")

    is_correct     = models.BooleanField(default=0, verbose_name="Réponse correcte ?")
    customexercise = models.ForeignKey(Customexercise, related_name="choices", blank=True, null = True,  on_delete=models.CASCADE)
    def __str__(self):
        return self.answer 



class Subchoice(models.Model):
    """
    Modèle représentant un associé.
    """
    imageanswer = models.ImageField(upload_to=choice_directory_path,  null=True,  blank=True, verbose_name="Image", default="")
    answer      = models.TextField(max_length=255, default='', null=True,  blank=True, verbose_name="Réponse écrite")
    retroaction = models.TextField(max_length=255, default='', null=True,  blank=True, verbose_name="Rétroaction")

    is_correct  = models.BooleanField(default=0, verbose_name="Réponse correcte ?")
    choice      = models.ForeignKey(Choice, related_name="subchoices", blank=True, null = True,  on_delete=models.CASCADE)
    def __str__(self):
        return self.answer 
######################################################################
#####  type de réponse possible et choix pour les types de questions
######################################################################


class Autoposition(models.Model): # Commentaire et note pour les exercices customisés coté enseignant

    customexercise = models.ForeignKey(Customexercise,  on_delete=models.CASCADE,   related_name='autopositions', editable=False)
    parcours = models.ForeignKey(Parcours,  on_delete=models.CASCADE,   related_name='autopositions', editable=False)    
    student = models.ForeignKey(Student,  on_delete=models.CASCADE, blank=True,  related_name='autopositions', editable=False)
    date = models.DateTimeField(auto_now_add=True)
    criterion = models.ForeignKey(Criterion,  on_delete=models.CASCADE, blank=True,  related_name='autopositions', editable=False)
    position = models.PositiveIntegerField( default=0, ) 


    def __str__(self):        
        return "{} {} {}".format(self.customexercise, self.criterion , self.position)


class Variable(models.Model):

    name  = models.CharField(max_length=50,  blank=True, verbose_name="variable")
    customexercise  = models.ForeignKey(Customexercise, related_name="variables", blank=True, null = True,  on_delete=models.CASCADE)
    ## Variable numérique
    is_integer = models.BooleanField(default=1, verbose_name="Valeur entière ?")        
    maximum = models.IntegerField(default=10)
    minimum = models.IntegerField(default=0)
    ## Variable littérale
    words  = models.CharField(max_length=255,  blank=True, verbose_name="Liste de valeurs")

    def __str__(self):
        return self.name 


class Blacklist(models.Model):
    relationship   = models.ForeignKey(Relationship,  null=True, blank=True, on_delete=models.CASCADE,  related_name='relationship_individualisation',   editable= False)
    customexercise = models.ForeignKey(Customexercise,  null=True, blank=True, on_delete=models.CASCADE,  related_name='customexercise_individualisation',   editable= False)
    student        = models.ForeignKey(Student, null=True, blank=True, on_delete=models.CASCADE,  related_name='student_individualisation',  editable= False)
    
    def __str__(self):
        return f"{self.relationship} : {self.student}" 


class Customanswerbystudent(models.Model): # Commentaire et note pour les exercices customisés coté enseignant

    customexercise = models.ForeignKey(Customexercise,  on_delete=models.CASCADE,   related_name='customexercise_custom_answer', editable=False)
    parcours = models.ForeignKey(Parcours,  on_delete=models.CASCADE,   related_name='parcours_custom_answer', editable=False)    
    student = models.ForeignKey(Student,  on_delete=models.CASCADE, blank=True,  related_name='student_custom_answer', editable=False)
    date = models.DateTimeField(auto_now_add=True)
    # rendus
    file = models.FileField(upload_to= file_directory_student, blank = True, null=True,   verbose_name="Fichier pdf ou texte", default="")
    answer = RichTextUploadingField( default="", null=True,  blank=True, ) 
    # eval prof
    comment = models.TextField( default="", null=True) 
    point = models.CharField(default="", max_length=10, verbose_name="Note")
    is_corrected = models.BooleanField( default=0, editable=False ) 
    audio = models.FileField(upload_to=file_folder_path,verbose_name="Commentaire audio", blank=True, null= True,  default ="")
    is_reading  = models.BooleanField( default=0, editable=False ) # si l'élève a lu le commentaire

    def __str__(self):        
        return "{}".format(self.customexercise)

    class Meta:
        unique_together = ['student', 'parcours', 'customexercise']

class Customanswerimage(models.Model): # Commentaire et note pour les exercices customisés coté enseignant

    customanswerbystudent = models.ForeignKey(Customanswerbystudent,  on_delete=models.CASCADE,   related_name='customexercise_custom_answer_image', editable=False)
    date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to= file_directory_to_student, blank = True, null=True,   verbose_name="Scan ou image ou Photo", default="")
    imagecanvas = models.TextField( blank = True, null=True, editable=False)   

    def __str__(self):        
        return "{}".format(self.customanswerbystudent)

class Correctionskillcustomexercise(models.Model): # Evaluation des compétences pour les exercices customisés coté enseignant 

    customexercise = models.ForeignKey(Customexercise,  on_delete=models.CASCADE,   related_name='customexercise_correctionskill', editable=False)
    parcours = models.ForeignKey(Parcours,  on_delete=models.CASCADE,   related_name='parcours_customskill_answer', editable=False)    
    student = models.ForeignKey(Student,  on_delete=models.CASCADE, blank=True,  related_name='student_correctionskill', editable=False)
    skill = models.ForeignKey(Skill,  on_delete=models.CASCADE,   related_name='skill_correctionskill', editable=False)
    date = models.DateTimeField(auto_now_add=True)
    point = models.PositiveIntegerField(default=-1,  editable=False)
    
    def __str__(self):        
        return "{}".format(self.customexercise)

    class Meta:
        unique_together = ['student', 'customexercise','skill']

class Correctionknowledgecustomexercise(models.Model): # Evaluation des savoir faire pour les exercices customisés coté enseignant

    customexercise = models.ForeignKey(Customexercise,  on_delete=models.CASCADE,   related_name='customexercise_correctionknowledge', editable=False)
    parcours = models.ForeignKey(Parcours,  on_delete=models.CASCADE,   related_name='parcours_customknowledge_answer', editable=False)    
    student = models.ForeignKey(Student,  on_delete=models.CASCADE, blank=True,  related_name='student_correctionknowledge', editable=False)
    knowledge = models.ForeignKey(Knowledge,  on_delete=models.CASCADE,   related_name='knowledge_correctionknowledge', editable=False)
    date = models.DateTimeField(auto_now_add=True)
    point = models.PositiveIntegerField(default=-1,  editable=False)
    
    def __str__(self):        
        return "{}".format(self.customexercise)

    class Meta:
        unique_together = ['student', 'customexercise','knowledge']

class Exerciselocker(ModelWithCode):

    relationship = models.ForeignKey(Relationship,  on_delete=models.CASCADE, blank=True, null=True,  related_name='relationship_exerciselocker', editable=False) 
    customexercise = models.ForeignKey(Customexercise,  on_delete=models.CASCADE, blank=True, null=True,  related_name='customexercise_exerciselocker', editable=False) 
    custom  = models.BooleanField(default=0, editable=False)    
    student = models.ForeignKey(Student,  on_delete=models.CASCADE, blank=True,  related_name='student_exerciselocker', editable=False)
    lock = models.DateTimeField(null=True, blank=True, editable=False)

    def __str__(self):        
        return "{}".format(self.student)

########################################################################################################################################### 
########################################################################################################################################### 
################################################################   Cours    ############################################################### 
########################################################################################################################################### 
########################################################################################################################################### 
class Course(models.Model): # pour les 
    FORMES = (
        ("ACTIVITE", "ACTIVITE"),
        ("APPLICATION", "APPLICATION"),
        ("COURS"  , "COURS"),
        ("CONSIGNE"  , "CONSIGNE"),
        ("EXEMPLE", "EXEMPLE"),
        ("EXPLICATION", "EXPLICATION"),
        ("HISTOIRE", "HISTOIRE"),
        ("ILLUSTRATION", "ILLUSTRATION"),
        ("MÉTHODE", "MÉTHODE"),
        (""       , "PRESENTATION"),
        ("VIDEO"  , "VIDEO"),
    )
    parcours = models.ForeignKey(Parcours,  on_delete=models.CASCADE, blank=True, null=True,  related_name='course') 
    title = models.CharField(max_length=50, default='',  blank=True, verbose_name="Titre")    
    annoncement = RichTextUploadingField( blank=True, verbose_name="Texte*") 
    author = models.ForeignKey(Teacher, related_name = "author_course", blank=True, null=True, on_delete=models.CASCADE, editable=False )
    teacher = models.ForeignKey(Teacher, related_name = "course", on_delete=models.CASCADE, editable=False )
    duration = models.PositiveIntegerField(  default=15,  blank=True,  verbose_name="Durée estimée de lecture")  

    is_publish = models.BooleanField( default= 0, verbose_name="Publié ?")
    publish_start = models.DateTimeField(default=timezone.now,  blank=True, max_length=255, verbose_name="Début à", help_text="Changer les dates des cours peut remplacer les réglages de leur durée de disponibilité et leur placement dans les pages de cours ou le tableau de bord. Veuillez confirmer les dates d’échéance avant de modifier les dates des cours. ")
    publish_end = models.DateTimeField( blank=True, null=True,  max_length=255, verbose_name="Se termine à")


    ranking = models.PositiveIntegerField(  default=1,  blank=True, null=True,  verbose_name="Ordre") 
    
    is_task = models.BooleanField( default=0,    verbose_name="Tache à rendre ?") 
    is_paired = models.BooleanField( default=0,    verbose_name="Elèves créateurs ?") 
    is_active = models.BooleanField( default=0,  verbose_name="Contenu en cours")  
    is_share = models.BooleanField( default=0,  verbose_name="Mutualisé ?")  

    date_limit = models.DateTimeField( null=True, blank=True, verbose_name="Date limite du rendu")

    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modified = models.DateTimeField(auto_now=True, verbose_name="Date de modification") 

    notification = models.BooleanField( default=0,  verbose_name="Informer des modifications ?", help_text="Envoie un message aux participants." )     
 
    students = models.ManyToManyField(Student, blank=True,  related_name='students_course', verbose_name="Attribuer à/au")
    creators = models.ManyToManyField(Student, blank=True,  related_name='creators_course', verbose_name="Co auteurs élève") 
    relationships = models.ManyToManyField(Relationship, blank=True,  related_name='relationships_courses', verbose_name="Lier ce cours à") 

    level   = models.ForeignKey(Level, on_delete=models.CASCADE,  related_name="courses", default=None,  blank=True, null=True , verbose_name="Niveau")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE,  related_name="courses", default=None,   blank=True, null=True, verbose_name="Enseignement" )

    forme   = models.CharField(max_length=50,choices=FORMES, default='COURS',  blank=True, verbose_name="Type")    

    def __str__(self):
        return self.title 

    def subjects(self):
        subjects = []
        for k in self.parcours.knowledges.all() :
            if k.theme.subject  not in subjects :
                subjects.append(k.theme.subject)

        for s in self.skills.all() :
            if s.subject not in subjects :
                subjects.append(s.subject)

        if len(subjects) == 0 :
            for sb in self.teacher.subjects.all() :
                if sb  not in subjects :
                    subjects.append(sb)       
        return subjects



    def levels(self):
        levels = []
        for k in self.knowledges.all() :
            if k.level  not in levels :
                levels.append(k.level)

 
        if len(levels) == 0 :
            for sb in self.teacher.levels.all() :
                if sb  not in levels :
                    levels.append(sb)       
        return levels

    def type_of_document(self):
        return 2
########################################################################################################################################### 
########################################################################################################################################### 
#############################################################  Remediation       ########################################################## 
########################################################################################################################################### 
###########################################################################################################################################  
class Remediation(models.Model):

    title = models.CharField(max_length=255, default='',  blank=True,verbose_name="Titre")
    relationship = models.ForeignKey(Relationship, on_delete=models.CASCADE, default='',   blank=True, related_name='relationship_remediation') 
    video = models.CharField(max_length=255, default='',  blank=True,   verbose_name="url de la vidéo")
    mediation = models.FileField(upload_to=file_directory_path,verbose_name="Fichier", blank=True,   default ="")
    audio = models.BooleanField( default=0,    verbose_name="Audio texte ?") 
    duration = models.PositiveIntegerField(  default=15,  blank=True,  verbose_name="Durée estimée (en min.)")  
    consigne = models.BooleanField( default=0,    verbose_name="Consigne ?") 
    courses = models.ManyToManyField(Course, blank=True,  related_name='courses_remediation', verbose_name="Cours") 

    def __str__(self):        
        return "title {}".format(self.title)

class Remediationcustom(models.Model):

    title = models.CharField(max_length=255, default='',  blank=True,verbose_name="Titre")
    customexercise = models.ForeignKey(Customexercise,  on_delete=models.CASCADE, default='',   blank=True, related_name='customexercise_remediation') 
    video = models.CharField(max_length=255, default='',  blank=True,   verbose_name="url de la vidéo")
    mediation = models.FileField(upload_to=file_folder_path,verbose_name="Fichier", blank=True,   default ="")
    audio = models.BooleanField( default=0,    verbose_name="Audio texte ?") 
    duration = models.PositiveIntegerField(  default=15,  blank=True,  verbose_name="Durée estimée (en min.)")  
    consigne = models.BooleanField( default=0,    verbose_name="Consigne ?") 
    courses = models.ManyToManyField(Course, blank=True,  related_name='courses_remediationcustom', verbose_name="Cours") 

    def __str__(self):        
        return "title {}".format(self.title)

class Constraint(models.Model):

    code = models.CharField(max_length=8, default='', editable=False)# code de l'exo qui constraint
    relationship = models.ForeignKey(Relationship, on_delete=models.CASCADE, default='',   blank=True, related_name='relationship_constraint') 
    scoremin = models.PositiveIntegerField(  default=80, editable=False)  


    def __str__(self):        
        return "{} à {}%".format(self.code , self.scoremin)

########################################################################################################################################### 
########################################################################################################################################### 
########################################################   Demande d'exo    ############################################################### 
########################################################################################################################################### 
########################################################################################################################################### 
class Demand(models.Model):
    level = models.ForeignKey(Level, related_name="demand", on_delete=models.PROTECT, verbose_name="Niveau")
    theme = models.ForeignKey(Theme, related_name="demand", on_delete=models.PROTECT, verbose_name="Thème")
    knowledge = models.ForeignKey(Knowledge, on_delete=models.PROTECT, related_name='demand', verbose_name="Savoir faire associé - Titre")
    demand = models.TextField(blank=True, verbose_name="Votre demande explicitée*")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    file = models.FileField(upload_to= directory_path, verbose_name="Exercice souhaité", default="", null = True, blank= True) 
    teacher = models.ForeignKey(Teacher, related_name = "demand", on_delete=models.CASCADE, editable=False, default="" )    
    done = models.BooleanField( default=0,  verbose_name="Fait", null = True, blank= True) 
    code = models.CharField(max_length=10, default='',  blank=True, null=True,  verbose_name="id de l'exercice créé")    

    def __str__(self):
        return "{}".format(self.demand)

########################################################################################################################################### 
########################################################################################################################################### 
########################################################   Mastering        ############################################################### 
########################################################################################################################################### 
########################################################################################################################################### 
class Mastering(models.Model):

    relationship = models.ForeignKey(Relationship, related_name="relationship_mastering", on_delete=models.CASCADE, verbose_name="Exercice")
    consigne = models.CharField(max_length=255, default='',  blank=True,   verbose_name="Consigne")   
    video = models.CharField(max_length=50, default='',  blank=True,   verbose_name="code de vidéo Youtube")   
    mediation = models.FileField(upload_to= directory_path_mastering, verbose_name="Fichier", default="", null = True, blank= True) 
    writing = models.BooleanField( default=0,  verbose_name="Page d'écriture", ) 
    duration = models.PositiveIntegerField(  default=15,  blank=True,  verbose_name="Durée estimée")    

    scale = models.PositiveIntegerField(default=3, editable= False) 
    ranking = models.PositiveIntegerField(default=0,  editable= False) 
    exercise = models.ForeignKey(Exercise, related_name = "exercise", on_delete=models.CASCADE, editable=False, default="", null = True, blank= True )   
    courses = models.ManyToManyField(Course, blank=True, related_name='courses_mastering')
    
    def __str__(self):
        return "{}".format(self.relationship)

    def is_done(self,student): 
        is_do = False  
        if Mastering_done.objects.filter(mastering = self, student = student).count() > 0 :  
            is_do = True  
        return is_do       


class Mastering_done(models.Model):

    mastering = models.ForeignKey(Mastering, related_name="mastering_done", editable=False, on_delete=models.CASCADE, verbose_name="Exercice")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, editable=False, related_name='students_mastering_done')
    writing = RichTextUploadingField( blank=True, verbose_name="Texte*") 
    
    def __str__(self):
        return "{}".format(self.mastering)


########################################################################################################################################### 
########################################################################################################################################### 
################################################   Mastering  from customexercise       ################################################### 
########################################################################################################################################### 
########################################################################################################################################### 
class Masteringcustom(models.Model):

    customexercise = models.ForeignKey(Customexercise, related_name="customexercise_mastering_custom", on_delete=models.PROTECT, verbose_name="Exercice")
    consigne = models.CharField(max_length=255, default='',  blank=True,   verbose_name="Consigne")   
    video = models.CharField(max_length=50, default='',  blank=True,   verbose_name="code de vidéo Youtube")   
    mediation = models.FileField(upload_to= directory_path_mastering, verbose_name="Fichier", default="", null = True, blank= True) 
    writing = models.BooleanField( default=0,  verbose_name="Page d'écriture", ) 
    duration = models.PositiveIntegerField(  default=15,  blank=True,  verbose_name="Durée estimée")    

    scale = models.PositiveIntegerField(default=3, editable= False) 
    ranking = models.PositiveIntegerField(default=0,  editable= False) 
    exercise = models.ForeignKey(Exercise, related_name = "exercise_mastering_custom", on_delete=models.PROTECT, editable=False, default="", null = True, blank= True )   
    courses = models.ManyToManyField(Course, blank=True, related_name='courses_mastering_custom')
    
    def __str__(self):
        return "{}".format(self.customexercise)



    def is_done(self,student): 
        is_do = False  
        if Masteringcustom_done.objects.filter(mastering = self, student = student).count() > 0 :  
            is_do = True  
        return is_do       

class Masteringcustom_done(models.Model):

    mastering = models.ForeignKey(Masteringcustom, related_name="mastering_custom_done", editable=False, on_delete=models.CASCADE, verbose_name="Exercice")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, editable=False, related_name='students_mastering_custom_done')
    writing = RichTextUploadingField( blank=True, verbose_name="Texte*") 
    
    def __str__(self):
        return "{}".format(self.mastering)

########################################################################################################################################### 
########################################################################################################################################### 
##############################################################  Annotations       ######################################################### 
########################################################################################################################################### 
########################################################################################################################################### 

class Comment(models.Model): # Commentaire du l'enseignant vers l'élève pour les exercices non autocorrigé coté enseignant

    teacher = models.ForeignKey(Teacher,  on_delete=models.CASCADE, blank=True,  related_name='teacher_comment', editable=False)
    comment = models.TextField() 

    def __str__(self):        
        return "{} : {}".format(self.comment, self.teacher)

class Generalcomment(models.Model): # Commentaire conservé d'une copie  coté enseignant

    teacher = models.ForeignKey(Teacher,  on_delete=models.CASCADE, blank=True,  related_name='teacher_generalcomment', editable=False)
    comment = models.TextField() 

    def __str__(self):        
        return "{} : {}".format(self.comment, self.teacher)

class CommonAnnotation(models.Model):
 
    classe = models.CharField(max_length=255, editable=False)   
    style = models.CharField(max_length=255, editable=False) 
    attr_id = models.CharField(max_length=255, editable=False) 
    content = models.TextField(editable=False) 
  
    class Meta:
        abstract = True

class Annotation(CommonAnnotation):

    writtenanswerbystudent = models.ForeignKey(Writtenanswerbystudent, on_delete=models.CASCADE,related_name='annotations') 

    def __str__(self):
        return "{}".format(self.writtenanswerbystudent)

    class Meta:
        unique_together = ['writtenanswerbystudent', 'attr_id']

class Customannotation(CommonAnnotation):

    customanswerbystudent = models.ForeignKey(Customanswerbystudent, on_delete=models.CASCADE, related_name='annotations') 

    def __str__(self):
        return "{}".format(self.customanswerbystudent)


    class Meta:
        unique_together = ['customanswerbystudent', 'attr_id']    


########################################################################################################################################### 
########################################################################################################################################### 
######################################################   Test des documents       ######################################################### 
########################################################################################################################################### 
########################################################################################################################################### 

class DocumentReport(models.Model):

    document = models.CharField(max_length=100, editable= False)   
    document_id = models.PositiveIntegerField(default=3, editable= False)  
    report = RichTextUploadingField( blank=True, default="RAS",  verbose_name="Remarque*") 
    user = models.ForeignKey(User,  on_delete=models.CASCADE, blank=True,  related_name='user_document_report', editable= False) 
    date_created = models.DateTimeField(auto_now_add=True)
    is_done = models.BooleanField( default=0,  verbose_name="Fait") 


    def __str__(self):
        return "{}".format(self.document)

########################################################################################################################################### 
########################################################################################################################################### 
######################################################        Tracker             ######################################################### 
########################################################################################################################################### 
########################################################################################################################################### 
 
class Tracker(models.Model):
    """Savoir où se trouve un utilisateur """
    user = models.ForeignKey(User, blank=True, related_name="tracker", on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    parcours = models.ForeignKey(Parcours,  on_delete=models.CASCADE, blank=True,  related_name='tracker', editable= False)
    exercise_id = models.PositiveIntegerField(default=0, null=True,   editable= False)  
    is_custom = models.BooleanField( blank=True, default=0, ) #0 Pour les exos sacado et 1 pour les exo personnels

    def __str__(self):
        return "Traceur de : {}".format(self.user)



########################################################################################################################################### 
########################################################################################################################################### 
######################################################      Prep_eval             ######################################################### 
########################################################################################################################################### 
########################################################################################################################################### 

class Prepeval(models.Model):

    student      = models.ForeignKey(Student, blank=True, related_name="prepevals", on_delete=models.CASCADE, editable= False)
    date_created = models.DateField(auto_now_add=True)
    parcours     = models.ForeignKey(Parcours,  on_delete=models.CASCADE, blank=True,  related_name='prepevals', editable= False)
    date         = models.DateField()  
    mark         = models.DecimalField(default=-1,  max_digits=5, decimal_places=2 , blank=True)

    def __str__(self):
        return "Prep'éval de : {}".format(self.student.user)


class Slot(models.Model):

    date          = models.DateField( editable= False )
    content       = models.TextField( blank=True, null=True, editable= False )
    relationships = models.ManyToManyField(Relationship,  related_name='slots', blank=True, editable= False) 
    prepeval      = models.ForeignKey(Prepeval,  on_delete=models.CASCADE, blank=True, null=True,  related_name='slots', editable= False)
    done          = models.BooleanField( blank=True, default=0, )
    def __str__(self):
        return "{}".format(self.date)

    def dataset(self):
        data = {}
        nbr     = self.relationships.exclude(type_id=2).count()
        student_answers = self.prepeval.student.answers.filter(parcours=self.prepeval.parcours)
        nb_ans  = student_answers.values_list('exercise_id',flat=True).distinct().count()
        nbr_no  = nbr - nb_ans
        try :
            student_answers = student_answers.filter(parcours=self.prepeval.parcours).aggregate(average=Avg("point"))
            percent = int(student_answers["average"])
        except :
            percent = 0
        if percent == 0 : 
            comment = "Il est temps de commencer ta révision quotidienne. Bonne préparation."
            color = '#9975e0' 
        elif percent > 92 : 
            comment = "Bravo ! Cette session doit te donner confiance. Tu réalises une excellente séance de travail."
            color = '#1d6718' 
        elif  percent > 70 : 
            comment = "Tu réalises une bonne séance de travail."
            color = '#62d85a'
        elif  percent > 50 : 
            comment = "Tu réalises une moyenne séance de travail."  
            color = '#b5a32b' 
        else : 
            comment = "Tu  réalises une séance de travail insuffisante pour te permettre de réussir ton évaluation. Tu dois recommencer les exercices."
            color = '#b5322b' 

        is_end = False
        if nbr <= nb_ans + 2 : is_end = True
        
        data["nb_ans"] = nb_ans
        data["percent"] = percent 
        data["nbr_no"] = nbr_no
        data["comment"] = comment
        data["color"] = color
        data['end'] = is_end
        return data