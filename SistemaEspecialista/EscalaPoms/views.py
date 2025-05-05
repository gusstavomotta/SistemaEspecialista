import datetime
import os
from django.conf        import settings

# Autenticação e controle de usuários
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as deslogar, authenticate, login
from django.contrib.auth.hashers import make_password

# Manipulação de requisições e respostas
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages

# Imports de formulários, modelos e backends
from .forms import *
from .models import Treinador, Aluno, EscalaPoms, ClassificacaoRecomendacao
from .backends import aluno_required, treinador_required
from .maquina_inferencia import (
    carregar_regras_poms,
    classificar_niveis_emocoes
)

# Utilitários do projeto
from .utils import (
    validar_numero_telefone,
    obter_usuario_por_cpf,
    processar_dados_escala,
    validar_cpf
)

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
    return render(request, 'EscalaPoms/login.html')

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
    return render(request, 'EscalaPoms/cadastro.html', {
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

        try:
            usuario = Treinador.objects.get(cpf=cpf)
        except Treinador.DoesNotExist:
            try:
                usuario = Aluno.objects.get(cpf=cpf)
            except Aluno.DoesNotExist:
                messages.error(request, 'CPF não encontrado.')
                return redirect('redefinir_senha')

        usuario.senha = make_password(nova_senha)
        usuario.save()
        messages.success(request, 'Senha redefinida com sucesso.')
        return redirect('login')
    
    return render(request, 'EscalaPoms/redefinir_senha.html')

@login_required
def home(request):
    cpf = request.user.username 
    usuario = obter_usuario_por_cpf(cpf)  

    if isinstance(usuario, Treinador):
        tipo = 'Treinador'
    elif isinstance(usuario, Aluno):
        tipo = 'Aluno'

    context = {'nome': usuario.nome, 'tipo': tipo}
    return render(request, 'EscalaPoms/home.html', context)

@login_required
@aluno_required
def escala(request):
    aluno = get_object_or_404(Aluno, cpf=request.user.username)

    if request.method == 'POST':
        try:
            # 1) Processa os dados brutos e soma os domínios
            dados = processar_dados_escala(request)

            observacoes = request.POST.get('observacoes', '').strip() or None

            # 2) Cria a EscalaPoms
            escala = EscalaPoms.objects.create(
                aluno=aluno,
                data=datetime.date.today(),
                observacoes=observacoes,
                **dados
            )

            # 3) Monta o dicionário de somas para a inferência
            somas = {
                'soma_tensao':      escala.soma_tensao,
                'soma_depressao':   escala.soma_depressao,
                'soma_hostilidade': escala.soma_hostilidade,
                'soma_fadiga':      escala.soma_fadiga,
                'soma_confusao':    escala.soma_confusao,
                'soma_vigor':       escala.soma_vigor,
                'soma_desajuste':   escala.soma_desajuste,
            }

            # 4) Define o caminho do arquivo de regras POMS
            caminho_regras = os.path.join(settings.BASE_DIR, 'EscalaPoms', 'regras.txt')

            # 5) Chama a máquina de inferência para obter os níveis
            niveis = classificar_niveis_emocoes(caminho_regras, somas)

            # 6) Cria o registro de classificação/recomendação
            ClassificacaoRecomendacao.objects.create(
                escala=escala,
                nivel_tensao      = niveis.get('nivel_tensao'),
                nivel_depressao   = niveis.get('nivel_depressao'),
                nivel_hostilidade = niveis.get('nivel_hostilidade'),
                nivel_fadiga      = niveis.get('nivel_fadiga'),
                nivel_confusao    = niveis.get('nivel_confusao'),
                nivel_vigor       = niveis.get('nivel_vigor'),
                nivel_desajuste   = niveis.get('nivel_desajuste'),
                # Se quiser, gere aqui um texto de recomendação:
                # recomendacao=gerar_recomendacao(niveis)
            )

            messages.success(request, "Dados salvos e classificados com sucesso!")
            return redirect('home')

        except ValueError as ev:
            messages.error(request, str(ev))

    return render(request, 'EscalaPoms/escala.html')

@login_required
@treinador_required
def meus_alunos(request):
    treinador = Treinador.objects.get(cpf=request.user.username)
    # Captura termo de busca
    q = request.GET.get('q', '').strip()

    # Filtra alunos do treinador
    alunos = Aluno.objects.filter(treinador=treinador)
    if q:
        alunos = alunos.filter(nome__icontains=q)
    
    alunos = alunos.order_by('nome')
    return render(request, 'EscalaPoms/meus_alunos.html', {'alunos': alunos, 'q': q,})

@login_required
@treinador_required
def historico_aluno(request, aluno_cpf):
    aluno = get_object_or_404(Aluno, cpf=aluno_cpf, treinador__cpf=request.user.username)
    escalas = EscalaPoms.objects.filter(aluno=aluno).order_by('data').select_related('classificacao')
    return render(request, 'EscalaPoms/historico_aluno.html', {'aluno': aluno, 'escalas': escalas})

@login_required
def perfil(request):
    cpf = request.user.username
    usuario = obter_usuario_por_cpf(cpf)

    if request.method == 'POST':
        if 'remove_foto' in request.POST:
            if usuario.foto:
                usuario.foto.delete(save=False) 
                usuario.foto = None              
                usuario.save()
                messages.success(request, 'Foto removida com sucesso.')
            return redirect('perfil')
        
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')
        foto = request.FILES.get('foto')

        if not validar_numero_telefone(telefone):
            messages.error(request, 'Telefone inválido. Use DDD e apenas números.')
            return render(request, 'EscalaPoms/perfil.html', {
                'usuario': usuario,
                'url_dashboard': reverse('home')
            })
    
        usuario.email = email
        usuario.num_telefone = telefone
        if foto:
            usuario.foto = foto
            
        usuario.save()
        messages.success(request, 'Perfil atualizado com sucesso.')
        return redirect('home')

    return render(request, 'EscalaPoms/perfil.html', {
        'usuario': usuario,
        'url_dashboard': reverse('home')
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
        .select_related('classificacao')    # aqui!

    )

    return render(request, 'EscalaPoms/minhas_escalas.html', {
        'aluno': aluno,
        'escalas': escalas_do_aluno,
        
    })

@login_required
def logout_view(request):
    deslogar(request)
    return redirect('login')


def sobre(request):
    return render(request, 'EscalaPoms/sobre.html')