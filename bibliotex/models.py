import uuid
from django.db import models
from datetime import date, datetime, timedelta
 
from group.models import  Group
from django.utils import timezone
from account.models import Student, Teacher, ModelWithCode, generate_code, User
from socle.models import  Knowledge, Level , Theme, Skill , Subject 
from qcm.models import Folder , Parcours , Course
from django.apps import apps
from ckeditor_uploader.fields import RichTextUploadingField
from django.db.models import Q, Min, Max
import os.path
from django.utils import timezone
from general_fonctions import *
# Pour créer un superuser, il faut depuis le shell taper :
# from account.models import User 
# User.objects.create_superuser("admin","admin@gmail.com","motdepasse", user_type=0).save()
########################################################################################################
########################################################################################################
# cette parties sert à créer un répertoire par user pour sauvegarder les fichiers
 
 
def image_directory_path(instance, filename):
    return "bibliotex/{}/{}".format(instance.author.id, filename)


########################################################################################################
########################################################################################################
class Exotex(models.Model):

    title = models.CharField(max_length=255, blank=True,  default="", null=True,  verbose_name="Titre")

    content = models.TextField( verbose_name="Enoncé en LaTeX")
    content_html = RichTextUploadingField( blank=True,  verbose_name="Enoncé pour html") 

    author = models.ForeignKey(Teacher, related_name="author_exotexs", on_delete=models.PROTECT, editable=False)
    #### pour validation si le qcm est noté
    calculator = models.BooleanField(default=0, verbose_name="Calculatrice ?")
    #### pour donner une date de remise
 
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modified = models.DateTimeField(auto_now=True, verbose_name="Date de modification")
 
    duration = models.PositiveIntegerField(default=15, blank=True, verbose_name="Durée estimée - en minutes")
    point = models.PositiveIntegerField(  default=0,  blank=True, null=True ,  verbose_name="Points") 
    ###### Socle
    subject = models.ForeignKey(Subject, default =1 , on_delete=models.PROTECT,  related_name='subject_exotexs', verbose_name="Enseignement associé")
    knowledge = models.ForeignKey(Knowledge, on_delete=models.PROTECT,  related_name='knowledge_exotexs', verbose_name="Savoir faire associé")
    level = models.ForeignKey(Level, related_name="level_exotexs", on_delete=models.PROTECT, verbose_name="Niveau")
    theme = models.ForeignKey(Theme, related_name="theme_exotexs", on_delete=models.PROTECT, verbose_name="Thème")
    skills = models.ManyToManyField(Skill, blank=True, related_name='skills_exotexs', verbose_name="Compétences ciblées")
    knowledges = models.ManyToManyField(Knowledge, blank=True,  default="",  related_name='other_knowledge_exotexs', verbose_name="Savoir faire associés complémentaires")

    is_share     = models.BooleanField(default=1, verbose_name="Mutualisé ?")
    is_python    = models.BooleanField(default=0, verbose_name="Python ?")
    is_scratch   = models.BooleanField(default=0, verbose_name="Scratch ?")
    is_tableur   = models.BooleanField(default=0, verbose_name="Tableur ?")
    is_corrected = models.BooleanField(default=0, verbose_name="Correction ?")
    is_annals    = models.BooleanField(default=0, verbose_name="Annale ?")

    correction = models.TextField( blank=True, default="", null=True, verbose_name="Corrigé")
    correction_html = RichTextUploadingField( blank=True,  verbose_name="Correction pour html") 

    ranking = models.PositiveIntegerField(  default=0,  blank=True, null=True, editable=False)


    def __str__(self): 
        knowledge = self.knowledge.name[:20]       
        return "{} > {} > {}".format(self.level.name, self.theme.name, knowledge)



    def is_selected(self,bibliotex):
        test = False
        try : 
            if self in bibliotex.exotexs.all() :
                test = True
        except:
            pass
        return test

 


