/* Mise à jour du texte du bouton lors du changement de statut avec/Sans inscirption */
function maj_bouton(id) {
    var text_bouton=document.getElementById(id.toString()+'_text_bouton')
    var avec_inscription=document.getElementById(id.toString()+'_avec_inscription')
    if (avec_inscription.checked) {
      text_bouton.value="Cliquer pour s'inscrire"
    } else {
      text_bouton.value="Accès libre"
    }
}

/* appel de l'API pour gérer un click(éventuellement) et mettre 
à jour les créneaux concernés */
function modifie(id,type_lien) {
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
    text_lien=document.getElementById(lid+'text_lien')
    formData.append('lien',text_lien.value)
    type_creneau=document.getElementsByName(lid+'type_creneau')
    for (var i=0; i < type_creneau.length; i++)  {
      if (type_creneau[i].checked) {
        formData.append('type_creneau',type_creneau[i].value)
      }
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
    for (var tmp in creneaux) {
        creneau=creneaux[tmp]
        inter=creneau.pk
        lid=inter.toString()+'_'
        var noeud=document.createElement('div')
        noeud.setAttribute('id',inter)
        noeud.setAttribute('class',"modif")

        var child=document.createElement('div')
        child.setAttribute('class','item_formulaire center')
        var label=document.createElement('label')
        label.innerHTML="date : "+creneau["joliedate"]
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
        label.innerHTML="horaire/intitulé : "
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
        label.innerHTML="lien HTML : "
        child.appendChild(label)
        var lien=document.createElement('input')
        lien.value=creneau["lien"]
        lien.setAttribute('id',lid+'text_lien')
        child.appendChild(lien)
        noeud.appendChild(child)
        
        
        var child=document.createElement('div')
        var ip=document.createElement('input')
        ip.setAttribute('type','radio')
        ip.setAttribute('id',lid+'sans_inscription')
        ip.setAttribute('name',lid+'type_creneau')
        ip.setAttribute('value','0')
        if (creneau.type_creneau == 0 ) {
          ip.checked=true
        }
        child.appendChild(ip)
        var lab=document.createElement('label')
        lab.setAttribute('for',lid+'sans_inscription')
        lab.innerHTML="créneau libre"
        child.appendChild(lab)
        var ip=document.createElement('input')
        ip.setAttribute('type','radio')
        ip.setAttribute('id',lid+'avec_inscription')
        ip.setAttribute('name',lid+'type_creneau')
        ip.setAttribute('value','1')
        if (creneau.type_creneau == 1 ) {
          ip.checked=true
        }
        child.appendChild(ip)
        var lab=document.createElement('label')
        lab.setAttribute('for',lid+'avec_inscription')
        lab.innerHTML="avec inscription"
        child.appendChild(lab)
        noeud.appendChild(child)


        var child=document.createElement('div')
        var ip=document.createElement('input')
        ip.setAttribute('type','radio')
        ip.setAttribute('id',lid+'lien')
        ip.setAttribute('name',lid+'type_creneau')
        ip.setAttribute('value','2')
        if (creneau.type_creneau == 2 ) {
          ip.checked=true
        }        
        child.appendChild(ip)
        var lab=document.createElement('label')
        lab.setAttribute('for',lid+'lien')
        lab.innerHTML="lien HTML"
        child.appendChild(lab)
        noeud.appendChild(child)        




        var bout_modifie=document.createElement('button')
        bout_modifie.setAttribute('onclick','modifie('+inter.toString()+','+')')
        bout_modifie.innerHTML="Enregistrer les modifs de ce créneau"
        noeud.appendChild(bout_modifie)

        var bout_supprime=document.createElement('button')
        bout_supprime.setAttribute('onclick','supprime('+inter.toString()+',true)')
        bout_supprime.innerHTML="Supprimer ce créneau"
        noeud.appendChild(bout_supprime)
        divCreneaux.appendChild(noeud)
    }
}
