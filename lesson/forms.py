from django import forms
from .models import Event,ConnexionEleve , Slot, Credit
from account.models import User
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError

def get_hours():
    return ["{:02d}:{:02d}".format(i//60,i%60) for i in range(8*60,20*60,15)]
 

 
CHOICES = [( datetime.strptime(e , "%H:%M").time() ,e) for e in get_hours()]
 


class EventForm(forms.ModelForm):

	class Meta:
	    model = Event
	    fields =  (  'user', 'title', 'date', 'start', 'duration', 'comment', 'color','users')	    


	def __init__(self, user, *args, **kwargs):
		super(EventForm, self).__init__(*args, **kwargs)
		students = user.teacher.students.order_by("level__ranking")
		self.fields['users'] = forms.ModelMultipleChoiceField(queryset=students,required=False)
		self.fields['start'] = forms.ChoiceField(choices = CHOICES)

    
	def clean(self):
		cleaned_data=super().clean()
		user      = cleaned_data.get("user") 
		sdate     =   cleaned_data.get("date")#start de self
		sstart    = cleaned_data.get("start")  #start de self
		sduration = cleaned_data.get('duration')  # end de self
		sstart    =  datetime.strptime( sstart  , "%H:%M:%S").time()
		# verification : pas de conflit avec une autre visio du prof
		events = Event.objects.filter(user=user, date=sdate ,start__lte=sstart)
		for e in events :
			event_date   = e.date
			event_start  = datetime.combine(event_date, e.start )
			event_sstart = datetime.combine(event_date, sstart )
			event_end    = event_start + timedelta(minutes=e.duration)

			if event_end >= event_sstart :
				raise ValidationError("Cette visio est en conflit avec la visio "+str(e), code="conflitVisios")
         
		# verification : pas de conflit avec une autre visio du prof
		event_s = Event.objects.filter(user=user, date=sdate ,start__gte=sstart)
		for e in event_s :
			event_date   = e.date
			event_start  = datetime.combine(event_date, e.start )
			event_sstart = datetime.combine(event_date, sstart )
			event_end    = event_start + timedelta(minutes=e.duration)
			if event_sstart  <= event_end :
				raise ValidationError("Cette visio est en conflit avec la visio "+str(e), code="conflitVisios")


 


class GetEventForm(forms.ModelForm):

	class Meta:
	    model = Event
	    fields =  ( 'date', 'start', 'duration', 'comment')	    

	def clean(self):
		cleaned_data=super().clean()
		user      = cleaned_data.get("user") 
		sdate     = cleaned_data.get("date")#start de self
		sstart    = cleaned_data.get("start")  #start de self
		sduration = cleaned_data.get('duration')  # end de self
		if sstart :
			# verification : pas de conflit avec une autre visio du prof
			events = Event.objects.filter(user=user, date=sdate ,start__lte=sstart)
			for e in events :
				event_date   = e.date
				event_start  = datetime.combine(event_date, e.start )
				event_sstart = datetime.combine(event_date, sstart )
				event_end    = event_start + timedelta(minutes=e.duration)

				if event_end >= event_sstart :
					raise ValidationError("Cette visio est en conflit avec la visio "+str(e), code="conflitVisios")
	         
			# verification : pas de conflit avec une autre visio du prof
			event_s = Event.objects.filter(user=user, date=sdate ,start__gte=sstart)
			for e in event_s :
				event_date   = e.date
				event_start  = datetime.combine(event_date, e.start )
				event_sstart = datetime.combine(event_date, sstart )
				event_end    = event_start + timedelta(minutes=e.duration)
				if event_sstart  <= event_end :
					raise ValidationError("Cette visio est en conflit avec la visio "+str(e), code="conflitVisios")


 



class SlotForm(forms.ModelForm):

	class Meta:
	    model = Slot
	    fields =  ( 'user', 'datetime')	    


	def __init__(self, user, *args, **kwargs):
		super(SlotForm, self).__init__(*args, **kwargs)



class CreditForm(forms.ModelForm):

	class Meta:
	    model = Credit
	    fields =  "__all__"  


 


 


