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

    if foto:
        usuario.foto = foto

    if not validar_numero_telefone(telefone):
        messages.error(request, 'Telefone inválido. Use DDD e apenas números.')
        return render(request, template, {
            'usuario': usuario,
            'url_dashboard': reverse('perfil')
        })

    usuario.email = email
    usuario.num_telefone = telefone
    usuario.save()
    messages.success(request, 'Perfil atualizado com sucesso.')
    return redirect('perfil')


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
    from ..validators import normalizar_cpf

    cpf_numeros = normalizar_cpf(cpf)
    try:
        return Treinador.objects.get(cpf=cpf_numeros)
    except Treinador.DoesNotExist:
        pass

    try:
        return Aluno.objects.get(cpf=cpf_numeros)
    except Aluno.DoesNotExist:
        return None

def enviar_email(codigo, email):
    from django.core.mail import send_mail
    from django.conf import settings

    subject = 'Código de Verificação'
    message = f'Seu código de verificação é: {codigo}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]

    send_mail(subject, message, email_from, recipient_list)
    
def erro_redirect(request, mensagem, rota):
    messages.error(request, mensagem)
    return redirect(rota)