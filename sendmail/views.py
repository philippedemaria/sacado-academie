from django.conf import settings # récupération de variables globales du settings.py
from django.shortcuts import render, redirect
from django.db.models import Q
from account.models import User, Teacher, Student
from qcm.models import Studentanswer, Relationship
from setup.models import Tweeter
from group.models import Group
from sendmail.models import Email, Communication, Discussion ,  Message
from sendmail.forms import EmailForm, CommunicationForm , DiscussionForm  ,  MessageForm
from django.http import JsonResponse
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib import messages
from sendmail.decorators import user_is_email_teacher, user_is_active
from django.views.decorators.csrf import csrf_exempt

from django.utils import timezone
import re
import html
import pytz
from general_fonctions import *
from qcm.views import tracker_execute_exercise



def list_emails(request):
 
	user = request.user
	users = []
	if request.user.is_authenticated :
		if user.is_teacher:
			today = time_zone_user(request.user)
			teacher = user.teacher
			groups =  teacher.groups.order_by("level__ranking") 
			shared_groups = teacher.teacher_group.order_by("level__ranking") 
			groups = groups | shared_groups

			request.session["tdb"] = False # permet l'activation du surlignage de l'icone dans le menu gauche

			group_students = set()
			for group in groups:
				group_students.update(group.students.all())


			studentanswers = Studentanswer.objects.filter(student__user__in =  group_students).order_by("-date")[:100]
			tasks = Relationship.objects.filter(parcours__teacher = teacher,  exercise__supportfile__is_title=0).exclude(date_limit=None).order_by("-date_limit")[:50] 
			sent_emails = Email.objects.distinct().filter(author=user).order_by("-today")
			emails = Email.objects.distinct().filter(receivers=user).order_by("-today")
			form = EmailForm(request.POST or None, request.FILES or None)

			discussions = Discussion.objects.all().order_by("-date_created")
			nb_discussions = discussions.count()
 
			return render(request,
			          'sendmail/list.html',
			          { 'emails': emails, 'sent_emails': sent_emails, 'form': form, 'users': users, 'groups': groups,  'today': today, 'communications': [], 
			           'discussions' : discussions, 'nb_discussions': nb_discussions ,  'studentanswers': studentanswers, 'tasks': tasks})

		elif user.is_student:

			tracker_execute_exercise(False, user)
			student = Student.objects.get(user=user)
			groups = student.students_to_group.all()
			today = time_zone_user(request.user)
			for group in groups:
				for student in group.students.order_by("user__last_name"):
				    if student.user.email :
				        users.append(student.user)
				if group.teacher.is_mailing :
					users.append(group.teacher.user)

			sent_emails = Email.objects.distinct().filter(author=user).order_by("-today")
			emails = Email.objects.distinct().filter(receivers=user).order_by("-today")
			form = EmailForm(request.POST or None, request.FILES or None)
			tweeters = Tweeter.objects.all().order_by("-date_created")
			return render(request,
			          'sendmail/list.html',
			          {'tweeters': tweeters, 'emails': emails, 'sent_emails': sent_emails, 'form': form, 'users': users, 'groups': groups, 'today': today, 'communications': [], 'student' : student , 
			           'studentanswers': [], 'tasks': []})
		else:
			raise PermissionDenied
	else:
		return redirect('index')


@user_is_active
def create_email(request):
 
	form = EmailForm(request.POST or None,request.FILES or None)
	user = request.user
	today = time_zone_user(user)

	if form.is_valid():		
		new_f = form.save(commit=False)
		new_f.author = user
		new_f.save()
		form.save_m2m()

		subject = request.POST.get('subject')
		texte = request.POST.get('texte') + "\n\n Ce message est envoyé par : "+str(user)
		receivers = request.POST.getlist('receivers')
		groups = request.POST.getlist('groups')
		rcv = []
 
		for receiver  in receivers :
			u = User.objects.get(pk = int(receiver))
			new_f.receivers.add(u)
			rcv.append(str(u.email))

		for group_id  in groups :
			group = Group.objects.get(pk = int(group_id))
			for s in group.students.all():
				if s.user.email :
					new_f.receivers.add(s.user)	
					rcv.append(str(s.user.email)) 


		send_mail(subject, cleanhtml(unescape_html(texte)) , settings.DEFAULT_FROM_EMAIL, rcv )
		send_mail(subject, cleanhtml(unescape_html(texte)) , settings.DEFAULT_FROM_EMAIL, [str(request.user.email)] )

	else:
		messages.error(request, "Le corps de message est obligatoire !")

	return redirect('emails')


@user_is_email_teacher
def delete_email(request,id):

	if Email.objects.filter(id=id).count() == 1 :
	    email = Email.objects.get(id=id)
	    email.receivers.clear()
	    email.delete()
	return redirect('emails')




def show_email(request):

	email_id = int(request.POST.get("email_id"))
	email = Email.objects.get(id=email_id)
	data = {} 
	if request.user == email.author or request.user in email.receivers.all() :
		form = EmailForm(request.POST or None,request.FILES or None)
		html = render_to_string('sendmail/show.html',{ 'email' : email  , 'form' : form  , 'communications': [],  })
		data['html'] = html
	else :
		data['html'] = ""		

	return JsonResponse(data)



