from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CadastroForm
from .models import *
import datetime
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from .decorators import treinador_required, aluno_required
#Todas as funções verificam se o método é post get
#Caso for post realiza o processamento adequado
#Caso for get renderiza a página correspondente

def login_view(request):
    if request.method == 'POST':
        cpf = request.POST.get('cpf')
        senha = request.POST.get('senha')
        user = authenticate(request, username=cpf, password=senha)
        if user is not None:
            login(request, user)
            messages.success(request, "Login efetuado com sucesso!")
            return redirect('dashboard')
        else:
            messages.error(request, "CPF ou senha incorretos.")
    return render(request, 'EscalaPoms/login.html')

def logout_view(request):
    auth_logout(request)
    return redirect('login')

def cadastro(request):
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Cadastro realizado com sucesso!")
                return redirect('login')
            except Exception as e:
                form.add_error(None, f"Ocorreu um erro ao salvar o cadastro: {e}")
        else:
            messages.error(request, "Verifique os erros abaixo.")
    else:
        form = CadastroForm()

    return render(request, 'EscalaPoms/cadastro.html', {'form': form})

@login_required
def perfil(request):
    cpf = request.user.username
    try:
        perfil = Treinador.objects.get(cpf=cpf)
    except Treinador.DoesNotExist:
        perfil = Aluno.objects.get(cpf=cpf)
    return render(request, 'EscalaPoms/perfil.html', {'usuario': perfil})

@login_required
def escala(request):
    if request.method == 'POST':
        cpf = request.session.get('cpf_usuario')
        try:
            aluno = Aluno.objects.get(cpf=cpf)
        except Aluno.DoesNotExist:
            messages.error(request, "Aluno não encontrado.")
            return redirect('login')
        
        try:
            somaTensao = sum([int(request.POST.get(f'tensao_{i}')) for i in range(1, 6)])
            somaDepressao = sum([int(request.POST.get(f'depressao_{i}')) for i in range(1, 6)])
            somaHostilidade = sum([int(request.POST.get(f'hostilidade_{i}')) for i in range(1, 6)])
            somaFadiga = sum([int(request.POST.get(f'fadiga_{i}')) for i in range(1, 6)])
            somaConfusao = sum([int(request.POST.get(f'confusao_{i}')) for i in range(1, 6)])
            somaVigor = sum([int(request.POST.get(f'vigor_{i}')) for i in range(1, 7)])
            somaDesajuste = sum([int(request.POST.get(f'desajuste_{i}')) for i in range(1, 6)])
            somaTotal = somaTensao + somaDepressao + somaHostilidade + somaFadiga + somaConfusao + somaVigor + somaDesajuste
            
            sono = request.POST.get('sono')
            volume_treino = request.POST.get('volume_treino')
            freq_cardiaca_media = request.POST.get('freq_cardiaca_media')
            
            # Converte os campos opcionais para inteiro, se possível; caso contrário, tómalos como None.
            sono = int(sono) if sono and sono.isdigit() else None
            volume_treino = int(volume_treino) if volume_treino and volume_treino.isdigit() else None
            freq_cardiaca_media = int(freq_cardiaca_media) if freq_cardiaca_media and freq_cardiaca_media.isdigit() else None
            
            try:
                EscalaPoms.objects.create(
                    aluno=aluno,
                    data=datetime.date.today(),
                    somaTensao=somaTensao,
                    somaDepressao=somaDepressao,
                    somaHostilidade=somaHostilidade,
                    somaFadiga=somaFadiga,
                    somaConfusao=somaConfusao,
                    somaVigor=somaVigor,
                    somaDesajuste=somaDesajuste,
                    somaTotal=somaTotal,
                    sono=sono,
                    volume_treino=volume_treino,
                    freq_cardiaca_media=freq_cardiaca_media
                )
                messages.success(request, "Dados salvos com sucesso!")
                return redirect('dashboard')
            
            except Exception as e:
                messages.error(request, f"Erro ao salvar os dados: {e}")
                return redirect('escala')
            
        except ValueError:
            messages.error(request, "Erro ao processar os dados.")
            return redirect('escala')
        
    return render(request, 'EscalaPoms/escala.html')

@login_required
def dashboard(request):
    #aqui serão feitos os cálculos para gerar os gráficos e as informações que serão mostradas no dashboard
    return render(request, 'EscalaPoms/dashboard.html')

@login_required
def relatorio(request):
    #aqui será feito o processamento para gerar os relatórios, somas e gráficos
    return render(request, 'EscalaPoms/relatorio.html')