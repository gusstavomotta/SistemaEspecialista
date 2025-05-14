import random

from django.contrib.auth import logout as deslogar, authenticate, login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.utils.dateformat import DateFormat

from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages

from .forms import *
from .models import Treinador, Aluno, EscalaPoms
from .backends import aluno_required, treinador_required
from .validators import validar_cpf
from django.db.models import Max
from datetime import timedelta
from django.utils import timezone
from .services.usuario_service import (
    enviar_resumo_escalas_pendentes,
    obter_usuario_por_cpf,
    remover_foto_usuario,
    atualizar_dados_usuario,
    enviar_codigo_email
)
from .services.escala_service import confirmar_treinador, salvar_e_classificar_escala
from django.core import signing

"""
Módulo de views: autenticação, cadastro, gestão de escalas e perfil de usuário.
"""

def login_view(request):
    """
    Exibe e processa o formulário de login.

    Parâmetros:
    - request: objeto HttpRequest contendo dados da requisição.

    Fluxo:
    1. No POST, obtém CPF e senha do formulário.
    2. Autentica o usuário via authenticate().
    3. Se autenticado, faz login e define o tipo de usuário na sessão.
       - Se for Treinador, envia resumo de escalas pendentes.
    4. Exibe mensagem de sucesso ou erro.
    5. Renderiza template de login com valor de CPF preenchido.
    """
    cpf_digitado = ''
    if request.method == 'POST':
        cpf_digitado = request.POST.get('cpf', '').strip()
        senha = request.POST.get('senha', '')
        usuario = authenticate(request, username=cpf_digitado, password=senha)
        if usuario:
            login(request, usuario)
            obj = obter_usuario_por_cpf(usuario.username)
            if isinstance(obj, Treinador):
                request.session['tipo_usuario'] = 'treinador'
                enviar_resumo_escalas_pendentes(obj)
            elif isinstance(obj, Aluno):
                request.session['tipo_usuario'] = 'aluno'
            messages.success(request, "Login efetuado com sucesso!")
            return redirect('home')
        messages.error(request, "CPF ou senha incorretos.")
    return render(request, 'EscalaPoms/auth/login.html', {'cpf': cpf_digitado})


def cadastro(request):
    """
    Exibe e processa o cadastro de Treinador ou Aluno.

    Parâmetros:
    - request: objeto HttpRequest contendo dados da requisição.

    Fluxo:
    1. Determina tipo de usuário (treinador ou aluno) por POST ou GET.
    2. Instancia o formulário apropriado (TreinadorForm ou AlunoForm).
    3. No POST, valida e salva o formulário.
       - Mensagem de sucesso e redireciona para login se válido.
       - Mensagem de erro em caso de campos inválidos.
    4. Para alunos, carrega lista de treinadores para seleção.
    5. Renderiza template de cadastro com contexto.
    """
    if request.method == 'POST':
        tipo = request.POST.get('tipo_usuario')
    else:
        tipo = request.GET.get('tipo')
    form = TreinadorForm(request.POST) if request.method == 'POST' and tipo == 'treinador' else (
        AlunoForm(request.POST) if request.method == 'POST' else (
            TreinadorForm() if tipo == 'treinador' else AlunoForm()
        )
    )
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Cadastro realizado com sucesso!")
            return redirect('login')
        messages.error(request, "Por favor, corrija os erros abaixo.")
    treinadores = Treinador.objects.all().values('cpf', 'nome') if tipo != 'treinador' else []
    return render(request, 'EscalaPoms/auth/cadastro.html', {
        'form': form,
        'treinadores': treinadores,
        'tipo_usuario': tipo,
    })


def redefinir_senha(request):
    """
    Inicia o fluxo de redefinição de senha.

    Parâmetros:
    - request: HttpRequest.

    Fluxo:
    1. No POST, obtém CPF e email.
    2. Valida formato de CPF.
    3. Verifica existência do usuário e correspondência de email.
    4. Gera código de 6 dígitos e armazena na sessão.
    5. Envia código por email e redireciona para confirmação.
    6. Renderiza template com campos preenchidos em caso de erro.
    """
    cpf_digitado = ''
    email_digitado = ''
    if request.method == 'POST':
        cpf_digitado = request.POST.get('cpf', '').strip()
        email_digitado = request.POST.get('email', '').strip()
        try:
            cpf_normalizado = validar_cpf(cpf_digitado)
        except Exception:
            messages.error(request, 'CPF inválido.')
            return render(request, 'EscalaPoms/auth/redefinir_senha.html', {'cpf': cpf_digitado, 'email': email_digitado})
        usuario = obter_usuario_por_cpf(cpf_normalizado)
        if not usuario:
            messages.error(request, 'CPF não encontrado.')
        elif usuario.email.strip().lower() != email_digitado.lower():
            messages.error(request, 'Email não corresponde ao CPF.')
        else:
            codigo = f"{random.randint(100000, 999999):06}"
            request.session['reset_cpf'] = cpf_normalizado
            request.session['reset_codigo'] = codigo
            enviar_codigo_email(codigo, usuario.email)
            messages.info(request, 'Enviamos um código para o seu e-mail. Insira-o abaixo.')
            return redirect('confirmar_codigo')
    return render(request, 'EscalaPoms/auth/redefinir_senha.html', {'cpf': cpf_digitado, 'email': email_digitado})


