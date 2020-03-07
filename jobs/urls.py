from django.urls import path
from jobs import views

urlpatterns = [
   path('jobs/', views.job_list),
]
