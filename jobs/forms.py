
from django import forms
from backupserver.models import BackupServer
import datetime

BKCHOICES = [("--ALL--", "ALL")]+[(server.id, server.name) for server in BackupServer.objects.all()]

class FilterForm(forms.Form):
   backupserver = forms.ChoiceField(choices=BKCHOICES, initial="--ALL--", required=False, label="Backup Server")
   fromDate = forms.DateField(widget=forms.TextInput(attrs={'id':'datefield'}), label="From")
   toDate = forms.DateField(widget=forms.TextInput(attrs={'id':'datefield'}), label="To")
   def __init__(self, *args, **kwargs):
      form_initial = kwargs.get('form_initial', None)
      updated_initial = {}
      if form_initial:
         updated_initial["backupserver"] = form_initial["backupserver"]
         updated_initial["fromDate"] = form_initial["fromDate"]
         updated_initial["toDate"] = form_initial["toDate"]
      kwargs.update(initial = updated_initial)
      #BKCHOICES is only loaded once on the initialization of the application so to update the choice with what is in the DB the init module needs to be modified
      super(FilterForm, self).__init__(*args, **kwargs)
      BKCHOICES = [("--ALL--", "ALL")]+[(server.id, server.name) for server in BackupServer.objects.all()]
      self.fields['backupserver'] = forms.ChoiceField(choices=BKCHOICES, initial="--ALL--", required=False, label="Backup Server")
   

