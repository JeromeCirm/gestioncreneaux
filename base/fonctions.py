import datetime
import locale
from re import U
from this import d
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate,login
from .models import *
from .config import *

# premier groupe : pour autoriser un créneau pour tout le monde
sans_groupe=Group.objects.get(name="tout le monde")
groupe_staff=Group.objects.get(name="staff")
groupe_gestion_generale=Group.objects.get(name="gestion_generale")
groupe_gestion_creneaux=Group.objects.get(name="gestion_creneaux")

#fonctions générales
locale.setlocale(category=locale.LC_ALL,locale='fr_FR.UTF-8')
def jolie_date(date):
    return date.strftime('%A %e %B')

#fonctions définissant les menus selon le groupe de l'utilisateur : 
def menu(request):
    liste_menu=[
        ["creneaux","jeu libre"],
    ]
    if request.user.is_authenticated:
        lesgroupes=request.user.groups.all()
        if groupe_staff in lesgroupes:
            liste_menu+=[
                ["gestion_creneaux","gestion creneaux"],
                ["recapitulatif","recapitulatif"],
                ["coordonnees","coordonnées staff"],
            ]
        if groupe_gestion_creneaux in lesgroupes:
            liste_menu+=[
                ["creation_creneaux","creation creneaux"],
                ["modif_creneaux","modif creneaux"],
                ["inscrits","inscrits"],
            ]
        if groupe_gestion_generale in lesgroupes:
            liste_menu+=[
                ["gestion_generale","gestion generale"],
                ["initialisation","initialisation"],
            ]
    else:
        liste_menu.append(["connexion","Connexion"])
    return liste_menu

def menu_general(request):
    return menu(request)
    mmenu=[
        ["creneaux","Créneaux"],
        #["informations","Infos"],
    ]
    if request.user.is_authenticated:
        lesgroupes=request.user.groups.all()
        if groupe_staff in lesgroupes:
            mmenu.append(["gestion_creneaux","Menu Staff"])
        if groupe_gestion_creneaux in lesgroupes:
            mmenu.append(["creation_creneaux","Menu Admin"])    
    else:
        mmenu.append(["connexion","Connexion"])
    return mmenu

def menu_staff(request):
    return menu(request)
    mmenu=[
        ["creneaux","jeu libre"],
        ["gestion_creneaux","gestion creneaux"],
        ["recapitulatif","recapitulatif"],
        #["inscrits","inscrits"],
        #["coordonnees","coordonnees"],
    ]
    lesgroupes=request.user.groups.all()
    if groupe_gestion_creneaux in lesgroupes:
        mmenu.append(["creation_creneaux","Menu Admin"])     
    return mmenu

def menu_gestion(request):
    return menu(request)
    mmenu=[
        ["creneaux","jeu libre"],
        ["gestion_creneaux","Menu Staff"],
        ["creation_creneaux","creation creneaux"],
        ["modif_creneaux","modif creneaux"],
        ["gestion_generale","gestion generale"],
        ["initialisation","initialisation"],
    ]
    return mmenu

# récupère les créneaux existants et autorisés pour les groupes de l'utilisateur
# tous pour ne pas tenir compte du groupe de l'utilisateur
# intéressant pour un évènement avec un groupe autre que staff :
# par exemple M18 : staff ok pour gérer mais pas pour s'inscrire à l'évent?
# évènement extérieur : staff ok pour gérer mais pas d'inscription à l'évent.
def recupere_creneaux(request,tous=False):
    if tous:
        creneaux=Creneaux.objects.filter(date__gte=datetime.datetime.now()).order_by('date')
    else:
        lesgroupes_q=request.user.groups.all()
        lesgroupes=[x for x in lesgroupes_q]+[sans_groupe]
        creneaux=Creneaux.objects.filter(date__gte=datetime.datetime.now(),autorisation__groupe__in=lesgroupes).order_by('date')
    return creneaux

