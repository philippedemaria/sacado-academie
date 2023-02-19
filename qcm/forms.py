import datetime
from django import forms
from django.conf import settings 
from django.template.defaultfilters import filesizeformat
from django.forms.models import inlineformset_factory, BaseInlineFormSet , ModelChoiceIterator, ModelChoiceField, ModelMultipleChoiceField


from .models import  *
from account.models import Student , Teacher
from group.models import Group
from socle.models import Knowledge, Skill


from bootstrap_datepicker_plus import DatePickerInput, DateTimePickerInput
from itertools import groupby
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


 
class ParcoursForm(forms.ModelForm):

	class Meta:
		model = Parcours
		exclude = ("exercises" , "students")

	def __init__(self, *args, **kwargs):
		teacher = kwargs.pop('teacher')
		folder  = kwargs.pop('folder')
		group   = kwargs.pop('group')
		super(ParcoursForm, self).__init__(*args, **kwargs)
		self.fields['stop'].required = False

		if teacher:

			try : 
				#shared_groups = teacher.teacher_group.filter(group_folders=folder, level = group.level, subject = group.subject)
				shared_groups = teacher.teacher_group.filter(group_folders=folder, level = group.level,is_hidden=0)
			except :
				shared_groups = teacher.teacher_group.filter(is_hidden=0)
			
			if folder and group :
				all_folders = group.group_folders.filter(level = group.level, subject = group.subject,is_trash=0)				
				groups      = folder.groups.filter(level=folder.level,group_folders=folder,is_hidden=0)
 
			elif folder :

				all_folders = teacher.teacher_folders.filter(level = folder.level, subject = folder.subject,is_trash=0)				
				groups      = folder.groups.filter(level=folder.level,group_folders=folder,is_hidden=0)

			elif group :
				all_folders = group.group_folders.filter(level = group.level, subject = group.subject,is_trash=0)		
				groups      = teacher.groups.filter(level=group.level,is_hidden=0 )

			else :
				all_folders = teacher.teacher_folders.filter(is_trash=0)	
				groups      = teacher.groups.filter(is_hidden=0 )


			these_groups  = groups|shared_groups
			all_groups    = these_groups.order_by("teachers").distinct()

			self.fields['groups']  = forms.ModelMultipleChoiceField(queryset=all_groups.order_by("level","name"), widget=forms.CheckboxSelectMultiple,  required=False)
			self.fields['subject'] = forms.ModelChoiceField(queryset=teacher.subjects.all(),  required=False)
			self.fields['level']   = forms.ModelChoiceField(queryset=teacher.levels.exclude(pk=13).order_by("ranking"),  required=False)
			self.fields['folders'] = forms.ModelMultipleChoiceField(queryset=all_folders.order_by("level","title"), widget=forms.CheckboxSelectMultiple,  required=False)

	def clean(self):
		"""
		Vérifie que la fin de l'évaluation n'est pas avant son début
		"""
		cleaned_data = super().clean()
		start_date = cleaned_data.get("start")
		stop_date = cleaned_data.get("stop")
		try :
			if stop <= start:
				raise forms.ValidationError("La date de verrouillage ne peut pas être antérieure à son début.")
		except:
			pass

class Parcours_GroupForm(forms.ModelForm):

	class Meta:
		model = Parcours
		fields = ('groups',)


	def __init__(self, *args, **kwargs):
		teacher = kwargs.pop('teacher')
		super(Parcours_GroupForm, self).__init__(*args, **kwargs)
 
		if teacher:
			groups        = teacher.groups.filter(is_hidden=0 )
			shared_groups = teacher.teacher_group.filter(is_hidden=0)
			these_groups  = groups|shared_groups
			all_groups    = these_groups.order_by("teachers")
			self.fields['groups']	     = forms.ModelMultipleChoiceField(queryset=all_groups, widget=forms.CheckboxSelectMultiple, required=False)
 
