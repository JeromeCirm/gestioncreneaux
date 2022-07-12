import datetime
import locale
from django.contrib.auth.models import Group
from .models import *
from .config import *

# premier groupe : pour autoriser un créneau pour tout le monde
sans_groupe=Group.objects.get(name="tout le monde")
groupe_staff=Group.objects.get(name="staff")
groupe_gestion_generale=Group.objects.get(name="gestion_generale")
groupe_gestion_creneaux=Group.objects.get(name="gestion_creneaux")

#fonctions générales
locale.setlocale(locale.LC_ALL,'french')
def jolie_date(date):
    return date.strftime('%A %e %B')

#fonctions définissant les menus selon le groupe de l'utilisateur
def menu_general(request):
    menu=[
        ["creneaux","Les créneaux"],
        ["informations","Infos"],
    ]
    if request.user.is_authenticated:
        lesgroupes=request.user.groups.all()
        if groupe_staff in lesgroupes:
            menu.append(["gestion_creneaux","Menu Staff"])
        if groupe_gestion_creneaux in lesgroupes:
            menu.append(["creation_creneaux","Menu Admin"])    
    else:
        menu.append(["connexion","Connexion"])
    return menu

def menu_staff(request):
    menu=[
        ["creneaux","jeu libre"],
        ["gestion_creneaux","gestion_creneaux"],
        ["recapitulatif","recapitulatif"],
        ["inscrits","inscrits"],
        ["coordonnees","coordonnees"],
    ]
    lesgroupes=request.user.groups.all()
    if groupe_gestion_creneaux in lesgroupes:
        menu.append(["creation_creneaux","Menu Admin"])     
    return menu

def menu_gestion(request):
    menu=[
        ["creneaux","jeu libre"],
        ["gestion_creneaux","Menu Staff"],
        ["creation_creneaux","creation_creneaux"],
        ["modif_creneaux","modif_creneaux"],
        ["gestion_generale","gestion_generale"],
        ["initialisation","initialisation"],
    ]
    return menu

# récupère les créneaux existants et autorisés pour les groupes de l'utilisateur
# tous pour ne pas tenir compte du groupe de l'utilisateur
# intéressant pour un évènement avec un groupe autre que staff :
# par exemple M18 : staff ok pour gérer mais pas pour s'inscrire à l'évent?
# évènement extérieur : staff ok pour gérer mais pas d'inscription à l'évent.
def recupere_creneaux(request,tous=False):
    if tous:
        creneaux=Creneaux.objects.filter(date__gte=datetime.datetime.now())
    else:
        lesgroupes_q=request.user.groups.all()
        lesgroupes=[x for x in lesgroupes_q]+[sans_groupe]
        creneaux=Creneaux.objects.filter(date__gte=datetime.datetime.now(),autorisation__groupe__in=lesgroupes)
    return creneaux

# récupère les créneaux existants et autorisés pour les groupes de l'utilisateur
# en renvoyant un dictionnaire pour json
# joli=True pour transformer les dates en format français lisible
def json_creneaux(request,tous=False,joli=True):
    creneaux=recupere_creneaux(request,tous)
    inscrits=Inscription.objects.filter(statut="inscrit")
    res={ x.pk : {"date": jolie_date(x.date) if joli else str(x.date),"intitulé" : x.intitulé,"text_bouton" : x.text_bouton,
    "avec_inscription" : x.avec_inscription,"avec_commentaire" : x.avec_commentaire,
    "staff" : x.staff,"nbinscrits" : 0} for x in creneaux}
    for x in inscrits:
        if x.idcreneau.pk in res:
            res[x.idcreneau.pk]["nbinscrits"]+=1
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
            res[x.idcreneau.pk]["present"].append(x.user.username)
    for x in sibesoin:
        if x.idcreneau.pk in res:
            res[x.idcreneau.pk]["sibesoin"].append(x.user.username)
    for x in res:
        res[x]["nb"]=len(res[x]["present"])
    return res

# fonctions pour récupérer les textes d'annonce
def recupere_information():
    try:
        return Textes.objects.get(nom="information")
    except:
        return "" # si la base de données est corrompue, ne doit pas arriver

def recupere_annonce():
    try:
        return Textes.objects.get(nom="annonce")
    except:
        return "" # si la base de données est corrompue, ne doit pas arriver

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
    try:
        if post['avecclick']=="false":
            print('initilisation')
            return
        id=int(post['id'])
        creneau=Creneaux.objects.get(pk=id)
        creneau.delete()
    except:
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
    new_user=User.objects.create_user(username=login,first_name=prenom,last_name=nom,email=mail,password=password)
    new_user.save()
    le_hash=hash()
    new_utilisateur=Utilisateur(user=new_user,telephone="",csrf_token=le_hash,date_demande=datetime.datetime.now())
    new_utilisateur.save()
    msg="Bonjour "+prenom+",\n\nVoici le lien pour activer le compte sur le site SSA (valable 7 jours): \n" 
    msg+=MA_URL_COMPLETE+"validation_compte/"+login+"/"+le_hash
    msg+="\n\nL'équipe SSA"    
    envoie_mail([mail],'inscription site SSA',msg)
    return True,"reussi"

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
import smtplib
from email.message import EmailMessage
from ssl import create_default_context

def envoie_mail(liste_destinataire,sujet,corps_mail):
    smtpserver = smtplib.SMTP(ENVOIE_MAIL_HOST,ENVOIE_MAIL_PORT)
    user = ENVOIE_MAIL_USER
    password = ENVOIE_MAIL_PASSWORD
    smtpserver.starttls(context=create_default_context())
    smtpserver.ehlo()
    smtpserver.login(user, password)
    msg = EmailMessage()
    msg.set_content(msg)
    msg['From'] = user
    msg['Subject'] = sujet
    msg.set_content(corps_mail)
    for to in liste_destinataire:
        msg['To'] = to
        smtpserver.send_message(msg)
    smtpserver.close()