# récupère les créneaux existants et autorisés pour les groupes de l'utilisateur
# en renvoyant un dictionnaire pour json
# joli=True pour transformer les dates en format français lisible
# on veux garder l'ordre et json réordonne par les clefs donc attention
# d'où une liste et non un dictionnaire
def json_creneaux(request,tous=False,joli=True):
    def aux(pk): # compte le nb d'inscrits du créneau pk
        val=0
        for x in inscrits:
            if x.idcreneau.pk==pk:
                val+=1
        return val
    try:
        delai=int(Textes.objects.get(nom="delai").contenu)
        if delai<0 or delai>7:
            delai=2
    except:
        delai=2
    date_limite=datetime.date.today()+datetime.timedelta(days=delai)
    creneaux=recupere_creneaux(request,tous)
    inscrits=Inscription.objects.filter(statut="inscrit")
    res=[ {"pk" : x.pk,"date": jolie_date(x.date) if joli else str(x.date),"intitulé" : x.intitulé,"text_bouton" : x.text_bouton,
    "avec_inscription" : x.avec_inscription,"avec_commentaire" : x.avec_commentaire,
    "staff" : x.staff,"nbinscrits" : aux(x.pk), "soon" : x.date<date_limite} for x in creneaux]
    return res

# json de la liste des inscriptions de l'utilisateur
# staff indique si c'est une inscription pour gestion staff ou juste pour jouer
def json_inscription(request,staff=False):
    inscription=Inscription.objects.filter(user=request.user)
    res={}
    for x in inscription:
        if staff and x.statut in ["staff_oui","staff_sibesoin"]:
            res[x.idcreneau.pk]={"statut" : x.statut,"commentaire" : x.commentaire}
        if (not staff) and x.statut=="inscrit":
            res[x.idcreneau.pk]={"statut" : x.statut,"commentaire" : x.commentaire}
    return res

# recupère la liste des créneaux et du staff présent
def creneau_et_staff():
    creneaux=recupere_creneaux(None,True)
    present=Inscription.objects.filter(statut="staff_oui")
    sibesoin=Inscription.objects.filter(statut="staff_sibesoin")
    res={ x.pk : {"date": jolie_date(x.date),"intitulé" : x.intitulé,
    "present" : [],"sibesoin" : []} for x in creneaux}
    for x in present:
        if x.idcreneau.pk in res:
            res[x.idcreneau.pk]["present"].append(x.user.first_name+" "+x.user.last_name)
    for x in sibesoin:
        if x.idcreneau.pk in res:
            res[x.idcreneau.pk]["sibesoin"].append(x.user.first_name+" "+x.user.last_name)
    for x in res:
        res[x]["nb"]=len(res[x]["present"])
    return res

# fonctions pour récupérer les textes d'annonce
def recupere_information(request):
    try:
        if request.user.is_authenticated:
            if not request.user.utilisateur.information:
                return False
        information=Textes.objects.get(nom="information")
        return (information.contenu).split('\n')
    except:
        return False # si la base de données est corrompue, ne doit pas arriver

def recupere_annonce():
    try:
        annonce=Textes.objects.get(nom="annonce")
        return (annonce.contenu).split('\n')
    except:
        return [] # si la base de données est corrompue, ne doit pas arriver

# traitement click sur un créneau pour le staff
def click_staff(request):
    try:
        if (request.POST['avecclick']!="true"): return
        id=int(request.POST['id'])
        creneau=Creneaux.objects.get(pk=id)
        #autorisation=Autorisation.objects.filter(idcreneau=creneau)
        #lesgroupes=request.user.groups.all()
        #for x in autorisation:
        #    if x.groupe==sans_groupe or x.groupe in lesgroupes:
                # le créneau existe et est autorisé pour user
        if True: # début à enlever : le staff gère tout sans pb d'autorisation
                inscriptions=Inscription.objects.filter(idcreneau=creneau,user=request.user)
                for inscription in inscriptions:
                    if inscription.statut=="staff_sibesoin":
                        inscription.statut="staff_oui"
                        inscription.save()
                        creneau.staff=creneau.staff+1
                        creneau.save()
                        return 
                    if inscription.statut=="staff_oui":  
                        inscription.delete()
                        creneau.staff=max(creneau.staff-1,0)
                        creneau.save()
                        return
                # on n'a pas trouvé d'inscription en gestion staff
                new_inscription=Inscription(idcreneau=creneau,user=request.user,statut="staff_sibesoin")
                new_inscription.save()
                return
    except:
        #print("click non traité pour cause d'erreur")
        pass
        
