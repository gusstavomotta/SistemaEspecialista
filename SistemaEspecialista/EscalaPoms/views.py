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
from .services.usuario_service import enviar_resumo_escalas_pendentes

from .services.usuario_service import (
    obter_usuario_por_cpf,
    remover_foto_usuario,
    atualizar_dados_usuario,
    enviar_codigo_email
)
from .services.escala_service import confirmar_treinador, salvar_e_classificar_escala

from django.core import signing


def login_view(request):
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

    return render(request, 'EscalaPoms/auth/login.html', {
        'cpf': cpf_digitado,
    })
    
def cadastro(request):
    if request.method == 'POST':
        tipo = request.POST.get('tipo_usuario')
    else:
        tipo = request.GET.get('tipo')

    if request.method == 'POST':
        if tipo == 'treinador':
            form = TreinadorForm(request.POST)
        else:
            form = AlunoForm(request.POST)
    else:
        form = TreinadorForm() if tipo == 'treinador' else AlunoForm()

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Cadastro realizado com sucesso!")
            return redirect('login')
        else:
            messages.error(request, "Por favor, corrija os erros abaixo.")

    treinadores = []
    if tipo != 'treinador':
        treinadores = Treinador.objects.all().values('cpf', 'nome')

    return render(request, 'EscalaPoms/auth/cadastro.html', {
        'form': form,
        'treinadores': treinadores,
        'tipo_usuario': tipo,
    })


def redefinir_senha(request):
    cpf_digitado = ''
    email_digitado = ''

    if request.method == 'POST':
        cpf_digitado = request.POST.get('cpf', '').strip()
        email_digitado = request.POST.get('email', '').strip()

        try:
            cpf_digitado_normalizado = validar_cpf(cpf_digitado)
        except ValidationError:
            messages.error(request, 'CPF inválido.')
            return render(request, 'EscalaPoms/auth/redefinir_senha.html', {
                'cpf': cpf_digitado,
                'email': email_digitado,
            })

        usuario = obter_usuario_por_cpf(cpf_digitado_normalizado)
        if not usuario:
            messages.error(request, 'CPF não encontrado.')
        elif usuario.email.strip().lower() != email_digitado.lower():
            messages.error(request, 'Email não corresponde ao CPF.')
        else:
            codigo = f"{random.randint(100000, 999999):06}"
            request.session['reset_cpf'] = cpf_digitado_normalizado
            request.session['reset_codigo'] = codigo
            enviar_codigo_email(codigo, usuario.email)
            messages.info(request, 'Enviamos um código para o seu e-mail. Insira-o abaixo.')
            return redirect('confirmar_codigo')

    return render(request, 'EscalaPoms/auth/redefinir_senha.html', {
        'cpf': cpf_digitado,
        'email': email_digitado,
    })

    
