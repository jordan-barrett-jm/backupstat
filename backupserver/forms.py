from django import forms

APPLICATION_CHOICES = (
('Veritas', 'Veritas/Symantec BackupExec'),
('Vembu', 'Vembu Backup'),
('Azure', 'Azure Cloud Backup'),
('Veeam', 'Veeam Backup'),
('ArcServer', 'ArcServe')
)

#Form for creating a new backup backup server
class BackupsvrForm(forms.Form):
   application = forms.ChoiceField(choices=APPLICATION_CHOICES, required=True, label="Application")
   name = forms.CharField(label="Backup Server Name", required=True)
   company = forms.CharField(label="Company Name", required=True)
