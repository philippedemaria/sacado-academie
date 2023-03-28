from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Teacher, User, Student, Parent , Response , Newpassword , Avatar , Background, Description

from django.core.exceptions import ValidationError
from django.forms import BaseFormSet

from django.db import transaction
from django.contrib.auth.hashers import make_password


class UserForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password1', 'password2', 'cgu')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.pop("autofocus", None)

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError("Ce nom d'utilisateur est déjà utilisé. Merci d'en choisir un autre.", code='invalid')
        return username


class AvatarForm(forms.ModelForm):
    class Meta:
        model = Avatar
        fields = '__all__'

class DescriptionForm(forms.ModelForm):
    class Meta:
        model = Description
        fields = '__all__'


class AvatarUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('avatar',)


class BacktitleUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('backtitle',)


class BackgroundForm(forms.ModelForm):
    class Meta:
        model = Background
        fields = '__all__'


class BackgroundUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('background',)
 



class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'
        exclude = ('code',)


class StudentUpdateForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'



class TeacherForm(forms.ModelForm):

    class Meta :
        model = Teacher
        fields = '__all__'




class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'
        exclude = ['user_permissions', 'groups',  'is_active', 'is_superuser', 'last_login', 'date_joined', 'user_type', 'is_extra', 'password', 'cgu','schools','is_testeur','avatar','background']



class ManagerForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'
        exclude = ['user_permissions', 'groups',  'is_active', 'is_superuser', 'last_login', 'date_joined',    'user_type', 'password','cgu','avatar','background','schools' ]


class ManagerUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'
        exclude = ['user_permissions', 'groups', 'is_active', 'is_superuser', 'last_login', 'date_joined',  'user_type', 'password','cgu','avatar','background','schools' ]


class NewUserTForm(forms.ModelForm):

    class Meta:
        model = User
        fields = '__all__'
        exclude = ['user_permissions', 'groups',  'is_active', 'is_superuser', 'last_login', 'date_joined',   'is_extra','user_type','time_zone', 'password','avatar','background','schools' ]


  

class NewUserSForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'
        exclude = ['user_permissions', 'groups',  'is_active', 'is_superuser', 'last_login', 'date_joined',   'user_type', 'is_manager',  'is_extra',  'time_zone', 'password' ,'cgu','schools' ,'avatar','background']




class ParentForm(forms.ModelForm):
    class Meta:
        model = Parent
        fields = '__all__'
 

class ParentUpdateForm(forms.ModelForm):
    class Meta:
        model = Parent
        fields = '__all__'
        exclude = ['user_permissions', 'groups', 'is_staff', 'is_active', 'is_superuser', 'last_login', 'date_joined', 'user_type', 'password' , 'cgu','schools','avatar','background']




class BaseUserFormSet(BaseFormSet):
    def clean(self):
        """Checks that no two articles have the same title."""
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        titles = []
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            username = form.cleaned_data.get('username')
            if User.objects.filter(username = username):
                raise ValidationError("Deux utilisateurs doivent avoir des identifiants différents.")


class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = '__all__'


class NewpasswordForm(forms.ModelForm):
    class Meta:
        model = Newpassword
        fields = '__all__'


class SetnewpasswordForm(UserCreationForm):
    class Meta:
        model = User
        fields = ( 'password1', 'password2' )
