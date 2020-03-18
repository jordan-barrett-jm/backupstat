from django.contrib.auth import views as auth_views
from django.urls import path
from useradmin import views
from django.conf.urls import include, url

urlpatterns=[
   path('', views.userList, name="users"),
   path('detail/<username>', views.userDetail, name="user_detail"),
   path('create/', views.createUser, name="create"),
   path('delete/<username>', views.deleteUser, name="user_delete"),
   path('login/', auth_views.LoginView.as_view(template_name='useradmin/login.html'), name="login"),
   path('logout/', auth_views.LogoutView.as_view(template_name="useradmin/logout.html"), name="logout"),
   path('passwordchange/', auth_views.PasswordChangeView.as_view(), name="password_change")
]

