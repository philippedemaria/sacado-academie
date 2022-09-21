
from django import http
from sacado.settings import BBB_SERVEUR, BBB_SECRET, DEFAULT_FROM_EMAIL
import json
from xml.etree import ElementTree # pour lire le xml de la reponse de BBB
import subprocess
from django.utils import timezone
from django.utils.timezone import make_aware
from django.shortcuts import render, redirect
from django.db.models import Q , Sum 
from lesson.models import Event, ConnexionEleve , Slot , Credit 
from lesson.forms import EventForm , SlotForm , GetEventForm , CreditForm
from account.models import User, Student , Parent, Teacher , Facture
from school.models import School
import locale
locale.setlocale(locale.LC_TIME,'')
from django.contrib import messages
from django.template.loader import render_to_string
from django.http import JsonResponse 
#from django.core import serializers
from django.core.mail import send_mail
from general_fonctions import time_zone_user


import urllib.parse
import requests # debuggage, à enlever en developpement
from hashlib import sha1  # pour l'API de bbb
from lesson.models import *
from datetime import datetime, timedelta , time as temps
import pytz
from general_fonctions import *
from payment_fonctions import *

def events_json(request):

    user =  request.user 
    events = user.events.all()
    slots = user.slots.all()

    event_list = []
    for event in events:
        # On récupère les dates dans le bon fuseau horaire
        event_date  = event.date
        event_start = datetime.combine(event_date, event.start )
        event_end   = event_start + timedelta(minutes=event.duration)
        event_end   = event_end.replace(tzinfo=utc) 

        event_list.append({
                    'id': event.id,
                    'start': event_start.strftime('%Y-%m-%d %H:%M:%S'),
                    'end': event_end.strftime('%Y-%m-%d %H:%M:%S'),
                    'title': event.title ,
                    'color' : event.color,
                    })

    for slot in slots:
        # On récupère les dates dans le bon fuseau horaire
        slot_start = slot.datetime.replace(tzinfo=utc)
        slot_end   = slot_start + timedelta(minutes=15)
        
        event_list.append({
                    'id': slot.id,
                    'start': slot_start.strftime('%Y-%m-%d %H:%M:%S'),
                    'end': slot_end.strftime('%Y-%m-%d %H:%M:%S'),
                    'title': "",
                    'color' : '#CCC',
                    })

    if len(event_list) == -1: 
        raise http.Http404
    else:
        return http.HttpResponse(json.dumps(event_list), content_type='application/json')
 


def events_my_teacher(request,idt):

    today = time_zone_user(request.user)

    slots = Slot.objects.filter(user_id=idt,is_occupied=0, datetime__gte=today)
 
    event_list = []
    for slot in slots:
        # On récupère les dates dans le bon fuseau horaire
        slot_start = slot.datetime
        slot_end   = slot_start + timedelta(minutes=15)
        event_list.append({
                    'id': slot.id,
                    'start': slot_start.strftime('%Y-%m-%d %H:%M:%S'),
                    'end': slot_end.strftime('%Y-%m-%d %H:%M:%S'),
                    'title': "",
                    'color' : '#CCC',
                    })

    if len(event_list) == -1: 
        raise http.Http404
    else:
        return http.HttpResponse(json.dumps(event_list), content_type='application/json')
 



def calendar_show(request,id=0):

    hours = []
    hour, minute = 8,0
    for i in range(12) :
        for j in range(4) :
            minute = 15*j
            if minute == 0:
                minute = "00"
            time = str(hour)+":"+str(minute)
            hours.append(time)
        hour=hour+1


    user      = request.user
    form      = EventForm(user, request.POST or None)
    form_slot = SlotForm(user, request.POST or None)
    students  = user.teacher.students.all()
    context   = { 'user_shown' : user , 'form' : form , 'hours' : hours , 'form_slot' : form_slot ,  'students' : students }  

    return render(request, "lesson/calendar_show.html" , context )
 

