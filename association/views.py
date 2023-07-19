from django.shortcuts import render, redirect, get_object_or_404
from django.forms import inlineformset_factory
from django.http import JsonResponse
from django.core import serializers
from django.template.loader import render_to_string
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
from account.decorators import user_is_board
from school.models import Stage , School, Country 
from school.forms import  SchoolForm
from templated_email import send_templated_mail
from django.db.models import Q , Sum
from django.contrib.auth.decorators import  permission_required,user_passes_test
############### bibliothèques pour les impressions pdf  #########################
from association.models import Accounting,Associate , Voting , Document, Section , Detail , Rate  , Holidaybook, Abonnement , Activeyear, Plancomptable , Accountancy  , Invoice , Subinvoice
from association.forms import AccountingForm,AssociateForm,VotingForm, DocumentForm , SectionForm, DetailForm , RateForm , AbonnementForm , HolidaybookForm ,  ActiveyearForm, AccountancyForm , InvoiceForm
from account.models import User, Student, Teacher, Parent ,  Response
from group.models import Group
from qcm.models import Exercise, Studentanswer , Customanswerbystudent , Writtenanswerbystudent , Supportfile , Parcours
from school.models import School
from school.forms import SchoolForm
from setup.models import Formule
from setup.forms import FormuleForm
from socle.models import Level
#################################################################################
import os
from django.utils import formats, timezone
from io import BytesIO, StringIO
from django.http import  HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, inch, landscape , letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image , PageBreak,Frame , PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import yellow, red, black, white, blue
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.enums import TA_JUSTIFY,TA_LEFT,TA_CENTER,TA_RIGHT
from html import escape
cm = 2.54
#################################################################################
import re
import pytz
from datetime import datetime  , timedelta
from general_fonctions import *
import xlwt
import uuid
import json 
 



#################################################################
# Suppression des fichiers non utilisés
#################################################################
@user_passes_test(user_is_board)
def transfert_asso_acad(request,idl,start):

    levels = Level.objects.exclude(pk=13).order_by('ranking')
    
    name_to_gets = []
    if idl :
        level = Level.objects.get(pk=idl)
        ressources   = '/var/www/sacado-academie/ressources/' 
        dirname      = ressources + 'ggbfilesTMP/' + str(idl)+"/"
        #back_up_root = ressources + 'ggbfiles_backup/' + str(idl)+"/" 

        files = os.listdir(dirname)

        messagers = []
        i=1
        for file in files :
            name_to_get = 'ggbfiles/' + str(idl)+"/"+file[:8]
            name_to_gets.append(name_to_get)

            supportfiles = Supportfile.objects.filter(ggbfile__startswith=name_to_get)
            for supportfile in supportfiles :
                if 'ex' in file and  'ggbfiles/' + str(idl)+"/"+str(file) != str(supportfile.ggbfile) :
                    old_file = ressources+'ggbfilesTMP/' + str(idl)+"/"+str(file) 
                    new_file = ressources+'ggbfiles/' + str(idl)+"/"+str(file)
                    messagers.append( str(i)+". Changement : <b>"+ str(supportfile.ggbfile) +"</b> en <b> ggbfiles/" + str(idl)+"/"+str(file)  +"</b><br/> -> Déplacement de : <b>"+ str(old_file) +"</b> vers <b>"+ str(new_file) +"</b>")               
                    supportfile.ggbfile = 'ggbfiles/' + str(idl)+"/"+str(file)
                    i+=1

                    if start == 1 :
                        os.rename(  old_file  , new_file )
                        supportfile.save()

    else :
        level = None
        messagers = []



    context = { 'levels' : levels, 'level' : level , 'messagers' : messagers  }        
    return render(request, 'association/transfert_to_acad.html', context )


@user_passes_test(user_is_board)
def to_clean_database(request,idl,start):

    levels = Level.objects.exclude(pk=13).order_by('ranking')
    list_to_remove , list_to_keep = [] , []
    names = []
    if idl :
        level = Level.objects.get(pk=idl)
        supportfiles = Supportfile.objects.values_list('ggbfile',flat=True)

        ressources   = '/var/www/sacado-academie/ressources/' 
        dirname      = ressources + 'ggbfiles/' + str(idl)
        back_up_root = ressources + 'ggbfiles_backup/' + str(idl)+"/" 

        files = os.listdir(dirname)

        

        for file in files :
            data_file = 'ggbfiles/'+ str(idl)+"/"+file
            if data_file not in supportfiles :
                list_to_remove.append(data_file)
                if start == 1 :
                    os.rename( ressources + data_file , back_up_root + file )
            else :
                list_to_keep.append(file)



        list_to_remove.sort()
        list_to_keep.sort()

    else :
        level = None



    context = {'list_to_keep' : list_to_keep , 'levels' : levels, 'level' : level ,  'list_to_remove' : list_to_remove}        
    return render(request, 'association/to_clean_database.html', context )


#################################################################
# Suppression des fichiers non utilisés
#################################################################



def get_active_year():
    """ renvoi d'un tuple sous forme 2021-2022  et d'un entier 2021 """
    active_year = Activeyear.objects.get(is_active=1)
    int_year = active_year.year
    return active_year, int_year


def get_active_abonnements(user):

    active_year, this_year = get_active_year() # active_year = 2020-2021 ALORS QUE this_year est 2020
    strt = datetime(this_year,6,1)
    start = dt_naive_to_timezone(strt,user.time_zone)


    abonnements = Abonnement.objects.filter(date_start__gte = start).exclude(accounting__date_payment = None).order_by("school__country__name")
    return abonnements


def get_pending_abonnements(user):

    active_year, this_year = get_active_year() # active_year = 2020-2021 ALORS QUE this_year est 2020
    strt = datetime(this_year,9,1)
    stp  = datetime(this_year+1,8,31)
    start = dt_naive_to_timezone(strt,user.time_zone)
    stop  = dt_naive_to_timezone(stp,user.time_zone)

    abonnements = Abonnement.objects.filter(date_start__gte = start , date_stop__lte = stop, accounting__date_payment = None).order_by("school__country__name")
    return abonnements




def get_accountings(user):

    active_year, this_year = get_active_year()
    if this_year == 2021 : 
        date_start   = datetime(2021, 1, 1) 
    else :
        date_start   = datetime(this_year, 9,1) 
    date_stop    = datetime(this_year+1, 9, 1) # gestion de l'année en cours début le 1er septembre

    start = dt_naive_to_timezone(date_start,user.time_zone)
    stop  = dt_naive_to_timezone(date_stop,user.time_zone)

    accountings = Accounting.objects.filter(date__gte = start , date__lt = stop )

    return accountings


def module_bas_de_page(elements, nb_inches,bas_de_page):

    elements.append(Spacer(0,nb_inches*inch)) 
    asso = Paragraph(  "___________________________________________________________________"  , bas_de_page_blue )
    elements.append(asso)
    asso2 = Paragraph( "Association SacAdo"  , bas_de_page )
    elements.append(asso2)
    asso3 = Paragraph( "siren : 903345569"  , bas_de_page )
    elements.append(asso3)
    asso30 = Paragraph( "siret : 903345569 00011"  , bas_de_page )
    elements.append(asso30)
    asso4 = Paragraph( "2B Avenue de la pinède, La Capte, 83400 Hyères - FRANCE"  , bas_de_page )
    elements.append(asso4)
    return elements


def module_logo(elements):
    logo = Image('https://sacado.xyz/static/img/sacadoA1.png')
    logo_tab = [[logo, "Association SacAdo\nhttps://sacado.xyz \nassociation@sacado.xyz" ]]
    logo_tab_tab = Table(logo_tab, hAlign='LEFT', colWidths=[0.7*inch,5.2*inch ])
    elements.append(logo_tab_tab)
    return elements

def module_style(elements):

    sacado = ParagraphStyle('sacado', 
                            fontSize=20, 
                            leading=26,
                            borderPadding = 0,
                            alignment= TA_CENTER,
                            )
    bas_de_page = ParagraphStyle('sacado', 
                            fontSize=9, 
                            borderPadding = 0,
                            alignment= TA_CENTER,
                            )
    bas_de_page_blue = ParagraphStyle('sacado', 
                            fontSize=9, 
                            borderPadding = 0,
                            alignment= TA_CENTER,
                            textColor=colors.HexColor("#00819f"),
                            )
    title = ParagraphStyle('title', 
                            fontSize=16,                             
                            alignment= TA_CENTER,
                            textColor=colors.HexColor("#00819f"),
                            )
    subtitle = ParagraphStyle('title', 
                            fontSize=14, 
                            textColor=colors.HexColor("#00819f"),
                            )
    mini = ParagraphStyle(name='mini',fontSize=9 )  
    normal = ParagraphStyle(name='normal',fontSize=12,)   
    dateur_style = ParagraphStyle('dateur_style', 
                            fontSize=12, 
                            leading=26,
                            borderPadding = 0,
                            alignment= TA_RIGHT,
                            )
    signature_style = ParagraphStyle('dateur_style', 
                            fontSize=11, 
                            borderPadding = 0,
                            alignment= TA_RIGHT,
                            )
    signature_style_mini = ParagraphStyle('dateur_style', 
                            fontSize=9, 
                            borderPadding = 0,
                            alignment= TA_RIGHT,
                            )
    signature_style_blue = ParagraphStyle('dateur_style', 
                            fontSize=12, 
                            borderPadding = 0,
                            alignment= TA_RIGHT,
                            textColor=colors.HexColor("#00819f"),
                            )
    style_cell = TableStyle(
            [
                ('SPAN', (0, 1), (1, 1)),
                ('TEXTCOLOR', (0, 1), (-1, -1),  colors.Color(0,0.7,0.7))
            ]
        )
    offset = 0 # permet de placer le bas de page
    return sacado , bas_de_page, bas_de_page_blue, title , subtitle , mini , normal , dateur_style , signature_style , signature_style_mini, signature_style_blue , style_cell


#####################################################################################################################################
#####################################################################################################################################
####    payment_accepted from Paypal
#####################################################################################################################################
#####################################################################################################################################

def payment_complete(request):
    body = json.loads(request.body)
 
    Accounting.objects.filter(pk = body['accounting_id']).update(is_active = 1)
    return JsonResponse('Payement completed !', safe = False)


#####################################################################################################################################
#####################################################################################################################################
####    Holidaybook
#####################################################################################################################################
#####################################################################################################################################
@user_passes_test(user_is_board)
def display_holidaybook(request):

    try :
        holidaybook = Holidaybook.objects.get(pk = 1)
        form = HolidaybookForm(request.POST or None, instance = holidaybook )

    except :
        form = HolidaybookForm(request.POST or None )
 
    if request.method == "POST":
        is_display = request.POST.get("is_display")
        if is_display == 'on' :
            is_display = 1
        else :
            is_display = 0 
        holidaybook, created = Holidaybook.objects.get_or_create(pk =  1, defaults={  'is_display' : is_display } )
        if not created :
            holidaybook.is_display = is_display
            holidaybook.save()
        
        return redirect('association_index')
 

    context = {'form': form  }

    return render(request, 'association/form_holidaybook.html', context)

@user_passes_test(user_is_board)
def update_formule(request, id):

    formule = Formule.objects.get(id=id)
    form = FormuleForm(request.POST or None, instance=formule )

    if request.method == "POST":
        if form.is_valid():
            form.save()
        else :
            print(form.errors)
        
        return redirect('list_rates')

    context = {'form': form, 'formule' : formule }

    return render(request, 'association/form_formule.html', context )


@user_passes_test(user_is_board)
def delete_formule(request, id):

    formule = Formule.objects.get(id=id)
    formule.delete()
    return redirect('list_rates')
 
#####################################################################################################################################
#####################################################################################################################################
####    accounting
#####################################################################################################################################
#####################################################################################################################################

# def school_to_customer():
#     today       = datetime.now()
#     abonnements = Abonnement.objects.values_list('school').distinct()
#     liste=[]
#     for school in abonnements :
#         if not school in liste :
#             liste.append(school)
#             Customer.objects.create(school_id = school[0],status=3 )

 


@user_passes_test(user_is_board)
def all_schools(request):
 
    schools = School.objects.exclude(pk=50)
    context = { 'schools': schools }

    return render(request, 'association/all_schools.html', context ) 


@user_passes_test(user_is_board)
def delete_selected_schools(request):
    
    school_ids = request.POST.getlist("school_id")
    for school_id in school_ids :
        School.objects.get(pk=school_id).delete()

    return redirect( 'all_schools' ) 






@user_passes_test(user_is_board) 
def create_school_admin(request):

    form = SchoolForm(request.POST or None, request.FILES  or None)
    if form.is_valid():
        school = form.save()
        school.is_active = 1
        school.save()

        return redirect('all_schools')

    return render(request,'association/form_school.html', { 'form':form })




@user_passes_test(user_is_board) 
def update_school_admin(request,id):

    today    = datetime.now()
    today_time = today -   timedelta(days = 15)
    school = School.objects.get(id=id)
    form = SchoolForm(request.POST or None, request.FILES  or None, instance=school)

    teachers = school.users.filter(user_type=2) 


    nb_total = school.users.filter(user_type=0).count()
    nb = 150
    if nb > nb_total:
        nb = nb_total

    abonnements = school.abonnement.all()

    abonnement = abonnements.last()

    if abonnement :
        status = "Abonné"
    else :
        status = "Non abonné"
        if school.accountings.filter(date_payment=None, date__lte=today_time).last() :
            status = "En attente de paiement"

    if form.is_valid():
        school = form.save()
        school.is_active = 1
        school.save()


    return render(request,'association/form_school.html', { 'abonnements':abonnements, 'form':form,  'communications' : [],'school':school ,'nb':nb ,'nb_total':nb_total ,'teachers' : teachers , 'status' : status })




