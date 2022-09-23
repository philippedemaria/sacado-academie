from django.db import models
from datetime import date
from ckeditor_uploader.fields import RichTextUploadingField
from account.models import User , ModelWithCode
from django.apps import apps
from django.utils import   timezone
from django.db.models import Q
from school.models import School , Country 
# Pour créer un superuser, il faut depuis le shell taper :
# from account.models import User
# User.objects.create_superuser("admin","admin@gmail.com","motdepasse", user_type=0).save()
from datetime import date



class Plancomptable(models.Model):

    code = models.PositiveIntegerField(verbose_name="code")
    name = models.CharField(max_length=255,   verbose_name="Nom") 
    def __str__(self):
        return "{} : {}".format(self.code,self.name)

annee = date.today().year
if date.today().month < 9 :  
    annee = annee -1

YEARS = []
for i in range (20) :
    a = annee + i
    b = annee + i + 1
    YEARS.append( (a , str(a)+"-"+str(b)) )

 
def compta_directory_path(instance, filename):
    return "accountancy/{}/{}".format(instance.year, filename)        

class Activeyear(models.Model):

    year      = models.PositiveIntegerField(default=2021, choices=YEARS , verbose_name="Année de l'exercice") 
    solde     = models.DecimalField(default=0, blank=True , max_digits=10, decimal_places=2,   verbose_name="Résultat de l'exercice précédent")
    is_active = models.BooleanField(default=0,  verbose_name="Année active")
    balance   = models.FileField(upload_to=compta_directory_path, verbose_name="Balance",blank=True, default="" )
    book      = models.FileField(upload_to=compta_directory_path, verbose_name="Grand livre",blank=True, default="" )
    bilan     = models.FileField(upload_to=compta_directory_path, verbose_name="Bilan",blank=True, default="" )
    istest = models.BooleanField(default=0,  verbose_name="Année active")

    def __str__(self):
        nexty = self.year + 1 
        return "{}-{}".format(self.year,nexty)



class Holidaybook(models.Model):

    is_display = models.BooleanField(default=0, verbose_name="Afficher ?") 
 
    def __str__(self):
        return "{}".format(self.is_display)


 
def accounting_directory_path(instance, filename):
    return "association/{}/{}".format(instance.id, filename)


QUALITIES = (
        ("actif", 'membre actif'),    
        ("honneur", "membre d'honneur"),
        ("bienfaiteur", 'membre bienfaiteur'),    
        ("bénéficiaire", "membre bénéficiaire"),
    )


class Rate(models.Model):
    """
    Modèle représentant les tarifs.
    """
    amount    = models.DecimalField(default=0, blank=True , max_digits=10, decimal_places=2, verbose_name="Tarif")
    discount    = models.DecimalField(default=0, blank=True , max_digits=10, decimal_places=2, verbose_name="Réduction" )
    quantity  = models.PositiveIntegerField(default=0,  verbose_name="Nombre d'élèves")
    year      = models.CharField(max_length=255, default='',  verbose_name="Année")
    is_active = models.BooleanField(default=0,  verbose_name="Année active")

    def __str__(self):
        return "{} {}, {}".format(self.amount, self.quantity, self.year)


class Associate(models.Model):
    """
    Modèle représentant un associé.
    """
    user = models.ForeignKey(User, blank=True, default=True, null=True,   related_name="associated", verbose_name="Membre inscrit",  on_delete=models.CASCADE)
    quality = models.CharField(max_length=255, default='', choices=QUALITIES, verbose_name="Qualité")
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=0, editable=False)

    first_name   = models.CharField(max_length=255,  blank=True,default='', null=True,   verbose_name="Nom")
    last_name = models.CharField(max_length=255,  blank=True, default='' , null=True, verbose_name="Prénom")
    email = models.CharField(max_length=255,  blank=True, default='', null=True,  verbose_name="Email")
    observation = RichTextUploadingField( blank=True, default="", null=True, verbose_name="Remarque") 


    def __str__(self):
        lname = self.user.last_name.capitalize()
        fname = self.user.first_name.capitalize()

        return "{} {}, {}".format(lname, fname, quality)


    def has_vote(self, user) :
        my_vote = False
        if self.voting.filter(user = user) :
            my_vote = self.voting.get(user = user)
        return my_vote

    def ratio(self) :
        s = self.voting.count()
        v = 4
        r = self.voting.filter(choice=1).count()
        data = {}
        if s > 0 :
            rat = r / v * 100
            data["rate"] = str(r) +"/" +str(v)+ " = "  + str(rat) + "%"
        else :
            data["rate"] = "en attente"
        data["fin"] = ""
        if s == 4 :
            data["fin"] = " fin du scrutin"
        return data


