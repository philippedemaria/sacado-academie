from django.db import models
from group.models import Group
from socle.models import Subject , Level

# Create your models here.

class Holidaybook(models.Model):

    title = models.CharField(max_length=255, blank=True,  default="", null=True,  verbose_name="Titre")
 
    level   = models.ForeignKey(Level, related_name="holidaybooks", on_delete=models.CASCADE, verbose_name="Niveau")
    subject = models.ForeignKey(Subject, related_name="holidaybooks", on_delete=models.CASCADE, verbose_name="Matière")
    group   = models.OneToOneField(Group, related_name="holidaybook", blank=True,  default="", null=True,  on_delete=models.CASCADE, verbose_name="Groupe")

    is_publish = models.BooleanField(default=1, verbose_name="Visible ?")
    price      = models.PositiveIntegerField(  default=5	,  blank=True )


    vignette   = models.ImageField(  default=""	,  blank=True )

    def __str__(self):      
        return "Cahier Vacances > {}".format(self.level.shortname)



    def level_next(self):

        lvs = ["CE1","CE2","CM1","CM2","6è","5è","4è","3è","2de","1è","T",0,0,"CP"]

        return lvs[self.level.id-1]