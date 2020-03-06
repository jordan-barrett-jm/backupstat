from rest_framework import serializers
from models import BackupServer

class BackupServerSerializer(serializers.Serializer):
   name = serializers.CharField(max_length=100, default='')
   company = serializers.CharField(max_length=100, default='')
   class Meta:
      model = BackupServer
      fields = ('name', 'company')
