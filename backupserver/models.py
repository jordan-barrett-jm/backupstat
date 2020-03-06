from django.db import models

# Create your models here.
class BackupServer(models.Model):
   name = models.CharField(max_length=100, default='')
   company = models.CharField(max_length=100, default='')
