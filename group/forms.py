from django import forms
from .models import Group 



class GroupForm(forms.ModelForm):
    class Meta:
        model = Group 
        fields = ('name','color','level','assign','suiviparent','lock','subject','studentprofile','formule_id' ) 




class GroupTeacherForm(forms.ModelForm):
	class Meta:
		model = Group 
		fields = ('name','color','level','assign','suiviparent','lock','subject','studentprofile','recuperation','formule_id') 


	def __init__(self, *args, **kwargs):
		teacher = kwargs.pop('teacher')
		super(GroupTeacherForm, self).__init__(*args, **kwargs)
		if teacher:
			
			subjects = teacher.subjects.all()
			levels = teacher.levels.all()
			self.fields['subject']	 = forms.ModelChoiceField(queryset=subjects,  required=True)    
			self.fields['level']	 = forms.ModelChoiceField(queryset=levels,  required=True)         
      