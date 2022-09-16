from django.db import models
from django.utils import timezone
from django.apps import apps
from datetime import datetime , timedelta
from django.db.models import Q



def image_directory_path(instance, filename):
    return "schools/{}".format(filename)


class Country(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nom") 
 
    def __str__(self):
        return self.name


class School(models.Model):
    name        = models.CharField(max_length=255, verbose_name="nom")
    country     = models.ForeignKey(Country, default='', blank=True, related_name='school', related_query_name="school", on_delete=models.PROTECT, verbose_name="Pays")
    town        = models.CharField(max_length=255, default='', verbose_name="ville")
    code_acad   = models.CharField(max_length=255, default='999efe',   verbose_name="Code UAI ou RNE")
    address     = models.CharField(max_length=255, blank=True, verbose_name="Adresse")
    complement  = models.CharField(max_length=255, blank=True, verbose_name="Complément d'adresse")
    zip_code    = models.CharField(max_length=255, default='99999', blank=True, verbose_name="Code postal")
    nbstudents  = models.PositiveIntegerField(default=500, verbose_name="Nombre d'élèves")
    is_active   = models.BooleanField(default=0,   editable=False)
    logo        = models.ImageField(upload_to=image_directory_path, verbose_name="Logo de l'établissement", blank=True, default="")
    is_managing = models.BooleanField(default=1, verbose_name="Admin unique ?")

    def __str__(self):
        return "{} - {} ".format(self.name, self.town)

    def student_and_teacher(self):
        nbt, nbs = 0, 0
        for u in self.users.all():
            if u.is_teacher:
                nbt += 1
            elif u.is_student:
                nbs += 1
        nb = {"nbt": nbt, "nbs": nbs}
        return nb



    def admin(self):
        User = apps.get_model('account', 'User')

        users = User.objects.filter(school_id = self.pk, is_manager = 1)
        return users



    def get_data(self) :

        Group = apps.get_model('group', 'Group')
        nbg = Group.objects.filter(Q(teacher__user__school=self)|Q(teacher__user__schools=self)).count()
        try:
            stage = self.aptitude.first()
            if stage:
                eca, ac, dep , low , medium , up  = stage.medium - stage.low, stage.up - stage.medium, 100 - stage.up , stage.low , stage.medium , stage.up 
            else:
                eca, ac, dep , low , medium , up   = 20, 15, 15 , 50 , 70, 85 
        except:
            eca, ac, dep , low , medium , up  = 20, 15, 15 , 50 , 70, 85


        nbt, nbs = 0, 0
        for u in self.users.exclude(username__contains="_e-test"):
            if u.is_teacher:
                nbt += 1
            elif u.is_student:
                nbs += 1
        data_nb = {"nbt": nbt, "nbs": nbs}

        data_nb.update({"nbg": nbg , "low": low , "eca": eca, "ac": ac , "dep": dep, "medium": medium , "up": up  })
 
        return data_nb



    def fee(self):
        """ cotisation pour un établissement suivant le nombre de ses élèves"""
        try :
            Rate = apps.get_model('association', 'Rate')            
            rate = Rate.objects.filter( is_active  =  1, quantity__gte = self.nbstudents ).order_by("quantity").first()
            today = datetime.now()
            limit = datetime(today.year,6,30)
            f = rate.amount
            #if today < limit :
            #    f = rate.discount
        except :
            f = 350
        return f


    def adhesion(self) : 
        today = datetime.now()
        return self.abonnement.filter( date_start__lte=today , date_stop__gte=today ).count()


    def active_accounting(self) :
        today = datetime.now()
        try :
            abonnement  = self.abonnement.filter( date_start__lte = today , date_stop__gte = today ).last()
            account = abonnement.accounting
        except :
            account  = False
        return account



class Stage(models.Model):
    """" Niveau d'aquisition """
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='aptitude', editable=False)
    low = models.PositiveIntegerField(default=50, verbose_name="Seuil 1 : NA à ECA")
    medium = models.PositiveIntegerField(default=70, verbose_name="Seuil 2 : ACE à acquis")
    up = models.PositiveIntegerField(default=85, verbose_name="Seuil 3 : acquis à dépassé")

    def __str__(self):
        return "seuils d'aquisition {}".format(self.school.name)
