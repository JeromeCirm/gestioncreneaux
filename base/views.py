from django.shortcuts import render,redirect
from django.contrib.auth import logout,authenticate, login
from django.http import HttpResponse
import json

from gestioncreneaux.settings import SECURE_SSL_REDIRECT
from .fonctions import *
from .forms import *

# A FAIRE !!!!!!!!!!!!
# - connexion : se débrouiller pour revenir sur la bonne page :
#     soit selon le groupe, soit selon la page(à enregistrer) d'appel de connexion
# - réglage : afficher le bon menu et pas celui d'un simple utilisateur, si staff/admin? anecdotique
# - si le statut du créneau change : inscription/non : supprimer les inscrits?
# - nettoyer la base avec les comptes non validés au bout d'un moment?
#  - enlever les fonctions menus en trop une fois que c'est bien géré
# # !!!!!!!!!!!!!!!!!!!!!!

# décorateur pour vérifier si le groupe de l'utilisateur est dans la liste
# renvoie vers la page de connexion sinon
# pas d'arguments (ou liste vide) si on veut juste un utilisateur quelconque connecté
def auth(group_list=[]):
    def teste(func):
        def nouvelle_func(request,*args,**kwargs):
            if request.user.is_authenticated:
                if group_list==[]:
                    return func(request,*args,**kwargs)
                lesgroupes=request.user.groups.all()
                for x in group_list:
                    if x in lesgroupes:
                        return func(request,*args,**kwargs)
            return connexion(request)
        return nouvelle_func
    return teste

# pages générales pour tout le monde
def creneaux(request):
    if request.method=='POST':
        if request.user.is_authenticated:
            click_creneau(request)
            response_data = {"creneaux":json_creneaux(request),
            "inscription":json_inscription(request)}
        else:
            if ("avecclick" in request.POST) and (request.POST["avecclick"]=="true"):
                response_data={"demande" : "creneaux"}
            else:
                response_data={"creneaux":json_creneaux(request),"inscription" :{}}
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    context={"menu" : menu_general(request)}
    context["annonce"]=recupere_annonce()
    context["information"]=recupere_information(request)
    return render(request,'base/creneaux.html',context)

def informations(request):
    context={"menu" : menu_general(request)}
    return render(request,'base/informations.html',context)

