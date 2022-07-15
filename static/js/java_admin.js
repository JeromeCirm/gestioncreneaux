/* modèle de créneau */
var intitule=document.getElementById("id_intitulé")
var textebouton=document.getElementById("id_text_bouton")
var avecinscription=document.getElementById("id_avec_inscription")
var aveccommentaire=document.getElementById("id_avec_commentaire")

function jeu_libre_classique() {
    intitule.value=""
    textebouton.value="Accès libre"
    avecinscription.checked=false
    aveccommentaire.checked=false
}

function jeu_libre_inscription() {
    intitule.value=""
    textebouton.value="Cliquer pour s'inscrire"
    avecinscription.checked=true
    aveccommentaire.checked=false
}

function cmb() {
    intitule.value="CMB "
    textebouton.value="Cliquer pour s'inscrire"
    avecinscription.checked=true
    aveccommentaire.checked=false
}

/* met à jour le texte par défaut du bouton quand on change le champ inscription*/
function MajInscription() {
    if (avecinscription.checked) {
        textebouton.value="Cliquer pour s'inscrire"
    } else {
        textebouton.value="Accès libre"
    }
}

/* sans doute le plus courant */
jeu_libre_classique()