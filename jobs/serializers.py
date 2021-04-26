from rest_framework import serializers
from jobs.models import BackupJob, Server
from backupserver.models import BackupServer

class ServerSerializer(serializers.ModelSerializer):
   backupsvr = serializers.PrimaryKeyRelatedField(queryset=BackupServer.objects.all())
   class Meta:
      model = Server
      fields = ('id','name', 'backupsvr')

class JobSerializer(serializers.ModelSerializer):
   server = serializers.PrimaryKeyRelatedField(queryset=Server.objects.all())
   start_time = serializers.DateTimeField(input_formats=["%m/%d/%Y %H:%M:%S"])
   class Meta:
      model = BackupJob
      fields = ('id','name', 'type', 'start_time', 'status', 'comment', 'server')
      
