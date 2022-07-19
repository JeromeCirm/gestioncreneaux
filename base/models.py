from operator import mod
from django.db import models
from django.contrib.auth.models import Group, User

class Utilisateur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telephone = models.CharField(max_length=30)
    date_demande=models.DateField(null=True)
    csrf_token=models.TextField(null=True)
    en_attente_confirmation=models.BooleanField(default=True) # lien envoyé et non validé par mail
    reinitialisation_password=models.BooleanField(default=False)
    information=models.BooleanField(default=True)

class Creneaux(models.Model):
    date=models.DateField()
    intitulé=models.CharField(max_length=100)
    text_bouton=models.CharField(max_length=100,default="")
    avec_inscription=models.BooleanField(default=False)
    avec_commentaire=models.BooleanField(default=False)
    staff=models.IntegerField(default=0,blank=True)

class Inscription(models.Model):
    idcreneau=models.ForeignKey(Creneaux,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    commentaire=models.CharField(max_length=100)
    statut=models.CharField(max_length=50,default="")

class Autorisation(models.Model):
    idcreneau=models.ForeignKey(Creneaux,on_delete=models.CASCADE)
    groupe=models.ForeignKey(Group,on_delete=models.CASCADE)

class Textes(models.Model):
    nom=models.CharField(max_length=50)
    contenu=models.TextField()
