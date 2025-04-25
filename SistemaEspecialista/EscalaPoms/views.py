from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CadastroForm
from .models import *

#Todas as funções verificam se o método é post get
#Caso for post realiza o processamento adequado
#Caso for get renderiza a página correspondente

def login(request):
    
    if request.method == 'POST':
        cpf = request.POST.get('cpf')
        senha = request.POST.get('senha')
        
        try:
            usuario = Treinador.objects.get(cpf=cpf)
            tipo_usuario = 'treinador'
        
        except Treinador.DoesNotExist:
            try:
                usuario = Aluno.objects.get(cpf=cpf)
                tipo_usuario = 'aluno'
                
            except Aluno.DoesNotExist:
                messages.error(request, "Usuário não encontrado.")
                return render(request, 'EscalaPoms/login.html')
        
        if not check_password(senha, usuario.senha):
            messages.error(request, "Senha incorreta.")
            return render(request, 'EscalaPoms/login.html')
        
        request.session['cpf_usuario'] = usuario.cpf
        request.session['tipo_usuario'] = tipo_usuario
        
        messages.success(request, "Login efetuado com sucesso!")
        return redirect('dashboard')

    return render(request,'EscalaPoms/login.html')

def cadastro(request):
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Cadastro realizado com sucesso!")
                return redirect('dashboard')
            except Exception as e:
                # Caso ocorra algum erro ao salvar, exiba-o.
                form.add_error(None, f"Ocorreu um erro ao salvar o cadastro: {e}")
        else:
            messages.error(request, "Verifique os erros abaixo.")
    else:
        form = CadastroForm()

    return render(request, 'EscalaPoms/cadastro.html', {'form': form})


def perfil(request):
    
    cpf = request.session.get('cpf_usuario')
    tipo_usuario = request.session.get('tipo_usuario')
    
    if tipo_usuario == 'treinador':
        usuario = Treinador.objects.get(cpf=cpf)
    
    elif tipo_usuario == 'aluno':
        usuario = Aluno.objects.get(cpf=cpf)
    
    dados_usuario = {
        'usuario': usuario,
    }
    return render(request, 'EscalaPoms/perfil.html', dados_usuario)


def escala(request):
    if request.method == 'POST':
       return redirect('dashboard')

    return render(request, 'EscalaPoms/escala.html')

def dashboard(request):
    #aqui serão feitos os cálculos para gerar os gráficos e as informações que serão mostradas no dashboard
    return render(request, 'EscalaPoms/dashboard.html')

def relatorio(request):
    #aqui será feito o processamento para gerar os relatórios, somas e gráficos
    return render(request, 'EscalaPoms/relatorio.html')