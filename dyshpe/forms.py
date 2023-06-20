import datetime
from django import forms
from .models import  Autotest
from account.models import Student , Teacher
from socle.models import Knowledge, Skill
from group.models import Group
from bootstrap_datepicker_plus import DatePickerInput, DateTimePickerInput

from django.template.defaultfilters import filesizeformat
from django.conf import settings

 
from general_fonctions import *



def validation_file(content):
    if content :
	    content_type = content.content_type.split('/')[0]
	    if content_type in settings.CONTENT_TYPES:
	        if content._size > settings.MAX_UPLOAD_SIZE:
	            raise forms.ValidationError("Taille max : {}. Taille trop volumineuse {}".format(filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(content._size)))
	    else:
	        raise forms.ValidationError("Type de fichier non accepté")
	    return content


 
class AutotestForm(forms.ModelForm):

	class Meta:
		model = Autotest
		fields = "__all__"
 

			 

	def clean(self):
		"""
		Vérifie que la fin de l'évaluation n'est pas avant son début
		"""
		cleaned_data = super().clean()
		start_date = cleaned_data.get("start")
		stop_date = cleaned_data.get("stop")
		try :
			if stop <= start:
				raise forms.ValidationError("La date ne peut pas être postérieure à son début.")
		except:
			pass

