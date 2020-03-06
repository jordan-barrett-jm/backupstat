from django.db import models
from backupserver.models import BackupServer

class Server(models.Model):
#the server that is backed up
   name = models.CharField(max_length=100, default='')
   backupsvr = models.ForeignKey(BackupServer, on_delete=models.CASCADE)

class BackupJob(models.Model):
   name = models.CharField(max_length=100, default='', null=True, blank=True)
   type = models.CharField(max_length=100, default='', null=True, blank=True)
   start_time = models.CharField(max_length=100, default='', null=True, blank=True)
   status = models.CharField(max_length=50, default='', null=True, blank=True)
   comment = models.CharField(max_length=250, default='', null=True, blank=True)
   server = models.ForeignKey(Server, on_delete=models.CASCADE)