class FolderForm(forms.ModelForm):

	class Meta:
		model = Folder
		fields = '__all__'

	def __init__(self, *args, **kwargs):
		teacher = kwargs.pop('teacher')
		level   = kwargs.pop('level')
		subject = kwargs.pop('subject')
		super(FolderForm, self).__init__(*args, **kwargs)
		self.fields['stop'].required = False
		if teacher and level and subject:
			groups        = teacher.groups.filter(level = level , subject = subject,is_hidden=0)
			shared_groups = teacher.teacher_group.filter(level = level , subject = subject,is_hidden=0 )
			these_groups  = groups|shared_groups
			all_groups    = these_groups.order_by("teacher")
		else :
			groups        = teacher.groups.filter( is_hidden=0 ) 
			shared_groups = teacher.teacher_group.filter( is_hidden=0 )
			these_groups  = groups|shared_groups
			all_groups    = these_groups.order_by("teacher")
		

		coteachers    = Teacher.objects.filter(user__school=teacher.user.school).order_by("user__last_name")

		self.fields['groups']	  = forms.ModelMultipleChoiceField(queryset=all_groups, widget=forms.CheckboxSelectMultiple, required=False)
		self.fields['coteachers'] = forms.ModelMultipleChoiceField(queryset=coteachers,  required=False)
		

		self.fields['level']    = forms.ModelChoiceField(queryset=teacher.levels.exclude(pk=13).order_by("ranking"),  required=False)
		self.fields['subject']  = forms.ModelChoiceField(queryset=teacher.subjects.filter(is_active=1),  required=False)
		if subject and level :
			parcours                = teacher.teacher_parcours.filter(subject=subject,level=level,is_trash=0,is_archive=0).order_by("title")
			self.fields['parcours'] = forms.ModelMultipleChoiceField(queryset=parcours, widget=forms.CheckboxSelectMultiple, required=False)

		else :
			parcours                = teacher.teacher_parcours.filter(is_trash=0,is_archive=0).order_by("title")
			self.fields['parcours'] = forms.ModelMultipleChoiceField(queryset=parcours, widget=forms.CheckboxSelectMultiple, required=False)
 
			
	def clean(self):
 
		cleaned_data = super().clean()
		start_date = cleaned_data.get("start")
		stop_date = cleaned_data.get("stop")
		try :
			if stop <= start:
				raise forms.ValidationError("La date de verrouillage ne peut pas être antérieure à son début.")
		except:
			pass

class AudioForm(forms.ModelForm):
	class Meta:
		model = Exercise
		fields = ('audiofile',)

	def clean_content(self):
		audiofile = self.cleaned_data['audiofile']
		validation_file(audiofile)

class RelationshipForm(forms.ModelForm):
	class Meta:
		model = Relationship
		fields = '__all__'
		exclude = ('exercise', 'parcours', 'order', 'skill')

class RemediationForm(forms.ModelForm):
	class Meta:
		model = Remediation
		fields = '__all__'

	def __init__(self, *args, **kwargs):
		teacher = kwargs.pop('teacher')
		super(RemediationForm, self).__init__(*args, **kwargs)
		if teacher:
			courses = teacher.course.order_by("parcours","ranking")			
			self.fields['courses']= forms.ModelMultipleChoiceField(queryset=courses, widget=forms.CheckboxSelectMultiple,  required=False)

	def clean_content(self):
		content = self.cleaned_data['mediation']
		validation_file(content)

class RemediationcustomForm(forms.ModelForm):
	class Meta:
		model = Remediationcustom
		fields = '__all__'

	def __init__(self, *args, **kwargs):
		teacher = kwargs.pop('teacher')
		super(RemediationcustomForm, self).__init__(*args, **kwargs)	
		if teacher:
			courses = teacher.course.order_by("parcours","ranking")	
			self.fields['courses'] = forms.ModelMultipleChoiceField(queryset=courses, widget=forms.CheckboxSelectMultiple,  required=False)

	def clean_content(self):
		content = self.cleaned_data['mediation']
		validation_file(content)


class SupportfileForm(forms.ModelForm):
	class Meta:
		model = Supportfile
		fields = '__all__'
		exclude = ('attach_file','is_subtitle')

	def __init__(self, *args, **kwargs):
		teacher = kwargs.pop('teacher')
		super(SupportfileForm, self).__init__(*args, **kwargs)

		subjects = teacher.subjects.all()
		knowledges = Knowledge.objects.filter(theme__subject__in= subjects)
		self.fields['knowledge'] = forms.ModelChoiceField(queryset=knowledges) 
		self.fields['skills']    =  forms.ModelMultipleChoiceField(queryset= Skill.objects.filter(subject__in= subjects))
		self.fields['level']     =  forms.ModelChoiceField(queryset= teacher.levels.exclude(pk= 13).order_by('ranking'))

	def clean_content(self):
		content = self.cleaned_data['imagefile']
		validation_file(content)
		attach_file = self.cleaned_data['attach_file'] 
		validation_file(attach_file)
		