# traitement click sur un créneau pour l'inscription à l'évènement'
def click_creneau(request):
    try:
        if (request.POST['avecclick']!="true"): return
        id=int(request.POST['id'])
        creneau=Creneaux.objects.get(pk=id)
        if not creneau.avec_inscription : return # pas d'inscription demandée? Ne doit pas arriver
        autorisation=Autorisation.objects.filter(idcreneau=creneau)
        lesgroupes=request.user.groups.all()
        for x in autorisation:
            if x.groupe==sans_groupe or x.groupe in lesgroupes:
                # le créneau existe et est autorisé pour user
                inscriptions=Inscription.objects.filter(idcreneau=creneau,user=request.user)
                for inscription in inscriptions:
                    if inscription.statut=="inscrit":  
                        inscription.delete()
                        return
                # on n'a pas trouvé d'inscription à l'évènement
                new_inscription=Inscription(idcreneau=creneau,user=request.user,statut="inscrit")
                new_inscription.save()
                return
        #print("pas d'autorisation")
    except:
        #print("click non traité pour cause d'erreur")
        pass

#partie gestion : modif/suppression d'un créneau 
def supprime_creneau(post):
    if True: #try:
        if post['avecclick']=="false":
            return
        id=int(post['id'])
        creneau=Creneaux.objects.get(pk=id)
        lesinscrits=Inscription.objects.filter(idcreneau=creneau)
        liste_mail=[x.user.email for x in lesinscrits]
        if liste_mail!=[]:
            msg="Bonjour !\n\n"
            msg+="Le créneau de "+jolie_date(creneau.date)+" "+creneau.intitulé+" ne peut être maintenu, nous devons le supprimer.\n"
            msg+="A bientôt sur le sable,\n\n"
            msg+="L'équipe SSA"
            envoie_mail(liste_mail,"Annulation de créneau",msg)
        creneau.delete()
    #except:
        pass #ne doit pas arriver : formulaire incorrect
        # éventuellement possible si admin loggué deux fois

def modifie_creneau(post):
    try:
        id=int(post['id'])
        creneau=Creneaux.objects.get(pk=id)
        creneau.date=post['date']
        creneau.intitulé=post['intitule']
        creneau.text_bouton=post['text_bouton']
        if 'avec_inscription' in post:
            creneau.avec_inscription=True  
        else:
            creneau.avec_inscription=False
        creneau.text_bouton=post['text_bouton']
        if 'avec_commentaire' in post:
            creneau.avec_commentaire=True
        else:
            creneau.avec_commentaire=False
        creneau.save()
    except:
        pass #ne doit pas arriver : formulaire incorrect
        # éventuellement possible si admin loggué deux fois

# fonction de demande de creation de compte utilisateur
# si les champs sont corrects et le compte inexistant, initialise le compte
# et envoie un lien par mail pour activer le compte
import string,random
def hash(n=40):
    #renvoie 40 lettres/chiffres aléatoires
    val=string.digits+string.ascii_letters
    return ''.join(random.choice(val) for i in range(n))

def demande_creation_compte(request):
    try:
        login=request.POST['login']
        prenom=request.POST['prenom']
        nom=request.POST['nom']
        mail=request.POST['mail']
        telephone=request.POST['telephone']
        password=request.POST['password']
        password_verif=request.POST['password_verif']
        if password!=password_verif:
            return False,"les mots de passe ne sont pas identiques"
        # teste si l'utilisateur existe déjà
        utilisateurs=User.objects.filter(username=login)
        if len(utilisateurs)>0:
            return False,"ce login n'est pas disponible"
        # inutile normalement sauf base corrompue
        utilisateurs=Utilisateur.objects.filter(user__username=login)
        if len(utilisateurs)>0:
            return False,"ce login n'est pas disponible"
    except:        
        return False,"Le formulaire est incomplet."
    try:
        new_user=User.objects.create_user(username=login,first_name=prenom,last_name=nom,email=mail,password=password)
        new_user.save()
        le_hash=hash()
        new_utilisateur=Utilisateur(user=new_user,telephone=telephone,csrf_token=le_hash,date_demande=datetime.datetime.now())
        new_utilisateur.save()
        msg="Bonjour "+prenom+",\n\nVoici le lien pour activer le compte sur le site SSA (valable 7 jours): \n" 
        msg+=MA_URL_COMPLETE+"validation_compte/"+login+"/"+le_hash
        msg+="\n\nL'équipe SSA"    
        envoie_mail([mail],'inscription site SSA',msg)
        return True,"reussi"
    except:
        return False,"erreur lors de la création de compte"

