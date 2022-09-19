from django.core.exceptions import PermissionDenied
from account.models import Teacher, User, Parent, Student
from group.models import Group
from django.contrib import messages
from django.db.models import Q
from school.models import School 

def user_can_create(user):
    test = False
    if user.is_teacher   :
        test = True
    return test

def user_is_superuser(user):
    test = False
    if user.is_superuser   :
        test = True
    return test

def user_is_board(user):
    test = False
    if user.is_board   :
        test = True
    return test


def user_is_creator(user):
    test = False
    if user.is_superuser or user.is_extra :
        test = True
    return test



def user_is_testeur(user):
    test = False
    if user.is_superuser or user.is_extra or user.is_testeur :
        test = True
    return test



def this_school_in_session(request):

    school_id = request.session.get("school_id",None) 
    if school_id :
        school = School.objects.get(pk = int(school_id))
    else :
        school = None
    return school 




def decide(this_student, role, asker):
    test = False
    if role == 0:  # role = request.user.user_type
        if this_student.user == asker:  # asker = request.user
            test = True
    elif role == 1:
        parent = Parent.objects.get(user=asker)
        parents = Parent.objects.filter(students=this_student)
        if parent in parents:
            test = True
    else:
        teacher = Teacher.objects.get(user=asker)
        groups = Group.objects.filter(students=this_student, teacher=teacher)
        if len(groups) > 0:
            test = True
    return test


def user_can_read_details(function):  # id est associé à un user
    def wrap(request, *args, **kwargs):
        user = User.objects.get(pk=kwargs['id'])
        student = Student.objects.get(user=user)  # détail de ce student
        testeur = decide(student, user.user_type, user)
        if testeur:
            return function(request, *args, **kwargs)
        else:
            #raise PermissionDenied
            messages.error(request, " Vous passez par un espace interdit.")
            return function(request, *args, **kwargs)
    return wrap


def who_can_read_details(function):   # id est associé à un student
    def wrap(request, *args, **kwargs):


        student = Student.objects.get(pk=kwargs['id'])
        testeur = decide(student, request.user.user_type, request.user)

        if testeur:
            return function(request, *args, **kwargs)
        else:
            #raise PermissionDenied
            messages.error(request, " Vous passez par un espace interdit.")
            return function(request, *args, **kwargs)
    return wrap



def user_can_read_discussion(function):   # id est associé à un student
    def wrap(request, *args, **kwargs):


        discussion = Discussion.objects.get(pk=kwargs['idd'])
        student = discussion.user.student
        testeur = decide(student, request.user.user_type, request.user)

        if testeur:
            return function(request, *args, **kwargs)
        else:
            #raise PermissionDenied
            messages.error(request, " Vous passez par un espace interdit.")
            return function(request, *args, **kwargs)
    return wrap







def is_manager_of_this_school(function): 
    def wrap(request, *args, **kwargs):

        school = this_school_in_session(request)
        users = User.objects.filter( Q(school=school)| Q(schools=school),pk = request.user.id ).filter( is_manager=1)
 

        if request.user in users or request.user.is_superuser :
            return function(request, *args, **kwargs)
        else:
            #raise PermissionDenied
            return function(request, *args, **kwargs)
    return wrap


def can_register(function): 
    def wrap(request, *args, **kwargs):

 

        users = User.objects.filter(is_manager=1)
        user = request.user

        if user in users or user.is_superuser:
            return function(request, *args, **kwargs)
        else:
            #raise PermissionDenied
            return function(request, *args, **kwargs)
    return wrap



def user_is_admin_school(function): 
    def wrap(request, *args, **kwargs):


        if request.user.is_manager:
            return function(request, *args, **kwargs)
        else:
            #raise PermissionDenied
            return function(request, *args, **kwargs)
    return wrap