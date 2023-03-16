from django.db import models
from datetime import date
from account.models import Student, Teacher, ModelWithCode, generate_code
from school.models import School
from socle.models import Level, Subject , Waiting , Vignette 
from django.apps import apps
from django.utils import timezone
from django.db.models import Q
# Pour créer un superuser, il faut depuis le shell taper :
# from account.models import User
# User.objects.create_superuser("admin","admin@gmail.com","motdepasse", user_type=0).save()

 
class Group(ModelWithCode):

    FORMULES = (
        (1, "Autonomie"),
        (2, "Suivi"),
        (3, "Prép'Exam"),
        (4, "Prep'Classe"), 
    )


    """ Group est une classe d'élèves coté enseignant -- Ce qui permet de faire un groupe avec une ou plusieurs divisions """
    name           = models.CharField(max_length=255, verbose_name="Nom*")
    color          = models.CharField(max_length=255, default='#46119c', blank=True, null=True, verbose_name="Couleur*")
    students       = models.ManyToManyField(Student, related_name="students_to_group", blank=True, verbose_name="Élèves*")
    teacher        = models.ForeignKey(Teacher, blank=True, null=True, on_delete=models.CASCADE, related_name="groups", verbose_name="Enseignant*")
    level          = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="groups", verbose_name="Niveau*")
    assign         = models.BooleanField(default=1)
    suiviparent    = models.BooleanField(default=0)
    studentprofile = models.BooleanField(default=1)
    lock           = models.BooleanField(default=0)
    recuperation   = models.BooleanField(default=0)
    teachers       = models.ManyToManyField(Teacher, blank=True,   editable=False, through="Sharing_group", related_name="teacher_group")
    subject        = models.ForeignKey(Subject, default = "" ,  null=True, on_delete=models.CASCADE, related_name="subject_group", verbose_name="Matière*")
    school         = models.ForeignKey(School, default = "" ,  editable=False, blank=True,  null=True, on_delete=models.CASCADE, related_name="school_group" )
    formule_id     = models.PositiveSmallIntegerField( default = 1 , choices=FORMULES)



    class Meta:
        ordering = ['name']

    def __str__(self):
        nb = self.students.exclude(user__username__contains= "_e-test").count()
        eleve ="élève"
        if nb > 1 :
            eleve ="élèves"
            if self.teachers.count() > 0 :
                return "[CoA] : {} [{} {}]".format(self.name, nb , eleve)
            else :
                return "{} [{} {}]".format(self.name, nb , eleve)
        else :
            return "{} [{} {}]".format(self.name, nb , eleve)

    def contrastColorText(self):
        """ donne le noir ou blanc selon la couleur initiale  """
        color1 = self.color[1:3]
        color2 = self.color[3:5]
        color3 = self.color[5:7]
        if 0.299 * int(color1, 16) + 0.587 * int(color2, 16) + 0.114 * int(color3, 16) > 150:
            return "#000000"
        else:
            return "#FFFFFF"

    def nb_exos_in(self):
        Exercise = apps.get_model('qcm', 'Exercise')
        nb = Exercise.objects.filter(level=self.level).count()
        return nb


    def all_selected_exercices(self):
        Exercise = apps.get_model('qcm', 'Exercise')
        nb_group = self.parcours.exercises.count()
        nb = Exercise.objects.filter(level=self.level).count()
        return nb_group == nb


    def is_task_exists(self):
        Relationship = apps.get_model('qcm', 'Relationship')
        today = timezone.now() 
        test = False
        students = self.students.prefetch_related("students_relationship")
        for student in students:
            if student.students_relationship.filter(date_limit__gte=today).count() > 0:
                test = True
                break
        return test

    def level_themes(self) :
        return self.level.themes.filter(subject=self.subject)


    def just_students(self):
        return self.students.exclude(user__username__contains="_e-test").order_by("user__last_name")


    def just_students_count(self):
        return self.students.exclude(user__username__contains="_e-test").count()


    def data_image(self):

        image = self.subjet.subject_vignettesubject.values_list("vignette__imagefile").filter(level=self.level).first()

        return image



    def parcours_counter(self,teacher):
        """
        Donne le nombre total de parcours/évaluations, le nombre de visibles et de publiés du groupe
        """
        students = self.students.all()
        studnts = students.exclude(user__username__contains= "_e-test") 
        snt = studnts.count()
        profil = students.filter(user__username__contains= "_e-test").count()
        profilTest = False
        if profil > 0 : 
            profilTest = True

        my_students = [s for s in teacher.students.all() if s in studnts ]

        print(my_students)
            
 
        parcourses = self.group_parcours.filter(Q(teacher=teacher)|Q(author=teacher)|Q(coteachers = teacher), subject = self.subject, level = self.level ,  folders=None, is_favorite=1,  is_archive=0, is_trash=0) 
        folders    = self.group_folders.filter(Q(teacher=teacher)|Q(author=teacher)|Q(coteachers=teacher), subject = self.subject, level = self.level ,  is_favorite=1,  is_archive=0,  is_trash=0) 
 
        nb_folders = folders.count()
        nb_folders_published = folders.filter(is_publish=1).count()

        data, nb, nbf, nbp, nbef , nbe = {}, 0, 0, 0, 0, 0
        for parcours in parcourses :
            if parcours.is_favorite and not parcours.is_evaluation :
                nbf += 1
            if parcours.is_publish and not parcours.is_evaluation :
                nbp += 1
            if parcours.is_evaluation:
                nbe  += 1
            if not parcours.is_evaluation:
                nb += 1
            if parcours.is_evaluation and parcours.is_favorite :
                nbef += 1


        data["my_students"] = my_students
        data["count_students"] = snt
        data["students"] = students.values("user__id", "user__last_name", "user__first_name").exclude(user__username__contains= "_e-test").order_by("user__last_name") 
        data["nb_parcours"] = nb
        data["nb_parcours_visible"] = nbp
        data["nb_parcours_favorite"] = nbf
        data["nb_evaluation_favorite"] = nbef 
        data["nb_evaluation"] = nbe
        data["students_no_test"] = snt
        data["profiltest"] = profilTest  
        data["nb_folders"] = nb_folders 
        data["nb_folders_published"] = nb_folders_published
        data["nb_documents"] = nb_folders + nbe + nb_folders + nb

        return data



    


    def folders_published(self):
        data = {}
        folders = self.group_folders.filter(is_publish = 1, subject = self.subject, level=self.level, is_trash=0)
        nb_folders_published = folders.count()
        data["folders"] = folders 
        data["nb_folders_published"] = nb_folders_published  
        return data

    def parcours_visible(self):
        parcours = self.parcours.filter(is_publish = 1, subject = self.subject, level=self.level, is_trash=0 , folders= None)
        return parcours



    def themes(self):
        data = {}
        folders = self.group_folders.filter(is_publish = 1, subject = self.subject, level=self.level, is_trash=0)
        nb_folders_published = folders.count()
        data["folders"] = folders 
        data["nb_folders_published"] = nb_folders_published 
        parcours = self.group_parcours.filter(subject = self.subject, level=self.level, is_trash=0, is_publish=1 , folders= None)
        nb_parcours_published = parcours.count()
        data["parcours"] = parcours 
        data["nb_parcours_published"] = nb_parcours_published 

        data["nb"] = nb_parcours_published + nb_folders_published

        return data



    def sharing_role(self,teacher):
        """
        Renvoie le role d'un enseignant pour un groupe donné
        """
        data = {}
        reader , publisher = False , False
        if self.group_sharingteacher.filter(teacher=teacher).exists() :
            shared_grps = Sharing_group.objects.get(group = self , teacher=teacher)
            if shared_grps.role == 0 :
                reader = True
            else :
                publisher = True

        data["publisher"] = publisher
        data["reader"] = reader 
        return data


    def is_pending_correction(self):
        """
        Prédicat pour tester s'il existe des corrections en attente
        """

        submit = False

        for student in self.students.all() :
            if student.student_custom_answer.filter(is_corrected = 0, parcours__subject= self.subject) :
                submit = True 
                break
            if student.student_written_answer.filter(is_corrected = 0, relationship__parcours__subject= self.subject) :
                submit = True 
                break
        return submit

 
    def is_shared(self):
        """
        Prédicat pour tester si le groupe est en co animation
        """
        is_shared = False
        if len(self.group_sharingteacher.all()) > 0 :
            is_shared = True

        return is_shared



    def waitings(self):
        return Waiting.objects.filter(level = self.level, theme__subject = self.subject)
    

 
    def authorize_access(self, teacher): 
        """
        Authorise l'acces de ce groupe à un enseignant
        """
        access, role = False, False
        if teacher.teacher_sharingteacher.filter(group = self).count() > 0 :
            access = True
        if self.teacher == teacher or access :
            access = True 
        if access and teacher.teacher_sharingteacher.filter(group = self).exists():
            sg = teacher.teacher_sharingteacher.filter(group = self).last()
            role = sg.role

        data = {}
        data["role"] = role
        data["access"] = access

        return data


def vignette(self):

    try :
        url = Vignette.objects.values("imagefile").get(level=self.level, subject=self.subject)
        is_exists = True
    except :
        url = False 
        is_exists = False

    data = {}
    data["is_exists"] = is_exists
    data["url"] = url
    return data



class Sharing_group(models.Model):

    group = models.ForeignKey(Group, on_delete=models.CASCADE,  null=True, blank=True,   related_name='group_sharingteacher',  editable= False)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True,  related_name='teacher_sharingteacher',  editable= False)
    role = models.BooleanField(default=0)
 
    

    def __str__(self):
        return "{} : {} : {}".format(self.group, self.teacher, self.role)
 
    

