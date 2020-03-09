from django.urls import path
from backupserver import views
from django.conf.urls import include, url

urlpatterns=[
   path('', views.backupsvrList, name="backup"),
   path('detail/<int:server_id>', views.backupsvrDetail, name="backup_detail"),
   path('add/', views.addBackupsvr, name="add"),
   path('delete/<int:server_id>', views.deleteBackupsvr),
]
