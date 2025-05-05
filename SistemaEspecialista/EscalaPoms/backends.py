from functools import wraps
from django.contrib.auth.hashers import check_password
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from .models import Treinador, Aluno
from .validators import normalizar_cpf
class CPFBackend(BaseBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        cpf = normalizar_cpf(username)
        perfil = None

        try:
            perfil = Treinador.objects.get(cpf=cpf)
        except Treinador.DoesNotExist:
            try:
                perfil = Aluno.objects.get(cpf=cpf)
            except Aluno.DoesNotExist:
                return None
            
        if not perfil.ativo:
            return None

        if not check_password(password, perfil.senha):
            return None

        user, created = User.objects.get_or_create(username=cpf)
        if created:
            user.set_unusable_password()
            user.save()

        if not perfil.ativo:
            user.is_active = False
        else:
            user.is_active = True
        user.save()
        
        if not user.is_active:
            return None

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id, is_active=True)
        except User.DoesNotExist:
            return None


def treinador_required(view_func):

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        cpf = normalizar_cpf(request.user.username)
        if not Treinador.objects.filter(cpf=cpf).exists():
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped


def aluno_required(view_func):

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        cpf = normalizar_cpf(request.user.username)
        if not Aluno.objects.filter(cpf=cpf).exists():
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped

