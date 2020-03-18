from django.shortcuts import render
from useradmin.forms import UserForm
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate
from django.db import IntegrityError

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
         try:
            new_user = User.objects.create_user(username, email, password)
            new_user.save()
         except IntegrityError:
            form = UserForm()
            context = {"form": form, "error": 1}
            return render(request, 'useradmin/add_user.html', context)
         return HttpResponseRedirect('/useradmin')
   form = UserForm()
   context = {"form": form}
   return render(request, 'useradmin/add_user.html', context)

def deleteUser(request, username):
   user = User.objects.get(username=username)
   user.delete()
   return HttpResponseRedirect('/useradmin')


