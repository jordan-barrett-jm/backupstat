from django.urls import path
from jobs import views

urlpatterns = [
   path('', views.job_list),
   path('api/', views.job_post)
]
