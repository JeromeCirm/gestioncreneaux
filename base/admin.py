from django.contrib import admin
from .models import *

class UtilisateurAdmin(admin.ModelAdmin):
    list_display=('user','telephone','date_demande','en_attente_confirmation','reinitialisation_password')

class CreneauxAdmin(admin.ModelAdmin):
    list_display=('date','intitulé','text_bouton','type_creneau','lien','staff')

class InscriptionAdmin(admin.ModelAdmin):
    list_display=('idcreneau','user','commentaire','statut')

class AutorisationAdmin(admin.ModelAdmin):
    list_display=('idcreneau','groupe')

class TextesAdmin(admin.ModelAdmin):
    list_display=('nom','contenu')

admin.site.register(Utilisateur,UtilisateurAdmin)
admin.site.register(Creneaux,CreneauxAdmin)
admin.site.register(Inscription,InscriptionAdmin)
admin.site.register(Autorisation,AutorisationAdmin)
admin.site.register(Textes,TextesAdmin)