@user_passes_test(user_is_board)
def association_index(request):


    today_start  = datetime.date(datetime.now())
    nb_teachers  = Teacher.objects.all().count()
    nb_students  = Student.objects.all().count()#.exclude(user__username__contains="_e-test_")
    nb_exercises = Exercise.objects.filter(supportfile__is_title=0).count()

    abonnements  = get_active_abonnements(request.user)
    nb_schools   = abonnements.count()

    months       = [1,2,3,4,5,6,7,8,9,10,11,12]
    days         = [31,28,31,30,31,30,31,31,30,31,30,31]
    month_start  = today_start.month
    list_months  = months[month_start:12] + months[0:month_start]

    list_reals   = []
    for i in range(month_start,13+month_start) :
        list_reals.append(i)

    year   = today_start.year -1

    string = ""
    somme = 0
    run = 0
    for m in list_reals :        
        if m > 12 :
            year = today_start.year
            m = m-12
        sep = ""
        if run > 0 and run < 13 :
            sep = ","
        date_start   = datetime(year,m,1,0,0,0)
        date_stop    = datetime(year,m,days[m-1],23,59,59)

        n = Teacher.objects.filter(user__date_joined__lte=date_stop, user__date_joined__gte=date_start ).count()
        string += sep+str(n)
        somme += n
        run += 1


    nb_answers   = Studentanswer.objects.filter(date__gte= today_start).count() + Customanswerbystudent.objects.filter(date__gte= today_start).count() + Writtenanswerbystudent.objects.filter(date__gte= today_start).count()
    if Holidaybook.objects.all() :
        holidaybook  = Holidaybook.objects.values("is_display").get(pk=1)
    else :
        holidaybook = False

    active_year, this_year = get_active_year()

    context = { 'nb_teachers': nb_teachers , 'nb_students': nb_students , 'nb_exercises': nb_exercises, 
                'nb_schools': nb_schools, 'nb_answers': nb_answers, 'holidaybook': holidaybook ,
                'list_months': list_months, 'string': string,  'month_start' : month_start , 'active_year' : active_year , 
                }

    return render(request, 'association/dashboard.html', context )



