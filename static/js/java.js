/* appel de l'API pour gérer un click(éventuellement) et récupérer les créneaux 
partie gestion staff */
function click_staff(id,avecclick=true) {
    var formData = new FormData();
	formData.append('id', id);
    formData.append('avecclick',avecclick)
    csrf=document.getElementsByName('csrfmiddlewaretoken')[0]
    formData.append('csrfmiddlewaretoken',csrf.value)
	fetch("gestion_creneaux", {
	  method : 'POST',
	  headers : {
		'Accept': 'application/json, text/plain, */*',
  	  },
  	  body: formData
	}).then(function(res){ return res.json();})
	  .then(function(res){
        affiche_creneau_staff(res["creneaux"],res["inscription"],id,avecclick)
 	  })
  	  .catch(function(err){ console.log('Erreur requête', err);});
}

/* insère les créneaux dans la DOM avec le style approprié au statut 
partie gestion staff */
function affiche_creneau_staff(creneaux,inscription,id,avecclick) {
    var divCreneaux=document.getElementById('creneaux_staff')
    divCreneaux.innerHTML="";
    for (var tmp in creneaux) {
        creneau=creneaux[tmp]
        inter=creneau.pk
        var noeud=document.createElement('div')
        noeud.innerHTML=creneau.date+" : "+creneau["intitulé"]
        if (creneau.staff==0) {
            noeud.setAttribute('class','red cwhite')
        }
        divCreneaux.appendChild(noeud)
        var noeud=document.createElement('div')
        noeud.innerHTML=creneau.staff.toString()+" inscrit(e)s"
        divCreneaux.appendChild(noeud)
        var noeud=document.createElement('div')
        var label=document.createElement('label')
        label.setAttribute('onclick','click_staff('+inter.toString()+')')
        if (inter in inscription) {
            if (inscription[inter].statut=="staff_sibesoin") {
                label.innerHTML="Si Besoin"
                label.setAttribute('class','round darkblue cwhite pointer')
            } else {
                label.innerHTML="Présent(e)"
                label.setAttribute('class','round orange cblack pointer')
            }
        } else {
            label.innerHTML="Absent(e)"
            label.setAttribute('class','round blue cwhite pointer')
            if ((inter==id) && (avecclick) && creneau.staff==0) {
                alert("Attention, tu étais la seule personne du staff sur ce créneau. Pense à prévenir les autres personnes sur le groupe WhatsApp !")
            }
        }
        noeud.appendChild(label)
        divCreneaux.appendChild(noeud)
    }
}

/* appel de l'API pour gérer un click(éventuellement) et récupérer les créneaux 
partie principale accessible à tous */
function click_creneau(id,avecclick=true) {
    var formData = new FormData();
	formData.append('id', id);
    formData.append('avecclick',avecclick)
    csrf=document.getElementsByName('csrfmiddlewaretoken')[0]
    formData.append('csrfmiddlewaretoken',csrf.value)
	fetch("creneaux", {
	  method : 'POST',
	  headers : {
		'Accept': 'application/json, text/plain, */*',
  	  },
  	  body: formData
	}).then(function(res){ return res.json();})
	  .then(function(res){
        if ('demande' in res) {
            document.location.href="connexion"
        } else {
            affiche_creneau_general(res["creneaux"],res["inscription"])
        }
 	  })
  	  .catch(function(err){ console.log('Erreur requête', err);});
}

/* insère les créneaux dans la DOM avec le style approprié au statut 
partie principale accessible à tous */
function affiche_creneau_general(creneaux,inscription) {
    var divCreneaux=document.getElementById('creneaux_general')
    divCreneaux.innerHTML="";
    for (var tmp in creneaux) {
        creneau=creneaux[tmp]
        inter=creneau.pk
        var noeud=document.createElement('div')
        noeud.innerHTML=creneau.date+" :<BR>"+creneau["intitulé"]
        divCreneaux.appendChild(noeud)
        var noeud=document.createElement('div')
        var label=document.createElement('label')
        if (creneau.soon && creneau.staff == 0) {
            label.innerHTML="Créneau en attente"
            label.setAttribute('class','round red')
            noeud.appendChild(label)
        } else if (creneau.avec_inscription) {
            label.setAttribute('onclick','click_creneau('+inter.toString()+')')
            if (inter in inscription) {
                label.innerHTML="Inscrit(e) !"
                label.setAttribute('class','round orange pointer')
            } else {
                label.innerHTML=creneau.text_bouton
                label.setAttribute('class','round blue pointer')
            }
            var nb=document.createElement('span')
            nb.innerHTML='<BR>'+creneau.nbinscrits.toString()+' inscrit(e)s'
            noeud.appendChild(label)
            noeud.appendChild(nb)
        } else {
            label.innerHTML=creneau.text_bouton
            label.setAttribute('class','roundlibre')
            noeud.appendChild(label)
        }
        divCreneaux.appendChild(noeud)
    }
}