def create_event(request): # CREATION PAR LE PROF

    user   =  request.user  
    form   = EventForm(user, request.POST or None)
    form_s = SlotForm(user, request.POST or None)

    is_lesson = request.POST.get("is_lesson",None)
    duration  = request.POST.get("duration",None)
    utc       = pytz.UTC

    #new_form.start = new_form.start + timedelta(hours=int(tabs[0]),minutes=int(tabs[1]))
    if is_lesson == "1" :
        if form.is_valid():    
            event = form.save(commit=False)
            event.user = request.user
            event.is_validate = 2      
            event.save()
            event.urlCreate=bbb_urlCreate(event)
            event.urlJoinProf=bbb_urlJoin(event,"MODERATOR",user.last_name+" "+user.first_name)
            event.save()  # pour avoir un id, necessaire pour les relations M2M
            students=form.cleaned_data.get("users")
            send_list = []
            ListeUrls=[]
            for student in students :
                event.users.add(student.user)
                conn=ConnexionEleve.objects.get(event=event,user=student.user)
                # conn.urlJoinEleve=bbb_urlJoin(event,"VIEWER",student.user.first_name+" "+student.user.last_name)
                ListeUrls.append(conn.urlJoinEleve)
                conn.save()
                if student.user.email!=None : 
                    send_list.append(student.user.email)    

            #-------------- envoi du mail au prof
            CorpsMessage="""Bonjour, 
Vous venez de créer une nouvelle leçon intitulée : {}.
Elle se déroulera le {} à {} pour {} minutes.
Voici le lien qui vous permettra d'accéder à la visio :
    {}

Normalement, la visio sera créée automatiquement 3 minutes avant le rendez-vous. 
En cas de problème, ou pour la créer à la main, voici le lien :
    {}  
            """.format(str(event.title) ,str(event.date.strftime("%A %d/%m")),str(event.start),str(event.duration),event.urlJoinProf,event.urlCreate)
            if len(students)==0 :
                CorpsMessage+="Cette leçon n'a pas d'élève, ce qui est curieux..."
            elif len(students)==1 :
                CorpsMessage+="Cette leçon est destinée à {} {}, et son lien d'accès est : \n{}\n"\
                .format(students[0].user.first_name.capitalize(), students[0].user.last_name.capitalize(),ListeUrls[0])
            else :
                CorpsMessage+="Voici la liste des élèves inscrits à cette leçon, et leurs liens d'accès respectifs : \n"
    			
                for i,student in enumerate(students):
                    CorpsMessage+=" - {} {} \n   {}\n".format(student.user.first_name.capitalize(),student.user.last_name.capitalize(),ListeUrls[i])
            CorpsMessage+="Cordialement,\nL'équipe de Sacado Académie"	  
            send_mail("Création d'une leçon",CorpsMessage,DEFAULT_FROM_EMAIL,[user.email])
            #---------------envoi du mail aux parents d'élèves et eventuellement aux eleves.
            for i,student in enumerate(students):
                student=Student.objects.get(user=student)
                dest=[p.user.email for p in student.students_parent.all()]
                if student.user.email != None : 
                    dest.append(student.user.email) 
                send_mail("Programmation d'une leçon par visio","""
Bonjour,
Une leçon par visio a été programmée par {} {}, à destination de {} {}.
Elle aura lieu le {} de {} et durera {} minutes.
Voici le lien d'accès à la visio :

    {}

Merci de bien vouloir contacter l'enseignant à l'adresse {} en cas d'indisponibilité.

Très cordialement,

L'équipe Sacado Académie.""".format(user.civilite,user.last_name.capitalize(),student.user.first_name.capitalize(),student.user.last_name.capitalize(), 
                       str(event.date.strftime("%A %d/%m")),str(event.start),str(event.duration),ListeUrls[i],user.email),DEFAULT_FROM_EMAIL,dest) 
        else :  
            print(form.errors)
    else :
        if form_s.is_valid():
            start_hour = request.POST.get("start_hour")
            tabs       = start_hour.split(":")
            start_hour = timedelta(hours=int(tabs[0]),minutes=int(tabs[1]))
            y,m,d      = request.POST.get("datetime").split("-")
            datet_nutc = datetime(int(y),int(m),int(d)) + start_hour
            try :
                datet      = make_aware(datet_nutc, timezone=pytz.timezone( request.user.timezone) )
            except :
                datet      = make_aware(datet_nutc, timezone=pytz.timezone("Europe/Paris") )
            for i in range(0,int(duration),15) :
                dateti = datet + timedelta(hours=1,minutes=i)
                Slot.objects.create(user = request.user , datetime = dateti , is_occupied = 0 )

        else :  
            print(form_s.errors)

    return redirect('calendar_show' , 0)


 