@user_passes_test(user_is_board)
def create_activeyear(request):

    form       = ActiveyearForm(request.POST or None, request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            form.save()
        else :
            print(form.errors)
        
        return redirect('activeyears')

    return render(request, 'association/form_activeyear.html', {'form': form     })



@user_passes_test(user_is_board)
def update_activeyear(request,id):

    activeyear = Activeyear.objects.get(pk=id)
    form       = ActiveyearForm(request.POST or None , request.FILES or None , instance = activeyear)
 

    if request.method == "POST":
        if form.is_valid():
            form.save()
        else :
            print(form.errors)
        
        return redirect('activeyears')

    return render(request, 'association/form_activeyear.html', {'form': form     })


@user_passes_test(user_is_board)
def activeyears(request):

    years = Activeyear.objects.all()

    return render(request, 'association/list_activeyear.html', { 'years' :years   })



def total(first_date, last_date) :

    accountings =  Accounting.objects.filter(date_payment__gte=first_date, date_payment__lte=last_date).exclude(date_payment=None)
    total_amount = 0
    total_amount_active = 0
    for a in accountings :
        if a.is_credit :
            total_amount += a.amount
        else :
            total_amount -= a.amount
    return total_amount



@user_passes_test(user_is_board)
def adhesions(request):

    today = datetime.now()
    this_month = today.month
    this_year = today.year
 

    activeyear, year = get_active_year()

 

    first_date_month =  datetime(year, this_month, 1)
    first_date_year  = datetime(year, 1, 1)

    if this_month > 0 and this_month < 9 :
        this_year = this_year - 1
    first_date_schoolyear = datetime(year, 9, 1)

    total_month = total(first_date_month, today)
    total_year = total(first_date_year, today)
    total_shoolyear =  total(first_date_schoolyear, today)

    date_start = datetime(year, 8, 31)
    date_stop  = datetime(year+1, 8, 31)

    schools = School.objects.all()
    abonnements = Abonnement.objects.filter( school__in=schools, date_stop__gte = today ).exclude(accounting__date_payment=None).order_by("-accounting__date")    

    context =  {'abonnements': abonnements , 'total_month': total_month, 'total_year': total_year, 'total_shoolyear': total_shoolyear ,'this_month' :this_month, 'activeyear' : activeyear }
 
    return render(request, 'association/adhesions.html', context )




@user_passes_test(user_is_board)
def list_paypal(request):

    active_year, this_year    = get_active_year() 
    accountings = Accounting.objects.filter(is_paypal=1).exclude(date_payment=None)
    accounting_no_payment,  accounting_amount = 0, 0
    pay_accountings = accountings.exclude(date_payment=None)
    no_accountings = accountings.filter(date_payment=None)

    for a in pay_accountings :
        accounting_amount += a.amount
    for a in no_accountings :
        accounting_no_payment += a.amount


    active_year, this_year = get_active_year() # active_year = 2020-2021 ALORS QUE this_year est 2020
    today = datetime.now()
    this_month = today.month

    first_date_month =  datetime(this_year, this_month, 1)

    if this_month > 0 and this_month < 9 :
        this_year = this_year - 1
    first_date_schoolyear = datetime(this_year, 5, 1) ##### A CHANGER  

    total_month     = total(first_date_month, today)
    total_shoolyear = total(first_date_schoolyear, today)

    return render(request, 'association/list_accounting.html', { 'accounting_amount':accounting_amount,  'accounting_no_payment' : accounting_no_payment   , 'accountings': accountings ,  'active_year' : active_year ,  'tp' : 3 , 'total_month': total_month,  'total_shoolyear': total_shoolyear ,'this_month' :this_month })



@user_passes_test(user_is_board)
def bank_activities(request):
    context = { }

    return render(request, 'association/bank_activities.html', context )



@user_passes_test(user_is_board)
def calcule_bank_bilan(request):
    """ page d'accueil de la comptabilité"""

 
    this_year     = Activeyear.objects.get(is_active=1).year  
    plan_sale     = Plancomptable.objects.filter(code__gte=700,code__lt=800).order_by("code")
    plan_purchase = Plancomptable.objects.filter(code__gte=600,code__lt=700 ).order_by("code")
    plan_immo     = Plancomptable.objects.filter(code__in= [411,486,5121,5122] ).order_by("code")
    plan_resultat = Plancomptable.objects.filter(code__in=[110, 487] )

    my_dico = {}
    list_sales , list_purchases,plan_immos , plan_resultats = [] , [] , [] , []

    charges, products   = 0 , 0  
    for p in plan_sale :
        my_dico = {}
        accountings_sales = Accountancy.objects.filter(current_year = this_year  ,  plan_id = p.code   ).aggregate(Sum('amount'))
        my_dico["code"] = p.code 
        my_dico["name"] = p.name
        my_dico["solde"]= accountings_sales["amount__sum"]
        try :
            products +=accountings_sales["amount__sum"]
        except :
            pass
        list_sales.append( my_dico )


    for p in plan_purchase :
        my_dico = {}
        accountings_sales = Accountancy.objects.filter(current_year = this_year  ,  plan_id = p.code   ).aggregate(Sum('amount'))
        my_dico["code"] = p.code 
        my_dico["name"] = p.name
        my_dico["solde"]= accountings_sales["amount__sum"]
        try :
            charges +=accountings_sales["amount__sum"]
        except :
            pass
        list_purchases.append( my_dico )

    cs, ps   = 0 , 0 
 
    for p in plan_immo :
        my_dico = {}
        
        if p.code ==411 :

            my_dico = {}
            accountings_sales_debit = Accountancy.objects.filter(current_year = this_year  ,  plan_id = p.code, is_credit=1   ).aggregate(Sum('amount'))
            accountings_sales_credit = Accountancy.objects.filter(current_year = this_year  ,  plan_id = p.code, is_credit=0   ).aggregate(Sum('amount'))
            my_dico["code"] = p.code 
            my_dico["name"] = p.name
            try :
                solde = accountings_sales_credit["amount__sum"] - accountings_sales_debit["amount__sum"]
            except :
                solde = accountings_sales_credit["amount__sum"]
                
            my_dico["solde"]= solde

            if p.code > 5000 :
                try :
                    my_dico["solde"]= solde
                except :
                    pass
                try :
                    cs -= solde
                except :
                    pass
            else :
                my_dico["solde"]= solde
                try :
                    cs += solde
                except :
                    pass
            plan_immos.append( my_dico )


        else : 
            accountings_sales = Accountancy.objects.filter(current_year = this_year  ,  plan_id = p.code    ).aggregate(Sum('amount'))
            my_dico["code"] = p.code
            my_dico["name"] = p.name
            if p.code > 5000 :
                try :
                    my_dico["solde"]= -accountings_sales["amount__sum"]
                except :
                    pass
                try :
                    cs -= accountings_sales["amount__sum"]
                except :
                    pass
            else :
                my_dico["solde"]= accountings_sales["amount__sum"]
                try :
                    cs += accountings_sales["amount__sum"]
                except :
                    pass
            plan_immos.append( my_dico )


    for p in plan_resultat :
        my_dico = {}
        accountings_sales = Accountancy.objects.filter(current_year = this_year  ,  plan_id = p.code   ).aggregate(Sum('amount'))
        my_dico["code"] = p.code 
        my_dico["name"] = p.name
        my_dico["solde"]= accountings_sales["amount__sum"]
        try :
            ps += accountings_sales["amount__sum"]
        except :
            pass
        plan_resultats.append( my_dico )

    results = products - charges
    rs =  cs - ps


    return list_sales ,  list_purchases ,  plan_resultats ,  plan_immos , results , products , charges, rs , ps , cs   



@user_passes_test(user_is_board)
def bank_bilan(request):

    list_sales ,  list_purchases ,  plan_resultats ,  plan_immos , results , products , charges, rs , ps , cs   = calcule_bank_bilan(request)

    context = {  'list_sales' : list_sales ,  'list_purchases' : list_purchases ,  'plan_resultats' :  plan_resultats ,  'plan_immos' : plan_immos ,  'results' : results ,  'products' : products ,  'charges' :  charges ,  'rs' : rs  , 'ps' : ps, 'cs' : cs }  

    return render(request, 'association/bank_bilan.html', context )   

 
@user_passes_test(user_is_board)
def print_bank_bilan(request):

    list_sales ,  list_purchases ,  plan_resultats ,  plan_immos , results , products , charges, rs , ps , cs = calcule_bank_bilan(request)
    year_active = Activeyear.objects.get(is_active=1)
    #########################################################################################
    ### Instanciation
    #########################################################################################
    elements = []        
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Compte_resultat_'+str(year_active.year)+'.pdf"'
    doc = SimpleDocTemplate(response,   pagesize=(landscape(letter)), 
                                        topMargin=0.5*inch,
                                        leftMargin=0.5*inch,
                                        rightMargin=0.5*inch,
                                        bottomMargin=0.3*inch     )

    sample_style_sheet = getSampleStyleSheet()
    OFFSET_INIT = 0.2
    #########################################################################################
    ### Style
    #########################################################################################
    sacado = ParagraphStyle('sacado', 
                            fontSize=20, 
                            leading=26,
                            borderPadding = 0,
                            alignment= TA_CENTER,
                            )
    bas_de_page = ParagraphStyle('sacado', 
                            fontSize=9, 
                            borderPadding = 0,
                            alignment= TA_CENTER,
                            )
    bas_de_page_blue = ParagraphStyle('sacado', 
                            fontSize=9, 
                            borderPadding = 0,
                            alignment= TA_CENTER,
                            textColor=colors.HexColor("#00819f"),
                            )
    title = ParagraphStyle('title', 
                            fontSize=16,                             
                            alignment= TA_CENTER,
                            textColor=colors.HexColor("#00819f"),
                            )
    subtitle = ParagraphStyle('title', 
                            fontSize=14, 
                            textColor=colors.HexColor("#00819f"),
                            )
    mini = ParagraphStyle(name='mini',fontSize=9 )  
    normal = ParagraphStyle(name='normal',fontSize=12,)   
    dateur_style = ParagraphStyle('dateur_style', 
                            fontSize=12, 
                            leading=26,
                            borderPadding = 0,
                            alignment= TA_RIGHT,
                            )
    signature_style = ParagraphStyle('dateur_style', 
                            fontSize=11, 
                            borderPadding = 0,
                            alignment= TA_RIGHT,
                            )
    signature_style_mini = ParagraphStyle('dateur_style', 
                            fontSize=9, 
                            borderPadding = 0,
                            alignment= TA_RIGHT,
                            )
    signature_style_blue = ParagraphStyle('dateur_style', 
                            fontSize=12, 
                            borderPadding = 0,
                            alignment= TA_RIGHT,
                            textColor=colors.HexColor("#00819f"),
                            )
    style_cell = TableStyle(
            [
                ('SPAN', (0, 1), (1, 1)),
                ('TEXTCOLOR', (0, 1), (-1, -1),  colors.Color(0,0.7,0.7))
            ]
        )
    offset = 0 # permet de placer le bas de page
    return sacado , bas_de_page, bas_de_page_blue, title , subtitle , mini , normal , dateur_style , signature_style , signature_style_mini, signature_style_blue , style_cell


    #########################################################################################
    ### Logo Sacado
    #########################################################################################
    logo = Image('https://sacado.xyz/static/img/sacadoA1.png')
    logo_tab = [[logo, "Association SacAdo\nhttps://sacado.xyz \nassociation@sacado.xyz" ]]
    logo_tab_tab = Table(logo_tab, hAlign='LEFT', colWidths=[0.7*inch,5.2*inch ])
    elements.append(logo_tab_tab)
    #########################################################################################
    ### Facture
    #########################################################################################
    elements.append(Spacer(0,0.3*inch))
    f = Paragraph( "Compte de résultat" , sacado )
    elements.append(f) 
    elements.append(Spacer(0,0.1*inch))
    fa = Paragraph( "Résultat : " + str(cr) + " €" , title )
    elements.append(fa) 
    details_list_sales , details_list_purchases = [] , [] 
    #########################################################################################
    ### Details_list_purchases
    #########################################################################################
    for a in accountings_list_purchases :
        if str(a["solde"]) != "0" :
            details_list_purchases.append(    ( str(a["code"])+". "+ str(a["name"]) , str(a["solde"])  )    )
           
    details_table_purchases = Table(details_list_purchases, hAlign='LEFT', colWidths=[4.2*inch,0.8*inch])
    details_table_purchases.setStyle(TableStyle([
               ('INNERGRID', (0,0), (-1,-1), 0.25, colors.gray),
               ('BOX', (0,0), (-1,-1), 0.25, colors.gray),
                ('BACKGROUND', (0,0), (-1,0), colors.Color(1,1,1))
               ]))


    #########################################################################################
    ### Accountings_list_sales
    #########################################################################################
    for a in accountings_list_sales :
        if str(a["solde"]) != "0" :
            details_list_sales.append(  ( str(a["code"]) +". "+ str(a["name"]) , str(a["solde"])  )    )
           
    details_table_sales = Table(details_list_sales, hAlign='LEFT', colWidths=[4.2*inch,0.8*inch])
    details_table_sales.setStyle(TableStyle([
               ('INNERGRID', (0,0), (-1,-1), 0.25, colors.gray),
               ('BOX', (0,0), (-1,-1), 0.25, colors.gray),
                ('BACKGROUND', (0,0), (-1,0), colors.Color(1,1,1))
               ]))

    #########################################################################################
    ### A mettre sur 2 colonnes
    #########################################################################################

    elements.append(Spacer(0,0.3*inch))
    g = Paragraph( "Charges : " + str(accountings_purchase) +"€", subtitle )
    elements.append(g)    
    elements.append(Spacer(0,0.1*inch))
    elements.append(details_table_purchases)

    elements.append(Spacer(0,0.3*inch))
    h = Paragraph( "Produits: " +str(accountings_sale) +"€" , subtitle )
    elements.append(h) 
    elements.append(Spacer(0,0.1*inch))
    elements.append(details_table_sales)
    #########################################################################################
    ### Bilan  
    #########################################################################################

    elements.append(Spacer(0,0.3*inch))
    b = Paragraph( "Bilan" , sacado )
    elements.append(b) 
 

    #########################################################################################
    ### Bilan actif
    #########################################################################################
    elements.append(Spacer(0,0.3*inch))
    actif = Paragraph( "Actif"  , subtitle )
    elements.append(actif)  
    elements.append(Spacer(0,0.1*inch))
    accountings_list_qc = [ ("411. Client", a_411 ) , ("411. Banque CA", accountings_ca ) , ("411. Banque Paypal", accountings_paypal )   ]

           
    accountings_list_qc_ = Table(accountings_list_qc, hAlign='LEFT', colWidths=[4.2*inch,0.8*inch])
    accountings_list_qc_.setStyle(TableStyle([
               ('INNERGRID', (0,0), (-1,-1), 0.25, colors.gray),
               ('BOX', (0,0), (-1,-1), 0.25, colors.gray),
                ('BACKGROUND', (0,0), (-1,0), colors.Color(1,1,1))
               ]))
    elements.append(accountings_list_qc_)             

    #########################################################################################
    ### Bilan passif
    #########################################################################################

 
    elements.append(Spacer(0,0.3*inch))
    actif = Paragraph( "Passif"  , subtitle )
    elements.append(actif)  
    elements.append(Spacer(0,0.1*inch))
    accountings_list_qc = [ ("487 . Clients produits constatés d'avance", cpca["amount__sum"] ) , ( " Résultat", crf )   ]

           
    accountings_list_qc_ = Table(accountings_list_qc, hAlign='LEFT', colWidths=[4.2*inch,0.8*inch])
    accountings_list_qc_.setStyle(TableStyle([
               ('INNERGRID', (0,0), (-1,-1), 0.25, colors.gray),
               ('BOX', (0,0), (-1,-1), 0.25, colors.gray),
                ('BACKGROUND', (0,0), (-1,0), colors.Color(1,1,1))
               ]))
    elements.append(accountings_list_qc_)  
    #########################################################################################
    ### Bas de page
    #########################################################################################
    nb_inches = 4.4 - offset
    elements.append(Spacer(0,nb_inches*inch)) 
    asso = Paragraph(  "___________________________________________________________________"  , bas_de_page_blue )
    elements.append(asso)
    asso2 = Paragraph( "Association SacAdo"  , bas_de_page )
    elements.append(asso2)
    asso3 = Paragraph( "siren : 903345569"  , bas_de_page )
    elements.append(asso3)
    asso30 = Paragraph( "siret : 903345569 00011"  , bas_de_page )
    elements.append(asso30)
    asso4 = Paragraph( "2B Avenue de la pinède, La Capte, 83400 Hyères - FRANCE"  , bas_de_page )
    elements.append(asso4)


    doc.build(elements)

    return response    

@user_passes_test(user_is_board)
def print_balance(request):

    
 
    list_sales ,  list_purchases ,  plan_resultats ,  plan_immos , results , products , charges, rs , ps , cs = calcule_bank_bilan(request)
    year_active = Activeyear.objects.get(is_active=1)
    #########################################################################################
    ### Instanciation
    #########################################################################################
    elements = []        
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Compte_Balance_Résultat_'+str(year_active.year)+'.pdf"'
    doc = SimpleDocTemplate(response,   pagesize=(landscape(letter)), 
                                        topMargin=0.5*inch,
                                        leftMargin=0.5*inch,
                                        rightMargin=0.5*inch,
                                        bottomMargin=0.3*inch     )

    sample_style_sheet = getSampleStyleSheet()
    OFFSET_INIT = 0.2
    #########################################################################################
    ### Style
    #########################################################################################
    sacado = ParagraphStyle('sacado', 
                            fontSize=20, 
                            leading=26,
                            borderPadding = 0,
                            alignment= TA_CENTER,
                            )
    bas_de_page = ParagraphStyle('sacado', 
                            fontSize=9, 
                            borderPadding = 0,
                            alignment= TA_CENTER,
                            )
    bas_de_page_blue = ParagraphStyle('sacado', 
                            fontSize=9, 
                            borderPadding = 0,
                            alignment= TA_CENTER,
                            textColor=colors.HexColor("#00819f"),
                            )
    title = ParagraphStyle('title', 
                            fontSize=16,                             
                            alignment= TA_CENTER,
                            textColor=colors.HexColor("#00819f"),
                            )
    subtitle = ParagraphStyle('title', 
                            fontSize=14, 
                            textColor=colors.HexColor("#00819f"),
                            )
    mini = ParagraphStyle(name='mini',fontSize=9 )  
    normal = ParagraphStyle(name='normal',fontSize=12,)   
    dateur_style = ParagraphStyle('dateur_style', 
                            fontSize=12, 
                            leading=26,
                            borderPadding = 0,
                            alignment= TA_RIGHT,
                            )
    signature_style = ParagraphStyle('dateur_style', 
                            fontSize=11, 
                            borderPadding = 0,
                            alignment= TA_RIGHT,
                            )
    signature_style_mini = ParagraphStyle('dateur_style', 
                            fontSize=9, 
                            borderPadding = 0,
                            alignment= TA_RIGHT,
                            )
    signature_style_blue = ParagraphStyle('dateur_style', 
                            fontSize=12, 
                            borderPadding = 0,
                            alignment= TA_RIGHT,
                            textColor=colors.HexColor("#00819f"),
                            )
    style_cell = TableStyle(
            [
                ('SPAN', (0, 1), (1, 1)),
                ('TEXTCOLOR', (0, 1), (-1, -1),  colors.Color(0,0.7,0.7))
            ])
    offset = 0 # permet de placer le bas de page



    #########################################################################################
    ### Logo Sacado
    #########################################################################################
    logo = Image('https://sacado.xyz/static/img/sacadoA1.png')
    logo_tab = [[logo, "Association SacAdo\nhttps://sacado.xyz \nassociation@sacado.xyz" ]]
    logo_tab_tab = Table(logo_tab, hAlign='LEFT', colWidths=[0.7*inch,5.2*inch ])
    elements.append(logo_tab_tab)
    #########################################################################################
    ### Facture
    #########################################################################################
    elements.append(Spacer(0,0.3*inch))
    f = Paragraph( "Balance" , sacado )
    elements.append(f) 
    elements.append(Spacer(0,0.1*inch))
    fa = Paragraph( str(year_active.year) +" " + str(year_active.year +1)  , title )
    elements.append(fa) 
    elements.append(Spacer(0,0.3*inch))

    #########################################################################################
    ### Details_list_purchases
    #########################################################################################
    plan = Plancomptable.objects.order_by("code")

    for p in plan :
        paragraph = Paragraph( str(p.code) +". "+ p.name , subtitle )
        details_list  = [(   "Débit","Crédit" , "Solde")] 
        p_code = p.code
        accountancies = Accountancy.objects.filter(plan_id=p_code)
        i = 1
        a_debit , a_credit = 0 , 0
        for a in accountancies :
            if a. is_credit:
                a_credit +=  a.amount
            else :
                a_debit +=  a.amount 
            i+=1
        if p_code > 5000 : 
            solde = abs(a_debit) - abs(a_credit) # les débits sont en négatifs
        elif p_code == 411 : 
            solde =   abs(a_debit) - abs(a_credit)
        else :
            solde =  abs(a_credit) - abs(a_debit) # les débits sont en négatifs

        if solde:
            solde =  abs(solde)
            elements.append(paragraph)
            elements.append(Spacer(0, 0.15*inch))
            details_list.append(   (   str( abs(a_debit ))+ " €" , str(a_credit)+ " €" ,  str(solde) + " €" )    )
     
            ##########################################################################
            ####  
            ##########################################################################
            details_tabs = [ ('INNERGRID', (0,0), (-1,-1), 0.25, colors.gray)  ,  ('BOX', (0,0), (-1,-1), 0.25, colors.gray)  ,   ('BACKGROUND', (0,0), (-1,0), colors.Color(1,1,1))  ]
            details_listing = Table(details_list, hAlign='LEFT', colWidths=[  1.2*inch,1.2*inch,1.2*inch])
            details_listing.setStyle(TableStyle(  details_tabs   ))
            elements.append(details_listing) 


    #########################################################################################
    ### Bas de page
    #########################################################################################

    elements.append(Spacer(0,inch)) 
    asso = Paragraph(  "___________________________________________________________________"  , bas_de_page_blue )
    elements.append(asso)
    asso2 = Paragraph( "Association SacAdo"  , bas_de_page )
    elements.append(asso2)
    asso3 = Paragraph( "siren : 903345569"  , bas_de_page )
    elements.append(asso3)
    asso30 = Paragraph( "siret : 903345569 00011"  , bas_de_page )
    elements.append(asso30)
    asso4 = Paragraph( "2B Avenue de la pinède, La Capte, 83400 Hyères - FRANCE"  , bas_de_page )
    elements.append(asso4)
    doc.build(elements)

    return response 




@user_passes_test(user_is_board)
def create_accountancy(request):
    form = AccountancyForm(request.POST or None )
    year = Activeyear.objects.get(is_active=1).year
    plan = Plancomptable.objects.order_by("code")
    if request.method == "POST":
        plan_id_c = request.POST.get("plan_id_c",None)
        plan_id_d = request.POST.get("plan_id_d",None)
        amount = request.POST.get("amount",None)
        Accountancy.objects.create(accounting_id = 0 , ranking = 2 , plan_id = int(plan_id_c) , is_credit = 1, amount = float(amount)  , current_year = year )             
        Accountancy.objects.create(accounting_id = 0 , ranking = 1 , plan_id = int(plan_id_d) , is_credit = 0, amount = -float(amount) , current_year = year )  
        return redirect('list_accountancy')

    return render(request, 'association/form_accountancy.html', {'form': form , 'plan': plan ,    })


 

@user_passes_test(user_is_board)
def list_accountancy(request):
    year = Activeyear.objects.get(is_active=1).year
    accontancies = Accountancy.objects.filter(current_year=year)
    return render(request, 'association/list_accountancy.html', {'accontancies' : accontancies   })


@user_passes_test(user_is_board)
def print_big_book(request):
 
    list_sales ,  list_purchases ,  plan_resultats ,  plan_immos , results , products , charges, rs , ps , cs = calcule_bank_bilan(request)
    year_active = Activeyear.objects.get(is_active=1)
    #########################################################################################
    ### Instanciation
    #########################################################################################
    elements = []        
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Compte_GrandLivre_resultat_'+str(year_active.year)+'.pdf"'
    doc = SimpleDocTemplate(response,   pagesize=(landscape(letter)), 
                                        topMargin=0.5*inch,
                                        leftMargin=0.5*inch,
                                        rightMargin=0.5*inch,
                                        bottomMargin=0.3*inch     )

    sample_style_sheet = getSampleStyleSheet()
    OFFSET_INIT = 0.2
    #########################################################################################
    ### Style
    #########################################################################################
    sacado = ParagraphStyle('sacado', 
                            fontSize=20, 
                            leading=26,
                            borderPadding = 0,
                            alignment= TA_CENTER,
                            )
    bas_de_page = ParagraphStyle('sacado', 
                            fontSize=9, 
                            borderPadding = 0,
                            alignment= TA_CENTER,
                            )
    bas_de_page_blue = ParagraphStyle('sacado', 
                            fontSize=9, 
                            borderPadding = 0,
                            alignment= TA_CENTER,
                            textColor=colors.HexColor("#00819f"),
                            )
    title = ParagraphStyle('title', 
                            fontSize=16,                             
                            alignment= TA_CENTER,
                            textColor=colors.HexColor("#00819f"),
                            )
    subtitle = ParagraphStyle('title', 
                            fontSize=14, 
                            textColor=colors.HexColor("#00819f"),
                            )
    mini = ParagraphStyle(name='mini',fontSize=9 )  
    normal = ParagraphStyle(name='normal',fontSize=12,)   
    dateur_style = ParagraphStyle('dateur_style', 
                            fontSize=12, 
                            leading=26,
                            borderPadding = 0,
                            alignment= TA_RIGHT,
                            )
    signature_style = ParagraphStyle('dateur_style', 
                            fontSize=11, 
                            borderPadding = 0,
                            alignment= TA_RIGHT,
                            )
    signature_style_mini = ParagraphStyle('dateur_style', 
                            fontSize=9, 
                            borderPadding = 0,
                            alignment= TA_RIGHT,
                            )
    signature_style_blue = ParagraphStyle('dateur_style', 
                            fontSize=12, 
                            borderPadding = 0,
                            alignment= TA_RIGHT,
                            textColor=colors.HexColor("#00819f"),
                            )
    style_cell = TableStyle(
            [
                ('SPAN', (0, 1), (1, 1)),
                ('TEXTCOLOR', (0, 1), (-1, -1),  colors.Color(0,0.7,0.7))
            ])
    offset = 0 # permet de placer le bas de page



    #########################################################################################
    ### Logo Sacado
    #########################################################################################
    logo = Image('https://sacado.xyz/static/img/sacadoA1.png')
    logo_tab = [[logo, "Association SacAdo\nhttps://sacado.xyz \nassociation@sacado.xyz" ]]
    logo_tab_tab = Table(logo_tab, hAlign='LEFT', colWidths=[0.7*inch,5.2*inch ])
    elements.append(logo_tab_tab)
    #########################################################################################
    ### Facture
    #########################################################################################
    elements.append(Spacer(0,0.3*inch))
    f = Paragraph( "Grand livre de compte" , sacado )
    elements.append(f) 
    elements.append(Spacer(0,0.1*inch))
    fa = Paragraph( str(year_active.year) +" " + str(year_active.year +1)  , title )
    elements.append(fa) 
    elements.append(Spacer(0,0.3*inch))

    #########################################################################################
    ### Details_list_purchases
    #########################################################################################
    plan = Plancomptable.objects.order_by("code")

    for p in plan :
        paragraph = Paragraph( str(p.code)+". "+ p.name , subtitle )
        details_list  = [(" "," ","Date","Id journal","Débit","Crédit")] 
        p_code = p.code
        accountancies = Accountancy.objects.filter(plan_id=p_code)
        i = 1
        a_debit , a_credit = 0 , 0
        for a in accountancies :
            if a. is_credit:
                details_list.append(   (i ,  str(a.plan_id)  , a.date.strftime("%d %m %Y")    , a.id , " " , str(abs(a.amount))+ " €" )    )
                a_credit +=  a.amount
            else :
                details_list.append(  ( i ,str(a.plan_id)  , a.date.strftime("%d %m %Y")    ,  a.id ,  str(abs(a.amount)) + " €", " ")    )
                a_debit +=  a.amount 
            i+=1 
        if p.code > 5000 :
            solde =  -(a_credit + a_debit) # les débits sont en négatifs
        elif p.code == 411 : 
            solde =  a_debit - a_credit 
        else : 
            solde =  a_credit + a_debit # les débits sont en négatifs

        if solde :
            elements.append(paragraph)
            elements.append(Spacer(0, 0.15*inch))
            details_list.append(   ( "" , ""  ,   "", "Soldes"    , str( abs(a_debit ))+ " €" , str(a_credit)+ " €" )    )
            details_list.append(   ( "" ,  ""    , " " ,  "Résultat"   ,  str(solde) + " €" , " " )    )
            ##########################################################################
            ####  
            ##########################################################################
            details_tabs = [ ('INNERGRID', (0,0), (-1,-1), 0.25, colors.gray)  ,  ('BOX', (0,0), (-1,-1), 0.25, colors.gray)  ,   ('BACKGROUND', (0,0), (-1,0), colors.Color(1,1,1))  ]
            details_listing = Table(details_list, hAlign='LEFT', colWidths=[  0.9*inch,  0.9*inch, inch,1.2*inch,1.2*inch,1.2*inch])
            details_listing.setStyle(TableStyle(  details_tabs   ))
          
            elements.append(details_listing) 

    #########################################################################################
    ### Bas de page
    #########################################################################################

    elements.append(Spacer(0,inch)) 
    asso = Paragraph(  "___________________________________________________________________"  , bas_de_page_blue )
    elements.append(asso)
    asso2 = Paragraph( "Association SacAdo"  , bas_de_page )
    elements.append(asso2)
    asso3 = Paragraph( "siren : 903345569"  , bas_de_page )
    elements.append(asso3)
    asso30 = Paragraph( "siret : 903345569 00011"  , bas_de_page )
    elements.append(asso30)
    asso4 = Paragraph( "2B Avenue de la pinède, La Capte, 83400 Hyères - FRANCE"  , bas_de_page )
    elements.append(asso4)
    doc.build(elements)

    return response 




@user_passes_test(user_is_board)
def archive_accountancy(request):
    pass

 

 






@user_passes_test(user_is_board)
def accountings(request):
    """ page d'accueil de la comptabilité"""

    abonnements = get_active_abonnements(request.user)

    nb_schools        = abonnements.count()
    nb_schools_fr     = abonnements.filter(school__country_id = 5).count()
    nb_schools_no_fr  = abonnements.exclude(school__country_id =5).count() 
    nb_schools_no_pay = get_pending_abonnements(request.user).count()

 
    active_year, this_year    = get_active_year() 
 

    product , charge , actif  , commission_paypal, result_bank , result_paypal = 0 , 0 , 0 , 0 , 0 , 0
    accountings   = get_accountings(request.user).values_list("amount","is_credit","date_payment","objet","is_paypal") 


    charges_list = list()
    for a in accountings :
        if a[1] and a[2] != None and a[4] == 0: #Crédit encaissé en banque non paypal
            actif += a[0]
        elif a[1] and a[2] == None and a[4] == 0: #Crédit en attente non paypal
            product += a[0] 
        elif a[1]  and a[4] == 1: #Crédit encaissé en banque paypal
            result_paypal += a[0]
        elif a[1] == 0  and a[4] == 1: #Débit commission paypal
            commission_paypal += a[0]
        elif a[1] == 0 and a[4] == 0: #débit non paypal
            dico    = dict()
            dico["objet"]  = a[3]
            dico["amount"] = a[0]
            charges_list.append(dico)
            charge += abs(a[0])

    actif += result_paypal
    result       = actif - charge
    total        = actif + product

    today = datetime.now()

        
    context = { 'today' : today , 'charge': charge, 'product': product , 'result': result , 'actif': actif , 'total': total , 'result_paypal' : result_paypal ,  'nb_schools': nb_schools , 'abonnements': abonnements , 'charges_list' : charges_list ,
                'this_year' : this_year , 'active_year' : active_year , 'nb_schools': nb_schools , 'nb_schools_fr': nb_schools_fr , 'nb_schools_no_fr': nb_schools_no_fr ,  'nb_schools_no_pay': nb_schools_no_pay , 'commission_paypal' : commission_paypal }  



    return render(request, 'association/accountings.html', context )



def accounting_to_accountancy(request) :

    # Journal client
    accountings = Accounting.objects.filter(plan=18).exclude(date_payment=None)
    for accounting in accountings :
        is_credit1 = 0
        is_credit2 = 1
        if accounting.is_paypal : paypal = 5122
        else : paypal = 5121

        Accountancy.objects.create(accounting_id = accounting.id , ranking = 1 , plan_id = 411 , is_credit = 0, amount = -accounting.amount )  
        Accountancy.objects.create(accounting_id = accounting.id , ranking = 2 , plan_id = 706 , is_credit = 1, amount = accounting.amount )  

        Accountancy.objects.create(accounting_id = accounting.id , ranking = 3 , plan_id = 411 , is_credit = 1, amount = accounting.amount )  
        Accountancy.objects.create(accounting_id = accounting.id , ranking = 4 , plan_id = paypal , is_credit = 0, amount = -accounting.amount ) 


    accountings = Accounting.objects.filter(plan=18,date_payment=None)
    for accounting in accountings :

        if accounting.amount >= 0 :
            Accountancy.objects.create(accounting_id = accounting.id , ranking = 1 , plan_id = 411 , is_credit = 0, amount = accounting.amount )  
            Accountancy.objects.create(accounting_id = accounting.id , ranking = 2 , plan_id = 706 , is_credit = 1, amount = accounting.amount ) 

        else : 
            Accountancy.objects.create(accounting_id = accounting.id , ranking = 1 , plan_id = 411 , is_credit = 1, amount = accounting.amount )  
            Accountancy.objects.create(accounting_id = accounting.id , ranking = 2 , plan_id = 706 , is_credit = 0, amount = accounting.amount )

    # Journal bancaire
    accountings = Accounting.objects.exclude(plan=18) 
    for accounting in accountings :
        amount = accounting.amount
        if accounting.is_paypal : paypal = 5122
        else : paypal = 5121


        if accounting.is_credit :
            Accountancy.objects.create(accounting_id = accounting.id , ranking = 1 , plan_id = accounting.plan.code , is_credit = 1, amount = amount )  
            Accountancy.objects.create(accounting_id = accounting.id , ranking = 2 , plan_id = paypal , is_credit = 0, amount = amount ) 

        else :
            Accountancy.objects.create(accounting_id = accounting.id , ranking = 1 , plan_id = accounting.plan.code , is_credit = 0, amount = amount )  
            Accountancy.objects.create(accounting_id = accounting.id , ranking = 2 , plan_id = paypal , is_credit = 1, amount = amount )  

    return redirect('bank_bilan')
 


@user_passes_test(user_is_board)
def list_accountings(request,tp):

    active_year, this_year    = get_active_year() 
 

    # if tp == 0 :
    #     accountings = get_accountings(request.user).filter(plan__code__gte=700)
    # elif  tp == 1 :
    #     accountings = get_accountings(request.user).filter(plan__code__gte=600, plan__code__lt=700 )
    # else :
    #     accountings = get_accountings(request.user).exclude(is_paypal=1).exclude(date_payment=None)

    if tp == 0 :
        accountings = Accounting.objects.filter(plan__code__gte=700)
    elif  tp == 1 :
        accountings = Accounting.objects.filter(plan__code__gte=600, plan__code__lt=700 )
    else :
        accountings = Accounting.objects.exclude(is_paypal=1).exclude(date_payment=None)

    accounting_no_payment,  accounting_amount = 0, 0
    accountings_no_payments = accountings.filter(date_payment=None)

    for a in accountings :
        accounting_amount += a.amount
 
    for a in accountings_no_payments :
        accounting_no_payment += a.amount


    active_year, this_year = get_active_year() # active_year = 2020-2021 ALORS QUE this_year est 2020
    today = datetime.now()
    this_month = today.month

    first_date_month =  datetime(this_year, this_month, 1)

    if this_month > 0 and this_month < 9 :
        this_year = this_year - 1
    first_date_schoolyear = datetime(this_year, 1, 1) ##### A CHANGER  

    total_month     = total(first_date_month, today)
    total_shoolyear = total(first_date_schoolyear, today)

 

    return render(request, 'association/list_accounting.html', { 'accounting_amount':accounting_amount,  'accounting_no_payment' : accounting_no_payment   , 'accountings': accountings ,  'active_year' : active_year ,  'tp' : tp , 'total_month': total_month,  'total_shoolyear': total_shoolyear ,'this_month' :this_month })





@user_passes_test(user_is_board)
def ajax_total_month(request):
    data = {}
    month = int(request.POST.get("month"))

    today = datetime.now()
    active_year, this_year = get_active_year() # active_year = 2020-2021 ALORS QUE this_year est 2020
    first = datetime(this_year, month, 1)
    nb_days=[0,31,28,31,30,31,30,31,31,30,31,30,31]
    first = datetime(this_year, month, 1)
    last = datetime(this_year, month, nb_days[month])


    data['html'] = "<label><b>"+str(total(first, last)).replace(".",",")+" € </b></label>"
    rows = Accounting.objects.values_list("id", flat = True).filter(date_payment__lte=last, date_payment__gte=first).exclude(date_payment=None)
    data['rows'] = list(rows)
    data['len']  = len(list(rows))
    return JsonResponse(data)


def str_to_date(date_str):
    dtab = date_str.split("-")
    m = str(dtab[1]).replace("0","")
    return datetime( int(dtab[0]) , int(dtab[1]) , int(dtab[2]) )



@user_passes_test(user_is_board)
def ajax_total_period(request):
    data = {}
    from_date = request.POST.get("from_date",None)
    to_date = request.POST.get("to_date",None)

    if from_date and to_date :
        from_date = str_to_date(from_date)
        to_date = str_to_date(to_date)

        rows = Accounting.objects.values_list("id", flat = True).filter(date_payment__lte=to_date,date_payment__gte=from_date).exclude(date_payment=None)
        data['rows'] = list(rows)
        data['html'] = str(total(from_date, to_date)) +" €"
        data['len']  = len(list(rows))
    else :
        data['html'] = "Sélectionner deux dates"
        data['rows'] = False
        data['len']  = 0
    return JsonResponse(data)






@user_passes_test(user_is_board) 
def create_accounting(request,tp):
 
    form     = AccountingForm(request.POST or None )
    form_abo = AbonnementForm(request.POST or None )
    formSet  = inlineformset_factory( Accounting , Detail , fields=('accounting','description','amount',) , extra=0)
    form_ds  = formSet(request.POST or None)
    today    = datetime.now()


    if tp == 0 :
        template = 'association/form_accounting.html'
    elif tp == 1 :
        template = 'association/form_accounting_depense.html'   
    else :
        template = 'association/form_accounting_bank.html'


    if request.method == "POST":
        if form.is_valid():
            nf = form.save(commit = False)
            nf.user = request.user
            forme = request.POST.get("forme",None)
            nf.chrono = str(uuid.uuid4())[:5]
            if tp == 0 : 
                nf.chrono = create_chrono(Accounting, forme) # Create_chrono dans general_functions.py
            nf.tp = tp
            if tp == 0 :
                nf.plan_id = 23
                if forme == "FACTURE" :
                    nf.is_credit = 1
                else :
                    nf.is_credit = 0
            elif tp == 1 :
                if forme == "AVOIR" :
                    nf.is_credit = 0 
                else :
                    nf.is_credit = 1 
            else :
                nf.date_payment = today
            nf.save()


            form_ds = formSet(request.POST or None, instance = nf)
            for form_d in form_ds :
                if form_d.is_valid():
                    form_d.save()

            som = 0         
            details = nf.details.all()
            for d in details :
                som += d.amount



            if  tp == 1 :
                am =-som 
            else :
                am = som
            Accounting.objects.filter(pk = nf.id).update(amount=am)

            if nf.is_abonnement :
                if form_abo.is_valid():
                    fa = form_abo.save(commit = False)
                    fa.user = request.user
                    fa.accounting = nf
                    fa.school = nf.school
                    if nf.date_payment:
                        fa.is_active = 1

                    fa.save() 

            if request.POST.get("validation_demande",None) and tp == 0 :
                nb = 411
            elif nf.is_paypal :
                nb = 5212
            else :
                nb = 5211

            if tp == 0 :
                if nf.is_credit :
                    if not Accountancy.objects.create(accounting_id = nf.id , ranking = 1 , plan_id = nf.plan.code , is_credit = 1):
                        Accountancy.objects.create(accounting_id = nf.id , ranking = 1 , plan_id = nf.plan.code , is_credit = 1, amount = am )  
                        Accountancy.objects.create(accounting_id = nf.id , ranking = 2 , plan_id = nb , is_credit = 0, amount = -am ) 
                    else :
                        Accountancy.objects.filter(accounting_id = nf.id , ranking = 1 , plan_id = nf.plan.code , is_credit = 1 ).update(amount = am)  
                        Accountancy.objects.filter(accounting_id = nf.id , ranking = 2 , plan_id = nb , is_credit = 0 ).update(amount = -am)  
                else :
                   
                    if not Accountancy.objects.create(accounting_id = nf.id , ranking = 1 , plan_id = nf.plan.code , is_credit = 0):
                        Accountancy.objects.create(accounting_id = nf.id , ranking = 1 , plan_id = nf.plan.code , is_credit = 0, amount = -am )  
                        Accountancy.objects.create(accounting_id = nf.id , ranking = 2 , plan_id = nb , is_credit = 1, amount = am )
                    else :
                        Accountancy.objects.filter(accounting_id = nf.id , ranking = 1 , plan_id = nf.plan.code , is_credit = 0 ).update(amount = -am)  
                        Accountancy.objects.filter(accounting_id = nf.id , ranking = 2 , plan_id = nb , is_credit = 1 ).update(amount = am) 


            elif tp == 2 :

                if nf.is_credit :
                    if not Accountancy.objects.create(accounting_id = nf.id , ranking = 1 , plan_id = nf.plan.code , is_credit = 1):
                        Accountancy.objects.create(accounting_id = nf.id , ranking = 1 , plan_id = nf.plan.code , is_credit = 1, amount = am )  
                        Accountancy.objects.create(accounting_id = nf.id , ranking = 2 , plan_id = nb , is_credit = 0, amount = -am ) 
                    else :
                        Accountancy.objects.filter(accounting_id = nf.id , ranking = 1 , plan_id = nf.plan.code , is_credit = 1 ).update(amount = am)  
                        Accountancy.objects.filter(accounting_id = nf.id , ranking = 2 , plan_id = nb , is_credit = 0 ).update(amount = -am)  
                else :
                   
                    if not Accountancy.objects.create(accounting_id = nf.id , ranking = 1 , plan_id = nf.plan.code , is_credit = 0):
                        Accountancy.objects.create(accounting_id = nf.id , ranking = 1 , plan_id = nf.plan.code , is_credit = 0, amount = -am )  
                        Accountancy.objects.create(accounting_id = nf.id , ranking = 2 , plan_id = nb , is_credit = 1, amount = am )
                    else :
                        Accountancy.objects.filter(accounting_id = nf.id , ranking = 1 , plan_id = nf.plan.code , is_credit = 0 ).update(amount = -am)  
                        Accountancy.objects.filter(accounting_id = nf.id , ranking = 2 , plan_id = nb , is_credit = 1 ).update(amount = am)


            else :

                if nf.is_credit :
                    if not Accountancy.objects.create(accounting_id = nf.id , ranking = 1 , plan_id = nf.plan.code , is_credit = 1):
                        Accountancy.objects.create(accounting_id = nf.id , ranking = 1 , plan_id = nf.plan.code , is_credit = 1, amount = am )  
                        Accountancy.objects.create(accounting_id = nf.id , ranking = 2 , plan_id = nb , is_credit = 0, amount = -am ) 
                    else :
                        Accountancy.objects.filter(accounting_id = nf.id , ranking = 1 , plan_id = nf.plan.code , is_credit = 1 ).update(amount = am)  
                        Accountancy.objects.filter(accounting_id = nf.id , ranking = 2 , plan_id = nb , is_credit = 0 ).update(amount = -am)  
                else :
                   
                    if not Accountancy.objects.create(accounting_id = nf.id , ranking = 1 , plan_id = nf.plan.code , is_credit = 0):
                        Accountancy.objects.create(accounting_id = nf.id , ranking = 1 , plan_id = nf.plan.code , is_credit = 0, amount = -am )  
                        Accountancy.objects.create(accounting_id = nf.id , ranking = 2 , plan_id = nb , is_credit = 1, amount = am )
                    else :
                        Accountancy.objects.filter(accounting_id = nf.id , ranking = 1 , plan_id = nf.plan.code , is_credit = 0 ).update(amount = -am)  
                        Accountancy.objects.filter(accounting_id = nf.id , ranking = 2 , plan_id = nb , is_credit = 1 ).update(amount = am)




        else :
            print(form.errors)
        
        return redirect('list_accountings',tp)
 

    context = {'form': form, 'form_ds': form_ds, 'form_abo' : form_abo , 'tp' : tp , 'accounting' : None }

    return render(request, template , context)



@user_passes_test(user_is_board) 
def renew_accounting(request,ids):
 

    school   = School.objects.get(pk=ids)
    form     = AccountingForm(request.POST or None , initial = { 'school' : school, })
    form_abo = AbonnementForm(request.POST or None )
    formSet  = inlineformset_factory( Accounting , Detail , fields=('accounting','description','amount',) , extra=0)
    form_ds  = formSet(request.POST or None)
    today    = datetime.now()

    if request.method == "POST":
        if form.is_valid():
            nf = form.save(commit = False)
            nf.user = request.user
            forme = request.POST.get("forme",None)
            nf.chrono = str(uuid.uuid4())[:5]
            nf.chrono = create_chrono(Accounting, forme) # Create_chrono dans general_functions.py
            nf.plan_id = 23
            if forme == "FACTURE" :
                nf.is_credit = 1
            else :
                nf.is_credit = 0

            nf.save()

            form_ds = formSet(request.POST or None, instance = nf)
            for form_d in form_ds :
                if form_d.is_valid():
                    form_d.save()

            som = 0         
            details = nf.details.all()
            for d in details :
                som += d.amount

            Accounting.objects.filter(pk = nf.id).update(amount=som)

            if nf.is_abonnement :
                if form_abo.is_valid():
                    fa = form_abo.save(commit = False)
                    fa.user = request.user
                    fa.accounting = nf
                    fa.school = nf.school
                    if nf.date_payment:
                        fa.is_active = 1

                    fa.save()
        else :
            print(form.errors)
        
        return redirect('all_schools',)
 
    context = {'form': form, 'form_ds': form_ds, 'form_abo' : form_abo , 'tp' : 0 , 'accounting' : None }

    return render(request, 'association/form_accounting.html', context)




@user_passes_test(user_is_board)
def update_accounting(request, id,tp):
    ###### Création d'accountancy

    today      = datetime.now()
    accounting = Accounting.objects.get(id=id)
    valeur     = accounting.amount
    school     = accounting.school
    try :
        abonnement = accounting.abonnement 
        form_abo   = AbonnementForm(request.POST or None, instance= abonnement  )
    except :
        abonnement = False
        form_abo   = AbonnementForm(request.POST or None )

    form = AccountingForm(request.POST or None, instance=accounting )
    formSet = inlineformset_factory( Accounting , Detail , fields=('accounting','description','amount') , extra=0)
    form_ds = formSet(request.POST or None, instance = accounting)

    if tp == 0:
        template = 'association/form_accounting.html'
    else :
        template = 'association/form_accounting_bank.html'

    if request.method == "POST":
        if form.is_valid():
            nf = form.save(commit = False)
            nf.user = request.user
            forme = request.POST.get("forme", None)
            nf.chrono = update_chrono(Accounting, accounting, forme)

            date_payment = request.POST.get("date_payment", None)
            if date_payment :
                nf.tp = 2
                nf.is_credit = 1
            nf.save()
            

            for form_d in form_ds :
                if form_d.is_valid():
                    form_d.save()

            som = 0         
            details = nf.details.all()
            for d in details :
                som += d.amount

            Accounting.objects.filter(pk = accounting.id).update( amount = som  )
            
            if nf.is_abonnement :
                if form_abo.is_valid():
                    fa = form_abo.save(commit = False)
                    fa.user = request.user
                    fa.accounting = accounting
                    fa.school = school
                    Accounting.objects.filter(pk = accounting.id).update(is_abonnement = 1)
                    Accounting.objects.filter(pk = accounting.id).update(is_active = 1)
                    fa.is_active = 1
                    fa.save()
                else :
                    print(form_abo.errors)

                # Dans accountancy
                c_year       = Activeyear.objects.filter(is_active = 1).order_by("year").last()
                current_year = c_year.year
                if Accountancy.objects.filter(accounting_id = accounting.id , ranking = 1 , plan_id = 411 , is_credit = 0).count() == 0   : 
       
                    Accountancy.objects.create(accounting_id = accounting.id , ranking = 1 , plan_id = 411 , is_credit = 0 , amount = som , current_year = current_year )  
                    Accountancy.objects.create(accounting_id = accounting.id , ranking = 2 , plan_id = 706 , is_credit = 1 , amount = som , current_year = current_year)
                elif  som != valeur :
                    Accountancy.objects.filter(accounting_id = accounting.id , ranking = 1 , plan_id = 411 , is_credit = 0 ).update(amount = som)  
                    Accountancy.objects.filter(accounting_id = accounting.id , ranking = 2 , plan_id = 706 , is_credit = 1 ).update(amount = som)


                if  nf.date_payment :
                    if Accountancy.objects.filter(accounting_id = accounting.id , ranking = 1 , plan_id = 411 , is_credit = 0).count() == 0   : 
                        Accountancy.objects.create(accounting_id = accounting.id , ranking = 1 , plan_id = 411 , is_credit = 0, amount = som  , current_year = current_year)  
                        Accountancy.objects.create(accounting_id = accounting.id , ranking = 2 , plan_id = 706 , is_credit = 1, amount = som  , current_year = current_year)
                    elif  som != valeur :
                        Accountancy.objects.filter(accounting_id = accounting.id , ranking = 1 , plan_id = 411 , is_credit = 0 ).update(amount = som)  
                        Accountancy.objects.filter(accounting_id = accounting.id , ranking = 2 , plan_id = 706 , is_credit = 1 ).update(amount = som) 

                    if nf.is_paypal : bank = 5122
                    else : bank = 5121  
                    if Accountancy.objects.filter(accounting_id = accounting.id , ranking = 3 , plan_id = 411 , is_credit = 1).count() == 0   : 
                        Accountancy.objects.create(accounting_id = accounting.id , ranking = 3 , plan_id = 411 , is_credit = 1, amount = som  , current_year = current_year)  
                        Accountancy.objects.create(accounting_id = accounting.id , ranking = 4 , plan_id = bank , is_credit = 0 , amount = -som , current_year = current_year)
                    elif  som != valeur :
                        Accountancy.objects.filter(accounting_id = accounting.id , ranking = 3 , plan_id = 411 , is_credit = 1 ).update(amount = som)  
                        Accountancy.objects.filter(accounting_id = accounting.id , ranking = 4 , plan_id = bank  , is_credit = 0 ).update(amount = -som) 



            else :
                if Abonnement.objects.filter(accounting = accounting)  :
                    Abonnement.objects.filter(accounting = accounting).delete()
                    Accounting.objects.filter(pk = accounting.id).update(is_abonnement=0)
                    Accounting.objects.filter(pk = accounting.id).update(is_active=0)
                    messages.success(request,"Abonnement supprimé")
                else :
                    messages.error(request,"Abonnement déjà supprimé ou inexistant.")



            if int(tp) == 0 :
                return redirect('list_accountings', 0)
            elif int(tp) == 2 :
                return redirect('list_accountings', 2) 
            else :
                return redirect('list_paypal') 

        else :
            print(form.errors)
        

        if int(tp) == 0 :
            return redirect('list_accountings', 0)
        elif int(tp) == 2 :
            return redirect('list_accountings', 2) 
        else :
            return redirect('list_paypal') 
    
    context = {'form': form, 'form_ds': form_ds ,  'accounting': accounting,  'form_abo': form_abo, 'abonnement' : abonnement  }

    return render(request, template , context )


###############################################################################
#
#---------------------------------     GAR     --------------------------------
#
###############################################################################
 


def get_the_string_between(content,sub1,sub2) :
    # Récupère la valeur de la clé
    idx1 = content.index(sub1)
    idx2 = content.index(sub2)


    res = ''
    # getting elements in between
    for idx in range(idx1 + len(sub1) , idx2):
        res = res + content[idx]
    return res












@user_passes_test(user_is_board)
def create_avoir(request, id):
 
    accounting = Accounting.objects.get(id=id)
    amount     = accounting.amount
    chronof    = accounting.chrono

    accounting.pk = None
    accounting.amount = amount
    accounting.is_credit = 0

    accounting.forme = "AVOIR"
    chrono = create_chrono(Accounting, "AVOIR")
    accounting.chrono = chrono
    texte = " Avoir sur facture " + chronof
    accounting.objet = texte
    accounting.observation = texte
    accounting.mode = " Avoir sur facture " + chronof
    acc = accounting.save()

    # Création des avoirs
    Accountancy.objects.create(accounting_id = accounting.id , ranking = 1 , plan_id = 411 , is_credit = 1, amount = accounting.amount )  
    Accountancy.objects.create(accounting_id = accounting.id , ranking = 2 , plan_id = 706 , is_credit = 0, amount = -accounting.amount )  
 


    accounti = Accounting.objects.get(id=id) 
    accounti.objet += " Avoir sur " + chronof
    accounti.observation += " Avoir sur " + chronof
    accounti.is_active = 0
    accounti.is_abonnement = 0
    accounti.save()




    return redirect('list_accountings', 0)
    

 



@user_passes_test(user_is_board)
def show_accounting(request, id ):

    accounting = Accounting.objects.get(id=id)
    details = Detail.objects.filter(accounting=accounting)


    context = {  'accounting': accounting, 'details': details,  }

    return render(request, 'association/show_accounting.html', context )





def print_accounting(request, id ):

    accounting = Accounting.objects.get(id=id)

    if not request.user.is_superuser :
        if request.user.school != accounting.school :
            return redirect ("index")

    #########################################################################################
    ### Instanciation
    #########################################################################################
    elements = []        
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="'+str(accounting.chrono)+'.pdf"'
    doc = SimpleDocTemplate(response,   pagesize=A4, 
                                        topMargin=0.5*inch,
                                        leftMargin=0.5*inch,
                                        rightMargin=0.5*inch,
                                        bottomMargin=0.3*inch     )

    sample_style_sheet = getSampleStyleSheet()
    OFFSET_INIT = 0.2
    #########################################################################################
    ### Style
    #########################################################################################
    sacado = ParagraphStyle('sacado', 
                            fontSize=20, 
                            leading=26,
                            borderPadding = 0,
                            alignment= TA_CENTER,
                            )
    bas_de_page = ParagraphStyle('sacado', 
                            fontSize=9, 
                            borderPadding = 0,
                            alignment= TA_CENTER,
                            )
    bas_de_page_blue = ParagraphStyle('sacado', 
                            fontSize=9, 
                            borderPadding = 0,
                            alignment= TA_CENTER,
                            textColor=colors.HexColor("#00819f"),
                            )

    title = ParagraphStyle('title', 
                            fontSize=16, 
                            )

    subtitle = ParagraphStyle('title', 
                            fontSize=14, 
                            textColor=colors.HexColor("#00819f"),
                            )
 
    mini = ParagraphStyle(name='mini',fontSize=9 )  

    normal = ParagraphStyle(name='normal',fontSize=12,)   

    dateur_style = ParagraphStyle('dateur_style', 
                            fontSize=12, 
                            leading=26,
                            borderPadding = 0,
                            alignment= TA_RIGHT,
                            )
    signature_style = ParagraphStyle('dateur_style', 
                            fontSize=11, 
                            borderPadding = 0,
                            alignment= TA_RIGHT,
                            )
    signature_style_mini = ParagraphStyle('dateur_style', 
                            fontSize=9, 
                            borderPadding = 0,
                            alignment= TA_RIGHT,
                            )
    signature_style_blue = ParagraphStyle('dateur_style', 
                            fontSize=12, 
                            borderPadding = 0,
                            alignment= TA_RIGHT,
                            textColor=colors.HexColor("#00819f"),
                            )

    style_cell = TableStyle(
            [
                ('SPAN', (0, 1), (1, 1)),
                ('TEXTCOLOR', (0, 1), (-1, -1),  colors.Color(0,0.7,0.7))
            ]
        )
    offset = 0 # permet de placer le bas de page
    #########################################################################################
    ### Logo Sacado
    #########################################################################################
    dateur = "Date : " + accounting.date.strftime("%d-%m-%Y")
    logo = Image('https://sacado.xyz/static/img/sacadoA1.png')
    logo_tab = [[logo, "Association SacAdo\nhttps://sacado.xyz \nassociation@sacado.xyz", dateur]]
    logo_tab_tab = Table(logo_tab, hAlign='LEFT', colWidths=[0.7*inch,5.2*inch,inch])
    elements.append(logo_tab_tab)
    #########################################################################################
    ### Facture
    #########################################################################################
    elements.append(Spacer(0,0.3*inch))
    f = Paragraph( accounting.forme , sacado )
    elements.append(f) 
    #########################################################################################
    ### Bénéficiaire ou Etablissement
    #########################################################################################
    if accounting.school :
        beneficiaire = accounting.school.name
        address = accounting.school.address
        complement = accounting.school.complement
        town = accounting.school.town 
        country = accounting.school.country.name
        zip_code = accounting.school.zip_code
        contact = ""
        name_contact = ""
        for u in accounting.school.users.filter(is_manager=1) :
            contact += u.email +" "
            name_contact += u.last_name +" " + u.first_name +" - "
    else :    
        beneficiaire = accounting.beneficiaire
        address = accounting.address
        complement = accounting.complement
        zip_code = accounting.school.zip_code
        town = accounting.town 
        country = accounting.country.name
        contact = accounting.contact
        name_contact = ""

    beneficiaire = Paragraph( beneficiaire  , signature_style )
    elements.append(beneficiaire)
    elements.append(Spacer(0,0.1*inch))
    if address :
        address = Paragraph( address , signature_style_mini )
        elements.append(address)
        offset += OFFSET_INIT

    if complement :
        compl = Paragraph( complement , signature_style_mini )
        elements.append(compl)
        offset += OFFSET_INIT

    if zip_code :
        complementz = Paragraph( zip_code , signature_style_mini )
        elements.append(complementz)
        offset += OFFSET_INIT

    town = Paragraph( town + " - " + country , signature_style_mini )
    elements.append(town)


    #########################################################################################
    ### Code de facture
    #########################################################################################
 
    elements.append(Spacer(0,0.5*inch))
    code = Paragraph( accounting.forme+" "+accounting.chrono , normal )
    elements.append(code)
    elements.append(Spacer(0,0.1*inch))
    objet = Paragraph(  "Objet : "+accounting.objet , normal )
    elements.append(objet) 
    elements.append(Spacer(0,0.1*inch))
    licence = Paragraph(  "Licence : "+str(accounting.school.nbstudents)+" élèves" , normal )
    elements.append(licence) 
    elements.append(Spacer(0,0.2*inch))


    #########################################################################################
    ### Description de facturation
    #########################################################################################
    details_tab = [("Description", "Qté", "Px unitaire HT" ,  "Px Total HT" )]

    details = Detail.objects.filter(accounting = accounting)

    for d in details :
        details_tab.append((d.description, "1" , d.amount ,  d.amount ))
        offset += OFFSET_INIT
                
    details_table = Table(details_tab, hAlign='LEFT', colWidths=[4.1*inch,1*inch,1*inch,1*inch])
    details_table.setStyle(TableStyle([
               ('INNERGRID', (0,0), (-1,-1), 0.25, colors.gray),
               ('BOX', (0,0), (-1,-1), 0.25, colors.gray),
                ('BACKGROUND', (0,0), (-1,0), colors.Color(1,1,1))
               ]))
    elements.append(details_table)

    #########################################################################################
    ### Total de facturation
    #########################################################################################
    elements.append(Spacer(0,0.1*inch))
    details_tot = Table([("Total HT", str( accounting.amount) +"€" ), ("Net à payer en euros", str( accounting.amount) +"€" )], hAlign='RIGHT', colWidths=[2.8*inch,1*inch])
    details_tot.setStyle(TableStyle([
               ('INNERGRID', (0,0), (-1,-1), 0.25, colors.gray),
               ('BOX', (0,0), (-1,-1), 0.25, colors.gray),
                ('BACKGROUND', (0,0), (-1,0), colors.Color(0.9,0.9,0.9))
               ]))
    elements.append(details_tot)

    #########################################################################################
    ### TVA non applicable
    #########################################################################################

    elements.append(Spacer(0,0.1*inch)) 
    tva = Paragraph(  "« TVA non applicable, suivant article 293-b du CGI. »"  , signature_style_mini )
    elements.append(tva)


    #########################################################################################
    ### Observation
    #########################################################################################
    offs = 0
    if accounting.observation  :
        elements.append(Spacer(0,0.4*inch)) 

        
        for text in cleantext(accounting.observation) :
            observation = Paragraph( text , normal )
            elements.append(observation)
            elements.append(Spacer(0,0.1*inch))
            offs +=0.15 




 
    #########################################################################################
    ### Reglement facture
    #########################################################################################
    elements.append(Spacer(0,1*inch)) 
    label_facture = ""
    if accounting.date_payment  :
        label_facture = "Facture réglée le " + str(accounting.date_payment.strftime("%d-%m-%Y")) +" "+accounting.mode

    facture = Paragraph(  label_facture  , normal )
    elements.append(facture)
    offs +=1

    offset = offs + OFFSET_INIT


    #########################################################################################
    ### Bas de page
    #########################################################################################
    nb_inches = 4.4 - offset
    elements.append(Spacer(0,nb_inches*inch)) 
    asso = Paragraph(  "___________________________________________________________________"  , bas_de_page_blue )
    elements.append(asso)
    asso2 = Paragraph( "Association SacAdo"  , bas_de_page )
    elements.append(asso2)
    asso3 = Paragraph( "siren : 903345569"  , bas_de_page )
    elements.append(asso3)
    asso30 = Paragraph( "siret : 903345569 00011"  , bas_de_page )
    elements.append(asso30)
    asso4 = Paragraph( "2B Avenue de la pinède, La Capte, 83400 Hyères - FRANCE"  , bas_de_page )
    elements.append(asso4)

    doc.build(elements)

    return response
 




def print_bilan(request):

    date_start = request.POST.get("date_start")
    date_end   = request.POST.get("date_end")
    envoi      = request.POST.get("envoi") 
    date_start_obj = datetime.strptime(date_start, '%Y-%m-%d')
    date_end_obj   = datetime.strptime(date_end, '%Y-%m-%d')
    OFFSET_INIT = 0.2

    accountings = Accounting.objects.filter(date__gte=date_start_obj, date__lte=date_end_obj)
    #########################################################################################
    ### Instanciation
    #########################################################################################
    elements = []        
    response = HttpResponse(content_type='application/pdf')


    response['Content-Disposition'] = 'attachment; filename="Bilans.pdf"'
    doc = SimpleDocTemplate(response,   pagesize=A4, 
                                        topMargin=0.5*inch,
                                        leftMargin=0.5*inch,
                                        rightMargin=0.5*inch,
                                        bottomMargin=0.3*inch     )

    sample_style_sheet = getSampleStyleSheet()
    #########################################################################################
    ### Style
    #########################################################################################
    sacado = ParagraphStyle('sacado', 
                            fontSize=20, 
                            leading=26,
                            borderPadding = 0,
                            alignment= TA_CENTER,
                            )
    sacado_mini = ParagraphStyle('sacado', 
                            fontSize=14, 
                            leading=26,
                            borderPadding = 0,
                            alignment= TA_CENTER,
                            )
    bas_de_page = ParagraphStyle('sacado', 
                            fontSize=9, 
                            borderPadding = 0,
                            alignment= TA_CENTER,
                            )
    bas_de_page_blue = ParagraphStyle('sacado', 
                            fontSize=9, 
                            borderPadding = 0,
                            alignment= TA_CENTER,
                            textColor=colors.HexColor("#00819f"),
                            )
    title = ParagraphStyle('title', 
                            fontSize=16, 
                            )
    subtitle = ParagraphStyle('title', 
                            fontSize=14, 
                            textColor=colors.HexColor("#00819f"),
                            )
    mini = ParagraphStyle(name='mini',fontSize=9 )  
    normal = ParagraphStyle(name='normal',fontSize=12,)   
    dateur_style = ParagraphStyle('dateur_style', 
                            fontSize=12, 
                            leading=26,
                            borderPadding = 0,
                            alignment= TA_RIGHT,
                            )
    signature_style = ParagraphStyle('dateur_style', 
                            fontSize=11, 
                            borderPadding = 0,
                            alignment= TA_RIGHT,
                            )
    signature_style_mini = ParagraphStyle('dateur_style', 
                            fontSize=9, 
                            borderPadding = 0,
                            alignment= TA_RIGHT,
                            )
    signature_style_blue = ParagraphStyle('dateur_style', 
                            fontSize=12, 
                            borderPadding = 0,
                            alignment= TA_RIGHT,
                            textColor=colors.HexColor("#00819f"),
                            )
    style_cell = TableStyle(
            [
                ('SPAN', (0, 1), (1, 1)),
                ('TEXTCOLOR', (0, 1), (-1, -1),  colors.Color(0,0.7,0.7))
            ]
        )

    offset = 0 # permet de placer le bas de page
    #########################################################################################
    ### Logo Sacado
    #########################################################################################
    logo = Image('https://sacado.xyz/static/img/sacadoA1.png')
    logo_tab = [[logo, "Association SacAdo \nContact : assocation@sacado.xyz"]]
    logo_tab_tab = Table(logo_tab, hAlign='LEFT', colWidths=[0.7*inch,5.52*inch])
    logo_tab_tab.setStyle(TableStyle([ ('TEXTCOLOR', (0,0), (-1,0), colors.Color(0,0.5,0.62))]))
    elements.append(logo_tab_tab)
    #########################################################################################
    ### Facture
    #########################################################################################
    elements.append(Spacer(0,0.3*inch))
    bilan = Paragraph( "Bilans" , sacado )
    elements.append(bilan) 
    #########################################################################################
    ### Bénéficiaire ou Etablissement
    #########################################################################################
    date_s = Paragraph(  date_start + " - " + date_end , sacado_mini )
    elements.append(date_s)
    elements.append(Spacer(0,0.2*inch))  

    details_tab = []
    som = 0 
    i = 0
    for a in accountings :
        if a.beneficiaire :
            bene = a.beneficiaire
        else :
            bene = a.school.name
        details_tab.append((a.date.strftime("%d %b %Y")+ ": "+bene +" "+a.objet,  a.amount ))
        offset += OFFSET_INIT
        som += a.amount
        i+=1
        if i == 30 :
            elements.append(PageBreak())
                
    details_table = Table(details_tab, hAlign='LEFT', colWidths=[6.3*inch,1*inch])
    details_table.setStyle(TableStyle([
               ('INNERGRID', (0,0), (-1,-1), 0.25, colors.gray),
               ('BOX', (0,0), (-1,-1), 0.25, colors.gray),
                ('BACKGROUND', (0,0), (-1,0), colors.Color(1,1,1))
               ]))
    elements.append(details_table)
    #########################################################################################
    ### Total de facturation
    #########################################################################################
    elements.append(Spacer(0,0.1*inch))
    details_tot = Table([("Total TTC en euros", som  )], hAlign='LEFT', colWidths=[6.3*inch,1*inch])
    details_tot.setStyle(TableStyle([
               ('INNERGRID', (0,0), (-1,-1), 0.25, colors.gray),
               ('BOX', (0,0), (-1,-1), 0.25, colors.gray),
                ('BACKGROUND', (0,0), (-1,0), colors.Color(0.9,0.9,0.9))
               ]))
    elements.append(details_tot)
    #########################################################################################
    ### Signature Bruno
    #########################################################################################

    elements.append(Spacer(0,inch)) 
    signature = Paragraph(  "_______________________________"  , signature_style_blue )
    elements.append(signature)
    elements.append(Spacer(0,0.1*inch)) 
    signature2 = Paragraph( "Bruno Serres                     "  , signature_style )
    elements.append(signature2)
    signature2 = Paragraph( "Trésorier de l'association SacAdo"  , signature_style_mini )
    elements.append(signature2)
    #########################################################################################
    ### Bas de page
    #########################################################################################
    nb_inches = 4.6 - offset
    elements.append(Spacer(0,nb_inches*inch)) 
    asso = Paragraph(  "___________________________________________________________________"  , bas_de_page_blue )
    elements.append(asso)
    asso2 = Paragraph( "Association SacAdo"  , bas_de_page )
    elements.append(asso2)
    asso3 = Paragraph( "siren : 903345569"  , bas_de_page )
    elements.append(asso3)
    asso4 = Paragraph( "2B Avenue de la pinède, La Capte, 83400 Hyères"  , bas_de_page )
    elements.append(asso4)

    doc.build(elements)

    return response


def export_bilan(request):

    date_start = request.POST.get("date_start")
    date_end   = request.POST.get("date_end")
    envoi      = request.POST.get("envoi")
    date_start_obj = datetime.strptime(date_start, '%Y-%m-%d')
    date_end_obj   = datetime.strptime(date_end, '%Y-%m-%d')

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="bilans.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet(date_start+'-'+date_end)

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Date', 'Date de valeur',  'Crédit/Débit', 'Objet', "Bénéficiaire", 'Etablissement', 
                'Address','Complément', 'Ville', 'Pays', 'Contact', 
                'Observation', 'Montant', 'Emetteur']

 
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()


    accountings = Accounting.objects.filter(date_payment__gte=date_start_obj, date_payment__lte=date_end_obj).values_list('date', 'date_payment', 'is_credit' , 'objet', 'beneficiaire','school', 'address', 'complement',  'town', 'country', 'contact', 'observation', 'amount', 'user' ).order_by("date")
    ############  Gestion des selects multiples #####################################
    row_n = 0
    for accounting in accountings :
        row_n += 1
 
 
        for col_num in range(len(accounting)):
            
            if col_num == 0 : 
                content =  accounting[col_num].strptime(date_start, '%Y-%m-%d')
            elif col_num == 1 :
                content =  accounting[col_num].strptime(date_start, '%Y-%m-%d')
            elif col_num == 2 :
                if  accounting[2] :
                    content = "Crédit"
                else :
                    content = "Débit"
            elif col_num == 11 :         
                content =  cleanhtml(str(unescape_html(accounting[col_num]))) 
            elif col_num == 13 :  
                user = User.objects.get(pk=accounting[col_num])       
                content =  user.last_name+ " "+  user.first_name 
            else :
                content =  accounting[col_num]
 
            if content  :           
                ws.write(row_n, col_num, content , font_style)
 
    wb.save(response)
    return response
 

