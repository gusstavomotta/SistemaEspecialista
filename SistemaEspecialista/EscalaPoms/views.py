import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as deslogar, authenticate, login
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages

from .forms import CadastroForm
from .models import Treinador, Aluno, EscalaPoms
from .backends import aluno_required, treinador_required
from .utils import obter_url_dashboard, obter_usuario_por_cpf, processar_dados_escala


def login_view(request):
    if request.method == 'POST':
        cpf = request.POST.get('cpf')
        senha = request.POST.get('senha')
        usuario = authenticate(request, username=cpf, password=senha)
        if usuario:
            login(request, usuario)
            messages.success(request, "Login efetuado com sucesso!")
            url_dashboard = obter_url_dashboard(usuario.username)
            if url_dashboard:
                return redirect(url_dashboard)
            messages.error(request, "Usuário não possui uma função atribuída.")
            return redirect('login')
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
            except Exception as erro:
                form.add_error(None, f"Ocorreu um erro ao salvar o cadastro: {erro}")
        else:
            messages.error(request, "Verifique os erros abaixo.")
    else:
        form = CadastroForm()
    return render(request, 'EscalaPoms/cadastro.html', {'form': form})


@login_required
@aluno_required
def home_aluno(request):
    return render(request, 'EscalaPoms/home_aluno.html')


@login_required
@treinador_required
def home_treinador(request):
    return render(request, 'EscalaPoms/home_treinador.html')

@login_required
@aluno_required
def escala(request):
    aluno = get_object_or_404(Aluno, cpf=request.user.username)
    if request.method == 'POST':
        try:
            dados = processar_dados_escala(request)
            EscalaPoms.objects.create(aluno=aluno, data=datetime.date.today(), **dados)
            messages.success(request, "Dados salvos com sucesso!")
            return redirect('perfil')
        except ValueError as ev:
            messages.error(request, str(ev))
        except Exception:
            messages.error(request, "Erro inesperado ao salvar os dados.")
    return render(request, 'EscalaPoms/escala.html')


@login_required
@treinador_required
def meus_alunos(request):
    treinador = get_object_or_404(Treinador, cpf=request.user.username)
    alunos = Aluno.objects.filter(treinador=treinador)
    return render(request, 'EscalaPoms/meus_alunos.html', {'alunos': alunos})


@login_required
@treinador_required
def historico_aluno(request, aluno_cpf):
    aluno = get_object_or_404(Aluno, cpf=aluno_cpf, treinador__cpf=request.user.username)
    escalas = EscalaPoms.objects.filter(aluno=aluno).order_by('-data')
    return render(request, 'EscalaPoms/historico_aluno.html', {'aluno': aluno, 'escalas': escalas})


@login_required
def perfil(request):
    cpf = request.user.username
    try:
        usuario = obter_usuario_por_cpf(cpf)
    except (Treinador.DoesNotExist, Aluno.DoesNotExist):
        messages.error(request, "Usuário não encontrado.")
        return redirect('login')

    if isinstance(usuario, Treinador):
        url_dashboard = reverse('home_treinador')
    else:
        url_dashboard = reverse('home_aluno')
    return render(request, 'EscalaPoms/perfil.html', {'usuario': usuario, 'url_dashboard': url_dashboard})


def logout_view(request):
    deslogar(request)
    return redirect('login')


@login_required
def relatorio(request):
    return render(request, 'EscalaPoms/relatorio.html')


def esqueceu_senha(request):
    return render(request, 'EscalaPoms/esqueceu_senha.html')
