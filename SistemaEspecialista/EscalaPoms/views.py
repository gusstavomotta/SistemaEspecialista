import datetime
from .backends import *
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CadastroForm
from django.shortcuts import reverse

def login_view(request):
    if request.method == 'POST':
        cpf = request.POST.get('cpf')
        senha = request.POST.get('senha')
        user = authenticate(request, username=cpf, password=senha)
        if user is not None:
            login(request, user)
            messages.success(request, "Login efetuado com sucesso!")

            if Treinador.objects.filter(cpf=user.username).exists():
                return redirect('home_treinador')
            elif Aluno.objects.filter(cpf=user.username).exists():
                return redirect('home_aluno')
            else:
                messages.error(request, "Usuário não possui uma função atribuída.")
                return redirect('login')
        else:
            messages.error(request, "CPF ou senha incorretos.")
    return render(request, 'EscalaPoms/login.html')

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

@aluno_required
@login_required
def home_aluno(request):
    
    return render(request, 'EscalaPoms/home_aluno.html')

@treinador_required
@login_required
def home_treinador(request):
    
    return render(request, 'EscalaPoms/home_treinador.html')

def logout_view(request):
    auth_logout(request)
    return redirect('login')

@login_required
def escala(request):
    if request.method == 'POST':
        cpf = request.user.username
        try:
            aluno = Aluno.objects.get(cpf=cpf)
        except Aluno.DoesNotExist:
            messages.error(request, "Aluno não encontrado.")
            return redirect('login')
        
        try:
            somaTensao = sum([int(request.POST.get(f'tensao_{i}')) for i in range(1, 7)])
            somaDepressao = sum([int(request.POST.get(f'depressao_{i}')) for i in range(1, 7)])
            somaHostilidade = sum([int(request.POST.get(f'hostilidade_{i}')) for i in range(1, 7)])
            somaFadiga = sum([int(request.POST.get(f'fadiga_{i}')) for i in range(1, 7)])
            somaConfusao = sum([int(request.POST.get(f'confusao_{i}')) for i in range(1, 7)])
            somaVigor = sum([int(request.POST.get(f'vigor_{i}')) for i in range(1, 7)])
            somaDesajuste = sum([int(request.POST.get(f'desajuste_{i}')) for i in range(1, 7)])
            pth = ((somaTensao + somaDepressao + somaHostilidade + somaFadiga + somaConfusao) - somaVigor )+ 100
            
            sono = request.POST.get('sono')
            volume_treino = request.POST.get('volume_treino')
            freq_cardiaca_media = request.POST.get('freq_cardiaca_media')
            
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
                    pth=pth,
                    sono=sono,
                    volume_treino=volume_treino,
                    freq_cardiaca_media=freq_cardiaca_media
                )
                messages.success(request, "Dados salvos com sucesso!")
                return redirect('perfil')
            
            except Exception as e:
                messages.error(request, f"Erro ao salvar os dados: {e}")
                return redirect('escala')
            
        except ValueError:
            messages.error(request, "Erro ao processar os dados.")
            return redirect('escala')
        
    return render(request, 'EscalaPoms/escala.html')


@login_required
@treinador_required
def meus_alunos(request):
    cpf = request.user.username
    try:
        treinador = Treinador.objects.get(cpf=cpf)
    except Treinador.DoesNotExist:
        messages.error(request, "Treinador não encontrado.")
        return redirect('login')
    alunos = Aluno.objects.filter(treinador=treinador)  
    return render(request, 'EscalaPoms/meus_alunos.html', {'alunos': alunos})


@login_required
@treinador_required
def historico_aluno(request, aluno_cpf):
    try:
        aluno = Aluno.objects.get(cpf=aluno_cpf)
        
        if aluno.treinador.cpf != request.user.username:
            messages.error(request, "Você não tem permissão para acessar as escalas deste aluno.")
            return redirect('meus_alunos')
        
        escalas = EscalaPoms.objects.filter(aluno=aluno).order_by('-data')
        return render(request, 'EscalaPoms/historico_aluno.html', {'aluno': aluno, 'escalas': escalas})
    except Aluno.DoesNotExist:
        messages.error(request, "Aluno não encontrado.")
        return redirect('meus_alunos')

@login_required
def perfil(request):
    cpf = request.user.username
    try:
        perfil = Treinador.objects.get(cpf=cpf)
        dashboard_url = reverse('home_treinador')
    except Treinador.DoesNotExist:
        perfil = Aluno.objects.get(cpf=cpf)
        dashboard_url = reverse('home_aluno')
    return render(request, 'EscalaPoms/perfil.html', {'usuario': perfil, 'dashboard_url': dashboard_url})


@login_required
def relatorio(request):
    return render(request, 'EscalaPoms/relatorio.html')

def esqueceu_senha(request):
    return render(request, 'EscalaPoms/esqueceu_senha.html')