def confirmar_codigo(request):
    """
    Confirma o código de redefinição enviado por email e atualiza a senha.

    Parâmetros:
    - request: HttpRequest.

    Fluxo:
    1. No POST, obtém código, nova senha e confirmação.
    2. Verifica código na sessão.
    3. Confere se as senhas coincidem.
    4. Atualiza senha do usuário e limpa sessão.
    5. Exibe mensagens e redireciona para login.
    6. Renderiza template em caso de erro.
    """
    codigo = ''
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        nova = request.POST.get('nova_senha')
        conf = request.POST.get('confirmar_senha')
        sessao = request.session.get('reset_codigo')
        cpf = request.session.get('reset_cpf')
        if not sessao or codigo != sessao:
            messages.error(request, 'Código inválido ou expirado.')
            return render(request, 'EscalaPoms/auth/confirmar_codigo.html', {'codigo_digitado': codigo})
        if nova != conf:
            messages.error(request, 'As senhas não coincidem.')
            return render(request, 'EscalaPoms/auth/confirmar_codigo.html', {'codigo_digitado': codigo})
        usuario = obter_usuario_por_cpf(cpf)
        if not usuario:
            messages.error(request, 'Sessão expirada. Tente novamente.')
            return render(request, 'EscalaPoms/auth/confirmar_codigo.html', {'codigo_digitado': codigo})
        usuario.senha = make_password(nova)
        usuario.save()
        request.session.pop('reset_codigo', None)
        request.session.pop('reset_cpf', None)
        messages.success(request, 'Senha redefinida com sucesso.')
        return redirect('login')
    return render(request, 'EscalaPoms/auth/confirmar_codigo.html')

@login_required
def home(request):
    """
    Página inicial com dashboard para Treinador ou Aluno.

    Parâmetros:
    - request: HttpRequest (usuário autenticado).

    Lógica:
    - Se Treinador:
      * Total de alunos, últimas escalas, escalas na semana,
        alunos sem escala recente ou sem nenhuma escala.
    - Se Aluno:
      * Total de escalas, última escala, alerta de prazo,
        e dados para gráficos de evolução (PTH e desajuste).
    - Renderiza template com contexto apropriado.
    """
    usuario = obter_usuario_por_cpf(request.user.username)
    if isinstance(usuario, Treinador):
        # dados para treinador
        tipo = 'Treinadora' if usuario.genero == 'feminino' else 'Treinador'
        total_alunos = Aluno.objects.filter(treinador=usuario).count()
        ultimas = EscalaPoms.objects.filter(aluno__treinador=usuario).select_related('aluno').order_by('-data')[:5]
        hoje = timezone.now()
        inicio = hoje - timedelta(days=7)
        count_semana = EscalaPoms.objects.filter(aluno__treinador=usuario, data__gte=inicio).count()
        ult_por_aluno = EscalaPoms.objects.filter(aluno__treinador=usuario).values('aluno').annotate(ultima_escala=Max('data'))
        sem_escala = [Aluno.objects.get(pk=i['aluno']) for i in ult_por_aluno if i['ultima_escala'] < inicio]
        sem_escala_ja = Aluno.objects.filter(treinador=usuario, escalas__isnull=True)
        context = {
            'nome': usuario.nome,
            'tipo': tipo,
            'total_alunos': total_alunos,
            'ultimas_escalas': ultimas,
            'escalas_ultima_semana': count_semana,
            'alunos_sem_escala': sem_escala,
            'alunos_sem_escala_ja': sem_escala_ja,
            'genero': usuario.genero[0].upper(),
        }
    else:
        # dados para aluno
        escalas = EscalaPoms.objects.filter(aluno=usuario).order_by('data')
        total = escalas.count()
        ultima = escalas.last()
        prazo = (timezone.now() - ultima.data) > timedelta(days=7) if ultima else False
        labels = [DateFormat(e.data).format('d/m') for e in escalas]
        pth = [e.pth for e in escalas]
        desaj = [e.soma_desajuste for e in escalas]
        context = {
            'nome': usuario.nome,
            'tipo': 'Aluna' if usuario.genero=='feminino' else 'Aluno',
            'treinador': usuario.treinador,
            'total_escalas': total,
            'ultima_escala': ultima.data if ultima else None,
            'labels': labels,
            'pth': pth,
            'desajuste': desaj,
            'tem_escalas': bool(escalas),
            'tempo_limite': prazo,
            'genero': usuario.genero[0].upper(),
        }
    return render(request, 'EscalaPoms/static/home.html', context)

