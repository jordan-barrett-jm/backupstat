
from django import forms
from backupserver.models import BackupServer
import datetime

BKCHOICES = [("--ALL--", "ALL")]+[(server.id, server.name) for server in BackupServer.objects.all()]


class FilterForm(forms.Form):
   backupserver = forms.ChoiceField(choices=BKCHOICES, initial="--ALL--", required=False, label="Backup Server")
   fromDate = forms.DateField(initial=datetime.datetime.today()-datetime.timedelta(days=7), label="From")
   toDate = forms.DateField(initial=datetime.datetime.today(), label="To")
   

