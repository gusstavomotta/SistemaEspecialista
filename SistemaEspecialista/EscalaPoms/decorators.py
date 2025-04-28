from django.shortcuts import redirect
from EscalaPoms.models import *

def treinador_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        cpf = request.user.username
        if Treinador.objects.filter(cpf=cpf).exists():
            return view_func(request, *args, **kwargs)
        else:
            return redirect('dashboard')  # Ou outra página de erro
    return _wrapped_view

def aluno_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        cpf = request.user.username
        if Aluno.objects.filter(cpf=cpf).exists():
            return view_func(request, *args, **kwargs)
        else:
            return redirect('dashboard')  # Ou outra página de erro
    return _wrapped_view