class SupportfileKForm(forms.ModelForm):
	class Meta:
		model = Supportfile
		fields = '__all__'
		exclude = ('knowledge','attach_file','is_subtitle')

	def __init__(self, *args, **kwargs):
		knowledge = kwargs.pop('knowledge')
		super(SupportfileKForm, self).__init__(*args, **kwargs)
		subject = knowledge.theme.subject 
		knowledges = Knowledge.objects.filter(theme__subject= subject)
		self.fields['knowledge'] = forms.ModelChoiceField(queryset=knowledges) 
		self.fields['skills']    =  forms.ModelMultipleChoiceField(queryset= Skill.objects.filter(subject= subject))
 
	def clean_content(self):
		content = self.cleaned_data['imagefile']
		validation_file(content)
		attach_file = self.cleaned_data['attach_file'] 
		validation_file(attach_file)

 
class UpdateSupportfileForm(forms.ModelForm):

	class Meta:
		model = Supportfile 
		fields = '__all__'
		exclude = ('attach_file','is_subtitle')

	def __init__(self, *args, **kwargs):
		knowledge = kwargs.pop('knowledge')
		subject = knowledge.theme.subject	
		super(UpdateSupportfileForm, self).__init__(*args, **kwargs)
		instance = kwargs.pop('instance')
		knowledges = Knowledge.objects.filter(theme__subject= subject)
		self.fields['knowledge'] = forms.ModelChoiceField(queryset=knowledges) 
		self.fields['skills']  = forms.ModelMultipleChoiceField(queryset=Skill.objects.filter(subject=subject), required=False)

	def clean_content(self):
		content = self.cleaned_data['imagefile']
		validation_file(content)
		attach_file = self.cleaned_data['attach_file'] 
		validation_file(attach_file)
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
                        prefix='supportchoice-{}-subchoice'.format( form.prefix ) )

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


formSetNested = inlineformset_factory(Supportfile, Supportchoice, fields=('answer','imageanswer','answerbis','imageanswerbis','is_correct','retroaction','xmin','xmax','tick','subtick','precision','is_written') , formset=BaseSupportchoiceFormset,   extra=1)
formSubSet    = inlineformset_factory(Supportchoice, Supportsubchoice, fields=('answer','imageanswer','label','is_correct','retroaction') , extra=2)

class BaseSupportchoiceUpdateFormset(BaseInlineFormSet):

    def add_fields(self, form, index):
        super().add_fields(form, index)
        # save the formset in the 'nested' property
        form.nested = formSubSetUpdate(
                        instance=form.instance,
                        data=form.data if form.is_bound else None,
                        files=form.files if form.is_bound else None,
                        prefix='supportchoice-{}-subchoice'.format( form.prefix ) )

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


formSetUpdateNested = inlineformset_factory(Supportfile, Supportchoice, fields=('answer','imageanswer','answerbis','imageanswerbis','is_correct','retroaction','xmin','xmax','tick','subtick','precision','is_written')  , formset=BaseSupportchoiceUpdateFormset,   extra=0)
formSubSetUpdate    = inlineformset_factory(Supportchoice, Supportsubchoice, fields=('answer','imageanswer','label','is_correct','retroaction') , extra=0)
#################################################################################################################################################################################
###################################    UPDATE FORMULAIRES GROUPES ET SOUS FORMULAIRES       #####################################################################################
#################################################################################################################################################################################

class AttachForm(forms.ModelForm):
	class Meta:
		model = Supportfile
		fields = ('attach_file','title','is_subtitle')
 
class CourseForm(forms.ModelForm):
	class Meta:
		model = Course
		fields = '__all__'

	def __init__(self, *args, **kwargs):
		parcours = kwargs.pop('parcours')
		super(CourseForm, self).__init__(*args, **kwargs)
		relations = Relationship.objects.filter(parcours=parcours)
		self.fields['relationships'] = forms.ModelMultipleChoiceField(queryset=relations, required=False )


class CourseNPForm(forms.ModelForm):
	class Meta:
		model = Course
		fields = '__all__'


	def __init__(self, *args, **kwargs):
		teacher = kwargs.pop('teacher')
		super(CourseNPForm, self).__init__(*args, **kwargs)
 
		self.fields['level']    = forms.ModelChoiceField(queryset=teacher.levels.exclude(pk=13).order_by("ranking"), required=False )
		self.fields['subject']  = forms.ModelChoiceField(queryset=teacher.subjects.all(), required=False )
		self.fields['parcours'] = forms.ModelChoiceField(queryset=teacher.teacher_parcours.all(), required=False )