def pending_notification(request):

	teacher_id = int(request.POST.get("teacher_id"))
	data = {} 
	Studentanswer.objects.filter(parcours__teacher_id = teacher_id).update(is_reading = 1)
	return JsonResponse(data)





def list_communications(request):
	communications = Communication.objects.all()
	form = CommunicationForm(request.POST or  None)
	context = {'form': form,  'communications': communications,  } 
	return render(request, 'sendmail/list_communications.html', context)



@csrf_exempt
def create_communication(request):  
	form = CommunicationForm(request.POST or  None)

	if request.method == "POST":
		if form.is_valid():
			new_f = form.save(commit=False)
			new_f.teacher = request.user
			new_f.save()

			if request.POST.get("sender") :
				users = User.objects.filter(user_type=2)
				rcv = []
				for u in users :
					if u.email :
						send_mail(new_f.subject, cleanhtml(unescape_html(new_f.texte)), settings.DEFAULT_FROM_EMAIL, [u.email] )

		else :
			print(form.errors)
 
	return redirect('communications')


def update_communication(request,id): # update

	communication = Communication.objects.get(id= id)
	form = CommunicationForm(request.POST or  None, instance = communication)

	if request.method == "POST":
		if form.is_valid():
			new_f = form.save(commit=False)
			new_f.teacher = request.user
			new_f.save()
			try :
				if request.POST.get("sender") :
					users = User.objects.filter(user_type=2)
					rcv = []
					for u in users :
						if u.email :
							send_mail(new_f.subject, cleanhtml(unescape_html(new_f.texte)), settings.DEFAULT_FROM_EMAIL, [u.email] )
			except :
				pass


			return redirect('communications')

		else :
			print(form.errors)

	return render(request,'sendmail/form_update_communication.html', {'form':form,'communication':communication,   })

 

def delete_communication(request, id):


	if Communication.objects.filter(id=id).count() == 1 :
	    communication = Communication.objects.get(id=id)
	    communication.delete()
	return redirect('communications')




def show_communication(request):
	communication_id = int(request.POST.get("communication_id"))
	communication = Communication.objects.get(id=communication_id)
	form = CommunicationForm(request.POST or None)
	data = {} 

	html = render_to_string('sendmail/show_communication.html',{ 'communication' : communication  , 'form' : form  ,   })
	data['html'] = html 		

	return JsonResponse(data)




def reader_communication(request):
	
	data = {} 
	teacher = Teacher.objects.get(user = request.user)  
	communications = Communication.objects.exclude(teachers = teacher)
	for c in communications:
		c.teachers.add(teacher)
	
	return JsonResponse(data)


def ajax_notification_group(request):
    
    data = {}
    group_id =  request.POST.get("group_id")
    group = Group.objects.get(pk=group_id)
   
    studentanswers = Studentanswer.objects.filter(student__in =  group.students.all(), parcours__subject = group.subject, parcours__level = group.level).order_by("-date")[:100]

    context = {  'studentanswers': studentanswers,   }
    data['html'] = render_to_string('sendmail/ajax_list.html', context)
 
    return JsonResponse(data)


def ajax_notification_student(request):


    data = {}

    datas =  request.POST.get("datas").split("__")

    student_id =  datas[1]
    group_id =   datas[0]
    group = Group.objects.get(pk=group_id)

    studentanswers = Studentanswer.objects.filter(student_id = student_id, parcours__subject = group.subject, parcours__level = group.level ).order_by("-date")[:100]

    context = {  'studentanswers': studentanswers,   }
    data['html'] = render_to_string('sendmail/ajax_list.html', context)
 
    return JsonResponse(data)


#######################################################################################################################################
#######################################################################################################################################
##### Forum
#######################################################################################################################################
#######################################################################################################################################


def create_discussion(request):  
	form   = DiscussionForm(request.POST or  None)
	form_m = MessageForm(request.POST or  None)
	if request.user.school :
		if request.method == "POST":
			if all((form.is_valid(),form_m.is_valid())):
				new_f = form.save(commit=False)
				new_f.user = request.user
				new_f.save()

				new_fm = form_m.save(commit=False)
				new_fm.user = request.user
				new_fm.discussion = new_f
				new_fm.save()

				try :
					for teacher in Teacher.objects.filter(is_mailing=1).values_list("user__email",flat=True).distinct():
						send_mail("sacado Forum : " +new_f.discussion  , cleanhtml(unescape_html(new_f.texte)) +"\n Pour répondre connectez-vous à Sacado : https://sacado-academie.fr", settings.DEFAULT_FROM_EMAIL, [teacher.user.email] )
				except :
					pass
				return redirect('emails')

			else :
				print(form.errors)

	else :
		messages.error(request,"Vous devez posséder la version Etablissement pour participer.")

	return render(request,'sendmail/form_discussion.html', { 'form' : form , 'form_m': form_m, })

 