class Voting(models.Model):
    """
    Modèle représentant un associé.
    """
    associate = models.ForeignKey(Associate, blank=True, related_name="voting", on_delete=models.CASCADE)
    choice = models.BooleanField(default=0, verbose_name="vote")
    justification = models.CharField(max_length=255, default='', blank=True ,  verbose_name="justification (facultatif)")
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, blank=True, related_name="votant", on_delete=models.CASCADE, editable=False)

    def __str__(self):
        lname = self.associated.user.last_name.capitalize()
        fname = self.associated.user.first_name.capitalize()

        return "{} {}".format(choice)

    class Meta:
        unique_together = ('associate', 'user')

 
class Accounting(models.Model):
    """ Accounting   """

    TYPES = (

        ("Période de test", "Période d'essai"),
        ("par carte de crédit", "Carte de crédit"),
        ("par virement bancaire", "Virement bancaire"),
        ("en espèces", "Espèces"),
        ("par mandatement administratif", "Mandatement administratif"),
    )

    FORMES = (
        ("FACTURE", "FACTURE"),        
        ("AVOIR", "AVOIR"),
    )


    amount = models.DecimalField(default=0, blank=True , max_digits=10, decimal_places=2, editable=False)
    is_credit = models.BooleanField(default=0, verbose_name="is_credit ?" )
    is_paypal = models.BooleanField(default=0, verbose_name="is_paypal ?" )
    objet = models.CharField(max_length=255, verbose_name="Objet*")
    chrono = models.CharField(max_length=50, blank=True, unique =True,  editable=False)


    mode = models.CharField(max_length=255, default='',  blank=True,  choices=TYPES, verbose_name="Mode de paiement")
    forme = models.CharField(max_length=255, default='FACTURE',  blank=True,  choices=FORMES, verbose_name="Format")

    beneficiaire = models.CharField(max_length=255, blank=True, verbose_name="En faveur de")
    address = models.CharField(max_length=255, blank=True, verbose_name="Adresse")
    complement = models.CharField(max_length=255, blank=True, verbose_name="Complément d'adresse")
    town = models.CharField(max_length=255, blank=True, verbose_name="Complément d'adresse")
    country = models.ForeignKey(Country, related_name="accountings", blank=True,  null=True,  on_delete=models.SET_NULL, verbose_name="Pays")
    contact = models.CharField(max_length=255, blank=True ,  verbose_name="Contact")

    school = models.ForeignKey(School, related_name="accountings", blank=True, null=True,  on_delete=models.CASCADE, verbose_name="Etablissement")  

    observation = RichTextUploadingField( blank=True, default="", null=True, verbose_name="Observation")

    date_payment  = models.DateTimeField(null=True, blank=True, verbose_name="Date d'effet") # date de paiement
    date          = models.DateTimeField(auto_now_add=True) # date de création de la facture
    user          = models.ForeignKey(User, related_name="accountings", null=True, blank=True,  on_delete=models.CASCADE, editable=False)
    is_active     = models.BooleanField(default=0, verbose_name="Actif ?")
    is_abonnement = models.BooleanField(default=0, verbose_name="Abonnement ?")

    ticket        = models.FileField(upload_to=accounting_directory_path, blank=True, verbose_name="Justificatif",  default="" )
    plan          = models.ForeignKey(Plancomptable, default=17, related_name="accountings", blank=True,  null=True,  on_delete=models.SET_NULL, verbose_name="Plan comptable")
    tp            = models.PositiveIntegerField(default=0, editable=False)


    def __str__(self):
        return self.beneficiaire


    def school_contact(self):
        cs = self.school.users.filter(is_extra=1)
        return  cs


    def solde(self):
        if self.date_payment :
            solde = 0
        else :
            solde = self.amount
        return solde


    def is_display(self):
        ok = False
        if not self.date_payment and self.forme=="FACTURE" and not "Avoir" in self.observation  :
            ok = True
        return ok

 
    def total_solde(self):
        accs = Accounting.objects.filter( date_payment__lte=self.date_payment,is_paypal=0).order_by("date_payment","id")
        s=0
        for a in accs :
            if a.is_credit :
                s +=a.amount
            else :
                s -=a.amount
        return s


    def total_solde_paypal(self):
        accs = Accounting.objects.filter( date_payment__lte=self.date_payment,is_paypal=1).order_by("date_payment","id")
        s=0
        for a in accs :
            if a.is_credit :
                s +=a.amount
            else :
                s -=a.amount
        return s



class Detail(models.Model):
    """ detail d'un Accounting   """
 
    accounting  = models.ForeignKey(Accounting, related_name="details", on_delete=models.CASCADE, verbose_name="Pays")
    description = models.CharField(max_length=255, blank=True ,   verbose_name="Description")
    amount      = models.DecimalField(default=0, blank=True , max_digits=10, decimal_places=2)
 
    def __str__(self):
        return self.accounting


