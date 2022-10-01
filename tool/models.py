from django.db import models
from datetime import date, datetime
from ckeditor_uploader.fields import RichTextUploadingField
from group.models import Group
from socle.models import *
from account.models import Student, Teacher, ModelWithCode , User
from qcm.models import Parcours , Exercise , Folder
from socle.models import Level
from django.utils import   timezone
from django.db.models import Q
from random import uniform , randint
from sacado.settings import MEDIA_ROOT
from time import strftime

# Pour créer un superuser, il faut depuis le shell taper :
# from account.models import User
# User.objects.create_superuser("admin","admin@gmail.com","motdepasse", user_type=0).save()
POLICES = (
        (16, '16'),
        (24, '24'), 
        (32, '32'), 
        (40, '40'),
        (48, '48'),
        (56, '56'),
    )



def choice_directory_path(instance, filename):
    return "choices/{}".format(filename) 

def question_directory_path(instance, filename):
    return "questions/{}".format(filename)

def quizz_directory_path(instance, filename):
    return "quizzes/{}/{}".format(instance.teacher.user.id, filename)

def tool_directory_path(instance, filename):
    return "tool/asso/{}".format( filename)

def variable_directory_path(instance, filename):
    return "tool/variable_qr/{}".format(filename)

def videocopy_directory_path(instance, filename):
    return "tool/videocopy/{}/{}".format(instance.teacher.user.id,filename)


class Tool(models.Model):
    """
    Modèle représentant un associé.
    """
    title         = models.CharField(max_length=255, default='',  blank=True, verbose_name="Titre")  
    remark        = RichTextUploadingField( blank=True, verbose_name="Texte*") 
    teachers      = models.ManyToManyField(Teacher, related_name = "tools", blank=True,   editable=False ) 
    date_created  = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modified = models.DateTimeField(auto_now=True, verbose_name="Date de modification") 
    imagefile     = models.ImageField(upload_to=tool_directory_path,   verbose_name="Image", default="")
    is_publish    = models.BooleanField(default=1, verbose_name="Publié ?")
    is_asso       = models.BooleanField(default=1, verbose_name="Nécessite l'adhésion SACADO ?")
    is_ebep       = models.BooleanField(default=0, verbose_name="Outils EBEP ?")
    url           =  models.CharField(max_length=255, default='' ,   blank=True, verbose_name="url de substitution")  
    exercises     = models.ManyToManyField(Exercise, blank=True, related_name='tools', verbose_name="Outils inclusifs", editable=False)
    levels        = models.ManyToManyField(Level, related_name = "tools", blank=True ) 



    def __str__(self):
        return self.title 


class Qrandom(models.Model):

    title      = models.CharField(max_length=50,  blank=True, verbose_name="Titre")
    texte      = RichTextUploadingField(  blank=True, verbose_name="Enoncé")
    knowledge  = models.ForeignKey(Knowledge, related_name="qrandom", blank=True, null = True,  on_delete=models.CASCADE) 
    is_publish = models.BooleanField(default=1, verbose_name="Publié ?")
    teacher    = models.ForeignKey(Teacher, related_name = "qrandom", blank=True,   editable=False ,  on_delete=models.CASCADE)
    ####  type de question
    qtype      = models.PositiveIntegerField(default=2, editable=False)
    calculator = models.BooleanField(default=0, verbose_name="Calculatrice ?")
    tool       = models.BooleanField(default=0, verbose_name="Barre d'outils ?")
    duration   = models.PositiveIntegerField(default=20, blank=True, verbose_name="Durée")

    def __str__(self):
        return self.title


    def instruction(self):

        var_dict = {}
        for v in self.variables.all():
            if v.variable_img.count() > 0 :
                vi_tab = list(v.variable_img.all())
                n_aleatoire = random.randint(0,len(vi_tab)-1)
                variable = "<img src='"+MEDIA_ROOT+"/"+vi_tab[n_aleatoire]+"' width='400px'/>"

            elif v.words :  
                word_tab = v.words.split(";")
                n_aleatoire = random.randint(0,len(word_tab)-1)
                variable =  word_tab[n_aleatoire]
            else :
                if v.is_integer :
                    variable = randint(v.minimum,v.maximum)
                else :
                    variable = uniforme(v.minimum,v.maximum)
            var_dict[v.name] = variable

        txt = self.texte
        for key,value in var_dict.items() :
            txt = txt.replace("__"+str(key)+"__",str(value))

        return txt

            
