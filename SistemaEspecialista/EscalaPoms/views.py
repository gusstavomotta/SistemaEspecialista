import random
# Autenticação e controle de usuários
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as deslogar, authenticate, login
from django.contrib.auth.hashers import make_password

# Manipulação de requisições e respostas
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages

# Imports de formulários, modelos e backends
from .forms import *
from .models import Treinador, Aluno, EscalaPoms
from .backends import aluno_required, treinador_required
from .validators import validar_cpf
from .services.usuario_service import obter_usuario_por_cpf, remover_foto_usuario, atualizar_dados_usuario, processar_troca_treinador
from .services.escala_service import confirmar_treinador, salvar_e_classificar_escala

def login_view(request):
    if request.method == 'POST':
        cpf = request.POST.get('cpf')
        senha = request.POST.get('senha')
        usuario = authenticate(request, username=cpf, password=senha)
        if usuario:
            login(request, usuario)
            messages.success(request, "Login efetuado com sucesso!")
            return redirect('home')
        messages.error(request, "CPF ou senha incorretos.")
    return render(request, 'EscalaPoms/auth/login.html')

def cadastro(request):
    if request.method == 'POST':
        tipo = request.POST.get('tipo_usuario')
        if tipo == 'treinador':
            form = TreinadorForm(request.POST)
        else:
            form = AlunoForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Cadastro realizado com sucesso!")
            return redirect('login')
        else:
            messages.error(request, "Verifique os erros abaixo.")
    else:
        form = TreinadorForm()

    treinadores = Treinador.objects.all().values('cpf', 'nome')
    return render(request, 'EscalaPoms/auth/cadastro.html', {
        'form': form,
        'treinadores': treinadores
    })

