import uuid
from django.db import models
from django_cron import CronJobBase, Schedule
from qcm.models import Parcours
from django.utils import formats, timezone
from datetime import datetime, timedelta       
from ckeditor_uploader.fields import RichTextUploadingField
from account.models import User


def webinaire_image_directory_path(instance, filename):
    return "webinaires/{}/{}".format(instance.id, filename)


class MyCronJob(CronJobBase):
    RUN_EVERY_MINS = 120 # every 2 hours

    today = timezone.now()

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = str(uuid.uuid4())[:64]    # a unique code

    def do(self):
        Parcours.objects.filter(stop__lt=today,is_trash=0).update(is_publish=0)


class Formule(models.Model):

	ADHESIONS = (
	    ('Mensuelle', 'Mensuelle'),
	    ('Trimestrielle', 'Trimestrielle'),
	    ('Annuelle', 'Annuelle'),
	)

	NAMES = (
	    ('Autonomie', 'Autonomie'),
	    ('Accompagnement', 'Accompagnement'),
	)

	name      = models.CharField(max_length=255, verbose_name="Nom", choices=NAMES)
	price     = models.DecimalField(max_digits=6, decimal_places = 2 , verbose_name="Montant")
	is_family = models.BooleanField(default=0, verbose_name="Forfait famille ?") 
	is_sale   = models.BooleanField(default=0, verbose_name="En vente ?")

	def __str__(self):
	    return "{}".format(self.name)

	def data(self) :

		coeff_two = 1.8
		coeff_three = 2.6
		coeff_four = 3.4
		coeff_more = 4.2

		data = {}
		date = datetime.now()

		price_tab = self.price.split(",")
		price = price_tab[0]+"."+price_tab[1]
		this_month = date.month


		if this_month < 13 and this_month > 6 :
			left_month = 19 - int(this_month)
		else :
			left_month= 7 - int(this_month) 

		if self.nb_month == 1 :
			left_month= 1   

		else :
			if self.nb_month == 3 :

				if left_month > 2  :
					left_month = 3

		end1 = date 	+ timedelta(days = 372)
		end2 = date 	+ timedelta(days = 99)
		end3 = date 	+ timedelta(days = 38)  
 
		adh =  float(self.price) 
		adh2 =  adh * coeff_two 
		adh3 =  adh * coeff_three
		adh4 =  adh * coeff_four
		adh5 =  adh * coeff_more

		data["today"] = date
		data["start"] = date 	+ timedelta(days = 7) 
		data["end1"] = end1
		data["end2"] = end2
		data["end3"] = end3

		#année
		data["total0a"] = round(12 * adh,2)
		data["price0a"] = round(adh,2)

		data["total1a"] = round(12 * adh,2)
		data["price1a"] = round(adh,2)


		data["total2a"] = round( 12 * adh2 ,2)
		data["price2"] = round(adh2,2)

		data["total3a"] = round( 12 * adh3 ,2)
		data["price3a"] = round(adh3,2)

		data["total4a"] = round( 12 * adh4 ,2)
		data["price4a"] = round(adh4,2)

		data["total5a"] = round( 12 * adh5 ,2)
		data["price5a"] = round(adh5,2)	
		

		#trimestre
		data["total0m"] = round(3*adh,2)
		data["price0m"] = round(adh,2)

		data["total1m"] = round(3*adh,2)
		data["price1m"] = round(adh,2)

		data["total2m"] = round(3*adh2 ,2)
		data["price2m"] = round(adh2,2)

		data["total3m"] = round(3*adh3 ,2)
		data["price3m"] = round(adh3,2)

		data["total4m"] = round(3*adh4 ,2)
		data["price4m"] = round(adh4,2)

		data["total5m"] = round(3*adh5 ,2)
		data["price5m"] = round(adh5,2)	


		#mois
		data["total0"] = round( adh,2)
		data["price0"] = round(adh,2)

		data["total1"] = round(adh,2)
		data["price1"] = round(adh,2)


		data["total2"] = round(adh2 ,2)
		data["price2"] = round(adh2,2)

		data["total3"] = round(adh3 ,2)
		data["price3"] = round(adh3,2)

		data["total4"] = round(adh4 ,2)
		data["price4"] = round(adh4,2)

		data["total5"] = round(adh5 ,2)
		data["price5"] = round(adh5,2)	

		return data


	def total(self) :
		return round( self.price   , 2)


class Formuleprice(models.Model):


	formule  = models.ForeignKey(Formule, on_delete=models.CASCADE,  related_name='prices', verbose_name="Menu")
	price    = models.DecimalField(max_digits=6, decimal_places = 2 , verbose_name="Montant")
	nb_month = models.PositiveIntegerField(default=1, verbose_name="Nombre de mois")     

	def __str__(self):
	    return "{}".format(self.formule.name)



TIMES = (
	    (20, 20),
	    (30, 30),
	    (40, 40),
	    (50, 50),
	    (60, 60),
	)

class Webinaire(models.Model):

    title = models.CharField(max_length=255, null=True, blank=True,   verbose_name="Titre")
    is_publish = models.BooleanField(default=0, verbose_name="Publié ?")
    date_time = models.DateTimeField(verbose_name="Date/heure")
    imagefile = models.ImageField(upload_to=webinaire_image_directory_path, verbose_name="Image", blank=True, null = True , default ="")

    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modified = models.DateTimeField(auto_now=True, verbose_name="Date de modification")

    topic = RichTextUploadingField( blank=True, default="", null=True, verbose_name="Remarques")
    duration = models.PositiveIntegerField(  default=0,  blank=True, null=True, verbose_name="Durée", choices = TIMES)

    users =  models.ManyToManyField(User, related_name="webinaires", blank=True,  verbose_name="Participants")

    def __str__(self):    
        return "{}".format(self.title)


 

class Tweeter(models.Model):

 
    title        = models.CharField(max_length=255, blank=True, verbose_name="Titre")  
    texte        = RichTextUploadingField(  verbose_name="Texte")      
    date_created = models.DateTimeField( auto_now_add= True)
 

    def __str__(self):
        return "{}".format(self.title)