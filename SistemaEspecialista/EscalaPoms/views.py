from django.shortcuts import render
from .models import *
# Create your views here.

#As views funcionam como controllers também, então aqui faremos a logica para as consultas no banco e chamada dos htmls passando os dados como parametros

def listar_alunos(request):
    alunos = Aluno.objects.all()
    return render(request, 'EscalaPoms/alunos.html', {'alunos': alunos})

def listar_personal(request):
    personal = Personal.objects.all()
    return render(request, 'EscalaPoms/personal.html', {'personal': personal})

def lista_escalas(request):
    escalas = EscalaPoms.objects.all()
    return render(request, 'EscalaPoms/escalas.html', {'escalas': escalas})