class DemandForm(forms.ModelForm):
	class Meta:
		model = Demand
		fields = '__all__'


class MasteringForm (forms.ModelForm):
	class Meta:
		model = Mastering
		fields = '__all__'


	def __init__(self, *args, **kwargs):
		relationship = kwargs.pop('relationship')
		super(MasteringForm, self).__init__(*args, **kwargs)
		#relations = Relationship.objects.filter(exercise__supportfile__is_title = 0, parcours=relationship.parcours)
		courses = Course.objects.filter(parcours=relationship.parcours)
		self.fields['courses']   = forms.ModelMultipleChoiceField(queryset=courses, widget=forms.CheckboxSelectMultiple,   required=False )
		#self.fields['practices'] = forms.ModelMultipleChoiceField(queryset=relations, widget=forms.CheckboxSelectMultiple,   required=False )

 
class MasteringDoneForm (forms.ModelForm):
	class Meta:
		model = Mastering_done
		fields = ('writing',)



class MasteringcustomForm (forms.ModelForm):
	class Meta:
		model = Masteringcustom
		fields = '__all__'

	def __init__(self, *args, **kwargs):
		customexercise = kwargs.pop('customexercise')
		super(MasteringcustomForm, self).__init__(*args, **kwargs)
		#relations = Relationship.objects.filter(exercise__supportfile__is_title = 0, parcours__in=customexercise.parcourses.filter(is_publish=1))
		courses = Course.objects.filter(parcours__in=customexercise.parcourses.filter(is_publish=1))
		self.fields['courses']   = forms.ModelMultipleChoiceField(queryset=courses, widget=forms.CheckboxSelectMultiple,   required=False )
		#self.fields['practices'] = forms.ModelMultipleChoiceField(queryset=relations, widget=forms.CheckboxSelectMultiple,   required=False )
 

class MasteringcustomDoneForm (forms.ModelForm):
	class Meta:
		model = Masteringcustom_done
		fields = ('writing',)

class WrittenanswerbystudentForm (forms.ModelForm):
	class Meta:
		model = Writtenanswerbystudent
		fields = ('imagefile','answer')

	def clean_content(self):
		content = self.cleaned_data['imagefile']
		validation_file(content)

class CustomanswerbystudentForm (forms.ModelForm):
	class Meta:
		model = Customanswerbystudent
		fields = ('file','answer')

class CustomanswerimageForm (forms.ModelForm):
	class Meta:
		model = Customanswerimage
		fields = ('image', )

	def clean_content(self):
		content = self.cleaned_data['image']
		validation_file(content)


class CustomexerciseForm (forms.ModelForm):
	
	class Meta:
		model = Customexercise
		fields = '__all__'

				
	def __init__(self, *args, **kwargs):
		parcours = kwargs.pop('parcours')
		teacher = kwargs.pop('teacher')
		parcours_subject = parcours.subject 

		super(CustomexerciseForm, self).__init__(*args, **kwargs)
		skills = Skill.objects.filter(subject = parcours_subject)
		knowledges = Knowledge.objects.filter(theme__subject = parcours_subject, level  = parcours.level)
		parcourses = teacher.author_parcours.exclude(pk=parcours.id)
		students = parcours.students.order_by("user__last_name")
		criterions = Criterion.objects.filter( subject = parcours_subject , level = parcours.level )

		self.fields['skills'] = forms.ModelMultipleChoiceField(queryset=skills,    required=False )
		self.fields['knowledges'] = forms.ModelMultipleChoiceField(queryset=knowledges,  required=False ) 
		self.fields['parcourses'] = forms.ModelMultipleChoiceField(queryset=parcourses,  required=False )  
		self.fields['students']   = forms.ModelMultipleChoiceField(queryset=students, widget=forms.CheckboxSelectMultiple,   required=False )
		self.fields['criterions'] = forms.ModelMultipleChoiceField(queryset=criterions, widget=forms.CheckboxSelectMultiple,  required=False ) 
  

class CustomexerciseNPForm (forms.ModelForm):

	class Meta:
		model = Customexercise
		fields = '__all__'

				
	def __init__(self, *args, **kwargs):
		teacher = kwargs.pop('teacher')
		custom = kwargs.pop('custom')
		super(CustomexerciseNPForm, self).__init__(*args, **kwargs)
		skills = Skill.objects.filter(subject__in = teacher.subjects.all())
		knowledges = Knowledge.objects.filter(theme__subject__in = teacher.subjects.all(), level__in = teacher.levels.exclude(pk=13))
		students = custom.students.all() 
		self.fields['skills'] = forms.ModelMultipleChoiceField(queryset=skills,    required=False )
		self.fields['knowledges'] = forms.ModelMultipleChoiceField(queryset=knowledges,  required=False ) 
		self.fields['students'] = forms.ModelMultipleChoiceField(queryset=students, widget=forms.CheckboxSelectMultiple,   required=False )
		