def get_the_slot(request): # CREATION PAR LE PROF

 
    form = GetEventForm(request.POST or None)
    idt  = request.POST.get("teacher_id")
    utc  = pytz.UTC

    if request.user.is_student and not request.user.student.can_ask_lesson() :
        messages.error(request,"Vous ne pouvez pas réserver de leçons. Crédits insuffisants ou épuisés ou date expirée.")
        return redirect("detail_student_lesson",request.user.id)

    elif request.user.is_parent :
        student = Student.objects.get(user_id=request.session.get("student_id"))
        if not request.user.student.can_ask_lesson() :
            messages.error(request,"Vous ne pouvez pas réserver de leçons. Crédits insuffisants ou épuisés ou date expirée.")
            return redirect("detail_student_lesson",request.user.is_student)


    if request.method == "POST" :
        if form.is_valid():
            user              = request.user     
            event             = form.save(commit=False)
            event.user_id     = idt
            event.title       = "Demande de leçon par visio"
            event.is_validate = user.user_type    
            event.save()
            duration = event.duration//15
            teacher = Teacher.objects.get(user_id=idt)

            som     = teacher.tarif * duration/60
            

            for i in range(duration) :
                event_date = datetime.combine(event.date, event.start ) + timedelta(minutes=i*15)
                datetmi    = event_date - timedelta(minutes=1)
                datetma    = event_date + timedelta(minutes=1)

                datetmin = datetmi.replace(tzinfo=utc) # transforme le temps naive en utc
                datetmax = datetma.replace(tzinfo=utc) 
                slots    = Slot.objects.filter(user_id=idt,datetime__gte=datetmin,datetime__lte=datetmax)
                slots.update(is_occupied = 1)

            if user.user_type  == 0 :

                event.users.add(user)

                #conn=ConnexionEleve.objects.get(event=event,user=request.user.)
                # conn.urlJoinEleve=bbb_urlJoin(event,"VIEWER",student.user.first_name+" "+student.user.last_name)
                #ListeUrls.append(conn.urlJoinEleve)
                #conn.save()

                #-------------- envoi du mail au prof
                CorpsMessage="""Bonjour, 
                Vous venez de demander une nouvelle leçon intitulée : {}.
                Date    : {} 
                Horaire : {}
                Durée   : {}
                En attente de validation par votre(vos) parent(s).
                Ceci est un mail automatique, ne pas répondre.
                Merci.
                """.format(str(event.title) ,str(event.date.strftime("%A %d/%m")),str(event.start),str(event.duration))

                CorpsMessage+="Cordialement,\nL'équipe de Sacado Académie" 
                if request.user.email :
                    send_mail("Création d'une leçon",CorpsMessage,DEFAULT_FROM_EMAIL,[request.user.email])

                #---------------envoi du mail aux parents d'élèves et eventuellement aux eleves.
                code = 1331371257987*event.id-43526754
                dest=[]
                for p in request.user.student.students_parent.all() :
                    dest.append(p.user.email)
                    cd = Credit.objects.filter(user=p.user).aggregate(Sum("amount"))
                    if cd["amount__sum"] > 0 :
                        Credit.objects.create(amount=-som , user=p.user,observation="Demande de réservation de leçon")


                send_mail("Programmation d'une leçon par visio","""
                Bonjour,
                Une leçon a été demandée par votre enfant {} {}.
                Elle aura lieu le {} à {} et durera {} minutes.
                 
                Vous devez confirmer cette demande pour votre enfant en cliquant sur le lien : https://sacado-academie.fr/lesson/confirmation/{} 

                Merci de bien vouloir contacter l'enseignant à l'adresse {} en cas d'indisponibilité.

                Très cordialement,

                L'équipe Sacado Académie.""".format(request.user.first_name.capitalize(),request.user.last_name.capitalize(), 
                               str(event.date.strftime("%A %d/%m")),str(event.start),str(event.duration),str(code) , event.user.email),DEFAULT_FROM_EMAIL,dest)  

            elif user.user_type  == 1 :
                student = Student.objects.get(user_id=request.session.get("student_id"))
                event.users.add(student.user)
                
                #---------------envoi du mail aux parents d'élèves et eventuellement aux eleves.
                dest=[request.user.email ]
                send_mail("Programmation d'une leçon par visio","""
                Bonjour,
                Une leçon par visio a été demandée par {} {}.
                Elle aura lieu le {} à {} et durera {} minutes.
                 
                Merci de bien vouloir contacter l'enseignant à l'adresse {} en cas d'indisponibilité.

                Très cordialement,

                L'équipe Sacado Académie.""".format(request.user.first_name.capitalize(),request.user.last_name.capitalize(), 
                           str(event.date.strftime("%A %d/%m")),str(event.start),str(event.duration),event.user.email),DEFAULT_FROM_EMAIL,dest)  

                #---------------envoi du mail au prof.
                send_mail("DEMANDE d'une leçon par visio","""
                Bonjour,
                Une leçon par visio a été demandée par {} {}.
                Elle aura lieu le {} à {} et durera {} minutes.
                L'équipe Sacado Académie.""".format(request.user.first_name.capitalize(),request.user.last_name.capitalize(), 
                           str(event.date.strftime("%A %d/%m")),str(event.start),str(event.duration)),DEFAULT_FROM_EMAIL,[event.user.email])  
                # le user est le parent
                Credit.objects.create(amount=-som, effective = -som, user = user , observation ="Demande de leçon à valider" )
                # le user devient l'élève pour l'envoyer dans le redirect
                user = student.user

            messages.success(request,"Demande de leçon SACADO ACADEMIE") 
            
            if request.session.get('student_id',None) :
                del request.session['student_id']

            return redirect( "detail_student_lesson" , user.id )
        else :  
            print(form.errors)
 
 
    return redirect( "display_calendar_teacher" , idt )

 

