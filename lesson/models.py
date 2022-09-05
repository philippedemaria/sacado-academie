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
    
    def __str__(self):
        return "Visio : prof={}, le {},  début = {}, durée = {}".format(self.user.last_name, self.date.strftime("%d %n"), self.start.strftime("de %Hh%M"), self.duration)   

    class Meta:
        verbose_name = _('event')



class ConnexionEleve(models.Model):
	event=models.ForeignKey(Event, on_delete=models.CASCADE)
	user=models.ForeignKey(User, on_delete=models.CASCADE)
	urlJoinEleve=models.CharField(_('url'), null=True,  blank=True,  max_length=250)



class Slot(models.Model): # disponibilité des profs

    user        = models.ForeignKey(User, null=True, blank = True, related_name='slots' , on_delete=models.CASCADE )    
    datetime    = models.DateTimeField(default=timezone.now,verbose_name=_('date'))
    is_occupied = models.BooleanField(_('Notification?'), default=False, blank=True) 
    is_oupied = models.BooleanField(_('Notification?'), default=False, blank=True) 

    def __str__(self):
        return "Dispo : prof={}, le {},  début = {}, libre ? {}".format(self.user.last_name, self.date.strftime("%d %n"), self.is_occupied)   
 