from django import forms
from .models import MainModel

class MainForm(forms.ModelForm):
    class Meta:
        model = MainModel
        fields = ['sel_archivo']

    sel_archivo = forms.FileField(
        required=True,
        label='Selecciona el archivo de los RFC',
        widget=forms.ClearableFileInput(attrs={'accept': '.txt,.xlsx', 'name' : 'sel_archivo'}),
    )