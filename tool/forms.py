import datetime
from django import forms
from .models import Tool , Question  , Choice  , Quizz , Diaporama , Slide , Qrandom ,Variable , Answerplayer, Videocopy, Positionnement
from account.models import Student , Teacher
from socle.models import Knowledge, Skill , Level
from group.models import Group
from bootstrap_datepicker_plus import DatePickerInput, DateTimePickerInput
from django.forms import MultiWidget, TextInput , CheckboxInput
from django.template.defaultfilters import filesizeformat
from django.conf import settings

from itertools import groupby
from django.forms.models import ModelChoiceIterator, ModelChoiceField, ModelMultipleChoiceField



def validation_file(content):
	if content :
		content_type = content.content_type.split('/')[0]
		if content_type in settings.CONTENT_TYPES:
			if content._size > settings.MAX_UPLOAD_SIZE:
				raise forms.ValidationError("Taille max : {}. Taille trop volumineuse {}".format(filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(content._size)))
		else:
			raise forms.ValidationError("Type de fichier non accepté")
		return content


class ToolForm(forms.ModelForm):

 
	class Meta:
		model = Tool
		fields = '__all__'

	def __init__(self, *args, **kwargs):
		super(ToolForm, self).__init__(*args, **kwargs)
		self.fields['levels'] = forms.ModelMultipleChoiceField(queryset=Level.objects.exclude(pk=13), required=False) 


class QuestionForm(forms.ModelForm):

	class Meta:
		model = Question
		fields = '__all__'
		widgets = {
            'is_correct' : CheckboxInput(),  
        }


	def __init__(self, *args, **kwargs):
		quizz = kwargs.pop('quizz')
		super(QuestionForm, self).__init__(*args, **kwargs)

		levels = quizz.levels.all()
		themes = quizz.themes.all()
		subject = quizz.subject
		knowledges = []
		if len(levels) > 0 and len(themes) > 0  :
			knowledges = Knowledge.objects.filter(theme__subject = subject ,level__in=levels, theme__in=themes )
		elif len(levels) > 0 :
			knowledges = Knowledge.objects.filter(theme__subject = subject ,level__in=levels)
		elif len(themes) > 0 :
			knowledges = Knowledge.objects.filter(theme__subject = subject ,theme__in=themes)
		self.fields['knowledge'] = forms.ModelChoiceField(queryset=knowledges, required=False)


	def clean_content(self):
		content = self.cleaned_data['imagefile']
		validation_file(content)  
		audio_ = self.cleaned_data['audio']
		validation_file(audio_) 
		video_ = self.cleaned_data['video']
		validation_file(video_) 



class QuestionPositionnementForm(forms.ModelForm):

	class Meta:
		model = Question
		fields = '__all__'
		widgets = {
            'is_correct' : CheckboxInput(),  
        }
 
	def __init__(self, *args, **kwargs):
		positionement = kwargs.pop('positionnement')
		super(QuestionPositionnementForm, self).__init__(*args, **kwargs)

		level = positionement.level
		subject = positionement.subject
		knowledges = []
			
		if subject and level :
			knowledges = Knowledge.objects.filter(theme__subject = subject ,level = level)
			self.fields['knowledge'] = forms.ModelChoiceField(queryset=knowledges, required=False)






class QuizzForm(forms.ModelForm):
 
	class Meta:
		model = Quizz
		fields = '__all__'

	def __init__(self, *args, **kwargs):
		teacher = kwargs.pop('teacher')
		folder  = kwargs.pop('folder')
		group   = kwargs.pop('group')

		super(QuizzForm, self).__init__(*args, **kwargs)
		

		if group : all_folders = group.group_folders.filter(is_archive=0,is_trash=0)
		else : all_folders = teacher.teacher_folders.filter(is_archive=0,is_trash=0) 

		if folder : parcours = folder.parcours.filter(is_archive=0,is_trash=0)
		else : parcours =  teacher.teacher_parcours.filter(is_archive=0,is_trash=0)

		coteacher_parcours = teacher.coteacher_parcours.filter(is_archive=0,is_trash=0) 
		all_parcours = parcours|coteacher_parcours

		groups =  teacher.groups.all() 
		teacher_groups = teacher.teacher_group.all() 
		all_groups = groups|teacher_groups

		self.fields['levels']   = forms.ModelMultipleChoiceField(queryset=teacher.levels.all(), required=False)
		self.fields['subject']  = forms.ModelChoiceField(queryset=teacher.subjects.all(), required=False)
		self.fields['groups']   = forms.ModelMultipleChoiceField(queryset=all_groups.order_by("teachers","level"), widget=forms.CheckboxSelectMultiple, required=True)
		self.fields['parcours'] = forms.ModelMultipleChoiceField(queryset = all_parcours.order_by("level"), widget=forms.CheckboxSelectMultiple,  required=False)
		self.fields['folders']  = forms.ModelMultipleChoiceField(queryset = all_folders.order_by("level"), widget=forms.CheckboxSelectMultiple,  required=False)
 


	def clean_content(self):
		content = self.cleaned_data['imagefile']
		validation_file(content) 





class PositionnementForm(forms.ModelForm):
 
	class Meta:
		model = Positionnement
		fields = '__all__'
	def __init__(self, *args, **kwargs):
		super(PositionnementForm, self).__init__(*args, **kwargs)
		self.fields['level']   = forms.ModelChoiceField( queryset=Level.objects.exclude(pk=13).order_by("ranking") , required=False)



class ChoiceForm(forms.ModelForm):
	class Meta:
		model = Choice
		fields = '__all__'
 

	def clean_content(self):
		content = self.cleaned_data['imagefile']
		validation_file(content) 





class DiaporamaForm(forms.ModelForm):
 
	class Meta:
		model = Diaporama
		fields = '__all__'

	def __init__(self, *args, **kwargs):
		teacher = kwargs.pop('teacher')
		super(DiaporamaForm, self).__init__(*args, **kwargs)
		groups = teacher.groups.order_by("level") | teacher.teacher_group.order_by("group__level")
 
		self.fields['levels'] = forms.ModelMultipleChoiceField(queryset=teacher.levels.all(), required=False)
		self.fields['subject'] = forms.ModelChoiceField(queryset=teacher.subjects.all(), required=False)
		self.fields['groups'] = forms.ModelMultipleChoiceField(queryset=teacher.groups.all(), required=False)
 

	def clean_content(self):
		content = self.cleaned_data['imagefile']
		validation_file(content) 
 

class SlideForm(forms.ModelForm):

	class Meta:
		model = Slide
		fields = '__all__'
 


 

class QrandomForm(forms.ModelForm):
 
	class Meta:
		model = Qrandom
		fields = '__all__'


	def clean_content(self):
		content = self.cleaned_data['imagefile']
		validation_file(content) 
 


class VariableForm(forms.ModelForm):

	class Meta:
		model = Variable
		fields = '__all__'



 

class AnswerplayerForm(forms.ModelForm):
 
	class Meta:
		model = Answerplayer
		fields = '__all__'




class VideocopyForm(forms.ModelForm):

 
	class Meta:
		model = Videocopy
		fields = '__all__'


	def clean_content(self):
		content = self.cleaned_data['image']
		validation_file(content)  