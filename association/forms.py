from django import forms
from .models import Accounting , Voting , Associate, Document , Section , Detail , Rate , Abonnement , Holidaybook , Activeyear , Accountancy , Invoice 
from school.models import School
from account.models import User

class HolidaybookForm(forms.ModelForm):
    class Meta:
        model = Holidaybook 
        fields = '__all__' 

class ActualForm(forms.ModelForm):
    class Meta:
        model = Actual 
        fields = '__all__' 

class AccountingForm(forms.ModelForm):

    class Meta:
        model = Accounting 
        fields = '__all__' 
    def __init__(self, *args, **kwargs):
        super(AccountingForm, self).__init__(*args, **kwargs)        
        schools = School.objects.all()
        self.fields['school'] = forms.ModelChoiceField(queryset=schools,    required=False )


class AccountancyForm(forms.ModelForm):
    class Meta:
        model = Accountancy 
        fields = '__all__' 



class DetailForm(forms.ModelForm):
    class Meta:
        model = Detail 
        fields = '__all__' 

class AbonnementForm(forms.ModelForm):
    class Meta:
        model = Abonnement 
        fields = '__all__' 


class AssociateForm(forms.ModelForm):
    class Meta:
        model = Associate
        fields = '__all__' 

    def __init__(self, *args, **kwargs):
        super(AssociateForm, self).__init__(*args, **kwargs)
        users = User.objects.filter(user_type = 2)
        self.fields['user'] = forms.ModelChoiceField(queryset=users,    required=False )

 
class VotingForm(forms.ModelForm):
    class Meta:
        model = Voting 
        fields = '__all__' 

 
class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document 
        fields = '__all__'  

 
class SectionForm(forms.ModelForm):
    class Meta:
        model = Section 
        fields = '__all__' 




class RateForm(forms.ModelForm):
    class Meta:
        model = Rate 
        fields = '__all__' 



class ActiveyearForm(forms.ModelForm):
    class Meta:
        model = Activeyear 
        fields = '__all__' 


 
class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice 
        fields = '__all__' 