class Variable(models.Model):

    name  = models.CharField(max_length=50,  blank=True, verbose_name="variable")
    qrandom  = models.ForeignKey(Qrandom, related_name="variables", blank=True, null = True,  on_delete=models.CASCADE)
    ## Variable numérique
    is_integer = models.BooleanField(default=1, verbose_name="Valeur entière ?")        
    maximum = models.IntegerField(default=10)
    minimum = models.IntegerField(default=0)
    ## Variable littérale
    words  = models.CharField(max_length=255,  blank=True, verbose_name="Liste de valeurs")

    def __str__(self):
        return self.name 


class VariableImage(models.Model):

    variable  = models.ForeignKey(Variable, related_name="variable_img", blank=True, null = True,  on_delete=models.CASCADE)
    image  = models.ImageField(upload_to=variable_directory_path,   verbose_name="Image", default="")

    def __str__(self):
        return self.variable.name 


class Question(models.Model):
    """
    Modèle représentant un associé.
    """

    title         = RichTextUploadingField( default='',  blank=True, verbose_name="Réponse écrite")
    calculator    = models.BooleanField(default=0, verbose_name="Calculatrice ?")
    date_modified = models.DateTimeField(auto_now=True)
    ####  type de question
    qtype         = models.PositiveIntegerField(default=3, editable=False)
    answer        = models.CharField(max_length=255, null = True,   blank=True, verbose_name="Réponse attendu")

    knowledge  = models.ForeignKey(Knowledge, related_name="question", blank=True, null = True,  on_delete=models.CASCADE) 
    skills     = models.ManyToManyField(Skill, related_name="question", blank=True)


    imagefile  = models.ImageField(upload_to=question_directory_path, blank=True, verbose_name="Image", default="")
    audio      = models.FileField(upload_to=question_directory_path, blank=True, verbose_name="Audio", default="")
    video      = models.TextField( default='',  blank=True, verbose_name="Vidéo intégrée")

    width         = models.PositiveIntegerField( verbose_name="Largeur",  blank=True, null = True )
    height         = models.PositiveIntegerField(verbose_name="Hauteur", blank=True, null = True )

    is_publish = models.BooleanField(default=1, verbose_name="Publié ?")
    is_radio   = models.BooleanField(default=0, verbose_name="Type de réponse ?")

    is_correction = models.BooleanField(default=0, verbose_name="Correction ?")
    duration      = models.PositiveIntegerField(default=20, blank=True, verbose_name="Durée")
    point         = models.PositiveIntegerField(default=1000, blank=True, verbose_name="Point")

 
    is_correct = models.BooleanField(default=1, verbose_name="Réponse correcte ?")
    ranking    = models.PositiveIntegerField(  default=0,  blank=True, null=True, editable=False)
    students   = models.ManyToManyField(Student, blank=True, through="Answerplayer", related_name="questions",   editable=False)

    size       = models.PositiveIntegerField(default=32, choices=POLICES,  verbose_name="Taille de police")
    theme      = models.BooleanField(default=1, verbose_name="Thème ?")

    def __str__(self):
        return self.title


    def ans_for_this_question (self,q, student):
        """
        retourne  la réponse de 'élève pour un quizz avec une question sous forme d'id.
        """
        try :
            answerplayer = self.questions_player.filter( quizz = q , student= student  ).last()
            return answerplayer
        except :
            return ""

    def has_choices_with_retroaction(self) :
        test = False
        if self.choices.exclude(retroaction="").count():
            test = True
        return test



    def real_ans_for_this_question (self,quizz, student):
        """
        retourne  la réponse de 'élève pour un quizz avec une question sous forme du choix proposé.
        """
        this_answer = dict()
        answer      = []
        is_correct  = 0 
        try : 
            answerplayer = Answerplayer.objects.filter(question = self,  quizz = quizz , student= student  ).last()
            if answerplayer.is_correct :
                is_correct = 1
            if self.qtype == 1 : # VRAI - FAUX
                answer = "FAUX"
                if int(answerplayer.answer) == 1 :
                    answer = "VRAI"
            elif  self.qtype == 2 : # réponse écrite
                    answer = answerplayer.answer
            else :
                tab = answerplayer.answer.split(",") # liste des id des choix réponses
                answer = []
                for id_c in tab:
                    choice = Choice.objects.get(pk=id_c)
                    if choice.imageanswer :
                        answer.append(choice.imageanswer)
                    else :
                        answer.append(choice.answer)
            this_answer["is_exist"] = True            
        except :
            is_correct = None
            this_answer["is_exist"] = False
        this_answer["answer"]     = answer
        this_answer["is_correct"] =   is_correct  
        return this_answer


    def success_percent (self,quizz):
        data_set = Answerplayer.objects.filter(question = self, quizz = quizz )
        good_answerplayers = data_set.filter(is_correct = 1 ).count()
        answerplayers = data_set.count()
        try : 
            percent = str(int(good_answerplayers/answerplayers)*100) +"%"
        except :
            percent = "Non traité"
 
        return percent