def redefinir_senha(request):
    if request.method == 'POST':
        cpf = request.POST.get('cpf')
        nova_senha = request.POST.get('nova_senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        if not validar_cpf(cpf):
            messages.error(request, 'CPF inválido.')
            return redirect('redefinir_senha')

        if nova_senha != confirmar_senha:
            messages.error(request, 'As senhas não coincidem.')
            return redirect('redefinir_senha')

        usuario = obter_usuario_por_cpf(cpf) 
        if not usuario:
            messages.error(request, 'CPF não encontrado.')
            return redirect('redefinir_senha')

        usuario.senha = make_password(nova_senha)
        usuario.save()
        messages.success(request, 'Senha redefinida com sucesso.')
        return redirect('login')
    
    return render(request, 'EscalaPoms/auth/redefinir_senha.html')

@login_required
def home(request):
    cpf = request.user.username 
    usuario = obter_usuario_por_cpf(cpf)  

    if isinstance(usuario, Treinador):
        tipo = 'Treinador'
    elif isinstance(usuario, Aluno):
        tipo = 'Aluno'

    context = {'nome': usuario.nome, 'tipo': tipo}
    return render(request, 'EscalaPoms/static/home.html', context)

@login_required
@aluno_required
def escala(request):
    aluno = get_object_or_404(Aluno, cpf=request.user.username)
    treinadores = Treinador.objects.all()

    if request.method == 'POST' and 'confirmar_treinador' in request.POST:
        return confirmar_treinador(aluno, request)

    if not aluno.treinador or not aluno.treinador.ativo:
        return render(request, 'EscalaPoms/escala/escala.html', {
            'usuario': aluno,
            'treinadores': treinadores,
        })

    if request.method == 'POST':
        return salvar_e_classificar_escala(aluno, request)

    return render(request, 'EscalaPoms/escala/escala.html', {
        'usuario': aluno,
        'treinadores': treinadores,
    })

@login_required
@treinador_required
def meus_alunos(request):
    treinador = Treinador.objects.get(cpf=request.user.username)
    q = request.GET.get('q', '').strip()

    alunos = Aluno.objects.filter(treinador=treinador)
    if q:
        alunos = alunos.filter(nome__icontains=q)
    
    alunos = alunos.order_by('nome')
    return render(request, 'EscalaPoms/escala/meus_alunos.html', {'alunos': alunos, 'q': q,})

@login_required
@treinador_required
def historico_aluno(request, aluno_cpf):
    aluno = get_object_or_404(Aluno, cpf=aluno_cpf, treinador__cpf=request.user.username)
    escalas = EscalaPoms.objects.filter(aluno=aluno).order_by('data').select_related('classificacao')
    return render(request, 'EscalaPoms/aluno/historico_aluno.html', {'aluno': aluno, 'escalas': escalas})

@login_required
def perfil(request):
    cpf = request.user.username
    usuario = obter_usuario_por_cpf(cpf)

    form_troca = None
    if request.method == 'POST':
        if 'treinador' in request.POST and hasattr(usuario, 'treinador') and usuario.treinador and not usuario.treinador.ativo:
            return processar_troca_treinador(usuario, request)
        elif 'remove_foto' in request.POST:
            return remover_foto_usuario(usuario, request)
        else:
            return atualizar_dados_usuario(usuario, request, 'EscalaPoms/aluno/perfil.html')

    if hasattr(usuario, 'treinador') and usuario.treinador and not usuario.treinador.ativo:
        form_troca = AlunoTrocaTreinadorForm(instance=usuario)

    return render(request, 'EscalaPoms/aluno/perfil.html', {
        'usuario': usuario,
        'form_troca': form_troca,
        'url_dashboard': reverse('perfil'),
    })

@login_required
@aluno_required
def minhas_escalas(request):

    aluno = get_object_or_404(
        Aluno,
        cpf=request.user.username
    )

    escalas_do_aluno = (
        EscalaPoms.objects
        .filter(aluno=aluno)
        .order_by('data')
        .select_related('classificacao')

    )

    return render(request, 'EscalaPoms/escala/minhas_escalas.html', {
        'aluno': aluno,
        'escalas': escalas_do_aluno,
        
    })
        
@login_required
def solicitar_exclusao(request):
    cpf = request.user.username
    usuario = obter_usuario_por_cpf(cpf)

    if request.method == 'POST':
        email_input = request.POST.get('email')
        if email_input != usuario.email:
            messages.error(request, "O email informado não corresponde ao email registrado.")
            return render(request, 'EscalaPoms/solicitar_exclusao.html', {'usuario': usuario})
        
        exclusao_codigo = random.randint(100000, 999999)
        request.session['exclusao_codigo'] = exclusao_codigo
        '''send_mail(
            'Código de Exclusão de Conta',
            f'Seu código para exclusão de conta é: {exclusao_codigo}',
            'noreply@seusite.com',
            [usuario.email],
        )'''
        print(f"\n\n\n\n\n\n\nSeu código para exclusão de conta é: {exclusao_codigo}\n\n\n\n\n\n\n")
        
        messages.success(request, "Um código foi enviado para o seu email. Por favor, insira o código na próxima tela para confirmar a exclusão.")
        return redirect('confirmar_exclusao')
    
    return render(request, 'EscalaPoms/exclusao/solicitar_exclusao.html', {'usuario': usuario})

@login_required
def confirmar_exclusao(request):
    
    cpf = request.user.username
    usuario = obter_usuario_por_cpf(cpf)

    if request.method == 'POST':
        codigo_digitado = request.POST.get('codigo')
        exclusao_codigo = request.session.get('exclusao_codigo')
        if not exclusao_codigo:
            messages.error(request, "Código expirado ou não gerado. Tente solicitar exclusão novamente.")
            return redirect('solicitar_exclusao')
        
        if str(exclusao_codigo) == codigo_digitado.strip():
            usuario.ativo = False
            usuario.save()
            
            del request.session['exclusao_codigo']
            deslogar(request)
            messages.success(request, "Sua conta foi desativada com sucesso.")
            return redirect('login')
        else:
            messages.error(request, "Código incorreto. Por favor, tente novamente.")
            return redirect('confirmar_exclusao')
    
    return render(request, 'EscalaPoms/exclusao/confirmar_exclusao.html', {'usuario': usuario})

@login_required
def logout_view(request):
    deslogar(request)
    return redirect('login')

@login_required
def sobre(request):
    return render(request, 'EscalaPoms/static/sobre.html')