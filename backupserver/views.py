
from django.shortcuts import render
from backupserver.models import BackupServer
from backupserver.forms import BackupsvrForm
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

#view all backup servers
@login_required(login_url='/useradmin/login/')
def backupsvrList(request):
#   BackupServer.objects.all().delete()
   servers = BackupServer.objects.all()
   context = {"servers":servers}
   return render(request, "backupserver/backupserver.html", context)

#detailed view for specific backup server
@login_required(login_url='/useradmin/login/')
def backupsvrDetail(request, server_id):
   backup_server = BackupServer.objects.get(id=server_id)
   return render(request, "backupserver/backupserver_detail.html", {"server": backup_server})

#add backup servers, GET returns the form
#POST saves the form fields to DB once valid
@login_required(login_url='/useradmin/login/')
def addBackupsvr(request):
   if request.method == "POST":
      form = BackupsvrForm(request.POST)
      if form.is_valid():
         name = form.cleaned_data['name']
         company = form.cleaned_data['company']
         app = form.cleaned_data['application']
         #instantiate the backup server object then save it
         server = BackupServer(name=name, company=company, application=app)
         server.save()
         #redirect to the backup server list view
         return HttpResponseRedirect('/backup')
   form = BackupsvrForm()
   return render(request, 'backupserver/addbackupserver.html', {'form':form})

#delete backupserver given ID
@login_required(login_url='/useradmin/login/')
def deleteBackupsvr(request, server_id):
   BackupServer.objects.get(id=server_id).delete()
   return HttpResponseRedirect('/backup')

