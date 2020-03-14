from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey
from jobs.models import Server, BackupJob
from backupserver.models import BackupServer
from jobs.serializers import ServerSerializer, JobSerializer
import json
import datetime
from jobs.forms import FilterForm

"""
Algorithm for saving from agent POST request

* Agent sends POST in JSON format
* Agent data should have an additional field, "Server Name" so the server ID of the associated Server the job is associated with can be fetched
* Fetch the server ID from the "Server Name" in the JSON request
* Append the server ID to the JSON, with a key of "server"
* Remove the "Server Name" key from the JSON
* return this new JSON string to the JobSerializer


The POST request will be in the following format
{"backupID": id,
 "jobs": [jobs]
}
"""

def addJobs(data):
#this function takes the POST request data and creates jobs from there
   backup_server = data["backupID"]
   jobs = data["jobs"]
   result = False
   for job in jobs:
      #don't save repeats
      jobfilter = BackupJob.objects.filter(name=job["name"].strip(), start_time=job["start_time"].strip())
      print (jobfilter)
      if jobfilter:
         print ("yes")
         continue
      serializer = JobSerializer(data=jobFormat(job, backup_server))
      if serializer.is_valid():
         serializer.save()
         result = True
      else:
         result = False
   return result

def createServer(server_name, backup_server):
#creates a server if it does not already exist
   backup_obj = BackupServer.objects.get(id=backup_server)
   server = Server(name=server_name, backupsvr=backup_obj)
   server.save()
   return server.id

def jobFormat(job, backup_server):
#formats the job JSON so it can be accepted by the serializer
   server_name = job["server"]
   server_ID = Server.objects.filter(name=server_name)
   if server_ID:
      server_ID = server_ID[0].id
   else:
      server_ID = createServer(server_name, backup_server)
   job["server"] = server_ID
   return job

#accepts JSON post requests only from agents that have an authorized API key
@api_view(['POST'])
@permission_classes([HasAPIKey])
def job_post(request):
   if addJobs(request.data):
      return Response(status=status.HTTP_201_CREATED)
   return Response(status=status.HTTP_400_BAD_REQUEST)

#filter backup jobs based on specifications from the form
#date from form is yyyy-mm-dd
def filterJobs(form):
   if form.cleaned_data["backupserver"] != "--ALL--":
      servers = Server.objects.filter(backupsvr__id=form.cleaned_data["backupserver"])
      jobs = []
      for server in servers:
         jobs += BackupJob.objects.filter(server__id=server.id)
   else:
      jobs = BackupJob.objects.all()
   fromDate = form.cleaned_data["fromDate"]
   toDate = form.cleaned_data["toDate"]
   filter_jobs = []
   if jobs:
      for job in jobs:
         job_date = datetime.datetime.strptime(job.start_time, "%m/%d/%Y %H:%M:%S").date()
         if toDate >= job_date >= fromDate:
            filter_jobs += BackupJob.objects.filter(id=job.id)
   return filter_jobs

#returns a list of backup jobs
def job_list(request):
   if request.method == 'POST':
      form = FilterForm(request.POST)
      if form.is_valid():
         filtered_jobs = filterJobs(form)
         newform = FilterForm()
         context = {"jobs":filtered_jobs, "form":newform}
         return render(request, 'jobs/jobs.html', context)
   elif request.method == 'DELETE':
      BackupJob.objects.get(pk=pk).delete()
      return Response(status=status.HTTP_204_NO_CONTENT)
   form = FilterForm()
   jobs = BackupJob.objects.all()
   context = {"jobs": jobs, "form":form}
   return render(request, 'jobs/jobs.html', context)
   