@login_required
@treinador_required
def meus_alunos(request):
    """
    Lista e busca de alunos vinculados ao treinador.

    Parâmetros:
    - request: HttpRequest (treinador autenticado).

    Fluxo:
    1. Obtém todos os alunos do treinador.
    2. Filtra por query string 'q' se fornecida.
    3. Ordena por nome e cria CPF assinado para links.
    4. Renderiza template com lista de alunos.
    """
    treinador = Treinador.objects.get(cpf=request.user.username)
    q = request.GET.get('q', '').strip()
    alunos = Aluno.objects.filter(treinador=treinador)
    if q:
        alunos = alunos.filter(nome__icontains=q)
    alunos = alunos.order_by('nome')
    for aluno in alunos:
        aluno.cpf_assinado = signing.dumps(aluno.cpf, salt='aluno-cpf-salt')
    return render(request, 'EscalaPoms/escala/meus_alunos.html', {'alunos': alunos, 'q': q})

@login_required
@treinador_required
def historico_aluno(request, aluno_cpf):
    """
    Exibe histórico de escalas de um aluno específico.

    Parâmetros:
    - request: HttpRequest (treinador autenticado).
    - aluno_cpf: CPF assinado pelo treinador.

    Fluxo:
    1. Dessigna o CPF e obtém o objeto Aluno.
    2. Carrega todas as escalas do aluno.
    3. Prepara dados para gráfico (labels, pth, desajuste).
    4. Renderiza template de histórico.
    """
    cpf = signing.loads(aluno_cpf, salt='aluno-cpf-salt')
    aluno = get_object_or_404(Aluno, cpf=cpf, treinador__cpf=request.user.username)
    escalas = EscalaPoms.objects.filter(aluno=aluno).order_by('data')
    labels = [DateFormat(e.data).format('d/m') for e in escalas]
    pth = [e.pth for e in escalas]
    desaj = [e.soma_desajuste for e in escalas]
    return render(request, 'EscalaPoms/aluno/historico_aluno.html', {
        'aluno': aluno,
        'escalas': escalas,
        'labels': labels,
        'pth': pth,
        'desajuste': desaj,
    })

@login_required
@aluno_required
def escala(request):
    """
    Exibe formulário de escala para o aluno preencher.

    Parâmetros:
    - request: HttpRequest (aluno autenticado).

    Fluxo:
    1. Carrega aluno e lista de treinadores.
    2. No POST, delega para confirmar_treinador ou salvar_e_classificar_escala.
    3. Renderiza template de escala.
    """
    aluno = get_object_or_404(Aluno, cpf=request.user.username)
    treinadores = Treinador.objects.all()
    if request.method == 'POST':
        if 'confirmar_treinador' in request.POST:
            return confirmar_treinador(aluno, request)
        return salvar_e_classificar_escala(aluno, request)
    return render(request, 'EscalaPoms/escala/escala.html', {'usuario': aluno, 'treinadores': treinadores})

@login_required
@aluno_required
def minhas_escalas(request):
    """
    Exibe as escalas já preenchidas pelo aluno.

    Parâmetros:
    - request: HttpRequest (aluno autenticado).

    Fluxo:
    1. Carrega todas as escalas do aluno.
    2. Prepara dados para gráficos de evolução.
    3. Renderiza template com lista e gráficos.
    """
    aluno = get_object_or_404(Aluno, cpf=request.user.username)
    escalas = EscalaPoms.objects.filter(aluno=aluno).order_by('data').select_related('classificacao')
    labels = [DateFormat(e.data).format('d/m') for e in escalas]
    pth = [e.pth for e in escalas]
    desaj = [e.soma_desajuste for e in escalas]
    return render(request, 'EscalaPoms/escala/minhas_escalas.html', {
        'aluno': aluno,
        'escalas': escalas,
        'labels': labels,
        'pth': pth,
        'desajuste': desaj,
    })

