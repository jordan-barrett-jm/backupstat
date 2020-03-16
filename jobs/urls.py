from django.urls import path
from jobs import views

urlpatterns = [
   path('', views.job_list, name="jobs"),
   path('api/', views.job_post)
]
