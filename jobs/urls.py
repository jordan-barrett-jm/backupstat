
from django.urls import path
from jobs import views

urlpatterns = [
   path('', views.job_list, name="jobs"),
   path('bool', views.bool),
   path('api/', views.job_post)
]