#####################################################################################################################################
#####################################################################################################################################
####    Associate
#####################################################################################################################################
#####################################################################################################################################


@user_passes_test(user_is_board)
def list_associate(request):
    user = request.user
    associates = Associate.objects.filter(is_active = 1)
    pending_associates = Associate.objects.filter(is_active = 0)

    nb_total = User.objects.filter(user_type=0).exclude(username__contains="_e-test_").count()

    return render(request, 'association/list_associate.html', {'associates': associates , 'pending_associates': pending_associates , 'user' : user  , 'nb_total':nb_total  })


@user_passes_test(user_is_board) 
def create_associate(request):
 
    form = AssociateForm(request.POST or None )

    if form.is_valid():
        nf = form.save(commit = False)
        nf.author = request.user
        nf.save()


        return redirect('list_associate')

    else:
        
        print(form.errors)

    context = {'form': form, }

    return render(request, 'association/form_associate.html', context)



@user_passes_test(user_is_board)
def update_associate(request, id):

    associate = Associate.objects.get(id=id)
    
    form = AssociateForm(request.POST or None, instance=associate )

    if form.is_valid():
        nf = form.save(commit = False)
        nf.author = request.user
        return redirect('list_associate')
    else:
        print(form.errors)

    context = {'form': form,  'associate': associate,  }

    return render(request, 'association/form_associate.html', context )



