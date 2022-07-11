from django.shortcuts import render,redirect
from django.contrib.auth import logout,authenticate, login
from django.http import HttpResponse
import json
from .fonctions import *
from .forms import *

# A FAIRE !!!!!!!!!!!!
# - connexion : se débrouiller pour revenir sur la bonne page :
#     soit selon le groupe, soit selon la page(à enregistrer) d'appel de connexion
# - réglage : afficher le bon menu et pas celui d'un simple utilisateur, si staff/admin? anecdotique
# - si le statut du créneau change : inscription/non : supprimer les inscrits?
# - nettoyer la base avec les comptes non validés au bout d'un moment?
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
    context["information"]=recupere_information()
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
    if request.metho=="POST":   
        pass
    context={}
    return render(request,'base/recuperation_password.html',context)

# pages générales si connecté
@auth()
def reglages(request):
    context={"menu" : menu_general(request)}
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
def inscrits(request):
    context={"menu" : menu_staff(request)}
    return render(request,'base/inscrits.html',context)

@auth([groupe_staff])
def coordonnees(request):
    context={"menu" : menu_staff(request)}
    return render(request,'base/coordonnees.html',context)

#pages accessibles aux gestionnaires de créneaux
@auth([groupe_gestion_creneaux])
def creation_creneaux(request):
    context={"menu" : menu_gestion(request)}
    if request.method=="POST":
        form=CreneauxForm(request.POST)
        if form.is_valid():
            new_creneau=form.save()
            autorisation_creneau=Autorisation(idcreneau=new_creneau,groupe=sans_groupe)
            autorisation_creneau.save()
    else:
        form=CreneauxForm()
    context['form']=form
    context['creneaux']=recupere_creneaux(request,tous=True)
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
    #context['creneaux']=recupere_creneaux(request,tous=True)
    return render(request,'base/modif_creneaux.html',context)

#pages accessibles aux gestionnaires avec tous les droits
@auth([groupe_gestion_generale])
def gestion_generale(request):
    context={"menu" : menu_gestion(request)}
    return render(request,'base/gestion_generale.html',context)

@auth([groupe_gestion_generale])
def initialisation(request):
    context={"menu" : menu_gestion(request)}
    return render(request,'base/initialisation.html',context)
