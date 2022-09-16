from account.models import User  
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from datetime import datetime, time
from django.utils import formats, timezone

class Event(models.Model):

    user         = models.ForeignKey(User, null=True, blank = True, related_name='events' , on_delete=models.CASCADE )    
    title        = models.CharField(_('title'), max_length=100)
    date         = models.DateField(default=timezone.now,verbose_name=_('date'))
    start        = models.TimeField(verbose_name=_('start'))
    duration     = models.PositiveIntegerField(default =   60 , verbose_name=_('duration'))
    notification = models.BooleanField(_('Notification?'), default=False, blank=True) 
    comment      = models.TextField( null=True, blank=True, verbose_name="Commentaire")      
    display      = models.BooleanField(default=0, verbose_name='Publication' ) 
    users        = models.ManyToManyField(User, default='',  blank=True, related_name='these_events', related_query_name="these_events",   verbose_name="Partagée avec", through="ConnexionEleve")
    color        = models.CharField(_('color'), default='#5d4391', max_length=50)
    urlCreate    = models.CharField(_('urlCreate'), null=True,  blank=True,  max_length=1000)
    urlJoinProf  = models.CharField(_('urlJoinProg'), null=True,  blank=True,  max_length=250)
    urlIsMeetingRunning = models.CharField(_('urlRunning?'), null=True,  blank=True,  max_length=250)
    is_validate  = models.PositiveIntegerField(_('Validation?'), default=0 , editable=False) # 0 : demande élève , 1 : validation parent, 2 validation prof


    def __str__(self):
        return "Visio : prof={}, le {},  début = {}, durée = {}".format(self.user.last_name, self.date.strftime("%d %n"), self.start.strftime("de %Hh%M"), self.duration)   

    class Meta:
        verbose_name = _('event')



class ConnexionEleve(models.Model):
	event       = models.ForeignKey(Event, related_name='ConnexionEleves' ,on_delete=models.CASCADE)
	user        = models.ForeignKey(User, related_name='ConnexionEleves' , on_delete=models.CASCADE)
	urlJoinEleve= models.CharField(_('url'), null=True,  blank=True,  max_length=250)



class Slot(models.Model): # disponibilité des profs

    user        = models.ForeignKey(User, null=True, blank = True, related_name='slots' , on_delete=models.CASCADE )    
    datetime    = models.DateTimeField(default=timezone.now,verbose_name=_('date'))
    is_occupied = models.BooleanField(_('Notification?'), default=False, blank=True) 

    def __str__(self):
        return "Dispo : prof={}, le {},  début = {}, libre ? {}".format(self.user.last_name, self.date.strftime("%d %n"), self.is_occupied)   


 
def credit_directory_path(instance, filename):
    return "lesson/{}/{}/{}".format(user.id, instance.id, filename)

 
class Credit(models.Model):
    """ Accounting   """

    amount      = models.DecimalField(default=0, blank=True , max_digits=10, decimal_places=2, editable=False)# montant payé
    effective   = models.DecimalField(default=0, blank=True , max_digits=10, decimal_places=2, editable=False)# crédit attribué
    observation = models.TextField( blank=True, default="", null=True, verbose_name="Observation")
    date        = models.DateTimeField(auto_now_add=True) # date de création de la facture
    user        = models.ForeignKey(User, related_name="credits", null=True, blank=True,  on_delete=models.CASCADE, editable=False)
    facture     = models.FileField(upload_to=credit_directory_path, blank=True, verbose_name="Facture",  default="" )
    chrono      = models.CharField(max_length=50, blank=True, unique =True,  editable=False)


    def __str__(self):
        return self.user