class Choice(models.Model):
    """
    Modèle représentant un associé.
    """

    imageanswer = models.ImageField(upload_to=choice_directory_path,  null=True,  blank=True, verbose_name="Image", default="")
    answer      = models.TextField(max_length=255, default='', null=True,  blank=True, verbose_name="Réponse écrite")
    retroaction = models.TextField(max_length=255, default='', null=True,  blank=True, verbose_name="Rétroaction")

    is_correct  = models.BooleanField(default=0, verbose_name="Réponse correcte ?")
    question    = models.ForeignKey(Question, related_name="choices", blank=True, null = True,  on_delete=models.CASCADE)
    def __str__(self):
        return self.answer 


class Quizz(ModelWithCode):
    """
    Modèle représentant un associé.
    """
    title         = models.CharField( max_length=255, verbose_name="Titre du quizz") 
    teacher       = models.ForeignKey(Teacher, related_name="teacher_quizz", blank=True, on_delete=models.CASCADE, editable=False ) 
    date_modified = models.DateTimeField(auto_now=True)
    color         = models.CharField(max_length=255, default='#5d4391', verbose_name="Couleur")
    
    levels    = models.ManyToManyField(Level, related_name="quizz", blank=True)
    themes    = models.ManyToManyField(Theme, related_name="quizz", blank=True)
    subject   = models.ForeignKey(Subject, related_name="quizz", blank=True, null = True, on_delete=models.CASCADE)
 
    vignette   = models.ImageField(upload_to=quizz_directory_path, verbose_name="Vignette d'accueil", blank=True, null = True , default ="")
    is_music   = models.BooleanField(default=0, verbose_name="En musique ?")
    is_share   = models.BooleanField(default=0, verbose_name="Mutualisé ?")
    is_publish = models.BooleanField(default=0, verbose_name="Publié ?")

    is_questions = models.BooleanField(default=0, editable=False )  # presentation ou questionnaire
    is_numeric   = models.BooleanField(default=0, verbose_name="Type de passation" )    # réponse sur papier ou sur smartphone
    is_mark      = models.BooleanField(default=0, verbose_name="Récupérer les réponses ?") 
    is_lock      = models.BooleanField(default=0, verbose_name="Verrouiller ?") 
    is_random    = models.BooleanField(default=0, verbose_name="Aléatoire ?") 
    nb_slide     = models.PositiveIntegerField(default=0, editable=False)  # Nombre de diapositive si le quizz est randomisé
    is_video     = models.BooleanField(default=0, verbose_name="Type de passation")  # Vidéo projection

    is_back      = models.BooleanField(default=0, verbose_name="Retour arrière ?")  
    is_ranking   = models.BooleanField(default=0, verbose_name="Ordre aléatoire des questions ?")  
    is_shuffle   = models.BooleanField(default=0, verbose_name="Ordre aléatoire des réponses ?") 
    is_result    = models.BooleanField(default=0, verbose_name="Afficher les réponses ?")
    is_result_final = models.BooleanField(default=0, verbose_name="Position des réponses ?")
    is_archive   = models.BooleanField(default=0, verbose_name="Archivé ?")
    interslide   = models.PositiveIntegerField(default=10, blank=True, verbose_name="Temps entre les questions")

    start = models.DateTimeField(null=True, blank=True, verbose_name="Début de publication")
    stop  = models.DateTimeField(null=True, blank=True, verbose_name="Verrouillé dès le")

    groups       = models.ManyToManyField(Group, blank=True, related_name="quizz" ) 
    questions    = models.ManyToManyField(Question, blank=True, related_name="quizz" , editable=False)  
    qrandoms     = models.ManyToManyField(Qrandom, blank=True, related_name="quizz" , editable=False)  
    parcours     = models.ManyToManyField(Parcours, blank=True, related_name="quizz"  ) 
    folders      = models.ManyToManyField(Folder, blank=True, related_name="quizz"  ) 
    
    students     = models.ManyToManyField(Student, blank=True,  related_name="quizz",   editable=False)

    def __str__(self):
        return self.title 


    def quizz_generated(self,group):
        return self.filter(group=group).order_by("-date_created")

    def duration(self):
        d = 0
        for q in self.questions.filter(is_publish=1) :
            d += q.duration + self.interslide
        return d


    def ans_for_this_question (self,q, student):
        t = []
        try :
            ans = Answerplayer.objects.get(quizz = self , student= student , question = q)
            
            if q.qtype == 2 :
                t = ans.answer
            else :
                if ans.answer :
                    a_tab = ans.answer.split(',')
                    for a in a_tab :
                        t.append(int(a))
        except :
            pass
        return t



    def type_of_document(self):
        return 3