@user_passes_test(user_is_board)
def delete_associate(request, id):

    associate = Associate.objects.get(id=id)
    associate.delete()
    return redirect('list_associate')
    

 
@user_passes_test(user_is_board)
def accept_associate(request, id):
    Associate.objects.filter(id=id).update(is_active = 1)
    return redirect('list_associate')

#####################################################################################################################################
#####################################################################################################################################
####    Voting
#####################################################################################################################################
#####################################################################################################################################
 



@user_passes_test(user_is_board) 
def create_voting(request,id):
 
    form = VotingForm(request.POST or None )

    if form.is_valid():
        nf = form.save(commit = False)
        nf.user = request.user
        nf.associate_id = id
        nf.save()
        try : 
            rcv = ["sacado.asso@gmail.com"]
            msg = "Une proposition de membre est postée par "+str(request.user)+". Rendez-vous sur https://sacado.xyz"
            send_mail("Proposition de membre", msg , 'info@sacado.xyz', rcv)
        except :
            pass
        return redirect('list_associate')

    else:
        print(form.errors)

    context = {'form': form,   }

    return render(request, 'association/form_voting.html', context)


 


 

@user_passes_test(user_is_board)
def show_voting(request, id):

    voting = Voting.objects.get(id=id)
    context = {  'voting': voting,   }

    return render(request, 'association/show_voting.html', context)




#####################################################################################################################################
#####################################################################################################################################
####    Section
#####################################################################################################################################
#####################################################################################################################################
 

@user_passes_test(user_is_board) 
def create_section(request):

    sections = Section.objects.all()
    form = SectionForm(request.POST or None )

    if form.is_valid():
        form.save()

        return redirect('create_document')
    else:
        print(form.errors)

    context = {'form': form, 'sections' : sections }

    return render(request, 'association/form_section.html', context)



@user_passes_test(user_is_board)
def update_section(request, id):

    sections = Section.objects.all()
    section = Section.objects.get(id=id)
    
    form = SectionForm(request.POST or None, instance=section )

    if form.is_valid():
        form.save()
        return redirect('list_documents')
    else:
        print(form.errors)

    context = {'form': form,  'section': section, 'sections' : sections   }

    return render(request, 'association/form_section.html', context )



@user_passes_test(user_is_board)
def delete_section(request, id):

    section = Section.objects.get(id=id)
    section.delete()
    return redirect('create_section')
    
 





@user_passes_test(user_is_board)
def list_documents(request):
    documents = Document.objects.order_by("section", "date_modified")
    document =  documents.first()
    return render(request, 'association/show_document.html', { 'documents': documents , 'document': document  })


@user_passes_test(user_is_board) 
def create_document(request):
 
    form = DocumentForm(request.POST or None )

    if form.is_valid():
        nf = form.save(commit = False)
        nf.user = request.user
        nf.save()

        return redirect('list_documents')
    else:
        print(form.errors)

    context = {'form': form, }

    return render(request, 'association/form_document.html', context)