class Bibliotex(models.Model):

    title    = models.CharField(max_length=255,  verbose_name="Titre")
    author   = models.ForeignKey(Teacher, related_name="author_bibliotexs", on_delete=models.CASCADE, editable=False)
    teacher  = models.ForeignKey(Teacher,  related_name="teacher_bibliotexs", on_delete=models.CASCADE,  editable=False)
    coteachers = models.ManyToManyField(Teacher, related_name="coteachers_bibliotexs", editable=False)
    color = models.CharField(max_length=255, default='#5d4391', verbose_name="Couleur")
    
    date_created  = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modified = models.DateTimeField(auto_now=True, verbose_name="Date de modification")
    vignette     = models.ImageField(upload_to=image_directory_path, verbose_name="Vignette d'accueil", default="",null=True, blank=True)

    is_favorite = models.BooleanField(default=0, verbose_name="Favori ?")
    is_share = models.BooleanField(default=0, verbose_name="Mutualisé ?")
    is_annal = models.BooleanField(default=0,  blank=True, null=True, verbose_name="Annale ?") 
    is_archive  = models.BooleanField(default=0, verbose_name="Archivé ?")
    is_publish = models.BooleanField(default=0, verbose_name="Publié ?")
    start = models.DateTimeField(null=True, blank=True, verbose_name="A partir de")
    stop = models.DateTimeField(null=True, blank=True, verbose_name="Date de verrouillage")

    folders  = models.ManyToManyField(Folder, blank=True,  related_name="bibliotexs", editable=False)
    groups   = models.ManyToManyField(Group,  blank=True,  related_name="bibliotexs",  verbose_name="Groupe éventuel" )
    parcours = models.ManyToManyField(Parcours, blank=True, related_name="bibliotexs"  ) 

    exotexs  = models.ManyToManyField(Exotex,  through="Relationtex", related_name="bibliotexs", editable=False)
    students = models.ManyToManyField(Student, related_name="bibliotexs", editable=False)

    levels = models.ManyToManyField(Level,  related_name="bibliotexs",  editable=False)
    subjects = models.ManyToManyField(Subject,  related_name="bibliotexs",  editable=False)

    ranking = models.PositiveIntegerField(  default=0,  blank=True, null=True, editable=False)


    def __str__(self):    
        return "{}".format(self.title)

    def skills(self):  
        skills = set()
        for exotex in self.exotexs.all():
            skills.update(exotex.skills.all())
        return skills

    def knowledges(self):    
        knowledges = set()
        for exotex in self.exotexs.all():
            knowledges.update(set([exotex.knowledge]))
            knowledges.update(exotex.knowledges.all())
        return knowledges


    def relationtex(self):    
        data = {}
        care = False
        relationtexs = self.relationtexs.all() 
        exotexs_published =  relationtexs.filter(is_publish=1) 
        data["nb_exotexs"] = relationtexs.count() 
        data["nb_exotexs_published"] = exotexs_published.count()  
        if  relationtexs.count() != exotexs_published.count() :
            care =  True
        data["care"] = care  
        return data


    def only_students(self,group):

        data = {}
        if group :
            group_students = group.students.all() #.exclude(user__username__contains="_e-test")
            self_students = self.students.exclude(user__username__contains="_e-test")
            intersection = list(set(group_students) & set(parcours_students))
        else :
            intersection = self.students.exclude(user__username__contains="_e-test")
 

        data["nb"]= len(intersection)
        data["students"] = intersection
        return data 

    def type_of_document(self):
        return 4
########################################################################################################
########################################################################################################
class Relationtex(models.Model):

    exotex = models.ForeignKey(Exotex,  on_delete=models.CASCADE,   related_name='relationtexs', editable= False)
    bibliotex = models.ForeignKey(Bibliotex, on_delete=models.CASCADE,  related_name='relationtexs',  editable= False)
    content = models.TextField( null=True, blank=True, verbose_name="Enoncé en LaTeX")
    content_html = models.TextField( null=True, blank=True,  editable= False)
    
    teacher = models.ForeignKey(Teacher, related_name="teacher_relationtexs", on_delete=models.PROTECT, editable=False)
    #### pour validation si le qcm est noté
    calculator = models.BooleanField(default=0, verbose_name="Calculatrice ?")
    #### pour donner une date de remise
 
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modified = models.DateTimeField(auto_now=True, verbose_name="Date de modification")
 
    duration = models.PositiveIntegerField(default=15, blank=True, verbose_name="Durée estimée - en minutes")
    point = models.PositiveIntegerField(  default=0,  blank=True, null=True ,  verbose_name="Points") 
    ###### Socle
    skills = models.ManyToManyField(Skill, blank=True, related_name='relationtexs', verbose_name="Compétences ciblées")
    knowledges = models.ManyToManyField(Knowledge, related_name='relationtexs', verbose_name="Savoir faire associés complémentaires")

    is_python = models.BooleanField(default=0, verbose_name="Python ?")
    is_scratch = models.BooleanField(default=0, verbose_name="Scratch ?")
    is_tableur = models.BooleanField(default=0, verbose_name="Tableur ?")
    is_print = models.BooleanField(default=0, verbose_name="Imprimé ?")
    is_publish = models.BooleanField(default=0, verbose_name="Publié ?")
    start = models.DateTimeField(null=True, blank=True, verbose_name="A partir de")
    stop = models.DateTimeField(null=True, blank=True, verbose_name="Date de verrouillage")

    ranking = models.PositiveIntegerField(  default=0,  blank=True, null=True, editable=False)

    correction = models.TextField( blank=True, default="", null=True, verbose_name="Enoncé")
    is_publish_cor = models.BooleanField(default=0, verbose_name="Publié ?")
    correction_html = models.TextField( blank=True, default="", null=True,  editable= False)

    courses = models.ManyToManyField(Course, related_name="relationtexs", blank=True, verbose_name="Cours éventuel"  )
    students = models.ManyToManyField(Student, related_name="relationtexs", editable=False)

    def __str__(self):       
        return "{} > {}".format(self.bibliotex.title,self.exotex.title)

    class Meta:
        unique_together = ('exotex', 'bibliotex')


    def only_students(self,group):

        data = {}
        if group :
            group_students = group.students.all() #.exclude(user__username__contains="_e-test")
            self_students = self.students.exclude(user__username__contains="_e-test")
            intersection = list(set(group_students) & set(parcours_students))
        else :
            intersection = self.students.exclude(user__username__contains="_e-test")
 
        data["nb"]= len(intersection)
        data["students"] = intersection.order_by("user__last_name")
        return data 

 
    def type_of_exercise(self):
        return 4













class Blacklistex(models.Model):

    relationtex = models.ForeignKey(Relationtex,  on_delete=models.CASCADE,   related_name='blacklistex', editable= False)
    student = models.ForeignKey(Student,  on_delete=models.PROTECT, related_name="blacklistex", editable=False)
   
    def __str__(self):   
        return "{} > {}".format(self.relationtex.id, self.student.user.id)

