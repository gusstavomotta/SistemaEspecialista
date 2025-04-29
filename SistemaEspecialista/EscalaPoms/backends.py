from django.contrib.auth.hashers import check_password
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from .models import Treinador, Aluno

class CPFBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        cpf = username
        try:
            usuario = Treinador.objects.get(cpf=cpf)
        except Treinador.DoesNotExist:
            try:
                usuario = Aluno.objects.get(cpf=cpf)
            except Aluno.DoesNotExist:
                return None
        if check_password(password, usuario.senha):
            user, created = User.objects.get_or_create(username=cpf)
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

from django.shortcuts import redirect
from EscalaPoms.models import *

def treinador_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        cpf = request.user.username
        if Treinador.objects.filter(cpf=cpf).exists():
            return view_func(request, *args, **kwargs)
        else:
            return redirect('dashboard')  
    return _wrapped_view

def aluno_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        cpf = request.user.username
        if Aluno.objects.filter(cpf=cpf).exists():
            return view_func(request, *args, **kwargs)
        else:
            return redirect('dashboard') 
    return _wrapped_view