def connexion(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=authenticate(request,username=username,password=password)
        if user is not None: 
            # on vérifie si le compte a bien été activé
            try:
                utilisateur=Utilisateur.objects.get(user=user)
                if not utilisateur.en_attente_confirmation:
                    login(request,user)
                    return redirect('creneaux')
                #compte en attente si on arrive ici
            except:
                pass
    context={"menu" : []}
    return render(request,'base/connexion.html',context)

def deconnexion(request):
    logout(request)
    return creneaux(request)

def creation_compte(request):
    context={"menu" : []}
    if request.method=="POST":
        reussi,err=demande_creation_compte(request)
        if reussi:
            context["reussi"]=True
        else:
            context["echec"]=True
            context["err"]=err
            context["ancien"]=request.POST
    return render(request,'base/creation_compte.html',context)

def validation_compte(request,login=None,lehash=None):
    if login==None:
        context={ "msg" : "Le lien n'est pas valide"}
    else:
        context={ "msg" : verifie_lien_validation(login,lehash)}
    return render(request,'base/validation_compte.html',context)

def recuperation_password(request):
    context={}
    if request.method=="POST":   
        context["msg"]=envoie_mail_recuperation_mot_de_passe(request)
    return render(request,'base/recuperation_password.html',context)

def demande_reinitialisation(request,login=None,lehash=None):
    if request.method=='POST':
        print("here")
        context={**reinitialise_mot_de_passe(request)}
    elif login==None:
        context={ "msg" : "Le lien n'est pas valide"}
    else:
        context={ **verifie_lien_reinitialisation(login,lehash)}
    return render(request,'base/demande_reinitialisation.html',context)

# pages générales si connecté
@auth()
def reglages(request):
    context={"menu" : menu_general(request)}
    if request.method=="POST":
        if 'action' in request.POST:
            if request.POST['action']=='change password':
                context["msg"]=change_mot_de_passe(request)
            if request.POST['action']=='reglages':
                context["msg"]=change_reglages(request)
    recupere_reglages(request,context)
    return render(request,'base/reglages.html',context)

# pages accessibles au staff
@auth([groupe_staff])
def gestion_creneaux(request):
    if request.method=='POST':
        click_staff(request)
        response_data = {"creneaux":json_creneaux(request,tous=True),
        "inscription":json_inscription(request,staff=True)}
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    context={"menu" : menu_staff(request)}
    return render(request,'base/gestion_creneaux.html',context)

@auth([groupe_staff])
def recapitulatif(request):
    context={"menu" : menu_staff(request)}
    context["creneau_et_staff"]=creneau_et_staff()
    return render(request,'base/recapitulatif.html',context)

@auth([groupe_staff])
def coordonnees(request):
    context={"menu" : menu_staff(request),"lestaff" : recupere_coordonnees_staff()}
    return render(request,'base/coordonnees.html',context)

#pages accessibles aux gestionnaires de créneaux
@auth([groupe_gestion_creneaux])
def creation_creneaux(request):
    context={"menu" : menu_gestion(request)}
    if request.method=="POST":
        form=CreneauxForm(request.POST)
        print(request.POST)
        if form.is_valid():
            new_creneau=form.save()
            autorisation_creneau=Autorisation(idcreneau=new_creneau,groupe=sans_groupe)
            autorisation_creneau.save()
    else:
        form=CreneauxForm()
    context['form']=form
    context['creneaux']=joli_date_creneaux(recupere_creneaux(request,tous=True))
    return render(request,'base/creation_creneaux.html',context)

@auth([groupe_gestion_creneaux])
def modif_creneaux(request):
    if request.method=='POST':
        if 'action' in request.POST:
            if request.POST['action']=='supprime':
                supprime_creneau(request.POST) 
            if request.POST['action'] =='modifie':
                modifie_creneau(request.POST)          
        #click_staff(request)
        response_data = {"creneaux":json_creneaux(request,tous=True,joli=False)}
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    context={"menu" : menu_gestion(request)}
    return render(request,'base/modif_creneaux.html',context)

@auth([groupe_staff])
def inscrits(request):
    context={"menu" : menu_staff(request), "inscriptions" : recupere_inscrits()}
    return render(request,'base/inscrits.html',context)

#pages accessibles aux gestionnaires avec tous les droits
@auth([groupe_gestion_generale])
def gestion_generale(request):
    res,err=None,""
    if request.method=='POST':
        if 'action' in request.POST:
            if request.POST['action']=='ajout':
                res,err=ajout_compte(request)
            if request.POST['action'] =='modifie':
                res,err=modifie_compte(request)
            if request.POST['action']=='annonce':
                res,err=modifie_annonce(request)
            if request.POST['action']=='information':
                res,err=modifie_information(request)
            if request.POST['action']=='delai':
                res,err=modifie_delai(request)
    try:
        delai=int(Textes.objects.get(nom="delai").contenu)
    except:
        delai=2
    context={"menu" : menu_gestion(request),"lescomptes" : recupere_comptes(),
     "reussi" : res, "err" : err, "annonce" : recupere_txt_annonce(), "delai" : delai,
     "information" : recupere_txt_information() }
    return render(request,'base/gestion_generale.html',context)

@auth([groupe_gestion_generale])
def stats(request):
    context={"menu" : menu_staff(request)}
    #la_liste=creneau_et_staff_ancien()
    #context["staff_en_or"]=ordonne(la_liste)
    #context["creneau_et_staff"]=la_liste
    return render(request,'base/stats.html',context)

@auth([groupe_gestion_generale])
def recupere_stats(request):
    if request.method=='POST' and "fonction" in request.POST:
        response_data=recupere_stats_fonction(request.POST["fonction"])
    else:
        response_data={}
    return HttpResponse(json.dumps(response_data), content_type="application/json")    

@auth([groupe_gestion_generale])
def initialisation(request):
    context={"menu" : menu_gestion(request)}
    envoie_mail_bis(['jerome.99@hotmail.fr'],"bienvenu à SSA","Bonjour\n\nCeci est un premier mail pour tester TLS\n\n Jerome")
    return render(request,'base/initialisation.html',context)
