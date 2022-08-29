from django import forms
from .models import Event,ConnexionEleve 
from account.models import User

class EventForm(forms.ModelForm):

	class Meta:
	    model = Event
	    exclude =  ('end',)
	    fields =  ('__all__')

	def __init__(self, user, *args, **kwargs):
		super(EventForm, self).__init__(*args, **kwargs)
		users = User.objects.filter(school=user.school, user_type=0 ).order_by("student__level__ranking")
		self.fields['users'] = forms.ModelMultipleChoiceField(queryset=users,required=False)

"""	def clean(self):
		cleaned_data=super().clean()
		sstart=cleaned_data.get("start")  #start de self
		send=cleaned_data.get('end')      # end de self

		if sstart>=send :
			raise ValidationError("La date de début est postérieure à la date de fin", code="datesinversees")
		        # verification : pas de conflit avec une autre visio du prof
		test1=Event.objects.filter(user=user,start__lte=sstart, end__gte=sstart)
		if len(test1)!=0 :
			raise ValidationError("Cette visio est en conflit avec la visio "+str(test1[0]), code="conflitVisios")
            
		test2=Event.objects.filter(user=user,start__gte=sstart, start__lte=send)
		if len(test2)!=0 :
			raise ValidationError("Cette visio est en conflit avec la visio "+str(test2[0]), code="conflitVisios")
"""
