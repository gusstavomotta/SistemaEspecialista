from django.contrib.auth.hashers import check_password
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from .models import Treinador, Aluno
from django.shortcuts import redirect
from EscalaPoms.models import *

class CPFBackend(BaseBackend):
    """
    Backend de autenticação personalizado que utiliza o CPF como identificador.

    Este backend tenta autenticar o usuário procurando primeiramente no modelo 
    Treinador e, se não encontrar, procura no modelo Aluno.
    Se o usuário for encontrado e a senha estiver correta, retorna um objeto User (do Django).
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Considera o 'username' fornecido como o CPF do usuário.
        cpf = username
        try:
            # Tenta buscar o usuário no modelo Treinador.
            usuario = Treinador.objects.get(cpf=cpf)
        except Treinador.DoesNotExist:
            try:
                # Se não encontrar no modelo Treinador, tenta no modelo Aluno.
                usuario = Aluno.objects.get(cpf=cpf)
            except Aluno.DoesNotExist:
                # Caso o CPF não seja encontrado em nenhum dos modelos, retorna None.
                return None

        # Verifica se a senha fornecida corresponde à senha armazenada (usando check_password).
        if check_password(password, usuario.senha):
            # Cria ou recupera um objeto User do Django utilizando o CPF como username.
            user, created = User.objects.get_or_create(username=cpf)
            return user
        # Se a senha estiver incorreta, retorna None.
        return None

    def get_user(self, user_id):
        """
        Recupera o objeto User com base no ID fornecido.
        
        Retorna o objeto User se ele existir ou None se não existir.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


def treinador_required(view_func):
    """
    Decorator que restringe o acesso a determinadas views apenas para usuários do tipo Treinador.

    Verifica se o CPF do usuário logado (armazenado em request.user.username) 
    está associado a um objeto do modelo Treinador.
    Caso não esteja, redireciona o usuário para a página 'dashboard'.
    """
    def _wrapped_view(request, *args, **kwargs):
        cpf = request.user.username
        # Verifica a existência de um Treinador com esse CPF.
        if Treinador.objects.filter(cpf=cpf).exists():
            return view_func(request, *args, **kwargs)
        else:
            return redirect('dashboard')
    return _wrapped_view

def aluno_required(view_func):
    """
    Decorator que restringe o acesso a determinadas views apenas para usuários do tipo Aluno.

    Verifica se o CPF do usuário logado (armazenado em request.user.username) 
    está associado a um objeto do modelo Aluno.
    Caso não esteja, redireciona o usuário para a página 'dashboard'.
    """
    def _wrapped_view(request, *args, **kwargs):
        cpf = request.user.username
        # Verifica a existência de um Aluno com esse CPF.
        if Aluno.objects.filter(cpf=cpf).exists():
            return view_func(request, *args, **kwargs)
        else:
            return redirect('dashboard')
    return _wrapped_view