# vérifie si on peut activer le compte login.
# renvoi "reussi" si c'est bon et un message d'erreur sinon
def verifie_lien_validation(login,lehash):
    try:
        user=User.objects.get(username=login)
        utilisateur=Utilisateur.objects.get(user=user,csrf_token=lehash)
        if not utilisateur.en_attente_confirmation:
            return "le compte associé est déjà validé"
        if utilisateur.date_demande+datetime.timedelta(days=7)<datetime.date.today():
            return "le lien a expiré"
        utilisateur.en_attente_confirmation=False
        utilisateur.save()
        return "le compte a bien été validé!"
    except:
        return "le lien est invalide"

# fonction d'envoi de mail
from django.core.mail import send_mail
from gestioncreneaux.settings import EMAIL_HOST_USER

def envoie_mail(liste_destinataire,sujet,corps_mail): 
    send_mail(subject=sujet,message=corps_mail,from_email=EMAIL_HOST_USER,recipient_list=liste_destinataire)

# création d'un compte staff
# vérifie que le login est dispo. 
# à faire : Si non, propose d'ajouter au groupe staff la personne
def ajout_compte(request):
    if True:#try:
        login=request.POST['login']
        nom=request.POST['nom']
        prenom=request.POST['prenom']
        mail=request.POST['mail']
        telephone=request.POST['telephone']
        password=request.POST['password']
        user=User.objects.filter(username=login)
        if len(user)>0:
            return False,"Ce login est déjà utilisé"
        if ('gr_gestion' in request.POST or 'gr_admin' in request.POST ) and (request.POST['confirmation']!='CONFIRMATION'):
            return False,"Pour créer un compte gestion ou admin, il faut entre CONFIRMATION dans le champs de confirmation"
        new_user=User.objects.create_user(username=login,first_name=prenom,last_name=nom,email=mail,password=password)
        new_user.save()
        if 'gr_staff' in request.POST:
            groupe_staff.user_set.add(new_user)
        if 'gr_gestion' in request.POST:
            groupe_gestion_creneaux.user_set.add(new_user)
        if 'gr_admin' in request.POST:
            groupe_gestion_generale.user_set.add(new_user)
        new_utilisateur=Utilisateur(user=new_user,telephone=telephone,csrf_token="e",date_demande=datetime.datetime.now(),en_attente_confirmation=False)
        new_utilisateur.save() 
        msg="Bonjour "+prenom+",\n\n"
        msg+="Ton compte vient d'être créé sur le site SSA.\n"
        msg+="Ton login est : "+login+ " et ton mot de passe est : "+password+"\n"
        msg+="Pour te connecter au site c'est ici : "+MA_URL_COMPLETE+"gestion_creneaux"
        msg+="\n\nL'équipe SSA"
        envoie_mail([mail],'Bienvenu au group staff SSA',msg)
        return True, "compte "+login+" créé"
    #except:
        return False,"Formulaire incorrect"

