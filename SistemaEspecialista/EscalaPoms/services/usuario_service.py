from django.shortcuts import redirect, render
from django.contrib import messages
from django.urls import reverse

from ..validators import validar_numero_telefone, normalizar_cpf
from ..models import Aluno, Treinador
from ..forms import AlunoTrocaTreinadorForm

def obter_usuario_por_cpf(cpf):
    cpf_numeros = normalizar_cpf(cpf)
    return (
        Treinador.objects.filter(cpf=cpf_numeros).first()
        or Aluno.objects.filter(cpf=cpf_numeros).first()
    )
    
def atualizar_dados_usuario(usuario, request, template):
    def erro(mensagem):
        messages.error(request, mensagem)
        return render(request, template, {
            'usuario': usuario,
            'url_dashboard': reverse('perfil'),
        })

    email = request.POST.get('email')
    telefone = request.POST.get('telefone')
    foto = request.FILES.get('foto')

    if email and email != usuario.email:
        em_uso = (
            Treinador.objects.filter(email=email).exclude(pk=usuario.pk).exists() or
            Aluno.objects.filter(email=email).exclude(pk=usuario.pk).exists()
        )
        if em_uso:
            return erro('Este e-mail já está em uso por outro usuário.')
        usuario.email = email

    if telefone:
        if not validar_numero_telefone(telefone):
            return erro('Telefone inválido. Use DDD e apenas números.')
        usuario.num_telefone = telefone

    if foto:
        usuario.foto = foto

    usuario.save()
    messages.success(request, 'Dados atualizados com sucesso!')
    return redirect('perfil')

def remover_foto_usuario(usuario, request):
    if usuario.foto:
        usuario.foto.delete(save=False)
        usuario.foto = None
        usuario.save()
        messages.success(request, 'Foto removida com sucesso.')
    return redirect('perfil')


def processar_troca_treinador(usuario, request):
    form = AlunoTrocaTreinadorForm(request.POST, instance=usuario)
    
    if form.is_valid():
        form.save()
        messages.success(request, 'Treinador atualizado com sucesso!')
        return redirect('perfil')
    
    messages.error(request, 'Selecione um treinador válido.')
    return redirect('perfil')


def enviar_codigo_email(codigo, email):
    from django.core.mail import send_mail
    from django.conf import settings

    subject = 'Código de Verificação'
    message = f'Seu código de verificação é: {codigo}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]

    send_mail(subject, message, email_from, recipient_list)
    