@login_required
def perfil(request):
    """
    Exibe e atualiza informações do perfil do usuário.

    Parâmetros:
    - request: HttpRequest (usuário autenticado).

    Fluxo:
    1. No POST, trata remoção de foto ou atualização de dados.
    2. Usa serviços para atualizar dados e remover foto.
    3. Renderiza template com dados atuais.
    """
    usuario = obter_usuario_por_cpf(request.user.username)
    if request.method == 'POST':
        if 'remove_foto' in request.POST:
            return remover_foto_usuario(usuario, request)
        return atualizar_dados_usuario(usuario, request, 'EscalaPoms/aluno/perfil.html')
    return render(request, 'EscalaPoms/aluno/perfil.html', {'usuario': usuario, 'url_dashboard': reverse('perfil')})

@login_required
def solicitar_exclusao(request):
    """
    Inicia fluxo de solicitação de exclusão de conta.

    Parâmetros:
    - request: HttpRequest (usuário autenticado).

    Fluxo:
    1. No POST, obtém email digitado e compara com o cadastro.
    2. Gera código de exclusão e envia por email.
    3. Armazena código na sessão e redireciona para confirmar.
    4. Renderiza template com feedback.
    """
    usuario = obter_usuario_por_cpf(request.user.username)
    email_digitado = ''
    if request.method == 'POST':
        email_digitado = request.POST.get('email', '').strip()
        if email_digitado.lower() != usuario.email.strip().lower():
            messages.warning(request, "Email diferente do da sua conta.")
        else:
            codigo = f"{random.randint(100000, 999999):06}"
            request.session['exclusao_codigo'] = codigo
            enviar_codigo_email(codigo, usuario.email)
            return redirect('confirmar_exclusao')
    return render(request, 'EscalaPoms/exclusao/solicitar_exclusao.html', {'usuario': usuario, 'email': email_digitado})

@login_required
def confirmar_exclusao(request):
    """
    Confirma o código de exclusão e desativa a conta.

    Parâmetros:
    - request: HttpRequest (usuário autenticado).

    Fluxo:
    1. No POST, obtém código digitado e compara com sessão.
    2. Se inválido, orienta a solicitar novamente.
    3. Se válido, marca usuário como inativo, faz logout e redireciona.
    4. Renderiza template de confirmação.
    """
    usuario = obter_usuario_por_cpf(request.user.username)
    codigo_digitado = ''
    if request.method == 'POST':
        codigo_digitado = request.POST.get('codigo', '').strip()
        sessao = request.session.get('exclusao_codigo')
        if not sessao:
            messages.error(request, "Código expirado ou não gerado. Tente solicitar exclusão novamente.")
            return redirect('solicitar_exclusao')
        if codigo_digitado != str(sessao):
            messages.error(request, "Código incorreto. Por favor, tente novamente.")
        else:
            usuario.ativo = False
            usuario.save()
            request.session.pop('exclusao_codigo', None)
            deslogar(request)
            messages.success(request, "Sua conta foi desativada com sucesso.")
            return redirect('login')
    return render(request, 'EscalaPoms/exclusao/confirmar_exclusao.html', {'usuario': usuario, 'codigo': codigo_digitado})

@login_required
def logout_view(request):
    """
    Realiza logout do usuário e redireciona para login.

    Parâmetros:
    - request: HttpRequest.

    Fluxo:
    1. Chama logout do Django.
    2. Redireciona para a view de login.
    """
    deslogar(request)
    return redirect('login')

@login_required
def sobre(request):
    """
    Exibe página estática 'Sobre'.

    Parâmetros:
    - request: HttpRequest (usuário autenticado).

    Fluxo:
    1. Renderiza template estático sobre a aplicação.
    """
    return render(request, 'EscalaPoms/static/sobre.html')

@login_required
@aluno_required
def trocar_treinador(request):
    """
    Permite ao aluno trocar seu treinador associado.

    Parâmetros:
    - request: HttpRequest (aluno autenticado).

    Fluxo:
    1. Carrega lista de treinadores.
    2. No POST, obtém novo CPF de treinador e atualiza o aluno.
    3. Exibe mensagem de sucesso ou erro.
    4. Renderiza template de troca de treinador.
    """
    aluno = get_object_or_404(Aluno, cpf=request.user.username)
    treinadores = Treinador.objects.all()
    if request.method == 'POST':
        novo_cpf = request.POST.get('treinador_id')
        try:
            novo = Treinador.objects.get(cpf=novo_cpf)
            aluno.treinador = novo
            aluno.save()
            messages.success(request, "Treinador atualizado com sucesso!")
            return redirect('perfil')
        except Treinador.DoesNotExist:
            messages.error(request, "Treinador não encontrado.")
    return render(request, 'EscalaPoms/aluno/trocar_treinador.html', {'usuario': aluno, 'treinadores': treinadores})