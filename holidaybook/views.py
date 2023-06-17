from django.shortcuts import render
from django.contrib.auth.decorators import  permission_required,user_passes_test
from django.contrib.auth.forms import    AuthenticationForm
from account.decorators import user_is_board
from .models import *
from group.models import Group
from qcm.models import Parcours
from account.forms import  UserForm, ParentForm, StudentForm ,  NewpasswordForm


def holidaybooks(request):

	form = AuthenticationForm()
	np_form = NewpasswordForm()

	hbooks = Holidaybook.objects.filter(is_publish = 1).order_by("level__ranking")
	return render(request, 'holidaybook/holidaybooks.html', {'hbooks': hbooks ,  'form' : form ,  'np_form' : np_form    })



def try_it(request,idl):


	form = AuthenticationForm()
	np_form = NewpasswordForm()

	group =  Group.objects.filter(level_id = idl,formule_id=5).last()
	hbook = Holidaybook.objects.filter(level_id = idl, is_publish = 1).first()
	parcours = group.group_parcours.filter(ranking=1).first()
	relationships = parcours.parcours_relationship.filter(is_publish=1).order_by("ranking")

	return render(request, 'holidaybook/try_it_book.html', {'parcours': parcours , 'relationships': relationships ,  'hbook' : hbook ,  'form' : form ,  'np_form' : np_form })


def buy_it(request,idl):

	parent_form = UserForm(request.POST or None)
	student_form = UserForm(request.POST or None)
	hbook = Holidaybook.objects.filter(level_id=idl).first()

	form = AuthenticationForm()
	np_form = NewpasswordForm()
	today = datetime.now().replace(tzinfo=timezone.utc)

	if  all((parent_form.is_valid(), student_form.is_valid())): 

		amount     = 5.00
		start      = today
		stop       = datetime(this_year,9,1).replace(tzinfo=timezone.utc)

		user_student = student_form.save()
		student      = Student.objects.create(user=user_student,level_id=idl)
		adhesion = Adhesion.objects.create( student = student , level_id = idl , start = start , amount = amount , stop = stop , formule_id  = 5 , year  = today.year , is_active = 0)


		user_prent  = parent_form.save()
		parent,create = Parent.objects.update_or_create(user = user_parent, defaults = { "task_post" : 1 })
		if create :  parent.students.add(student)

		facture = Facture.objects.create(chrono = "BL_" +  user_parent.last_name +"_"+str(today) ,  user_id = user_parent.id , file = "" , date = today , orderID = "" , is_lesson = 1  ) #orderID = Numéro de paiement donné par la banque"
		facture.adhesions.add(adhesion)


		this_year  = today.year
		student_id = user_student.id
		formule_id = 5


		student = Student.objects.get(pk=student_id)
		level   = Level.objects.get(pk=idl)
		formule = Formule.objects.get(pk=formule_id)
		user = request.user

		cmd     = cmd_abonnement(formule,facture.id)

		request.session["details_of_student"] = {'student_id' : student_id , 'level_id' : level_id ,  'formule_id' : formule_id , 'amount' : amount , 'today' : start , 'end_day' : stop }

		email=  request.user.email
		billing='<?xml version="1.0" encoding="utf-8" ?><Billing><Address><FirstName>{}</FirstName><LastName>{}</LastName><Address1>Sarlat</Address1><ZipCode>24200</ZipCode><City>Sarlat</City><CountryCode>250</CountryCode></Address></Billing>'.format("Académie","SACADO ACADÉMIE")
		try : y,m,d = stop.split("T")[0].split("-")
		except : y,m,d = stop.split("-")
		end_day = d+"-"+m+"-"+y
		champs_val=champs_briqueCA(amount,cmd,email,1,billing)

		context={ 'formule' : formule , 'level' : level , 'student' : student ,  'amount' : amount , 'end_day' : end_day , 'champs_val':champs_val}
		return render(request, 'setup/brique_credit_agricole.html', context) 

	group =  Group.objects.filter(level_id = idl,formule_id=5).last()
	parcours = group.group_parcours.filter(ranking=1).first()

	hbooks = Holidaybook.objects.filter(is_publish = 1).order_by("level__ranking")

	clas_sups = ["CE1","CE2","CM1","CM2","6ème","5ème","4ème","3ème","2nde","1ère","Terminale"]
	classe_sup = clas_sups[idl-1]

	return render(request, 'holidaybook/buy_it_book.html', {'hbooks': hbooks , 'hbook': hbook ,  'group' : group , 'classe_sup' : classe_sup ,
	  'parent_form' : parent_form ,  'student_form' : student_form  ,  'form' : form ,  'np_form' : np_form     })




@user_passes_test(user_is_board) 
def create_holidaybook(request):
 
    form = RateForm(request.POST or None )

    if form.is_valid():
        nf = form.save(commit = False)
        nf.author = request.user
        nf.save()

        messages.success(request,"Création des groupes et séquences effectuée avec succès.")
        return redirect('list_rates')

    else:
        
        print(form.errors)

    
    context = {'form': form, }

    return render(request, 'association/form_holidaybook.html', context)

 