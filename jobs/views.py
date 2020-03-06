from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from jobs.models import Server, BackupJob
from jobs.serializers import ServerSerializer, JobSerializer
# Create your views here.
"""
Algorithm for saving from agent POST request

* Agent sends POST in JSON format
* Agent data should have an additional field, "Server Name" so the server ID of the associated Server the job is associated with can be fetched
* Fetch the server ID from the "Server Name" in the JSON request
* Append the server ID to the JSON, with a key of "server"
* Remote the "Server Name" key from the JSON
* return this new JSON string to the JobSerializer
"""


@api_view(['GET', 'POST'])
def job_list(request):
   if request.method == 'GET':
      jobs = BackupJob.objects.all()
      serializer = JobSerializer(jobs, many=True)
      return Response(serializer.data)
   elif request.method == 'POST':
      serializer = JobSerializer(data=request.data)
      if serializer.is_valid():
         serializer.save()
         return Response(serializer.data, status=status.HTTP_201_CREATED)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   elif request.method == 'DELETE':
      BackupJob.objects.get(pk=pk).delete()
      return Response(status=status.HTTP_204_NO_CONTENT)

