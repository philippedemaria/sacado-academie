from account.models import User  
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from datetime import datetime, time

 
class Event(models.Model):

    user = models.ForeignKey(User, null=True, blank = True, related_name='events' , on_delete=models.CASCADE, editable=False)    
    title = models.CharField(_('title'), max_length=100)
    start = models.DateTimeField(_('start'))
    end = models.DateTimeField(_('end'))
    notification = models.BooleanField(_('Notification?'), default=False, blank=True) 
    comment =  models.TextField( null=True, blank=True, verbose_name="Commentaire")      
    display = models.BooleanField(default=0, verbose_name='Publication' ) 
    users = models.ManyToManyField(User, default='',  blank=True, related_name='these_events', 
       related_query_name="these_events",   verbose_name="Partagée avec", through="ConnexionEleve")
    color = models.CharField(_('color'), default='#00819F', max_length=50)
    urlCreate = models.CharField(_('urlCreate'), null=True,  blank=True,  max_length=1000)
    urlJoinProf = models.CharField(_('urlJoinProg'), null=True,  blank=True,  max_length=250)
    urlIsMeetingRunning = models.CharField(_('urlRunning?'), null=True,  blank=True,  max_length=250)
    
    def __str__(self):
        return "Visio : prof={}, debut={}, fin={}".format(self.user.last_name, self.start.strftime("%d/%m à %Hh%M"),
                    self.end.strftime("%d/%m à %Hh%M"))   

    class Meta:
        verbose_name = _('event')
        ordering = ['start', 'end']



class ConnexionEleve(models.Model):
	event=models.ForeignKey(Event, on_delete=models.CASCADE)
	user=models.ForeignKey(User, on_delete=models.CASCADE)
	urlJoinEleve=models.CharField(_('url'), null=True,  blank=True,  max_length=250)



