from django.shortcuts import render, redirect
from .models import *
# Create your views here.

#As views funcionam como controllers também, então aqui faremos a logica para as consultas no banco e chamada dos htmls passando os dados como parametros

def listar_alunos(request):
    alunos = Aluno.objects.all()
    return render(request, 'EscalaPoms/alunos.html', {'alunos': alunos})

def listar_personal(request):
    personal = Personal.objects.all()
    return render(request, 'EscalaPoms/personal.html', {'personal': personal})

def lista_escalas(request):
    escalas = EscalaPoms.objects.all()
    return render(request, 'EscalaPoms/escalas.html', {'escalas': escalas})

#Exemplo de view que recebe um POST do HTML e salva no banco de dados, depois ela redireciona para a lista de alunos ou retorna para o formulário original
#Não está sendo usando no momento
def adicionar_aluno(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')  
        novo_aluno = Aluno(nome=nome)    
        novo_aluno.save()                
        return redirect('listar_alunos') 
    else:
        return render(request, 'adicionar_aluno.html') 