class Positionnement(ModelWithCode):
    """
    Modèle représentant un associé.
    """
    title         = models.CharField( max_length=255, default="Test de positionnement" , verbose_name="Titre du test de positionnement") 
    teacher       = models.ForeignKey(Teacher, related_name="positionnements", blank=True, on_delete=models.CASCADE, editable=False ) 
    date_modified = models.DateTimeField(auto_now=True)
    
    level     = models.ForeignKey(Level, related_name="positionnements", blank=True, null = True, on_delete=models.CASCADE)
    subject   = models.ForeignKey(Subject, related_name="positionnements", blank=True, null = True, on_delete=models.CASCADE)
    vignette   = models.ImageField(upload_to=quizz_directory_path, verbose_name="Vignette d'accueil", blank=True, null = True , default ="")
    is_publish = models.BooleanField(default=0, verbose_name="Publié ?")
    is_back      = models.BooleanField(default=0, verbose_name="Retour arrière ?")  
    is_ranking   = models.BooleanField(default=0, verbose_name="Ordre aléatoire des questions ?")  
    is_shuffle   = models.BooleanField(default=0, verbose_name="Ordre aléatoire des réponses ?") 

    questions    = models.ManyToManyField(Question, blank=True, related_name="positionnements" , editable=False)  
    users        = models.ManyToManyField(User, blank=True,  related_name="positionnements",   editable=False)

    def __str__(self):
        return self.title 


    def duration(self):
        d = 0
        for q in self.questions.filter(is_publish=1) :
            d += q.duration 
        return d


    def skills(self):
        tab_skills = []
        skill_dict = {}
        for q in self.questions.all():
            for s in q.skills.all():
                if not s in tab_skills :
                    tab_skills.append(s.id)
                    skill_dict[s.name]=0
                else :
                    skill_dict[s.name]+=1

        final_skills = []
        final_dict   = {}

        for k,v in skill_dict.items():
            final_dict["key"] = k
            final_dict["nb"]  = v
            final_skills.append(final_dict)

        return final_skills


    def knowledges(self):
        tab_knowledges = []
        knowledge_dict = {}
        for q in self.questions.all():
            if not q.knowledge.id in tab_knowledges :
                tab_knowledges.append(q.knowledge.id)
                knowledge_dict[q.knowledge.name]=0
            else :
                knowledge_dict[q.knowledge.name]+=1

        final_knowledges = []
        final_dict       = {}

        for k,v in knowledge_dict.items():
            final_dict["key"] = k
            final_dict["nb"]  = v
            final_knowledges.append(final_dict)

        return final_knowledges





def time_zone_user(user):
    try :
        if user.time_zone :
            time_zome = user.time_zone
            timezone.activate(pytz.timezone(time_zome))
            today = timezone.localtime(timezone.now())
        else:
            today = timezone.now()
    except :
        today = timezone.now()

    return today


 
class Generate_qr(models.Model):
    """
    Modèle qui récupère les questions du quizz généré.
    """
    quizz        = models.ForeignKey(Quizz,  related_name="generate_qr",  default ="" ,  on_delete=models.CASCADE, editable=False) 
    qr_text      = models.TextField( editable=False) 
    qrandom      = models.ForeignKey(Qrandom, blank=True, null=True, related_name="generate_qr" ,  on_delete=models.CASCADE , editable=False)  
    ranking      = models.PositiveIntegerField(default = 1 , editable=False)    
    students     = models.ManyToManyField(Student, blank=True, through="Answerplayer", related_name="generate_qr",   editable=False)

    def __str__(self):
        return self.qr_text


    def is_correct_answer_quizz_random(self , student) :

        test = False
        quizz_student_answers = Answerplayer.objects.filter(qrandom = self, quizz = quizz, student = student)
        if quizz_student_answers.count() == 0:
            test = "A"
        else :
            for qsa in quizz_student_answers :
                test = quizz_student_answer.is_correct
            
        return test

 

