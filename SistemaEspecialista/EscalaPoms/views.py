import datetime

# Importa decorators e funções de autenticação
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as deslogar, authenticate, login
# Para renderizar templates e redirecionar
from django.shortcuts import render, redirect, reverse
# Para exibir mensagens para o usuário
from django.contrib import messages

from .forms import CadastroForm
from .models import Treinador, Aluno, EscalaPoms
from .backends import aluno_required, treinador_required
from .utils import obter_url_dashboard, obter_usuario_por_cpf, processar_dados_escala

def login_view(request):
    """
    View para realizar a autenticação do usuário.
    Verifica se a requisição é POST e extrai o CPF e senha.
    Caso a autenticação seja bem-sucedida, redireciona para o dashboard correspondente.
    Em caso de erro, exibe a mensagem adequada.
    """
    if request.method == 'POST':
        # Obtém os dados de CPF e senha do formulário de login
        cpf = request.POST.get('cpf')
        senha = request.POST.get('senha')
        usuario = authenticate(request, username=cpf, password=senha)
        if usuario:
            # Realiza o login e exibe mensagem de sucesso
            login(request, usuario)
            messages.success(request, "Login efetuado com sucesso!")
            # Determina a URL do dashboard baseado no tipo do usuário (Treinador ou Aluno)
            url_dashboard = obter_url_dashboard(usuario.username)
            if url_dashboard:
                return redirect(url_dashboard)
            messages.error(request, "Usuário não possui uma função atribuída.")
            return redirect('login')
        messages.error(request, "CPF ou senha incorretos.")
    # Renderiza a página de login
    return render(request, 'EscalaPoms/login.html')

def cadastro(request):
    """
    View responsável pelo cadastro de novos usuários.
    Se a requisição for POST, valida o formulário e tenta salvar o cadastro.
    Caso contrário, exibe o formulário vazio.
    """
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            try:
                # Tenta salvar o usuário (Treinador ou Aluno) conforme o formulário
                form.save()
                messages.success(request, "Cadastro realizado com sucesso!")
                return redirect('login')
            except Exception as erro:
                form.add_error(None, f"Ocorreu um erro ao salvar o cadastro: {erro}")
        else:
            messages.error(request, "Verifique os erros abaixo.")
    else:
        form = CadastroForm()
    # Renderiza o template de cadastro passando o formulário
    return render(request, 'EscalaPoms/cadastro.html', {'form': form})

@aluno_required
@login_required
def home_aluno(request):
    """
    View que exibe a home para alunos.
    É protegida pelos decorators que garantem que apenas alunos autenticados acessem a página.
    """
    return render(request, 'EscalaPoms/home_aluno.html')

@treinador_required
@login_required
def home_treinador(request):
    """
    View que exibe a home para treinadores.
    Apenas usuários com a função de treinador podem acessar.
    """
    return render(request, 'EscalaPoms/home_treinador.html')

@login_required
def escala(request):
    """
    View para que o aluno registre dados da escala.
    Processa dados enviados via POST, realiza a validação utilizando funções utilitárias
    e, em caso de sucesso, salva os dados e redireciona para o perfil.
    """
    if request.method == 'POST':
        cpf = request.user.username
        try:
            # Obtém o objeto Aluno com base no CPF do usuário logado
            aluno = Aluno.objects.get(cpf=cpf)
        except Aluno.DoesNotExist:
            messages.error(request, "Aluno não encontrado.")
            return redirect('login')
        try:
            # Processa e valida os dados enviados no formulário de escala
            dados_escala = processar_dados_escala(request)
        except ValueError as erro:
            messages.error(request, f"Erro ao processar os dados: {erro}")
            return redirect('escala')
        try:
            # Cria um registro de escala associado ao aluno
            EscalaPoms.objects.create(
                aluno=aluno,
                data=datetime.date.today(),
                **dados_escala
            )
            messages.success(request, "Dados salvos com sucesso!")
            return redirect('perfil')
        except Exception as erro:
            messages.error(request, f"Erro ao salvar os dados: {erro}")
            return redirect('escala')
    # Renderiza o formulário da escala se a requisição não for POST
    return render(request, 'EscalaPoms/escala.html')

@login_required
@treinador_required
def meus_alunos(request):
    """
    View que exibe os alunos associados a um treinador.
    Se o treinador não for encontrado, exibe uma mensagem de erro.
    """
    cpf = request.user.username
    try:
        # Obtém o objeto Treinador baseado no CPF do usuário logado
        treinador = Treinador.objects.get(cpf=cpf)
    except Treinador.DoesNotExist:
        messages.error(request, "Treinador não encontrado.")
        return redirect('login')
    # Filtra os alunos associados ao treinador
    alunos = Aluno.objects.filter(treinador=treinador)
    return render(request, 'EscalaPoms/meus_alunos.html', {'alunos': alunos})

@login_required
@treinador_required
def historico_aluno(request, aluno_cpf):
    """
    View que exibe o histórico de escalas de um aluno específico.
    Verifica se o treinador logado possui permissão para acessar o histórico do aluno.
    """
    try:
        # Obtém o objeto Aluno com base no CPF passado como parâmetro
        aluno = Aluno.objects.get(cpf=aluno_cpf)
        # Verifica se o treinador logado é realmente o treinador do aluno
        if aluno.treinador.cpf != request.user.username:
            messages.error(request, "Você não tem permissão para acessar as escalas deste aluno.")
            return redirect('meus_alunos')
        # Recupera o histórico de escalas ordenado por data descrescente
        escalas = EscalaPoms.objects.filter(aluno=aluno).order_by('-data')
        return render(request, 'EscalaPoms/historico_aluno.html', {'aluno': aluno, 'escalas': escalas})
    except Aluno.DoesNotExist:
        messages.error(request, "Aluno não encontrado.")
        return redirect('meus_alunos')

@login_required
def perfil(request):
    """
    View que exibe o perfil do usuário logado.
    Determina se o usuário é Treinador ou Aluno para definir a URL do dashboard.
    """
    cpf = request.user.username
    try:
        # Obtém o usuário (Treinador ou Aluno) com base no CPF
        usuario = obter_usuario_por_cpf(cpf)
        # Define a URL do dashboard conforme o tipo do usuário
        url_dashboard = reverse('home_treinador') if isinstance(usuario, Treinador) else reverse('home_aluno')
        return render(request, 'EscalaPoms/perfil.html', {'usuario': usuario, 'url_dashboard': url_dashboard})
    except (Treinador.DoesNotExist, Aluno.DoesNotExist):
        messages.error(request, "Usuário não encontrado.")
        return redirect('login')

def logout_view(request):
    """
    View para deslogar o usuário.
    Após o logout, redireciona para a página de login.
    """
    deslogar(request)
    return redirect('login')

@login_required
def relatorio(request):
    """
    View que renderiza a página de relatório.
    """
    return render(request, 'EscalaPoms/relatorio.html')

def esqueceu_senha(request):
    """
    View que renderiza a página de recuperação de senha.
    """
    return render(request, 'EscalaPoms/esqueceu_senha.html')
