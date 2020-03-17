from django.shortcuts import render
from useradmin.forms import UserForm
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate

def userList(request):
   users = User.objects.all()
   context = {"users": users}
   return render(request, "useradmin/user_list.html", context)

def userDetail(request, username):
   user = User.objects.get(username=username)
   context = {"user": user}
   return render(request, 'useradmin/user_detail.html', context)

def createUser(request):
   if request.method == "POST":
      form = UserForm(request.POST)
      if form.is_valid():
         username = form.cleaned_data["username"]
         email = form.cleaned_data["email"]
         password = form.cleaned_data["password"]
         new_user = User.objects.create_user(username, email, password)
         new_user.save()
         return HttpResponseRedirect('/users')
   form = UserForm()
   context = {"form": form}
   return render(request, 'useradmin/add_user.html', context)




