from django.forms import ModelForm
from .models import *

class CreneauxForm(ModelForm):
    class Meta:
        model=Creneaux
        fields='__all__'

class AutorisationForm(ModelForm):
    class Meta:
        model=Autorisation
        fields='__all__'
