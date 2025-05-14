from django.shortcuts import redirect, render
from django.contrib import messages
from django.urls import reverse

from ..validators import validar_numero_telefone, normalizar_cpf
from ..models import Aluno, Treinador
from ..forms import AlunoTrocaTreinadorForm

from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings

from ..models import Treinador, Aluno, EscalaPoms
from django.db import IntegrityError

def obter_usuario_por_cpf(cpf: str):
    """
    Busca um usuário (Treinador ou Aluno) pelo CPF.

    Args:
        cpf: string contendo o CPF (podendo ter formatação).

    Returns:
        Instância de Treinador ou Aluno correspondente ao CPF normalizado,
        ou None se não encontrado.
    """
    cpf_numeros = normalizar_cpf(cpf)
    return (
        Treinador.objects.filter(cpf=cpf_numeros).first()
        or Aluno.objects.filter(cpf=cpf_numeros).first()
    )

def atualizar_dados_usuario(usuario, request, template: str):
    """
    Atualiza email, telefone e foto de um usuário (Aluno ou Treinador).

    Args:
        usuario: instância de Aluno ou Treinador a ser atualizada.
        request: objeto HttpRequest contendo POST e FILES.
        template: nome do template a renderizar em caso de erro.

    Returns:
        HttpResponseRedirect para 'perfil' em caso de sucesso,
        ou HttpResponse renderizado com erros para correção.
    """
    is_aluno = isinstance(usuario, Aluno)
    form_troca = AlunoTrocaTreinadorForm(instance=usuario) if is_aluno else None

    def erro(mensagem: str):
        messages.error(request, mensagem)
        return render(request, template, {
            'usuario': usuario,
            'url_dashboard': reverse('perfil'),
            'is_aluno': is_aluno,
            'form_troca': form_troca,
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

    try:
        usuario.save()
    except IntegrityError:
        return erro('Não foi possível atualizar: conflito de dados no banco.')

    messages.success(request, 'Dados atualizados com sucesso!')
    return redirect('perfil')

def remover_foto_usuario(usuario, request):
    """
    Remove a foto de perfil de um usuário, se existir.

    Args:
        usuario: instância de Aluno ou Treinador.
        request: objeto HttpRequest para adicionar mensagem.

    Returns:
        HttpResponseRedirect para 'perfil'.
    """
    if usuario.foto:
        usuario.foto.delete(save=False)
        usuario.foto = None
        usuario.save()
        messages.success(request, 'Foto removida com sucesso.')
    return redirect('perfil')

def processar_troca_treinador(usuario, request):
    """
    Processa a troca de treinador para um Aluno usando formulário.

    Args:
        usuario: instância de Aluno.
        request: HttpRequest contendo POST com o novo treinador.

    Returns:
        HttpResponseRedirect para 'perfil' com mensagem de sucesso ou erro.
    """
    form = AlunoTrocaTreinadorForm(request.POST, instance=usuario)

    if form.is_valid():
        form.save()
        messages.success(request, 'Treinador atualizado com sucesso!')
        return redirect('perfil')

    messages.error(request, 'Selecione um treinador válido.')
    return redirect('perfil')

def enviar_codigo_email(codigo: str, email: str):
    """
    Envia um código de verificação por e-mail para o usuário confirmar exclusão.

    Args:
        codigo: string do código de verificação.
        email: endereço de e-mail de destino.
    """
    subject = 'Código de Verificação'
    message = (
        'Olá!\n\n'
        'Recebemos um pedido para excluir sua conta.\n'
        f'Seu código de verificação é: {codigo}\n\n'
        'Caso não tenha sido você, ignore este e-mail.\n'
        'Se foi você, insira o código acima para confirmar a exclusão.\n\n'
    )
    email_from = settings.EMAIL_HOST_USER
    send_mail(subject, message, email_from, [email])

def enviar_resumo_escalas_pendentes(treinador):
    """
    Envia um e-mail resumo de todas as escalas POMS pendentes de alunos de um treinador.

    Para cada escala pendente (enviado=False), lista aluno e data, envia e marca como enviado.

    Args:
        treinador: instância de Treinador cujo alunos serão verificados.
    """
    pendentes = (
        EscalaPoms.objects
            .filter(aluno__treinador=treinador, enviado=False)
            .select_related('aluno')
    )

    if not pendentes.exists():
        return

    linhas = [
        f"- {escala.aluno.nome}: {escala.data.strftime('%d/%m/%Y %H:%M')}"
        for escala in pendentes
    ]
    corpo = (
        f"Olá {treinador.nome},\n\n"
        "Enquanto você estava fora, estas escalas POMS foram cadastradas:\n\n"
        + "\n".join(linhas)
        + "\n\nAcesse o sistema para ver detalhes e recomendações."
    )

    send_mail(
        subject="Resumo de escalas POMS pendentes",
        message=corpo,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[treinador.email],
    )

    update_fields = {'enviado': True}
    if hasattr(EscalaPoms, 'data_envio'):
        update_fields['data_envio'] = timezone.now()
    pendentes.update(**update_fields)