def show_discussion(request,idd):
	discussion = Discussion.objects.get(id = idd)
	msgs = Message.objects.filter(discussion = discussion)
	m = msgs.last()
 
	form = MessageForm(request.POST or  None)

	if request.user.school :	
		if m.user == request.user :
			last_user = True
			form = MessageForm(request.POST or  None, instance = m)
		else :
			last_user = False
			form = MessageForm(request.POST or  None)
		if request.method == "POST":
			if form.is_valid():
				new_f = form.save(commit=False)
				new_f.user = request.user
				new_f.discussion = discussion
				new_f.save()
				try :				
					dest = []
					for e in discussion.discussion_message.values_list("user__email",flat=True).distinct():
						dest.append(e)
 
					send_mail("sacado Forum : " +new_f.discussion  , cleanhtml(unescape_html(new_f.texte)) +"\n Pour répondre connectez-vous à Sacado : https://sacado-academie.fr", settings.DEFAULT_FROM_EMAIL, dest )
				except :
					pass
			else :
				print(form.errors)

	else :
		messages.error(request,"Vous devez posséder la version Etablissement pour participer.")

	context = { 'form': form ,  'msgs': msgs ,  'discussion': discussion,  'last_user': last_user  }

	return render(request, 'sendmail/show_discussion.html', context)


 

def delete_message(request,idd, id):
	message = Message.objects.get(pk=id)

	if message.user == request.user :
		d = Discussion.objects.get(pk=idd)
		if d.discussion_message.count() == 1 :
			d.delete()
			message.delete()
			return redirect('emails')
		else :
			message.delete()
			return redirect('show_discussion' , idd)

	else :
		messages.error(request,"Vous ne pouvez pas supprimer un message dont vous n'êtes pas l'auteur.")
		return redirect('show_discussion' , idd)


 
 

#######################################################################################################################################
#######################################################################################################################################
##### Message pour la formule 3 
#######################################################################################################################################
#######################################################################################################################################


def list_discussion_lesson(request,idu):
	user = User.objects.get(pk=idu)
	form   = DiscussionForm(request.POST or  None)
	discussions = user.user_discussion.order_by("-date_created")
	context = {'form': form,  'discussions': discussions, 'user' : user  } 
	return render(request, 'sendmail/list_discussions.html', context)



def create_discussion_lesson(request):  
	form   = DiscussionForm(request.POST or  None)
	form_m = MessageForm(request.POST or  None)
	if request.user.school :
		if request.method == "POST":
			if all((form.is_valid(),form_m.is_valid())):
				new_f = form.save(commit=False)
				new_f.user = request.user
				new_f.save()

				new_fm = form_m.save(commit=False)
				new_fm.user = request.user
				new_fm.discussion = new_f
				new_fm.save()

				try :
					listing = []
					for user in User.objects.filter(is_superuser=1):
						listing.append(user.email)
					send_mail("Message : " +new_f.discussion  , cleanhtml(unescape_html(new_f.texte)) +"\n Pour répondre connectez-vous à : https://sacado-academie.fr", settings.DEFAULT_FROM_EMAIL, listing )
				except :
					pass

				return redirect('list_discussion_lesson', request.user.id)

			else :
				print(form.errors)

	else :
		messages.error(request,"Vous devez posséder la version Etablissement pour participer.")

	return render(request,'sendmail/form_discussion.html', { 'form' : form , 'form_m': form_m, })

 


def show_discussion_lesson(request,idd):
	discussion = Discussion.objects.get(id = idd)
	msgs = Message.objects.filter(discussion = discussion)
	m = msgs.last()
 
	form = MessageForm(request.POST or  None)

	if request.user.school :	
		if m.user == request.user :
			last_user = True
			form = MessageForm(request.POST or  None, instance = m)
		else :
			last_user = False
			form = MessageForm(request.POST or  None)
		if request.method == "POST":
			if form.is_valid():
				new_f = form.save(commit=False)
				new_f.user = request.user
				new_f.discussion = discussion
				new_f.save()
				try :				
					dest = []
					for e in discussion.discussion_message.values_list("user__email",flat=True).distinct():
						dest.append(e)
 
					send_mail("sacado Forum : " +new_f.discussion  , cleanhtml(unescape_html(new_f.texte)) +"\n Pour répondre connectez-vous à Sacado : https://sacado-academie.fr", settings.DEFAULT_FROM_EMAIL, dest )
				except :
					pass
			else :
				print(form.errors)

	else :
		messages.error(request,"Vous devez posséder la version Etablissement pour participer.")

	context = { 'form': form ,  'msgs': msgs ,  'discussion': discussion,  'last_user': last_user  }

	return render(request, 'sendmail/show_discussion.html', context)


 

def delete_message_lesson(request,idd, id):
	message = Message.objects.get(pk=id)

	if message.user == request.user :
		d = Discussion.objects.get(pk=idd)
		if d.discussion_message.count() == 1 :
			d.delete()
			message.delete()
			return redirect('emails')
		else :
			message.delete()
			return redirect('show_discussion' , idd)

	else :
		messages.error(request,"Vous ne pouvez pas supprimer un message dont vous n'êtes pas l'auteur.")
		return redirect('show_discussion' , idd)





