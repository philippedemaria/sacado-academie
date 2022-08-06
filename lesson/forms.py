from django import forms
from .models import Event  
from account.models import User

class EventForm(forms.ModelForm):

	class Meta:
	    model = Event
	    exclude =  ('end',)
	    fields =  ('__all__')

	def __init__(self, user, *args, **kwargs):
		super(EventForm, self).__init__(*args, **kwargs)
		students = user.teacher.students.order_by("level__ranking")
		self.fields['users'] = forms.ModelMultipleChoiceField(queryset=students,required=False)

 