def modifie_compte(request):
    try:
        pk=request.POST['mpk']
        nom=request.POST['mnom']
        prenom=request.POST['mprenom']
        mail=request.POST['mmail']
        telephone=request.POST['mtelephone']
        user=User.objects.get(pk=pk)
        if user.username=="admin":
            return False,"Impossible de modifier le compte admin"
        if ('gr_gestion' in request.POST or 'gr_admin' in request.POST ) and (request.POST['mconfirmation']!='CONFIRMATION'):
            return False,"Pour modifier un compte gestion ou admin, il faut entre CONFIRMATION dans le champs de confirmation"
        user.first_name=prenom
        user.last_name=nom
        user.email=mail
        user.save()
        utilisateur=Utilisateur.objects.get(user=user)
        utilisateur.telephone=telephone
        utilisateur.save()
        if 'gr_staff' in request.POST and user not in groupe_staff.user_set.all():
            groupe_staff.user_set.add(user)
        if 'gr_staff' not in request.POST and user in groupe_staff.user_set.all():
            groupe_staff.user_set.remove(user)       
        if 'gr_gestion' in request.POST and user not in groupe_gestion_creneaux.user_set.all():
            groupe_gestion_creneaux.user_set.add(user)
        if 'gr_gestion' not in request.POST and user in groupe_gestion_creneaux.user_set.all():
            groupe_gestion_creneaux.user_set.remove(user)   
        if 'gr_admin' in request.POST and user not in groupe_gestion_generale.user_set.all():
            groupe_gestion_generale.user_set.add(user)
        if 'gr_admin' not in request.POST and user in groupe_gestion_generale.user_set.all():
            groupe_gestion_generale.user_set.remove(user)   
        return True, "compte "+user.username+" modifié"
    except:
        return False,"Formulaire incorrect"

def recupere_comptes():
    tous=User.objects.all().exclude(username='admin').order_by('username')
    res={}
    for x in tous:
        gr=x.groups.all()
        res[x.pk]={'login' : x.username,'prenom' : x.first_name,'nom' : x.last_name,
        'mail' : x.email,"is_staff" : groupe_staff in gr,
        "is_gestion" : groupe_gestion_creneaux in gr,
        'is_admin' : groupe_gestion_generale in gr}
    tous=Utilisateur.objects.all()
    for x in tous:
        if x.user.pk in res:
            res[x.user.pk]['telephone']=x.telephone
    return res

def recupere_txt_annonce():
    try:
        return Textes.objects.get(nom="annonce").contenu
    except:
        return ""

def recupere_txt_information():
    try:
        return Textes.objects.get(nom="information").contenu
    except:
        return ""

def modifie_annonce(request):
    try:
        annonce=Textes.objects.get(nom="annonce")
        annonce.contenu=request.POST['annonce']
        annonce.save()
        return True,"annonce modifiée"
    except:
        return False,"erreur dans la base de données !"

def modifie_information(request):
    try:
        information=Textes.objects.get(nom="information")
        information.contenu=request.POST['information']
        information.save()
        return True,"information modifiée"
    except:
        return False,"erreur dans la base de données !"

def change_mot_de_passe(request):
    try:
        password=request.POST['password']
        newpassword=request.POST['newpassword']
        newpassword_confirm=request.POST['newpassword_confirm']
        user=authenticate(request,username=request.user.username,password=password)    
        if (newpassword!=newpassword_confirm):
            return "le nouveau mot de passe est mal écrit"
        if user is not None:
            user=User.objects.get(username=request.user.username)
            user.set_password(newpassword)
            user.save()
            login(request,user)
            return "changement de mot de passe effectué"
        return "le mot de passe est incorrect"
    except:
        return "erreur dans le formulaire"

# action refusée pour admin ou compte gestion generale
def envoie_mail_recuperation_mot_de_passe(request):
    msg="Si le login et le mail correspondent à un compte existant, un mail a été envoyé pour réinitialiser le mot de passe."
    try:
        login=request.POST['login']
        mail=request.POST['mail']
        if login=="admin":
            return msg
        user=User.objects.get(username=login,email=mail)
        if groupe_gestion_generale in user.groups.all():
            return msg
        lehash=hash()
        utilisateur=Utilisateur.objects.get(user=user)
        utilisateur.csrf_token=lehash
        utilisateur.date=datetime.datetime.now()
        utilisateur.reinitialisation_password=True
        utilisateur.save()
        msg_mail="Bonjour "+user.first_name+",\n\n"
        msg_mail+="Une demande de réinitialisation de mail vient d'être envoyé pour ton compte SSA\n"
        msg_mail+="clique sur ce lien pour changer de mot de passe : "
        msg_mail+=MA_URL_COMPLETE+"demande_reinitialisation/"+login+"/"+lehash
        msg_mail+="\n\nL'équipe SSA"
        envoie_mail([mail],'Demande de récupération de compte SSA',msg_mail)
        return msg
    except:
        return msg

