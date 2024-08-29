/* modèle de créneau */
var intitule=document.getElementById("id_intitulé")
var textebouton=document.getElementById("id_text_bouton")
var sans_inscription=document.getElementById("sans_inscription")
var avec_inscription=document.getElementById("avec_inscription")
var lien_html=document.getElementById("lien")

function jeu_libre_classique() {
    intitule.value=""
    textebouton.value="Accès libre"
    sans_inscription.checked=true
}

function jeu_libre_inscription() {
    intitule.value=""
    textebouton.value="Cliquer pour s'inscrire"
    avec_inscription.checked=true
}

function cmb() {
    intitule.value=" CMB "
    textebouton.value="Cliquer pour s'inscrire"
    avec_inscription.checked=true
}

function avec_lien() {
    intitule.value=""
    textebouton.value="Lien d'inscription"
    lien_html.checked=true
}

/* sans doute le plus courant */
jeu_libre_classique()