def confirmation(request,code):

    etape             = code + 43526754
    event_id          = etape//1331371257987
    event             = Event.objects.get(pk=event_id)
    event.is_validate = 1
    event.save()

    #---------------envoi du mail au prof.
    send_mail("DEMANDE d'une leçon par visio","""
Bonjour,

La leçon #{} du {} à {} d'une durée de {} minutes vient dêtre confirmée.

L'équipe Sacado Académie.""".format(event.id, str(event.date.strftime("%A %d/%m")),str(event.start),str(event.duration)),DEFAULT_FROM_EMAIL,[event.user.email])  
                

    return redirect('index')



def choose_student(request):
    students = request.user.parent.students.all
    
    context = {   'students' : students    }   
    return render(request, "lesson/choose_student.html" , context )





def update_event(request,id):
    user = User.objects.get(pk=request.user.id)
    event = Event.objects.get(pk=id)
    form = EventForm(user, request.POST or None, instance = event)

    is_lesson = request.POST.get("is_lesson",None)
    duration  = request.POST.get("duration",None)


    if is_lesson == "1" :
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.user = user 
            fullName = user.last_name+" "+user.first_name
            new_form.urlCreate=bbb_urlCreate(new_form)
            new_form.urlJoinProf=bbb_urlJoin(new_form,"MODERATOR",fullName)
            new_form.urlJoinEleve=bbb_urlJoin(new_form,"VIEWER",fullName)
            new_form.save()
        else :
            print(form.errors)

    else :
        if form_slot.is_valid():
            slot      = form_slot.save(commit=False)
            slot.user = request.user
            slot.save()
        else :
            print(form_slot.errors)
        
    return redirect('calendar_show' , 0)


def shift_event(request):
 
    event_id = request.POST.get('event_id')
    new_start_event = request.POST.get('start_event')
    event = Event.objects.filter(pk=event_id).update(start=new_start_event)
 
    data = {} 
    return JsonResponse(data)