class Answerplayer(models.Model):

    quizz    = models.ForeignKey(Quizz,  related_name="answerplayer", default ="" ,  on_delete=models.CASCADE ) 
    student  = models.ForeignKey(Student,  null=True, blank=True,   related_name='questions_player', on_delete=models.CASCADE,  editable= False)
    question = models.ForeignKey(Question,  null=True, blank=True, related_name='questions_player', on_delete=models.CASCADE, editable= False)
    qrandom  = models.ForeignKey(Generate_qr,  null=True, blank=True, related_name='questions_player', on_delete=models.CASCADE, editable= False)
    answer   = models.CharField( max_length=255, null=True, blank=True,  verbose_name="Réponse")  
    score    = models.PositiveIntegerField(default=0, editable=False)
    timer    = models.CharField(max_length=255, editable=False)  
    is_correct  = models.BooleanField(default=0, editable=False) 

    def __str__(self):
        return self.student.user.last_name


    def get_choice_with_these(self):
        tab_answer = self.answer.split(",")
        rep , sep  = "" , ", "
        i = 1
        for t in tab_answer :
            c = Choice.objects.get(pk=int(t))
            if i==len(tab_answer):
                sep = ""
            rep += c.answer + sep
            i +=1
        return rep



class Slide(models.Model):
    """
    Modèle représentant un associé.
    """
    title      = models.CharField( max_length=255, default="",  verbose_name="Titre") 
    content    = RichTextUploadingField(  default="", verbose_name="Texte")
    ranking    = models.PositiveIntegerField(  default=0,  blank=True, null=True, editable=False)
    duration   = models.PositiveIntegerField(default=0, blank=True, verbose_name="Durée d'affichage")
    is_publish = models.BooleanField(default=0, verbose_name="Publié ?")
 

    def __str__(self):
        return self.title 


class Diaporama(ModelWithCode):
    """
    Modèle représentant un associé.
    """
    title         = models.CharField( max_length=255, verbose_name="Titre du quizz") 
    teacher       = models.ForeignKey(Teacher, related_name="teacher_presentation", blank=True, on_delete=models.CASCADE, editable=False ) 
    students      = models.ManyToManyField(Student, related_name="user_presentation", blank=True , editable=False ) 
    date_modified = models.DateTimeField(auto_now=True)

    levels    = models.ManyToManyField(Level, related_name="presentation", blank=True)
    themes    = models.ManyToManyField(Theme, related_name="presentation", blank=True)
    subject   = models.ForeignKey(Subject, related_name="presentation", blank=True, null = True, on_delete=models.CASCADE)
 
    vignette   = models.ImageField(upload_to=quizz_directory_path, verbose_name="Vignette d'accueil", blank=True, null = True , default ="")

    is_share   = models.BooleanField(default=0, verbose_name="Mutualisé ?")
    is_publish = models.BooleanField(default=0, verbose_name="Publié ?")
    is_archive   = models.BooleanField(default=0, verbose_name="Archivé ?")

    groups     = models.ManyToManyField(Group, blank=True, related_name="presentation") 
    slides     = models.ManyToManyField(Slide, blank=True, related_name="diapositive" , editable=False) 
 
    def __str__(self):
        return self.title 


class Display_question(models.Model):
    """
    ENvoie un signale pour déclencher  l'interface élève et la vue de la question.
    """
    quizz       = models.ForeignKey(Quizz,  related_name="display_questions", default ="" ,   on_delete=models.CASCADE, editable=False) 
    question_id = models.PositiveIntegerField( default=0, ) 
    timestamp   = models.DateTimeField(auto_now=True)
    students    = models.ManyToManyField(Student,    blank=True,   related_name='display_questions' ,  editable= False)
    def __str__(self):
        return self.quizz.title 


class Videocopy(models.Model):
    """
    Prends la photo d'une copie.
    """
    teacher   = models.ForeignKey(Teacher, related_name="teacher_videocopy", blank=True, on_delete=models.CASCADE, editable=False ) 
    timestamp = models.DateTimeField(auto_now=True)
    image     = models.ImageField(upload_to=videocopy_directory_path, verbose_name="Photo", blank=True, null = True  )

    def __str__(self):
        return "videocopie" 



 