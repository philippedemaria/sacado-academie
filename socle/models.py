from django.db import models
from multiselectfield import MultiSelectField
from django.apps import apps
from django.db.models import Avg , Sum
from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from general_fonctions import *


def level_name(level):
    if level == "T" :
        my_level = level+"erm"
    elif level == '6' :
        my_level = str(level)+"ème"
    elif level == '5' :
        my_level = str(level)+"ème"
    elif level == '4' :
        my_level = str(level)+"ème"
    elif level == '3' :
        my_level = str(level)+"ème"
    elif level == '2' :
        my_level = str(level)+"nde"
    elif level == '1' :
        my_level = str(level)+"ère"
    elif level == 'Mater' :
        my_level = str(level)+"nelle"
    else :
        my_level = level 
    return my_level


def directory_path(instance, filename):
    return "subject_images/{}".format(filename)



class Subject(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nom")
    color = models.CharField(max_length=255, default ="" , verbose_name="Couleur")
    shortname = models.CharField(max_length=10, default ="" , verbose_name="Abréviation")
    is_active = models.BooleanField(default=0, verbose_name="Active ?")
 
    def __str__(self):
        return "{}".format(self.shortname)

    def nb_exercises(self):
        Exercise = apps.get_model('qcm', 'Exercise')
        return Exercise.objects.filter(theme__subject=self,supportfile__is_title=0).count()





    def level_min_max(self):
        Exercise = apps.get_model('qcm', 'Exercise')
        level_names = Exercise.objects.filter(theme__subject=self,supportfile__is_title=0).prefetch_related("level").values_list("level__shortname",flat=True).order_by("level__ranking").distinct()
        if len(level_names) == 1 :
            return level_name(level_names[0])
        elif len(level_names) > 1 :
            return level_name(level_names[0])+" à la "+level_name( level_names[len(level_names)-1] )
        else :
            return "-"



class Theme(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nom")
    slug = models.CharField(max_length=255, default ="" , editable=False)
    subject  = models.ForeignKey(Subject, related_name="theme", default="",  null = True , on_delete=models.PROTECT, verbose_name="Enseignement")

    def __str__(self):
        return "{} : {}".format(self.subject,self.name)

    def string_id(self):
        return "{}".format(self.id)

    def as_score_by_theme(self, student, group):

        Resultknowledge = apps.get_model('account', 'Resultknowledge')
        knowledges = self.knowledges.filter(level=group.level)
        resultknowledges = Resultknowledge.objects.filter(student = student, knowledge__in=knowledges)
        nb = len(resultknowledges)
        somme = 0
        for r in resultknowledges:
            somme += r.point
        try :
            avg = int(somme/nb)
        except :
            avg = ""
        return avg



    def all_details(self,parcours):
        Relationship = apps.get_model('qcm', 'Relationship')
        today = time_zone_user(parcours.teacher.user)
        detail = {}
        detail["pub"] = Relationship.objects.filter(parcours=parcours, exercise__theme = self,is_publish=1).count()
        detail["total"] = Relationship.objects.filter(parcours=parcours, exercise__theme = self).count()        
        detail["done"] = Relationship.objects.filter(parcours=parcours, exercise__theme = self).exclude(date_limit=None).count()
        detail["in_air"] = Relationship.objects.filter(parcours=parcours, exercise__theme = self,date_limit__gte=today).count()
        return detail



class Level(models.Model):

    CYCLES = (
        ('c1', 'Cycle 1'),
        ('c2', 'Cycle 2'),
        ('c3', 'Cycle 3'),
        ('c4', 'Cycle 4'),
        ('c5', 'Cycle 5'),
        ('c6', 'Post BaC'),
    )

    name      = models.CharField(max_length=255, null=True, blank=True, verbose_name="Nom")
    shortname = models.CharField(max_length=255, null=True, blank=True, verbose_name="Abréviation")
    cycle     = models.CharField(max_length=10, default='c1', choices=CYCLES,  verbose_name="Cycle")
    image     = models.CharField(max_length=255, null=True, blank=True, verbose_name="Image")    
    themes    = models.ManyToManyField(Theme, related_name = "theme_level", default="",  verbose_name="Thèmes")
    ranking   = models.PositiveIntegerField(  default=0,  blank=True, null=True, editable=False)
    color     = models.CharField(max_length=255, default='#46119c', blank=True, null=True, verbose_name="Couleur*")

    def __str__(self):
        return self.name

    def contrastColorText(self):
        """ donne le noir ou blanc selon la couleur initiale  """
        color1 = self.color[1:3]
        color2 = self.color[3:5]
        color3 = self.color[5:7]
        if 0.299 *  int(color1, 16) + 0.587 * int(color2, 16) + 0.114 * int(color3, 16)  > 150 :
            return "#000000"
        else :
            return "#FFFFFF"

    def nbknowlegde(self):
        return self.knowledges.count()

    def exotot(self):
        return self.exercises.select_related("supportfile","theme").filter(supportfile__is_title=0, theme__subject_id=1).count()


    def notexo(self):
        nb, m  = 0 , 0
        kws = self.knowledges
        n = kws.count()
        for k in kws.all() : 
            if self.exercises.filter(knowledge =k).exists():
                m+=1
        z = self.exercises.filter(knowledge__in = kws).count()
        nb = n - m
        return nb


    def is_level_theme(self,theme):
        this_theme = False
        if self.themes.filter(pk=theme.id).count() > 0:
            this_theme = True
        return this_theme

    def nb_level_subject(self, subject_id):
        nb = self.exercises.select_related("theme").filter(supportfile__is_title=0, theme__subject_id =  subject_id).count()
        return nb

    def shortname_full(self):
        level = self.shortname
        if level == "T" :
            my_level = level+"<sup>erm</sup>"
        elif level == '6' :
            my_level = str(level)+"<sup>ème</sup>"
        elif level == '5' :
            my_level = str(level)+"<sup>ème</sup>"
        elif level == '4' :
            my_level = str(level)+"<sup>ème</sup>"
        elif level == '3' :
            my_level = str(level)+"<sup>ème</sup>"
        elif level == '2' :
            my_level = str(level)+"<sup>nde</sup>"
        elif level == '1' :
            my_level = str(level)+"<sup>ère</sup>"
        elif level == 'Mater' :
            my_level = "M<sup>nelle</sup>"
        else :
            my_level = level 
        return my_level
 

    def details(self):
        data      = {}
        Activeyear  = apps.get_model('association', 'Activeyear')
        Adhesion  = apps.get_model('account', 'Adhesion')   
             
        activeyear= Activeyear.objects.get(is_active=1)
        a_year    = activeyear.year

        adhesions = self.adhesions.filter(student__user__school_id=50 ,  year= a_year ) 
        adheses   = adhesions.aggregate(total_amount=Sum('amount')) 

        data["nba"] = adhesions.count()

        if not adheses["total_amount"] :
            solde = 0
        else :
            solde = adheses["total_amount"]
        
        data["solde"] = solde

        return data




class Vignette(models.Model):
    subject = models.ForeignKey(Subject,  null=True, blank=True,   related_name='vignettes', on_delete=models.CASCADE, verbose_name="Enseignement")
    imagefile = models.ImageField(upload_to=directory_path,  verbose_name="Image" )
    level =  models.ForeignKey(Level,  null=True, blank=True, on_delete=models.CASCADE,  related_name='vignettes', verbose_name="Niveau" )

    def __str__(self):
        return "Vignette {}".format(self.level.name)


class Waiting(models.Model):
    name = models.CharField(max_length=500, verbose_name="Nom")
    theme  = models.ForeignKey(Theme, related_name="waitings",  on_delete=models.CASCADE, verbose_name="Thème")
    level = models.ForeignKey(Level, related_name="waitings", default="", on_delete=models.CASCADE, verbose_name="Niveau")

    def __str__(self):
        return "{} : {}".format(self.theme,self.name)


    def send_scorek(self,student):

        data = {}
        try:
            coef, score , score_ce  = 0, 0 , 0
            for k in self.knowledges.all():

 
                if k.results_k.filter(student=student).exists() :
                    r = k.results_k.filter(student=student).last()
                    score += int(r.point)
                    coef += 1

                if k.knowledge_correctionknowledge.filter(student=student).exists() :
                    ce = k.knowledge_correctionknowledge.filter(student=student).last()
                    score_ce += ce.point + 1 
                    coef += 1
 
            if coef != 0:
                score = int((score + score_ce)/coef)
            else :
                score = ""

        except ObjectDoesNotExist:
            score = ""

        data["score"] = score
        data["nombre"] = coef
        data["total"] = self.knowledges.count()
        return data


    def exercises_counter(self):
        Exercise = apps.get_model('qcm', 'Exercise')
        return Exercise.objects.filter(knowledge__waiting = self, supportfile__is_title=0).count()


    def supportfile_counter(self):
        Supportfile = apps.get_model('qcm', 'Supportfile')
        return Supportfile.objects.filter(knowledge__waiting = self, is_title=0).count()



    def exotexs_counter(self) :
        Exotex = apps.get_model('bibliotex', 'Exotex')
        return Exotex.objects.filter(knowledge__waiting = self).count()


class Knowledge(models.Model):
    level = models.ForeignKey(Level, related_name="knowledges", default="", on_delete=models.CASCADE, verbose_name="Niveau")
    theme = models.ForeignKey(Theme, related_name="knowledges", on_delete=models.CASCADE, verbose_name="Thème")
    name = models.CharField(max_length=10000, verbose_name="Nom")
    waiting  = models.ForeignKey(Waiting, related_name="knowledges", default="",  null = True , on_delete=models.CASCADE, verbose_name="Attendu")


    def __str__(self):
        return self.name

    def used(self):
        return self.nb_exercise() > 0

    def nb_exercise(self):
        return self.exercises.count()


    ### plus utilisée -----
    def nb_exercise_used(self,  parcours_tab): # parcours du groupe

        Relationship = apps.get_model('qcm', 'Relationship') 
        nb = 0
        relationships = Relationship.objects.filter(exercise__knowledge=self , parcours__in = parcours_tab).order_by("exercise").distinct()
      
        return nb 

    def exercices_by_knowledge(self,student,group):

        Exercise = apps.get_model('qcm', 'Exercise')
        exercises = Exercise.objects.filter(knowledge=self)
        return exercises


    def score_student_parcours(self,student,parcours):

        Studentanswer = apps.get_model('qcm', 'Studentanswer')
        r = Studentanswer.objects.filter(student = student, parcours = parcours , exercise__knowledge = self).aggregate(Avg('point'))
        if r["point__avg"] :
            score = int(r["point__avg"])
        else :
            score = ""

        return score


    def association_knowledge_supportfile(self, supportfile):

        Exercise = apps.get_model('qcm', 'Exercise')
        Parcours = apps.get_model('qcm', 'Parcours')

        if Exercise.objects.filter(supportfile=supportfile, knowledge=self).count() > 0:
            test = True
            exercises = Exercise.objects.filter(supportfile=supportfile, knowledge=self)
            som = 0
            for exercise in exercises:
                if Parcours.objects.filter(exercises=exercise,is_trash=0):
                    som += 1
            boolean = som > 0

        else:
            test = False
            boolean = False

        return {"exercise": test, "parcours": boolean}

    def custom_score(self, customexercise, student, parcours):
        Stage = apps.get_model('school', 'Stage')    
        try :
            stage = Stage.objects.get(school = student.user.school)
            up = stage.up
            med = stage.medium
            low = stage.low
        except :
            up = 85
            med = 65
            low = 35
        try :
            c_knowledge = self.knowledge_correctionknowledge.filter(customexercise = customexercise,  parcours = parcours, student = student).last()
            point = c_knowledge.point
            if point > up :
                crit = 4
            elif point > med :
                crit = 3
            elif point > low :  
                crit = 2
            elif point > -1 :  
                crit = 1
            else :  
                crit = 0
        except :
            crit = 0
        return crit



    def send_scorek(self,student):

        data = {}
        try:
            coef, score , score_ce = 0, 0 , 0
            if self.results_k.filter(student=student).exists() :
                r = self.results_k.filter(student=student).last()
                score = r.point
                coef += 1

            if self.knowledge_correctionknowledge.filter(student=student).exists() :
                ce = self.knowledge_correctionknowledge.filter(student=student).last()
                score_ce = ce.point + 1 
                coef += 1

            if coef != 0:
                score = int((score + score_ce)/coef)
            else :
                score = ""                

        except ObjectDoesNotExist:
            score = ""

        data["score"] = score
        data["nombre"] = coef
        data["total"] = ""
        return data




    def send_scorekp(self,student,parcours):

        Writtenanswerbystudent = apps.get_model("qcm","Writtenanswerbystudent")

        tab_set = set()
        tab = []
        for r in parcours.parcours_relationship.filter(is_publish=1,exercise__knowledge=self)[:5]:
            tab_set.update(set(parcours.answers.filter(exercise = r.exercise, student = student).order_by("-id")[:1]))

        tab_set.update(set(Writtenanswerbystudent.objects.filter(relationship__parcours = parcours, relationship__is_publish=1,relationship__exercise__knowledge=self)[:5]))
 
        tab_set.update(set(self.knowledge_correctionknowledge.filter(customexercise__parcourses = parcours, customexercise__is_publish=1)[:5]))

        return tab_set


    def supportfile_counter(self):
        return self.supportfiles.exclude(is_title=1).count()

    def exotexs_counter(self) :
        return self.knowledge_exotexs.count()


class Skill(models.Model): 
    name = models.CharField(max_length=10000, verbose_name="Nom")
    subject  = models.ForeignKey(Subject, related_name="skill", default="", on_delete=models.PROTECT, null = True ,  verbose_name="Enseignement")

    def __str__(self):
        return "{}".format(self.name )


    def custom_score(self, customexercise, student, parcours):

        Stage = apps.get_model('school', 'Stage')
        try :
            stage = Stage.objects.get(school = student.user.school)
            up = stage.up
            med = stage.medium
            low = stage.low
        except :
            up = 85
            med = 65
            low = 35
        try :
            c_skill = self.skill_correctionskill.filter(customexercise = customexercise,  parcours = parcours, student = student).last()
            pt = c_skill.point
            if pt > up :
                crit = 4
            elif pt > med :
                crit = 3
            elif pt > low :  
                crit = 2
            elif pt > -1 :  
                crit = 1
            else :  
                crit = 0
        except :
            crit = 0
        return crit



    def used(self):
        return self.nb_exercise() > 0

    def nb_exercise(self):
        return self.skills_relationship.count()


    def send_scorek(self,student):

        sk_set = set() 
        sk_set.update(student.students_relationship.filter(is_publish=1,skills=self) )
        sk_set.update(student.students_customexercises.filter(is_publish=1,skills=self) )
        total = len(sk_set)

        data = {}
        try:
            coef, score , score_ce = 0, 0 , 0
            if self.results_s.filter(student=student).exists() :
                r = self.results_s.filter(student=student).last()
                score = r.point
                coef += 1

            if self.skill_correctionskill.filter(student=student).exists() :
                ce = self.skill_correctionskill.filter(student=student).last()
                score_ce = ce.point + 1 
                coef += 1

            if coef != 0:
                score = int((score + score_ce)/coef)
            else :
                score = ""                

        except ObjectDoesNotExist:
            score = ""



        data["score"] = score
        data["nombre"] = min(coef,total)
        data["total"] = total
        return data



    def send_scorekp(self,student,parcours):

        sk_set = set() 
        sk_set.update(student.students_relationship.filter(parcours = parcours, is_publish=1,skills=self) )
        sk_set.update(student.students_customexercises.filter(parcourses = parcours,is_publish=1,skills=self))
        total = len(sk_set)
       
        data = {}

        try:
            coef, score   = 0, 0  
            for result_s in  self.skill_resultggbskills.filter(student=student,relationship__in = parcours.parcours_relationship.all()):
                score += result_s.point
                coef += 1

            for ce in  self.skill_correctionskill.filter(student=student,parcours=parcours) :
                score += ce.point 
                coef += 1

            if coef != 0:
                score = int(score/coef)
            else :
                score = ""                

        except ObjectDoesNotExist:
            score = ""


        data["score"] = score
        data["nombre"] = min(coef,total)
        data["total"] = total

        return data
 







 
 