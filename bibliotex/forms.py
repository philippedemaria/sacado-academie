from django import forms
from .models import Exotex , Bibliotex , Relationtex 
from socle.models import Knowledge , Skill


class ExotexForm(forms.ModelForm):
	class Meta:
		model = Exotex 
		fields = '__all__'

	def __init__(self, *args, **kwargs):
		teacher = kwargs.pop('teacher')
		knowledge = kwargs.pop('knowledge')

		super(ExotexForm, self).__init__(*args, **kwargs)
		if teacher:
			subjects = teacher.subjects.all()
			levels   = teacher.levels.all()
			if knowledge :
				skills     = knowledge.theme.subject.skill.all()
				knowledges = Knowledge.objects.filter(level = knowledge.level )
			else :
				skills     = Skill.objects.all()
				knowledges = Knowledge.objects.all()
			self.fields['subject']	  = forms.ModelChoiceField(queryset=subjects,  required=True) 
			self.fields['level']	  = forms.ModelChoiceField(queryset=levels,  required=True)         
			self.fields['skills']	  = forms.ModelMultipleChoiceField(queryset=skills,  required=True)   
			self.fields['knowledges'] = forms.ModelMultipleChoiceField(queryset=knowledges,  required=True)  
			self.fields['knowledges'].required = False 


class BibliotexForm(forms.ModelForm):
	class Meta:
		model = Bibliotex 
		fields = '__all__'

	def __init__(self, *args, **kwargs):
		teacher = kwargs.pop('teacher')
		folder  = kwargs.pop('folder')
		group   = kwargs.pop('group')
		super(BibliotexForm, self).__init__(*args, **kwargs)
		levels = teacher.levels.all()     
 
		

		if group : all_folders = group.group_folders.filter(is_archive=0,is_trash=0)
		else : all_folders = teacher.teacher_folders.filter(is_archive=0,is_trash=0) 

		if folder : parcours = folder.parcours.filter(is_archive=0,is_trash=0)
		else : parcours =  teacher.teacher_parcours.filter(is_archive=0,is_trash=0)

		coteacher_parcours = teacher.coteacher_parcours.filter(is_archive=0,is_trash=0) 
		all_parcours = parcours|coteacher_parcours

		groups =  teacher.groups.all() 
		teacher_groups = teacher.teacher_group.all() 
		all_groups = groups|teacher_groups

		self.fields['groups']   = forms.ModelMultipleChoiceField(queryset=all_groups.order_by("teachers","level"), widget=forms.CheckboxSelectMultiple, required=True)
		self.fields['parcours'] = forms.ModelMultipleChoiceField(queryset = all_parcours.order_by("level"), widget=forms.CheckboxSelectMultiple,  required=False)
		self.fields['folders']  = forms.ModelMultipleChoiceField(queryset = all_folders.order_by("level"), widget=forms.CheckboxSelectMultiple,  required=False)

 



class RelationtexForm(forms.ModelForm):
	class Meta:
		model = Relationtex 
		fields = ('content','calculator','duration','skills','knowledges','is_python','is_scratch','is_tableur','start','stop','correction','is_publish_cor','point')

	def __init__(self, *args, **kwargs):
		teacher = kwargs.pop('teacher')
 
		super(RelationtexForm, self).__init__(*args, **kwargs)
		if teacher:
			subjects = teacher.subjects.all()
			levels   = teacher.levels.all()
 
			skills = Skill.objects.filter(subject__in=subjects)
			knowledges = Knowledge.objects.filter(theme__subject__in=subjects,level__in=levels )   
			self.fields['skills']	  = forms.ModelMultipleChoiceField(queryset=skills,  required=True)   
			self.fields['knowledges'] = forms.ModelMultipleChoiceField(queryset=knowledges,  required=False) 


 