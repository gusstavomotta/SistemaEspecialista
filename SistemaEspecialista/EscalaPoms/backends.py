import re
from django.contrib.auth.hashers import check_password
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from .models import Treinador, Aluno


class CPFBackend(BaseBackend):
    """
    Backend de autenticação que usa CPF (apenas dígitos).
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Normaliza o CPF: mantém só dígitos
        cpf = re.sub(r'\D', '', username or '')
        usuario = None

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


def treinador_required(view_func):
    """
    Só permite Treinadores autenticados; senão 403.
    """
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        cpf = re.sub(r'\D', '', request.user.username)
        if not Treinador.objects.filter(cpf=cpf).exists():
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def aluno_required(view_func):
    """
    Só permite Alunos autenticados; senão 403.
    """
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        cpf = re.sub(r'\D', '', request.user.username)
        if not Aluno.objects.filter(cpf=cpf).exists():
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view