@user_passes_test(user_is_board)
def update_document(request, id):

 
    document = Document.objects.get(id=id)
    
    form = DocumentForm(request.POST or None, instance=document )

    if form.is_valid():
        nf = form.save(commit = False)
        nf.user = request.user
        nf.save()
        return redirect('list_documents')
    else:
        print(form.errors)

    context = {'form': form,  'document': document,  }

    return render(request, 'association/form_document.html', context )



@user_passes_test(user_is_board)
def delete_document(request, id):

    document = Document.objects.get(id=id)
    document.delete()
    return redirect('list_documents')


 
def ajax_shower_document(request):
    document_id =  int(request.POST.get("document_id"))
    document =  Document.objects.get(pk=document_id)
    data = {}
 
    context = {  'document': document   }
 
    data['html'] = render_to_string('association/ajax_shower_document.html', context)

    return JsonResponse(data)


#####################################################################################################################################
#####################################################################################################################################
####    Rate
#####################################################################################################################################
#####################################################################################################################################
@user_passes_test(user_is_board)
def list_rates(request):
    formules = Formule.objects.all()
    rates = Rate.objects.all()
    return render(request, 'association/list_rate.html', {'rates': rates , 'formules': formules   })


@user_passes_test(user_is_board)
def show_rate(request):

    rates = Rate.objects.filter(is_active = 1).order_by("quantity")
    return render(request, 'association/list_rate.html', {'rates': rates ,     })


@user_passes_test(user_is_board) 
def create_rate(request):
 
    form = RateForm(request.POST or None )

    if form.is_valid():
        nf = form.save(commit = False)
        nf.author = request.user
        nf.save()


        return redirect('list_rates')

    else:
        
        print(form.errors)

    context = {'form': form, }

    return render(request, 'association/form_rate.html', context)



@user_passes_test(user_is_board)
def update_rate(request, id):

    rate = Rate.objects.get(id=id)
    
    form = RateForm(request.POST or None, instance=rate )

    if form.is_valid():
        nf = form.save(commit = False)
        nf.author = request.user
        return redirect('list_rates')
    else:
        print(form.errors)

    context = {'form': form,  'rate': rate,  }

    return render(request, 'association/form_rate.html', context )



@user_passes_test(user_is_board)
def delete_rate(request, id):

    rate = Rate.objects.get(id=id)
    rate.delete()
    return redirect('list_rates')
    
 



@user_passes_test(user_is_board)
def reset_all_students_sacado(request):

    Parent.objects.all().delete()
    Response.objects.all().delete() 
    User.objects.filter(user_type=0).exclude(username__contains= "_e-test").delete()
    messages.success(request,"Ré-initialisation effectuée avec succès.")


    return redirect('association_index')






