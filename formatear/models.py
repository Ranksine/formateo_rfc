from django.db import models

# Create your models here.
class MainModel(models.Model):
    sel_archivo = models.FileField(
        upload_to='archivos/',
        max_length=100,
        null=True,
        blank=True,
    )
    
class persona(models.Model):
    id_persona = models.IntegerField(null=True, blank=True)
    nombre= models.CharField(max_length=255)
    paterno= models.CharField(max_length=255)
    materno= models.CharField(max_length=255)
    rfc= models.CharField(max_length=255)
    f_nac = models.CharField(max_length=255)
    
    rfc_13 = models.CharField(max_length=20)
    