def show_event(request):
    event_id = request.POST.get('event_id')
    event = Event.objects.get(pk=event_id)   
    user = User.objects.get(pk=request.user.id) 
    form = EventForm(user, request.POST or None, instance = event) 

    data = {}
     
    html = render_to_string('lesson/show.html',{ 'event' : event  ,   'form' : form  , 'Prof' : request.user.user_type==user.TEACHER  })
    data['html'] = html       

    return JsonResponse(data)




def delete_event(request,id):
 
    event = Event.objects.get(pk=id)    
    event.delete()
    return redirect('calendar_show' , 0)



def add_students_to_my_lesson_group(request):
 
    user = request.user
    if request.method == "POST":
        students = request.POST.getlist('students')

        for s in students :
            user.teacher.students.add(s)
        return redirect('calendar_show' , 0)

    today   = time_zone_user(user)
    students = Student.objects.filter(user__school_id = 50,user__user_type=0, user__closure__gte= today  ).order_by("level__ranking", "user__last_name")
    
    context = { 'user' : user , 'students' : students , 'teacher' : user.teacher   }   
    return render(request, "lesson/add_students_to_my_lesson_group.html" , context )



def delete_student_to_my_lesson_group(request,id):
 
    user = request.user  
    s= Student.objects.get(user_id=id) 
    user.teacher.students.remove(s)
    return redirect('calendar_show' , 0)





def dashboard_parent(request):
 
    parent = Parent.objects.get(user=request.user)
    students = parent.students.order_by("user__first_name")
    index_tdb = False  # Permet l'affichage des tutos Youtube dans le dashboard
    today = time_zone_user(request.user)
    context = {'parent': parent, 'students': students, 'today' : today , 'index_tdb' : index_tdb, }
    template = 'lesson/dashboard_lesson_parent.html'
      
    return render(request, template , context )




def detail_student_lesson(request,id):
 
    user = request.user
    if id == 0 :
        connexions = set()
        for student in request.user.parent.students.all() :
            connexions.update( student.user.ConnexionEleves.order_by("-event__date") )
        student = None 
    else :
        student = Student.objects.get(user_id=id)
        connexions = student.user.ConnexionEleves.order_by("-event__date")
    
    context = { 'user' : user , 'student' : student , 'connexions' : connexions   }   
    return render(request, "lesson/list_lessons.html" , context )





def ask_lesson(request,id):
 
    user = request.user
    student = Student.objects.get(user_id=id)
    request.session["student_id"] = student.user.id
    teachers = Teacher.objects.filter(user__school_id=50,is_lesson=1).order_by("user__last_name")
    try :
        event = user.events.order_by("date").last()
        my_teacher = event.user.teacher
    except :
        my_teacher = None
    context = { 'user' : user , 'student' : student , 'teachers' : teachers , 'my_teacher' : my_teacher   }   
    return render(request, "lesson/ask_lesson.html" , context )



def buy_credit(request) :

    user     = request.user
    credits  = Credit.objects.filter(user =user)
    form     = CreditForm(request.POST or None)
    cd       = Credit.objects.filter(user =user).aggregate(Sum('effective'))
    credit_dispo = cd["effective__sum"] 
    if request.method == "POST" :
        if form.is_valid():
            chrono = create_chrono(Facture,"F")
            #-----------creation d'une nouvelle facture
            #body=json.loads(request.body)
            #---------- Vérification du paiement auprès de paypal
            orderID = "123456AZERT"#body['orderID'] 
            new_fact=Facture()
            new_fact.chrono=chrono
            new_fact.user= user
            new_fact.orderID=orderID
            new_fact.is_lesson = 1 
            new_fact.date= time_zone_user(user)
            new_fact.save() #il faut sauver avant de pouvoir ajouter les adhesions 
            
            nf = form.save(commit = False)
            nf.user = user
            nf.chrono = chrono
            if nf.amount > 500 :
                nf.effective = nf.amount * 1.1
            else:
                nf.effective = nf.amount
            nf.facture = ""
            nf.date= time_zone_user(user)
            nf.save()
        return redirect('detail_student_lesson', 0)

    context = { 'form' : form , 'credits' : credits ,  'credit_dispo' : credit_dispo  }   
    return render(request, "lesson/buy_credit_form.html" , context )



