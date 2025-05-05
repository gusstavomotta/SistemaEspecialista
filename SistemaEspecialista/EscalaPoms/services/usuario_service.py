from django.shortcuts import redirect, render
from django.contrib import messages
from django.urls import reverse
from ..validators import validar_numero_telefone

def remover_foto_usuario(usuario, request):
    if usuario.foto:
        usuario.foto.delete(save=False)
        usuario.foto = None
        usuario.save()
        messages.success(request, 'Foto removida com sucesso.')
    return redirect('perfil')


def atualizar_dados_usuario(usuario, request, template):
    email = request.POST.get('email')
    telefone = request.POST.get('telefone')
    foto = request.FILES.get('foto')

    if not validar_numero_telefone(telefone):
        messages.error(request, 'Telefone inválido. Use DDD e apenas números.')
        return render(request, template, {
            'usuario': usuario,
            'url_dashboard': reverse('home')
        })

    usuario.email = email
    usuario.num_telefone = telefone
    usuario.foto = foto
    usuario.save()
    messages.success(request, 'Perfil atualizado com sucesso.')
    return redirect('home')


def processar_troca_treinador(usuario, request):
    from ..forms import AlunoTrocaTreinadorForm

    form = AlunoTrocaTreinadorForm(request.POST, instance=usuario)
    if form.is_valid():
        form.save()
        messages.success(request, 'Treinador atualizado com sucesso!')
    else:
        messages.error(request, 'Selecione um treinador válido.')
    return redirect('perfil')


def obter_usuario_por_cpf(cpf):
    from ..models import Treinador, Aluno
    try:
        return Treinador.objects.get(cpf=cpf)
    except Treinador.DoesNotExist:
        return Aluno.objects.get(cpf=cpf)
