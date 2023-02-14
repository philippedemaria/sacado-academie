import datetime
from django import forms
from .models import  *
from account.models import Student , Teacher
from socle.models import Knowledge, Skill , Level
from group.models import Group
from bootstrap_datepicker_plus import DatePickerInput, DateTimePickerInput
from django.forms import MultiWidget, TextInput , CheckboxInput
from django.template.defaultfilters import filesizeformat
from django.conf import settings

from itertools import groupby
from django.forms.models import inlineformset_factory, BaseInlineFormSet , ModelChoiceIterator, ModelChoiceField, ModelMultipleChoiceField


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

		level_id = int(positionement.level.id)
		if 1<level_id < 13 :
			level_id = level_id - 1
			level    = Level.objects.get(pk=level_id)
		elif level_id == 1 : level    = Level.objects.get(pk=1)
		elif level_id == 14 : level    = Level.objects.get(pk=14)


		subject = positionement.subject
		knowledges = []
			
		if subject and level :
			knowledges = Knowledge.objects.filter(theme__subject = subject ,level = level)
			self.fields['knowledge'] = forms.ModelChoiceField(queryset=knowledges, required=False)


#################################################################################################################################################################################
###################################        FORMULAIRES GROUPES ET SOUS FORMULAIRES       ########################################################################################
#################################################################################################################################################################################
def is_empty_form(form):
    if form.is_valid() and not form.cleaned_data:
        return True
    else:
        return False


def is_form_persisted(form):
    if form.instance and not form.instance._state.adding:
        return True
    else:
        return False

class BaseSupportchoiceFormset(BaseInlineFormSet):

    def add_fields(self, form, index):
        super().add_fields(form, index)
        # save the formset in the 'nested' property
        form.nested = formSubSet(
                        instance=form.instance,
                        data=form.data if form.is_bound else None,
                        files=form.files if form.is_bound else None,
                        prefix='choice-{}-subchoice'.format( form.prefix ) )

    def is_valid(self):
        result = super(BaseSupportchoiceFormset, self).is_valid()
        if self.is_bound:
            for form in self.forms:
                if hasattr(form, 'nested'):
                    result = result and form.nested.is_valid()
        return result

    def clean(self):
        super(BaseSupportchoiceFormset, self).clean()
        for form in self.forms:
            if not hasattr(form, "nested") or self._should_delete_form(form):
                continue

            if self._is_adding_nested_inlines_to_empty_form(form):
                form.add_error(
                    field=None,
                    error=_(
                        "You are trying to add image(s) to a book which "
                        "does not yet exist. Please add information "
                        "about the book and choose the image file(s) again."
                    ),
                )

    def save(self, commit=True):
        result = super(BaseSupportchoiceFormset, self).save(commit=commit)
        for form in self.forms:
            if hasattr(form, 'nested'):
                if not self._should_delete_form(form):
                    form.nested.save(commit=commit)
        return result


    def _is_adding_nested_inlines_to_empty_form(self, form):
        if not hasattr(form, "nested"):
            return False

        if is_form_persisted(form):
            return False

        if not is_empty_form(form):
            return False

        non_deleted_forms = set(form.nested.forms).difference(set(form.nested.deleted_forms))

        return any(not is_empty_form(nested_form) for nested_form in non_deleted_forms)


formSetNested = inlineformset_factory(Question, Choice, fields=('answer','imageanswer','answerbis','imageanswerbis','is_correct','retroaction','xmin','xmax','tick','subtick','precision','is_written') , formset=BaseSupportchoiceFormset,   extra=1)
formSubSet    = inlineformset_factory(Choice, Subchoice, fields=('answer','imageanswer','label','is_correct','retroaction') , extra=2)

class BaseSupportchoiceUpdateFormset(BaseInlineFormSet):

    def add_fields(self, form, index):
        super().add_fields(form, index)
        # save the formset in the 'nested' property
        form.nested = formSubSetUpdate(
                        instance=form.instance,
                        data=form.data if form.is_bound else None,
                        files=form.files if form.is_bound else None,
                        prefix='choice-{}-subchoice'.format( form.prefix ) )

    def is_valid(self):
        result = super().is_valid()
        if self.is_bound:
            for form in self.forms:
                if hasattr(form, 'nested'):
                    result = result and form.nested.is_valid()
        return result


    def save(self, commit=True):
        result = super().save(commit=commit)
        for form in self.forms:
            if hasattr(form, 'nested'):
                if not self._should_delete_form(form):
                    form.nested.save(commit=commit)

        return result


formSetUpdateNested = inlineformset_factory(Question, Choice, fields=('answer','imageanswer','answerbis','imageanswerbis','is_correct','retroaction','xmin','xmax','tick','subtick','precision','is_written')  , formset=BaseSupportchoiceUpdateFormset,   extra=0)
formSubSetUpdate    = inlineformset_factory(Choice, Subchoice, fields=('answer','imageanswer','label','is_correct','retroaction') , extra=0)
#################################################################################################################################################################################
###################################    UPDATE FORMULAIRES GROUPES ET SOUS FORMULAIRES       #####################################################################################
#################################################################################################################################################################################



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