let select=document.getElementById("select")
let inputpk=document.getElementById("mpk")
let prenom=document.getElementById("mprenom")
let nom=document.getElementById("mnom")
let mail=document.getElementById("mmail")
let telephone=document.getElementById("mtelephone")
let isstaff=document.getElementById("mid_gr_staff")
let isgenerale=document.getElementById("mid_gr_gestion")
let isadmin=document.getElementById("mid_gr_admin")

function ajusteDonnees() {
    pk=select.value
    inputpk.value=pk
    prenom.value=lescomptes[pk]['prenom']
    nom.value=lescomptes[pk]['nom']
    mail.value=lescomptes[pk]['mail']
    telephone.value=lescomptes[pk]['telephone']
    isstaff.checked=(lescomptes[pk]['is_staff']=="True")
    isgenerale.checked=(lescomptes[pk]['is_gestion']=="True")
    isadmin.checked=(lescomptes[pk]['is_admin']=="True")
}