class Provider(models.Model):
    name       = models.CharField(max_length=255, verbose_name="Nom") 
    address    = models.CharField(max_length=255, blank=True, verbose_name="Adresse")
    complement = models.CharField(max_length=255, blank=True, verbose_name="Complément d'adresse")
    town       = models.CharField(max_length=255, blank=True, verbose_name="Complément d'adresse")
    country    = models.ForeignKey(Country, related_name="providers", blank=True,  null=True,  on_delete=models.SET_NULL, verbose_name="Pays")
    contact    = models.CharField(max_length=255, blank=True ,  verbose_name="Contact")
    phone      = models.CharField(max_length=255, blank=True ,  verbose_name="Téléphone")


    def __str__(self):
        return self.name


class Bank(models.Model):
    name       = models.CharField(max_length=255, verbose_name="Nom") 
    address    = models.CharField(max_length=255, blank=True, verbose_name="Adresse")
    complement = models.CharField(max_length=255, blank=True, verbose_name="Complément d'adresse")
    town       = models.CharField(max_length=255, blank=True, verbose_name="Complément d'adresse")
    country    = models.ForeignKey(Country, related_name="banks", blank=True,  null=True,  on_delete=models.SET_NULL, verbose_name="Pays")
    contact    = models.CharField(max_length=255, blank=True ,  verbose_name="Contact")
    phone      = models.CharField(max_length=255, blank=True ,  verbose_name="Téléphone")


    def __str__(self):
        return self.name
 

class Accountancy(models.Model):
    """ Accounting   """

    TYPES = (

        ("Période de test", "Période d'essai"),
        ("par carte de crédit", "Carte de crédit"),
        ("par virement bancaire", "Virement bancaire"),
        ("en espèces", "Espèces"),
        ("par mandatement administratif", "Mandatement administratif"),
    )

    FORMES = (
        ("FACTURE", "FACTURE"),        
        ("AVOIR", "AVOIR"),
    )

    accounting_id = models.PositiveIntegerField(default=0, blank=True,  null=True, editable=False) # cet id doit se mettre dans les 2 lignes
    ranking       = models.PositiveIntegerField(default=1, editable=False) # cet id doit se mettre dans les 2 lignes
    plan_id       = models.PositiveIntegerField(default=0, verbose_name="Plan comptable") # cet id doit se mettre dans les 2 lignes
    is_credit     = models.BooleanField(default=0, verbose_name="is_credit ?" )
    amount        = models.DecimalField(default=0, blank=True , max_digits=10, decimal_places=2,  verbose_name="Montant")
    date          = models.DateTimeField(auto_now_add=True) # date de création de la facture
    current_year  = models.PositiveIntegerField(default=2021, verbose_name="Année") # date de création de la facture

    def __str__(self):
        return "{}.{}".format(self.accounting_id,self.ranking )

    def amount_valeur_absolue(self):
        return abs( self.amount) 

########################################################################################################################################### 
########################################################################################################################################### 
############################################################   Documents    ############################################################### 
########################################################################################################################################### 
########################################################################################################################################### 

class Section(models.Model): # pour l'asso' 

    title = models.CharField(max_length=255, default='',  blank=True, verbose_name="Titre")    
 
 
    def __str__(self):
        return self.title 


class Document(models.Model): # pour l'asso' 

 
    title = models.CharField(max_length=255, default='',  blank=True, verbose_name="Titre")    
    annoncement = RichTextUploadingField( blank=True, verbose_name="Texte*") 
    user = models.ForeignKey(User, related_name = "documents", on_delete=models.CASCADE, editable=False )
    section = models.ForeignKey(Section, related_name = "sections", on_delete=models.CASCADE, verbose_name="Section") 
    ranking = models.PositiveIntegerField(  default=0,  blank=True, null=True,  verbose_name="Ordre", editable=False )

    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modified = models.DateTimeField(auto_now=True, verbose_name="Date de modification") 
 
 
    def __str__(self):
        return self.title 






########################################################################################################################################### 
########################################################################################################################################### 
############################################################  Abonnement    ############################################################### 
########################################################################################################################################### 
########################################################################################################################################### 



class Abonnement(models.Model):

    school              = models.ForeignKey(School, on_delete=models.CASCADE, related_name='abonnement', editable=False)
    date_start          = models.DateTimeField( blank=True, verbose_name="Date de début")
    date_stop           = models.DateTimeField( blank=True, verbose_name="Date de fin")
    accounting          = models.OneToOneField(Accounting, on_delete=models.CASCADE,  related_name="abonnement", editable=False)
    user                = models.ForeignKey(User, on_delete=models.CASCADE, related_name='abonnement', editable=False)
    is_active           = models.BooleanField(default=0, verbose_name="Actif")

    def __str__(self):
        return "{}".format(self.school.name)