class CustomexerciseOnlyForm (forms.ModelForm):

	class Meta:
		model = Customexercise
		fields = '__all__'
	
	def __init__(self, *args, **kwargs):
		teacher = kwargs.pop('teacher')
		super(CustomexerciseOnlyForm, self).__init__(*args, **kwargs)
		subjects   = teacher.subjects.all()
		skills     = Skill.objects.filter(subject__in = subjects )
		knowledges = Knowledge.objects.filter(theme__subject__in = subjects , level__in = teacher.levels.exclude(pk=13)) 
		parcourses = teacher.teacher_parcours.order_by("subject","level")

		self.fields['subject']    = forms.ModelChoiceField(queryset=subjects,    required=True )
		self.fields['levels']     = forms.ModelMultipleChoiceField(queryset=teacher.levels.exclude(pk=13), required=True )
		self.fields['skills']     = forms.ModelMultipleChoiceField(queryset=skills,    required=True )
		self.fields['knowledges'] = forms.ModelMultipleChoiceField(queryset=knowledges,  required=True ) 
		self.fields['parcourses'] = forms.ModelMultipleChoiceField(queryset=parcourses,  required=False ) 
		


class WAnswerAudioForm (forms.ModelForm):
	class Meta:
		model = Writtenanswerbystudent
		fields = ('audio',)

	def clean_content(self):
		content = self.cleaned_data['audio']
		validation_file(content)

class CustomAnswerAudioForm (forms.ModelForm):
	class Meta:
		model = Customanswerbystudent
		fields = ('audio',)


	def clean_content(self):
		content = self.cleaned_data['audio']
		validation_file(content)
 


class CommentForm(forms.ModelForm):

	class Meta:
		model = Comment
		fields = ('comment',)

 

class DocumentReportForm (forms.ModelForm):

	class Meta:
		model = DocumentReport
		fields = '__all__'
		exclude = ("done",)



class CriterionForm (forms.ModelForm):

	class Meta:
		model = Criterion
		fields = '__all__'

	def __init__(self, *args, **kwargs):
		parcours = kwargs.pop('parcours')
		teacher = kwargs.pop('teacher')
		parcours_subject = parcours.subject 
		super().__init__(*args, **kwargs)

		self.fields['label'] = forms.CharField(widget=forms.Textarea(attrs={
		"placeholder": "Description du critère",
		"rows": 6,
		"cols": 50
		}))


		self.fields['subject'].initial = parcours.subject
		self.fields['subject'].widget = forms.HiddenInput()
		self.fields['level'].initial = parcours.level
		self.fields['level'].widget = forms.HiddenInput()

		skills = Skill.objects.filter(subject = parcours_subject)
		knowledges = Knowledge.objects.filter(theme__subject =  parcours_subject , level  = parcours.level)

		self.fields['skill'] = forms.ModelChoiceField(queryset=skills,    required=False )
		self.fields['knowledge'] = forms.ModelChoiceField(queryset=knowledges,  required=False ) 
 



class CriterionOnlyForm (forms.ModelForm):

	class Meta:
		model = Criterion
		fields = '__all__'

	def __init__(self, *args, **kwargs):
		teacher = kwargs.pop('teacher')
		super().__init__(*args, **kwargs)

		self.fields['label'] = forms.CharField(widget=forms.Textarea(attrs={
		"placeholder": "Description du critère",
		"rows": 6,
		"cols": 50
		}))

		subjects = teacher.subjects.all()
		skills     = Skill.objects.filter(subject__in = subjects )
		knowledges = Knowledge.objects.filter(theme__subject__in =  subjects , level__in  = teacher.levels.exclude(pk=13))

		self.fields['skill'] = forms.ModelChoiceField(queryset=skills,    required=False )
		self.fields['knowledge'] = forms.ModelChoiceField(queryset=knowledges,  required=False ) 

########################################################################################################################################### 
########################################################################################################################################### 
######################################################      Prep_eval             ######################################################### 
########################################################################################################################################### 
########################################################################################################################################### 

class PrepevalForm (forms.ModelForm):

	class Meta:
		model = Prepeval
		fields = ("date",)