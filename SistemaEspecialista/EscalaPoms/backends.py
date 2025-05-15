from functools import wraps

from django.contrib.auth.hashers import check_password
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from .models import Treinador, Aluno
from .validators import normalizar_cpf


class CPFBackend(BaseBackend):
    """
    Backend de autenticação que usa CPF + senha armazenada em modelos Treinador ou Aluno.
    """

    def authenticate(
        self, request, username: str = None, password: str = None, **kwargs
    ) -> User:
        """
        Tenta autenticar um usuário pelo CPF.

        Args:
            request: HttpRequest (pode ser None).
            username: CPF (com ou sem formatação).
            password: senha em texto puro para verificar contra o hash em perfil.senha.

        Returns:
            Instância de django.contrib.auth.models.User se autenticado com sucesso,
            ou None em caso de falha.
        """
        # Normaliza entrada do CPF (remove pontos, traços etc.)
        cpf_normalizado = normalizar_cpf(username)
        perfil = None

        # Tenta encontrar perfil de treinador
        try:
            perfil = Treinador.objects.get(cpf=cpf_normalizado)
        except Treinador.DoesNotExist:
            # Se não for treinador, tenta aluno
            try:
                perfil = Aluno.objects.get(cpf=cpf_normalizado)
            except Aluno.DoesNotExist:
                return None

        # Se perfil inativo, bloqueia autenticação
        if not perfil.ativo:
            return None

        # Verifica a senha fornecida contra o hash armazenado
        if not check_password(password, perfil.senha):
            return None

        # Garante que exista um User ligado a esse CPF
        user_obj, created = User.objects.get_or_create(username=cpf_normalizado)
        if created:
            # Previne login por senha Django, já que usamos hash próprio
            user_obj.set_unusable_password()
            user_obj.save()

        # Sincroniza flag is_active do User com perfil.ativo
        user_obj.is_active = perfil.ativo
        user_obj.save()

        if not user_obj.is_active:
            return None

        return user_obj

    def get_user(self, user_id: int) -> User:
        """
        Busca um User válido pelo ID, garantindo que esteja ativo.

        Args:
            user_id: primário do modelo User.

        Returns:
            Instância de User ou None.
        """
        try:
            return User.objects.get(pk=user_id, is_active=True)
        except User.DoesNotExist:
            return None


def treinador_required(view_func):
    """
    Decorator para restringir acesso de views apenas a Treinadores autenticados.
    """

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        # Redireciona não autenticados para login
        if not request.user.is_authenticated:
            return redirect("login")

        # Confere se o username (CPF) pertence a um treinador
        cpf_normalizado = normalizar_cpf(request.user.username)
        if not Treinador.objects.filter(cpf=cpf_normalizado).exists():
            raise PermissionDenied("Acesso permitido apenas a treinadores.")

        return view_func(request, *args, **kwargs)

    return _wrapped


def aluno_required(view_func):
    """
    Decorator para restringir acesso de views apenas a Alunos autenticados.
    """

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        # Redireciona não autenticados para login
        if not request.user.is_authenticated:
            return redirect("login")

        # Confere se o username (CPF) pertence a um aluno
        cpf_normalizado = normalizar_cpf(request.user.username)
        if not Aluno.objects.filter(cpf=cpf_normalizado).exists():
            raise PermissionDenied("Acesso permitido apenas a alunos.")

        return view_func(request, *args, **kwargs)

    return _wrapped