# vérifie si la demande de récupération de mail est légitime
# renvoie un dictionnaire de contexte pour le template
# le champs autorise est mis à vrai si c'est bien autorisé
# le message d'erreu est alors dans msg
def verifie_lien_reinitialisation(login,lehash):
    try:
        user=User.objects.get(username=login)
        utilisateur=Utilisateur.objects.get(user=user,csrf_token=lehash)
        if not utilisateur.reinitialisation_password:
            return {"autorise" : False, "msg":"le lien est invalide"}
        if utilisateur.date_demande+datetime.timedelta(days=7)<datetime.date.today():
            return {"autorise" : False, "msg":"le lien a expiré"}
        return {"autorise" : True, "login" : login,"hash" : lehash}
    except:
        return {"autorise" : False, "msg":"le lien est invalide"}

# réinitialisation interdite pour admin et groupe gestion générale
def reinitialise_mot_de_passe(request):
    try:
        username=request.POST['login']
        lehash=request.POST['hash']
        newpassword=request.POST['password']
        if username=="admin":
            return {"autorise" : False, "msg" : "action impossible"}
        user=User.objects.get(username=username)
        if groupe_gestion_generale in user.groups.all():
            return {"autorise" : False, "msg" : "action impossible"}
        utilisateur=Utilisateur.objects.get(user=user,csrf_token=lehash)
        if not utilisateur.reinitialisation_password:
            return {"autorise" : False, "msg":"le lien est invalide"}
        if utilisateur.date_demande+datetime.timedelta(days=7)<datetime.date.today():
            return {"autorise" : False, "msg":"le lien a expiré"}
        user.set_password(newpassword)
        user.save()
        login(request,user)                
        utilisateur.reinitialisation_password=False
        utilisateur.save()
        return {"autorise" : False, "msg" : "le mot de passe a été correctement modifié"}
    except:
        return {"autorise" : False, "msg":"le lien est invalide"}

# noms et téléphones du staff
def recupere_coordonnees_staff():
    lestaff=groupe_staff.user_set.all()
    res=[]
    for user in lestaff:
        res.append({"nom" : user.first_name+" "+user.last_name,"telephone" : user.utilisateur.telephone})
    return res

# liste des créneaux avec inscriptions et les personnes inscrites 
def recupere_inscrits():
    lescreneaux=Creneaux.objects.filter(avec_inscription=True,date__gte=datetime.datetime.now()).order_by('date')
    res=[]
    for uncreneau in lescreneaux:
        lesinscrits=Inscription.objects.filter(idcreneau=uncreneau)
        res.append({"creneau" : jolie_date(uncreneau.date),"inscrits" : lesinscrits})
    return res

# modifie le nombre de jours à partir duquel un créneau n'est pas indiqué en rouge sans staff
def modifie_delai(request):
    try:
        delai=int(request.POST['delai'])
        if delai<0 or delai>7:
            delai=2
        txt=Textes.objects.get(nom="delai")
        txt.contenu=delai
        txt.save()
        return True,"La durée a été mise à jour pour la gestion des créneaux sans staff"
    except:
        return False,"Erreur lors de la modification du de la gestion des créneaux sans staff"

# récupère les réglages d'un compte et les mets dans context
def recupere_reglages(request,context):
    try:
        context["information"]=request.user.utilisateur.information
        context["telephone"]=request.user.utilisateur.telephone
        context["nom"]=request.user.last_name
        context["prenom"]=request.user.first_name
        context["mail"]=request.user.email
    except:
        pass

def change_reglages(request):
    try:
        if "information" in request.POST:
            request.user.utilisateur.information=True
        else:
            request.user.utilisateur.information=False
        request.user.utilisateur.telephone=request.POST['telephone']
        request.user.email=request.POST['mail']
        request.user.first_name=request.POST['prenom']
        request.user.last_name=request.POST['nom']
        request.user.utilisateur.save()
        request.user.save()
        return "Les modifications des réglages ont été enregistrées."
    except:
        return "Erreur lors du changement des réglages"




