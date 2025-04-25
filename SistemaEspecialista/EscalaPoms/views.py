from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth.decorators import login_required

#Todas as funções verificam se o método é post get
#Caso for post realiza o processamento adequado
#Caso for get renderiza a página correspondente

def login(request):
    
    if request.method == 'POST':
        return redirect('dashboard')

    return render(request,'EscalaPoms/login.html')

def cadastro(request):
    
    if request.method == 'POST':
        return redirect('dashboard')

    return render(request, 'EscalaPoms/cadastro.html')

@login_required
def escala(request):
    if request.method == 'POST':
       return redirect('dashboard')

    return render(request, 'EscalaPoms/escala.html')
@login_required
def perfil(request):
    
    # cpf_logado = request.user.cpf
    # usuario = None

    # if Aluno.objects.filter(cpf=cpf_logado).exists():
    #     usuario = Aluno.objects.get(cpf=cpf_logado)
    # elif Treinador.objects.filter(cpf=cpf_logado).exists():
    #     usuario = Treinador.objects.get(cpf=cpf_logado)
    return render(request, 'EscalaPoms/perfil.html')

@login_required
def dashboard(request):
    #aqui serão feitos os cálculos para gerar os gráficos e as informações que serão mostradas no dashboard
    return render(request, 'EscalaPoms/dashboard.html')

@login_required
def relatorio(request):
    #aqui será feito o processamento para gerar os relatórios, somas e gráficos
    return render(request, 'EscalaPoms/relatorio.html')