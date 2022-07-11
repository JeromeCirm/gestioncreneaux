/* appel de l'API pour gérer un click(éventuellement) et mettre 
à jour les créneaux concernés */
function modifie(id) {
    var formData = new FormData();
	  formData.append('id', id);
    formData.append('action','modifie')
    csrf=document.getElementsByName('csrfmiddlewaretoken')[0]
    formData.append('csrfmiddlewaretoken',csrf.value)
    lid=id.toString()+'_'
    date=document.getElementById(lid+'date')
    formData.append('date',date.value)
    intitule=document.getElementById(lid+'intitule')
    formData.append('intitule',intitule.value)
    text_bouton=document.getElementById(lid+'text_bouton')
    formData.append('text_bouton',text_bouton.value)
    avec_inscription=document.getElementById(lid+'avec_inscription')
    if (avec_inscription.checked) {
      formData.append('avec_inscription','on')
    }
    avec_commentaire=document.getElementById(lid+'avec_commentaire')
    if (avec_commentaire.checked) {
      formData.append('avec_commentaire','on')
    }
    fetch("modif_creneaux", {
	  method : 'POST',
	  headers : {
		'Accept': 'application/json, text/plain, */*',
  	  },
  	  body: formData
	}).then(function(res){ return res.json();})
	  .then(function(res){
        affiche_creneau(res["creneaux"])
 	  })
  	  .catch(function(err){ console.log('Erreur requête', err);});
}

function supprime(id,avecclick=true) {
    var formData = new FormData();
	  formData.append('id', id);
    formData.append('avecclick',avecclick)
    formData.append('action','supprime')
    csrf=document.getElementsByName('csrfmiddlewaretoken')[0]
    formData.append('csrfmiddlewaretoken',csrf.value)
	  fetch("modif_creneaux", {
	  method : 'POST',
	  headers : {
		'Accept': 'application/json, text/plain, */*',
  	  },
  	  body: formData
	}).then(function(res){ return res.json();})
	  .then(function(res){
        affiche_creneau(res["creneaux"])
 	  })
  	  .catch(function(err){ console.log('Erreur requête', err);});
}

/* insère les créneaux dans la DOM */
function affiche_creneau(creneaux) {
    var divCreneaux=document.getElementById('liste_creneau')
    divCreneaux.innerHTML="";
    for (var inter in creneaux) {
        creneau=creneaux[inter]
        lid=inter.toString()+'_'
        var noeud=document.createElement('div')
        noeud.setAttribute('id',inter)
        noeud.setAttribute('class',"modif")

        var child=document.createElement('div')
        child.setAttribute('class','item_formulaire center')
        var label=document.createElement('label')
        label.innerHTML="date : "
        child.appendChild(label)
        var date=document.createElement('input')
        date.setAttribute('type','date')
        date.value=creneau["date"]
        date.setAttribute('id',lid+'date')
        child.appendChild(date)
        noeud.appendChild(child)

        var child=document.createElement('div')
        child.setAttribute('class','item_formulaire center')
        var label=document.createElement('label')
        label.innerHTML="intitulé : "
        child.appendChild(label)
        var intitule=document.createElement('input')
        intitule.value=creneau["intitulé"]
        intitule.setAttribute('id',lid+'intitule')
        child.appendChild(intitule)
        noeud.appendChild(child)

        var child=document.createElement('div')
        child.setAttribute('class','item_formulaire center')
        var label=document.createElement('label')
        label.innerHTML="texte bouton : "
        child.appendChild(label)
        var text_bouton=document.createElement('input')
        text_bouton.value=creneau["text_bouton"]
        text_bouton.setAttribute('id',lid+'text_bouton')
        child.appendChild(text_bouton)
        noeud.appendChild(child)

        var child=document.createElement('div')
        child.setAttribute('class','item_formulaire center')
        var label=document.createElement('label')
        label.innerHTML="avec inscription ? : "
        child.appendChild(label)
        var avec_inscription=document.createElement('input')
        avec_inscription.setAttribute('type','checkbox')
        avec_inscription.checked=creneau["avec_inscription"]
        avec_inscription.setAttribute('id',lid+'avec_inscription')
        child.appendChild(avec_inscription)
        noeud.appendChild(child)

        var child=document.createElement('div')
        child.setAttribute('class','item_formulaire center')
        var label=document.createElement('label')
        label.innerHTML="avec commentaire ? : "
        child.appendChild(label)
        var avec_commentaire=document.createElement('input')
        avec_commentaire.setAttribute('type','checkbox')
        avec_commentaire.checked=creneau["avec_commentaire"]
        avec_commentaire.setAttribute('id',lid+'avec_commentaire')
        child.appendChild(avec_commentaire)
        noeud.appendChild(child)

        var bout_modifie=document.createElement('button')
        bout_modifie.setAttribute('onclick','modifie('+inter.toString()+',true)')
        bout_modifie.innerHTML="Enregistrer les modifs de ce créneau"
        noeud.appendChild(bout_modifie)

        var bout_supprime=document.createElement('button')
        bout_supprime.setAttribute('onclick','supprime('+inter.toString()+')')
        bout_supprime.innerHTML="Supprimer ce créneau"
        noeud.appendChild(bout_supprime)
        divCreneaux.appendChild(noeud)
    }
}