def validate_lesson(request,idc) :

    user = request.user
    connexionEleve = ConnexionEleve.objects.get(pk=idc)
    student = connexionEleve.user.student

    if user.is_parent and student in user.parent.students.all()  :

        ConnexionEleve.objects.filter(pk=idc).update(is_validate=1)
        #---------------envoi du mail au prof.
        send_mail("VALIDATION d'une leçon par visio","""
        Bonjour,
        La leçon #{} du {} à {} d'une durée de {} minutes vient dêtre validée par le parent. Vérifier votre agenda SACADO.
        L'équipe Sacado Académie.""".format(connexionEleve.event.id, str(connexionEleve.event.date.strftime("%A %d/%m")),str(connexionEleve.event.start),str(connexionEleve.event.duration)),DEFAULT_FROM_EMAIL,[connexionEleve.event.user.email])        
        return redirect( "detail_student_lesson"  , student.user.id )

    elif user.is_teacher :
        ConnexionEleve.objects.filter(pk=idc).update(is_validate=2)
        messages.success(request,"Validation prise en compte. La leçon est inscrite dans votre agenda des leçons.")
        return redirect("index" )



def display_calendar_teacher(request,idt) :
   
    teacher    =  Teacher.objects.get(user_id = idt)
    student_id = request.session.get("student_id",None)
    student    = Student.objects.get(user_id=student_id)
    user       =  request.user
    form       = GetEventForm(request.POST or None)
    timezone   = time_zone_user(request.user) 
    context    = { 'user' : user ,  'teacher' : teacher ,  'form' : form , 'student' : student , 'timezone' : timezone  }   
    return render(request, "lesson/display_calendar_teacher.html" , context )


def CalcMeetingID(event):
    """calcule du meetingID d'une leçon"""
    ID=event.user.last_name+" "+event.start.strftime("%d/%m %Hh%M")
    return sha1(ID.encode()).hexdigest()[:6]
        

def bbb_urlCreate(event):
    name=event.title
    meetingID=CalcMeetingID(event)
    welcome="Leçon par vidéo, enseignant"+( "e" if event.user.civilite=="Mme" else "")
    welcome+=" "+event.user.first_name+" "+event.user.last_name
    duration=str(event.duration+15)  #arrêt automatique de la session 30mn après la durée prévue de fin, au cas ou qq'un laisserait la session ouverte
    endWhenNoModerator="false" #la session se ferme lorsque le prof se deconnecte
    request="name={}&meetingID={}&welcome={}&duration={}&endWhenNoModerator={}"
    request=request.format(urllib.parse.quote(name),meetingID,urllib.parse.quote(welcome),duration,endWhenNoModerator)

    hash=sha1(("create"+request+BBB_SECRET).encode()).hexdigest()
    request="https://"+BBB_SERVEUR+"/bigbluebutton/api/create?"+request+"&checksum="+hash
    
    # modification de crontab pour creer la reunion qq mn avant son début
    date_ouv = datetime.combine(event.date, event.start) - timedelta(minutes=3)
    date_ouv = date_ouv.strftime("%H:%M %m%d%y")
    com=open("/tmp/commande_"+str(event.id)+".txt","w")  #commande executée
    print("curl '" + request+"'", file=com )
    com.close()
    subprocess.run(['at', date_ouv, "-f", "/tmp/commande_"+str(event.id)+".txt"])
    return request

def bbb_urlJoin(event,role,fullName):
    """lien pour ouvrir une visio. Role="MODERATOR" pour le prof,
    "VIEWER" pour les eleves"""
    meetingID=CalcMeetingID(event)
    request="fullName={}&meetingID={}&role={}"
    request=request.format(urllib.parse.quote(fullName),meetingID,role)
    hash=sha1(("join"+request+BBB_SECRET).encode()).hexdigest()
    request="https://"+BBB_SERVEUR+"/bigbluebutton/api/join?"+request+"&checksum="+hash
    return request

def bbb_urlIsMeetingRunning(event):
	meetingID=CalcMeetingID(event)
	request="meetingID="+meetingID
	hash=sha1(("isMeetingRunning"+request+BBB_SECRET).encode()).hexdigest()
	request="https://"+BBB_SERVEUR+"/bigbluebutton/api/isMeetingRunning?"+request+"&checksum="+hash
	return request
 