def confirmar_codigo(request):
    codigo_digitado = ''
    nova_senha = ''
    confirmar_senha = ''

    if request.method == 'POST':
        codigo_digitado = request.POST.get('codigo')
        nova_senha = request.POST.get('nova_senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        codigo_sessao = request.session.get('reset_codigo')
        cpf = request.session.get('reset_cpf')

        if not codigo_sessao or codigo_digitado != codigo_sessao:
            messages.error(request, 'Código inválido ou expirado.')
            return render(request, 'EscalaPoms/auth/confirmar_codigo.html', {
                'codigo_digitado': codigo_digitado,  
            })

        if nova_senha != confirmar_senha:
            messages.error(request, 'As senhas não coincidem.')
            return render(request, 'EscalaPoms/auth/confirmar_codigo.html', {
                'codigo_digitado': codigo_digitado, 
            })

        usuario = obter_usuario_por_cpf(cpf)
        if not usuario:
            messages.error(request, 'Sessão expirada. Tente novamente.')
            return render(request, 'EscalaPoms/auth/confirmar_codigo.html', {
                'codigo_digitado': codigo_digitado,  
            })

        usuario.senha = make_password(nova_senha)
        usuario.save()

        request.session.pop('reset_codigo', None)
        request.session.pop('reset_cpf', None)

        messages.success(request, 'Senha redefinida com sucesso.')
        return redirect('login')

    return render(request, 'EscalaPoms/auth/confirmar_codigo.html')


@login_required
def home(request):
    cpf = request.user.username 
    usuario = obter_usuario_por_cpf(cpf)

    if isinstance(usuario, Treinador):
        # Tipo e total de alunos
        tipo = 'Treinadora' if usuario.genero == 'feminino' else 'Treinador'
        genero = 'F' if usuario.genero == 'feminino' else 'M'
        total_alunos = Aluno.objects.filter(treinador=usuario).count()


        ultimas_escalas = (
            EscalaPoms.objects
                .filter(aluno__treinador=usuario)
                .select_related('aluno')
                .order_by('-data')[:5]
        )

        # Escalas na última semana
        hoje = timezone.now()
        inicio_semana = hoje - timedelta(days=7)
        escalas_ultima_semana = EscalaPoms.objects.filter(
            aluno__treinador=usuario,
            data__gte=inicio_semana
        ).count()

        # Alunos sem escala nos últimos 7 dias
        ultimas_por_aluno = (
            EscalaPoms.objects
                .filter(aluno__treinador=usuario)
                .values('aluno')
                .annotate(ultima_escala=Max('data'))
        )
        alunos_sem_escala = []
        for item in ultimas_por_aluno:
            if item['ultima_escala'] < inicio_semana:
                aluno_obj = Aluno.objects.get(pk=item['aluno'])
                alunos_sem_escala.append({
                    'aluno': aluno_obj,
                    'ultima_escala': item['ultima_escala'],
                })

        # Alunos que nunca cadastraram escala
        alunos_sem_escala_ja = Aluno.objects.filter(
            treinador=usuario,
            escalas__isnull=True
        )


        context = {
            'nome': usuario.nome,
            'tipo': tipo,
            'total_alunos': total_alunos,
            'ultimas_escalas': ultimas_escalas,
            'escalas_ultima_semana': escalas_ultima_semana,
            'alunos_sem_escala': alunos_sem_escala,
            'alunos_sem_escala_ja': alunos_sem_escala_ja,
            'genero': genero,
        }
    else:
        tipo = 'Aluna' if usuario.genero == 'feminino' else 'Aluno'
        genero = 'F' if usuario.genero == 'feminino' else 'M'
        treinador = usuario.treinador
        escalas = EscalaPoms.objects.filter(aluno=usuario).order_by('data')

        total_escalas = escalas.count()
        ultima_escala = escalas.last()

        tempo_limite = False
        if ultima_escala:
            tempo_limite = (timezone.now() - ultima_escala.data) > timedelta(days=7)
                    
        labels = [DateFormat(e.data).format('d/m') for e in escalas]
        pth = [e.pth for e in escalas]
        desajuste = [e.soma_desajuste for e in escalas]

        context = {
            'nome': usuario.nome,
            'tipo': tipo,
            'treinador': treinador,
            'total_escalas': total_escalas,
            'ultima_escala': ultima_escala.data if ultima_escala else None,
            'labels': labels,
            'pth': pth,
            'desajuste': desajuste,
            'tem_escalas': escalas.exists(),
            'tempo_limite' : tempo_limite,
            'genero': genero,
    }

    return render(request, 'EscalaPoms/static/home.html', context)


@login_required
@treinador_required
def meus_alunos(request):
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
    cpf = signing.loads(aluno_cpf, salt='aluno-cpf-salt')
    aluno = get_object_or_404(Aluno, cpf=cpf, treinador__cpf=request.user.username)
    escalas = EscalaPoms.objects.filter(aluno=aluno).order_by('data').select_related('aluno')

    labels = [DateFormat(e.data).format('d/m') for e in escalas]
    pth = [e.pth for e in escalas]
    desajuste = [e.soma_desajuste for e in escalas]

    context = {
        'aluno': aluno,
        'escalas': escalas,
        'labels': labels,
        'pth': pth,
        'desajuste': desajuste,
    }

    return render(request, 'EscalaPoms/aluno/historico_aluno.html', context)

@login_required
@aluno_required
def escala(request):
    aluno = get_object_or_404(Aluno, cpf=request.user.username)
    treinadores = Treinador.objects.all()

    if request.method == 'POST':
        if 'confirmar_treinador' in request.POST:
            return confirmar_treinador(aluno, request)
        else:
            return salvar_e_classificar_escala(aluno, request)

    return render(request, 'EscalaPoms/escala/escala.html', {
        'usuario': aluno,
        'treinadores': treinadores,
    })
    

@login_required
@aluno_required
def minhas_escalas(request):
    aluno = get_object_or_404(Aluno, cpf=request.user.username)

    escalas = (
        EscalaPoms.objects
        .filter(aluno=aluno)
        .order_by('data')  # Ordem crescente para os gráficos
        .select_related('classificacao')
    )

    labels = [DateFormat(e.data).format('d/m') for e in escalas]
    pth = [e.pth for e in escalas]
    desajuste = [e.soma_desajuste for e in escalas]

    context = {
        'aluno': aluno,
        'escalas': escalas,
        'labels': labels,
        'pth': pth,
        'desajuste': desajuste,
    }

    return render(request, 'EscalaPoms/escala/minhas_escalas.html', context)
    

@login_required
def perfil(request):
    cpf = request.user.username
    usuario = obter_usuario_por_cpf(cpf)

    if request.method == 'POST':
        if 'remove_foto' in request.POST:
            return remover_foto_usuario(usuario, request)

        return atualizar_dados_usuario(usuario, request, 'EscalaPoms/aluno/perfil.html')

    return render(request, 'EscalaPoms/aluno/perfil.html', {
        'usuario': usuario,
        'url_dashboard': reverse('perfil'),
    })
    

@login_required
def solicitar_exclusao(request):
    cpf = request.user.username
    usuario = obter_usuario_por_cpf(cpf)
    email_digitado = ''

    if request.method == 'POST':
        email_digitado = request.POST.get('email', '').strip()

        if email_digitado.lower() != usuario.email.strip().lower():
            messages.warning(request, "Email diferente do da sua conta.")
        else:
            exclusao_codigo = f"{random.randint(100000, 999999):06}"
            request.session['exclusao_codigo'] = exclusao_codigo
            enviar_codigo_email(exclusao_codigo, usuario.email)
            print(f"Código de exclusão enviado para {usuario.email}: {exclusao_codigo}")
            return redirect('confirmar_exclusao')

    return render(request, 'EscalaPoms/exclusao/solicitar_exclusao.html', {
        'usuario': usuario,
        'email': email_digitado,
    })

@login_required
def confirmar_exclusao(request):
    cpf = request.user.username
    usuario = obter_usuario_por_cpf(cpf)
    codigo_digitado = ''

    if request.method == 'POST':
        codigo_digitado = request.POST.get('codigo', '').strip()
        exclusao_codigo = request.session.get('exclusao_codigo')

        if not exclusao_codigo:
            messages.error(request, "Código expirado ou não gerado. Tente solicitar exclusão novamente.")
            return redirect('solicitar_exclusao')

        if codigo_digitado != str(exclusao_codigo):
            messages.warning(request, "Código incorreto. Por favor, tente novamente.")

        else:
            usuario.ativo = False
            usuario.save()
            request.session.pop('exclusao_codigo', None)
            deslogar(request)
            messages.success(request, "Sua conta foi desativada com sucesso.")
            return redirect('login')

    return render(request, 'EscalaPoms/exclusao/confirmar_exclusao.html', {
        'usuario': usuario,
        'codigo': codigo_digitado,
    })

@login_required
def logout_view(request):
    deslogar(request)
    return redirect('login')

@login_required
def sobre(request):
    return render(request, 'EscalaPoms/static/sobre.html')

@login_required
@aluno_required
def trocar_treinador(request):
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

    return render(request, 'EscalaPoms/aluno/trocar_treinador.html', {
        'usuario':     aluno,
        'treinadores': treinadores,
    })