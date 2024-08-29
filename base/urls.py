from django.urls import path,re_path
from . import views

urlpatterns = [
    path('initialisation',views.initialisation,name='initialisation'),
    path('gestion_generale',views.gestion_generale,name='gestion_generale'),
    path('modif_creneaux',views.modif_creneaux,name='modif_creneaux'),
    path('creation_creneaux',views.creation_creneaux,name='creation_creneaux'),
    path('inscrits',views.inscrits,name='inscrits'),
    path('recapitulatif',views.recapitulatif,name='recapitulatif'),
    path('gestion_creneaux',views.gestion_creneaux,name='gestion_creneaux'),
    path('coordonnees',views.coordonnees,name='coordonnees'),
    path('connexion',views.connexion,name='connexion'),
    path('deconnexion',views.deconnexion,name='deconnexion'),
    path('recuperation_password',views.recuperation_password,name='recuperation_password'),
    path('recuperation_login',views.recuperation_login,name='recuperation_login'),
    path('creation_compte',views.creation_compte,name='creation_compte'),
    path('validation_compte/<str:login>/<str:lehash>',views.validation_compte,name='validation_compte'),
    re_path(r'validation_comptea*',views.validation_compte,name='validation_compte_erreur'),
    path('demande_reinitialisation/<str:login>/<str:lehash>',views.demande_reinitialisation,name='demande_reinitialisation'),
    re_path(r'demande_reinitialisationa*',views.demande_reinitialisation,name='demande_reinitialisation_erreur'),
    path('reglages',views.reglages,name='reglages'),
    path('informations',views.informations,name='informations'),
    path('stats',views.stats,name='stats'),
    path('recupere_stats',views.recupere_stats,name='recupere_stats'),
    re_path(r'a*', views.creneaux,name='creneaux'),   
]

