# myapp/backends.py
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from .models import Treinador, Aluno

class CPFBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        cpf = username
        # tenta Treinador
        try:
            usuario = Treinador.objects.get(cpf=cpf)
        except Treinador.DoesNotExist:
            # tenta Aluno
            try:
                usuario = Aluno.objects.get(cpf=cpf)
            except Aluno.DoesNotExist:
                return None
        # verifica hash
        if check_password(password, usuario.senha):
            # mapeia para um User do Django (ou cria um “virtual”)
            user, created = User.objects.get_or_create(username=cpf)
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
