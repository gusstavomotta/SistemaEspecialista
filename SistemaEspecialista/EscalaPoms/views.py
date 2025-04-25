from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CadastroForm
from .models import *
import datetime

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
                return redirect('login')
            except Exception as e:
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

def dashboard(request):
    #aqui serão feitos os cálculos para gerar os gráficos e as informações que serão mostradas no dashboard
    return render(request, 'EscalaPoms/dashboard.html')

def relatorio(request):
    #aqui será feito o processamento para gerar os relatórios, somas e gráficos
    return render(request, 'EscalaPoms/relatorio.html')