@user_passes_test(user_is_board)
def create_all_holidays_book(request):

    levels_ids = [1,2,3,4,5,6,7,8,9,10,11,14]
    teachers   = [89513,89507,89508,89510,89511,46245,46242,46246,46247,46222,46243,130243]
    


    t  = 0
    for level_id in levels_ids :
        group   = Group.objects.filter(name="Cahier Vacances", level_id = level_id , subject_id= 1).last()


        # first_name = "SacAdo"
        # last_name  = "Prof" 
        # username   = "SacAdoProf"+str(level_id)+"_e-test"
        # password   = make_password("sacado2020")  
        # email      = ""

        # user,created_u = User.objects.get_or_create(username=username , defaults= { 'last_name' : last_name, 'first_name' : first_name,  'password' : password , 'email' : email, 'user_type' : 0})
        # student ,cr    = Student.objects.get_or_create(user=user, level_id=level_id, code= str(uuid.uuid4())[:8]  )
        # group.students.add(student)

        for i in range(1,21):
            vignette = "vignettes/46247/J"+str(i)+"_3.png"
            colors   = ['#9100cb','#d000c0','#E700E3','#FF0000','#781798','#2759F6','#007CFF','#70DD7F','#FF00AF','#008bff','#0CB4A6','#ffb100','#3ad3bd','#ff00fb','#3e7fb7','#00c8ff','#4a9b85','#FB009D','#74ea5d','#008bff']
            p  = Parcours.objects.filter( title = "Jour"+str(i) , color = colors[i-1] ,   subject_id = 1 ,  level_id = level_id , vignette =  vignette , is_sequence = 1).last()
            p.ranking=i
            p.save()
        t += 1


    messages.success(request,"Création des groupes et séquences effectuée avec succès.")


    return redirect('association_index')



def customer(request,idp):

    parent   = Parent.objects.get(user_id=idp)

    context = {'parent': parent, }

    return render(request, 'association/customer.html', context )




@user_passes_test(user_is_board) 
def create_invoice(request,idp):

    form     = InvoiceForm(request.POST or None )
    formSet  = inlineformset_factory( Invoice , Subinvoice , fields=('invoice','description','amount',) , extra=1)
    form_ds  = formSet(request.POST or None)
 

    if idp : parent = Parent.objects.get(user__id=idp)  
    else :   parent = ""     

    if request.method == "POST":
        if form.is_valid():
            nf        = form.save(commit = False)

            if idp : nf.parent = parent

            forme     = request.POST.get("forme",None)
            nf.chrono = create_chrono(Invoice, forme) # Create_chrono dans general_functions.py
            nf.save()

            print(nf)

            form_ds = formSet(request.POST or None, instance = nf)
            for form_d in form_ds :
                if form_d.is_valid():
                    form_d.save()
                else :
                    print(form_d.errors)

            som = 0         
            details = nf.subinvoices.all()
            for d in details :
                som += d.amount
            Invoice.objects.filter(pk = nf.id).update(amount=som)

        else :
            print(form.errors)
        
        return redirect('list_invoices')
 

    context = {'form': form, 'form_ds': form_ds,  'invoice' : None , 'parent' : parent , 'idp' : idp }

    return render(request, 'association/form_invoice.html' , context)



def update_invoice(request,idp,idi):


    invoice = Invoice.objects.get(id=idi)
    form    = InvoiceForm(request.POST or None, instance = invoice)
    formSet = inlineformset_factory( Invoice , Subinvoice , fields=('invoice','description','amount') , extra=0)
    form_ds = formSet(request.POST or None, instance = invoice)
 

    if idp : parent = Parent.objects.get(user__id=idp)

    if request.method == "POST":
        if form.is_valid():
            nf = form.save(commit = False)

            if idp : nf.parent = parent 

            forme     = request.POST.get("forme",None)
            nf.chrono = create_chrono(Invoice, forme) # Create_chrono dans general_functions.py
            nf.save()

            form_ds = formSet(request.POST or None, instance = nf) 
            for form_d in form_ds :
                if form_d.is_valid():
                    form_d.save()
                else :
                    print(form_d.errors)

            som = 0         
            details = nf.subinvoices.all()
            for d in details :
                som += d.amount
            Invoice.objects.filter(pk = nf.id).update(amount=som)

        else :
            print(form.errors)
        
        return redirect('list_invoices')
 

    context = {'form': form, 'form_ds': form_ds,  'invoice' : None , 'idp' : idp }

    return render(request, 'association/form_invoice.html' , context)





@user_passes_test(user_is_board)
def delete_invoice(request,idp,idi):

    invoice = Invoice.objects.get(id=idi)
    invoice.delete()
    messages.success(request,"Suppression réussie")
    if idp == 0 :
        return redirect('list_invoices')
    else :
        return redirect('customer',idp)

 

@user_passes_test(user_is_board)
def list_invoices(request):

    invoices = Invoice.objects.order_by("parent__user__last_name")
    return render(request, 'association/list_invoices.html', { 'invoices':invoices,  })





def print_invoice(request, idi ):

    invoice = Invoice.objects.get(id=idi)

    if not request.user.is_superuser :
        if request.user != invoice.parent.user :
            return redirect ("index")

    #########################################################################################
    ### Instanciation
    #########################################################################################
    elements = []        
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="'+str(invoice.chrono)+'.pdf"'
    doc = SimpleDocTemplate(response,   pagesize=A4, 
                                        topMargin=0.5*inch,
                                        leftMargin=0.5*inch,
                                        rightMargin=0.5*inch,
                                        bottomMargin=0.3*inch     )

    sample_style_sheet = getSampleStyleSheet()
    OFFSET_INIT = 0.2
    #########################################################################################
    ### Style
    #########################################################################################
    sacado = ParagraphStyle('sacado', 
                            fontSize=20, 
                            leading=26,
                            borderPadding = 0,
                            alignment= TA_CENTER,
                            )
    bas_de_page = ParagraphStyle('sacado', 
                            fontSize=9, 
                            borderPadding = 0,
                            alignment= TA_CENTER,
                            )
    bas_de_page_blue = ParagraphStyle('sacado', 
                            fontSize=9, 
                            borderPadding = 0,
                            alignment= TA_CENTER,
                            textColor=colors.HexColor("#00819f"),
                            )
    title = ParagraphStyle('title', 
                            fontSize=16, 
                            )
    subtitle = ParagraphStyle('title', 
                            fontSize=14, 
                            textColor=colors.HexColor("#00819f"),
                            )
    mini = ParagraphStyle(name='mini',fontSize=9 )  
    normal = ParagraphStyle(name='normal',fontSize=12,)   
    dateur_style = ParagraphStyle('dateur_style', 
                            fontSize=12, 
                            leading=26,
                            borderPadding = 0,
                            alignment= TA_RIGHT,
                            )
    signature_style = ParagraphStyle('dateur_style', 
                            fontSize=11, 
                            borderPadding = 0,
                            alignment= TA_RIGHT,
                            )
    signature_style_mini = ParagraphStyle('dateur_style', 
                            fontSize=9, 
                            borderPadding = 0,
                            alignment= TA_RIGHT,
                            )
    signature_style_blue = ParagraphStyle('dateur_style', 
                            fontSize=12, 
                            borderPadding = 0,
                            alignment= TA_RIGHT,
                            textColor=colors.HexColor("#00819f"),
                            )
    style_cell = TableStyle(
            [
                ('SPAN', (0, 1), (1, 1)),
                ('TEXTCOLOR', (0, 1), (-1, -1),  colors.Color(0,0.7,0.7))
            ]
        )
    offset = 0 # permet de placer le bas de page
    #########################################################################################
    ### Logo Sacado
    #########################################################################################
    dateur = "Date : " + invoice.date.strftime("%d-%m-%Y")
    logo = Image('https://sacado-academie.fr/static/img/sanspb.png')
    logo_tab = [[logo, "SANSPB\nhttps://sacado-academie.fr\nsacado.academie@gmail.com", dateur]]
    logo_tab_tab = Table(logo_tab, hAlign='LEFT', colWidths=[0.7*inch,5.2*inch,inch])
    elements.append(logo_tab_tab)
    #########################################################################################
    ### Facture
    #########################################################################################
    elements.append(Spacer(0,0.3*inch))
    f = Paragraph( invoice.forme , sacado )
    elements.append(f) 
    #########################################################################################
    ### Bénéficiaire ou Etablissement
    #########################################################################################
    if invoice.parent :
        beneficiaire = invoice.parent.user.last_name + " "+invoice.parent.user.first_name
        address = invoice.parent.user.email
        complement = ""
        town = ""
        country = ""
        contact = ""
 
    else :    
        beneficiaire = invoice.beneficiaire
        address = invoice.address
        complement = invoice.complement
        town = invoice.town 
        country = invoice.country.name
        contact = invoice.contact

    beneficiaire = Paragraph( beneficiaire  , signature_style )
    elements.append(beneficiaire)
    elements.append(Spacer(0,0.1*inch))
    if address :
        address = Paragraph( address , signature_style_mini )
        elements.append(address)
        offset += OFFSET_INIT

    if complement :
        compl = Paragraph( complement , signature_style_mini )
        elements.append(compl)
        offset += OFFSET_INIT

    town = Paragraph( town + " - " + country , signature_style_mini )
    elements.append(town)


    #########################################################################################
    ### Code de facture
    #########################################################################################
 
    elements.append(Spacer(0,0.5*inch))
    code = Paragraph( invoice.forme+" "+invoice.chrono , normal )
    elements.append(code)
    elements.append(Spacer(0,0.1*inch))
    objet = Paragraph(  "Objet : "+invoice.objet , normal )
    elements.append(objet) 
    elements.append(Spacer(0,0.2*inch))


    #########################################################################################
    ### Description de facturation
    #########################################################################################
    details_tab = [("Description", "Qté", "Px unitaire HT" ,  "Px Total HT" )]

    details = Subinvoice.objects.filter(invoice = invoice)

    for d in details :
        details_tab.append((d.description, "1" , d.amount ,  d.amount ))
        offset += OFFSET_INIT
                
    details_table = Table(details_tab, hAlign='LEFT', colWidths=[4.1*inch,1*inch,1*inch,1*inch])
    details_table.setStyle(TableStyle([
               ('INNERGRID', (0,0), (-1,-1), 0.25, colors.gray),
               ('BOX', (0,0), (-1,-1), 0.25, colors.gray),
                ('BACKGROUND', (0,0), (-1,0), colors.Color(1,1,1))
               ]))
    elements.append(details_table)

    #########################################################################################
    ### Total de facturation
    #########################################################################################
    elements.append(Spacer(0,0.1*inch))
    details_tot = Table(["Hors taxe", str( invoice.amount) +"€" , "TVA 20%", str( round(float(invoice.amount) * 0.2,2)) +"€" , "Total TTC", str( round(float(invoice.amount) * 1.2,2)) +"€" ], hAlign='RIGHT', colWidths=[2.8*inch,1*inch])
    details_tot.setStyle(TableStyle([
               ('INNERGRID', (0,0), (-1,-1), 0.25, colors.gray),
               ('BOX', (0,0), (-1,-1), 0.25, colors.gray),
                ('BACKGROUND', (0,0), (-1,0), colors.Color(0.9,0.9,0.9))
               ]))
    elements.append(details_tot)
    #########################################################################################
    ### Observation
    #########################################################################################
    offs = 0
    if invoice.observation  :
        elements.append(Spacer(0,0.4*inch)) 

        
        for text in cleantext(invoice.observation) :
            observation = Paragraph( text , normal )
            elements.append(observation)
            elements.append(Spacer(0,0.1*inch))
  

    #########################################################################################
    ### TVA non applicable
    #########################################################################################

    elements.append(Spacer(0,0.1*inch))

    tva1 = "Paiement :"  
    bic1 = Paragraph(  tva1  , signature_style_mini )
    tva2 = "Domiciliation : Crédit Agricole Daglan"
    bic2 = Paragraph(  tva2  , signature_style_mini )
    tva3 = "Code Banque : 12406 Code Guichet : 00005" 
    bic3 = Paragraph(  tva3  , signature_style_mini ) 
    tva4 = "Numéro de compte : 80023056082 Clé RIB : 56" 
    bic4 = Paragraph(  tva4  , signature_style_mini )
    tva5 = "IBAN ( International Bank Account Number ) : FR76 1240 6000 0580 0230 5608 256" 
    bic5 = Paragraph(  tva5  , signature_style_mini )
    tva6 = "Code BIC ( Bank Identification Code ) - Code SWIFT : AGRIFRPP824"  
    bic6 = Paragraph(  tva6  , signature_style_mini )
    tva7 = "Pas d'escompte pour réglement anticipé"  
    bic7 = Paragraph(  tva7  , signature_style_mini )
    elements.append(bic1)
    elements.append(bic2)
    elements.append(bic3)
    elements.append(bic4)
    elements.append(bic5)
    elements.append(bic6)
    elements.append(bic7)





    #########################################################################################
    ### Bas de page
    #########################################################################################
    nb_inches = 3.4 - offset
    elements.append(Spacer(0,nb_inches*inch)) 
    asso = Paragraph(  "___________________________________________________________________"  , bas_de_page_blue )
    elements.append(asso)
    asso2 = Paragraph( "SANS PB"  , bas_de_page )
    elements.append(asso2)
    asso21 = Paragraph( "265 route des Chênes"  , bas_de_page )
    elements.append(asso21)
    asso22 = Paragraph( "La Garrigue"  , bas_de_page )
    elements.append(asso22)
    asso23 = Paragraph( "24620 Tamniès"  , bas_de_page )
    elements.append(asso23)


    asso3 = Paragraph( "siret : 921341921 00010"  , bas_de_page )
    elements.append(asso3)
    asso30 = Paragraph( "TVA intra-communautaire: FR08921341921"  , bas_de_page )
    elements.append(asso30)
    asso4 = Paragraph( "Tél : 06 03 54 27 47\nsanspb24@gmail.com"  , bas_de_page )
    elements.append(asso4)

    doc.build(elements)

    return response
 

