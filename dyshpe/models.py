from django.db import models

from account.models import User, Adhesion
from socle.models import Subject , Level


class Facturedys(models.Model):
    """docstring for Facture"""
    chrono    = models.CharField(max_length=50,  verbose_name="Chrono", editable= False) # Insertion du code de la facture.
    user      = models.ForeignKey(User, blank=True,  null=True, related_name="facturedys", on_delete=models.CASCADE, editable= False)
    adhesions = models.ManyToManyField(Adhesion, related_name="facturedys", blank=True, editable= False)
    date      = models.DateField(auto_now_add=True)
    orderID   = models.CharField(max_length=25, verbose_name="Numéro de paiement donné par CA", blank=True, null= True, default="") 


    def __str__(self):
        return "{} {}".format(self.user, self.file)


