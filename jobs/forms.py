
from django import forms
from backupserver.models import BackupServer
import datetime

BKCHOICES = [("--ALL--", "ALL")]+[(server.id, server.name) for server in BackupServer.objects.all()]

class FilterForm(forms.Form):
   backupserver = forms.ChoiceField(choices=BKCHOICES, initial="--ALL--", required=False, label="Backup Server")
   fromDate = forms.DateField(initial=datetime.datetime.today()-datetime.timedelta(days=7), label="From")
   toDate = forms.DateField(initial=datetime.datetime.today(), label="To")
   def __init__(self, *args, **kwargs):
      #BKCHOICES is only loaded once on the initialization of the application so to update the choice with what is in the DB the init module needs to be modified
      super(FilterForm, self).__init__(*args, **kwargs)
      BKCHOICES = [("--ALL--", "ALL")]+[(server.id, server.name) for server in BackupServer.objects.all()]
      self.fields['backupserver'] = forms.ChoiceField(choices=BKCHOICES, initial="--ALL--", required=False, label="Backup Server")
   

