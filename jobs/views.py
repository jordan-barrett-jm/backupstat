
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
from django.core.paginator import Paginator
from dateutil import tz
from django.contrib.auth.decorators import login_required

"""Algorithm for saving from agent POST request

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

def localTime():
   HERE = tz.gettz("America/Bogota")
   UTC = tz.gettz('UTC')
   now = datetime.datetime.utcnow()
   gmt = now.replace(tzinfo=UTC)
   gmt.astimezone(HERE)
   return gmt.astimezone(HERE)

def addJobs(data):
#this function takes the POST request data and creates jobs from there
   backup_server = data["backupID"]
   #update the backupserver with the last communication time
   bksvr = BackupServer.objects.get(id=backup_server)
   bksvr.last_communication = str(localTime())
   bksvr.save()
   jobs = data["jobs"]
   result = False
   for job in jobs:
      #don't save repeats
      jobfilter = BackupJob.objects.filter(name=job["name"].strip(), start_time=job["start_time"].strip())
      if jobfilter:
         print (job)
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

#returns a filtered job QuerySet for a specified time period
def timeFilter(jobs, fromDate, toDate):
   filter_jobs = 0
   for job in jobs:
      job_date = datetime.datetime.strptime(job.start_time, "%m/%d/%Y %H:%M:%S").date()
      if toDate >= job_date >= fromDate:
         if not filter_jobs:
            filter_jobs = BackupJob.objects.filter(id=job.id)
         else:
            filter_jobs |= BackupJob.objects.filter(id=job.id)
   return filter_jobs

#filter backup jobs based on specifications from the form
#date from form is yyyy-mm-dd
def filterJobs(form_dict):
   if form_dict["backupserver"] != "--ALL--":
      servers = Server.objects.filter(backupsvr__id=form_dict["backupserver"])
      jobs = 0
      for server in servers:
         if not jobs:
            jobs = BackupJob.objects.filter(server__id=server.id)
         else:
            jobs |= BackupJob.objects.filter(server__id=server.id)
   else:
      jobs = BackupJob.objects.all()
   fromDate = form_dict["fromDate"]
   toDate = form_dict["toDate"]
   if jobs:
      filter_jobs = timeFilter(jobs, fromDate, toDate)
      return filter_jobs
   return ""

#sort jobs by the specified sort type
def jobSort(sort_type, order, jobs):
   if order == "ascending":
      jobs = jobs.order_by(sort_type)
   else: 
      jobs = jobs.order_by(sort_type).reverse()
   return jobs

#returns a tuple with the sort value and the order
def sortType(rq):
   reverse_sort = 0
   try:
      sort_type = rq.get("sort-reverse")
      if sort_type:
         reverse_sort = 1
   except IndexError:
      pass
   if reverse_sort:
      return (sort_type, "descending")
   else:
      sort_type = rq.get("sort")
      return (sort_type, "ascending")

#returns a list of backup jobs
@login_required(login_url='/useradmin/login/')
def job_list(request):
   if request.method == 'DELETE':
      BackupJob.objects.get(pk=pk).delete()
      return Response(status=status.HTTP_204_NO_CONTENT)
   jobs = BackupJob.objects.all()
   #if the user has not specified a filter and is not requesting a filter to be applied then apply the default filter
   if "filter" not in request.session and "backupserver" not in request.GET:
      fromDate = datetime.datetime.today() - datetime.timedelta(days=7)
      toDate = datetime.datetime.today()
      jobs = timeFilter(jobs, fromDate.date(), toDate.date())
   #checks if there were additional parameters passed to the site in the URL (if there is a sort or filter being done)
   if request.GET:
   #if a sort request was made by the user then handle it
      if "sort" in request.GET or "sort-reverse" in request.GET:
          sort = sortType(request.GET)
          #save the user specified sort to the session
          request.session['sort'] = sort
          if "filter" in request.session:
             filter_data = request.session["filter"]
             #format the dates to a date object for use by the filterJobs function
             fromDate = datetime.datetime.strptime(filter_data["fromDate"], "%Y-%m-%d").date()
             toDate = datetime.datetime.strptime(filter_data["toDate"], "%Y-%m-%d").date()
             #put the data into a dictionary so filterJobs can operate on it
             form_dict = {"backupserver": filter_data["backupserver"], "fromDate": fromDate, "toDate": toDate}
             #apply and save the filter to jobs
             jobs = filterJobs(form_dict)
          if jobs:
             jobs = jobSort(sort[0], sort[1], jobs)
    #if backupserver parameter is in the site URL that means a filter is being done
      elif "backupserver" in request.GET:
         form = FilterForm(request.GET)
         if form.is_valid():
            #pass the data from the form to the fitlerJobs function to get jobs that meet the user specifications
            filtered_jobs = filterJobs(form.cleaned_data)
            form_data = form.cleaned_data
            #save the data from the form to the session
            request.session["filter"] = {'backupserver': form_data["backupserver"], "fromDate": str(form_data["fromDate"]), "toDate": str(form_data["toDate"])}
            #if the user previously specified a sort and filtered_jobs came back with results then sort these results based on previous user specifications for sort
            if filtered_jobs and "sort" in request.session:
               sort_type = request.session["sort"]
               filtered_jobs = jobSort(sort_type[0], sort_type[1],  filtered_jobs)
            newform = FilterForm()
            context = {"jobs":filtered_jobs, "form":newform}
            return render(request, 'jobs/jobs.html', context)
   else:
   #always filter before you sort. if you sort before filtering then the filter erases the sort.
      if "filter" in request.session:
         filter_data = request.session["filter"]
         fromDate = datetime.datetime.strptime(filter_data["fromDate"], "%Y-%m-%d").date()
         toDate = datetime.datetime.strptime(filter_data["toDate"], "%Y-%m-%d").date()
         form_dict = {"backupserver": filter_data["backupserver"], "fromDate": fromDate, "toDate": toDate}
         jobs = filterJobs(form_dict)
      if "sort" in request.session:
         sort_type = request.session["sort"]
         jobs = jobSort(sort_type[0], sort_type[1], jobs)
   #if the user has not specified a sort then provide default sort which is from latest start time to oldest
   if "sort" not in request.session:
      print ("right here")
      jobs = jobSort("start_time", "descending", jobs)
#   paginator = Paginator(jobs, 2)
#   print ('page' in request.GET)
#   page_num = request.GET.get('page')
#   job_page = paginator.get_page(page_num)
   form = FilterForm()
   context = {"jobs": jobs, "form":form}
   return render(request, 'jobs/jobs.html', context)
   

