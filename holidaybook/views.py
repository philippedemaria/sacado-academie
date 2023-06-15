from django.shortcuts import render
from django.contrib.auth.decorators import  permission_required,user_passes_test
from account.decorators import user_is_board
from .models import *
 
def holidaybooks(request):

    hbooks = Holidaybook.objects.filter(is_publish = 1).order_by("level__ranking")
    return render(request, 'holidaybook/holidaybooks.html', {'hbooks': hbooks ,     })


 
def try_it(request):

    hbooks = Holidaybook.objects.filter(is_publish = 1).order_by("level__ranking")
    return render(request, 'holidaybook/holidaybooks.html', {'hbooks': hbooks ,     })




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

 