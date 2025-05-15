from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password

from .models import Treinador, Aluno
from .validators import validar_cpf, validar_numero_telefone, normalizar_cpf


class PessoaForm(forms.ModelForm):
    """
    Formulário base para criação/edição de Treinador ou Aluno, incluindo validações
    de CPF, e‑mail, telefone e confirmação de senha.
    """

    senha2 = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirmar Senha",
        help_text="Digite novamente a senha para confirmação.",
    )
    aceite_termos = forms.BooleanField(
        label="",
        error_messages={
            "required": "Você deve aceitar os Termos de Uso para prosseguir."
        },
    )

    class Meta:
        model = Treinador
        fields = ["cpf", "nome", "email", "senha", "genero", "num_telefone"]
        widgets = {"senha": forms.PasswordInput(render_value=False)}

    def clean_cpf(self) -> str:
        """
        Normaliza e valida o CPF, garantindo unicidade entre Treinador e Aluno.
        """
        raw_cpf = self.cleaned_data["cpf"]
        cpf_normalizado = validar_cpf(raw_cpf)  # remove formatação e valida dígitos

        exists = (
            Treinador.objects.filter(cpf=cpf_normalizado).exists()
            or Aluno.objects.filter(cpf=cpf_normalizado).exists()
        )
        if exists:
            raise ValidationError("Já existe um usuário com este CPF.")

        return cpf_normalizado

    def clean_email(self) -> str:
        """
        Valida que o e‑mail não esteja cadastrado em outro usuário.
        """
        email = self.cleaned_data["email"]
        if (
            Treinador.objects.filter(email=email).exists()
            or Aluno.objects.filter(email=email).exists()
        ):
            raise ValidationError("Este e-mail já está cadastrado.")
        return email

    def clean_num_telefone(self) -> str:
        """
        Normaliza e valida o número de telefone, garantindo DDD + apenas números,
        e verifica unicidade.
        """
        telefone_raw = self.cleaned_data.get("num_telefone", "")
        telefone_normalizado = validar_numero_telefone(telefone_raw)
        if not telefone_normalizado:
            raise ValidationError("Telefone inválido. Use DDD e apenas números.")

        exists = (
            Treinador.objects.filter(num_telefone=telefone_normalizado).exists()
            or Aluno.objects.filter(num_telefone=telefone_normalizado).exists()
        )
        if exists:
            raise ValidationError("Este número de telefone já está em uso.")

        return telefone_normalizado

    def clean(self):
        """
        Valida tamanho mínimo da senha e conferência entre senha e confirmação.
        """
        cleaned = super().clean()
        senha = cleaned.get("senha")
        senha2 = cleaned.get("senha2")

        # Senha mínima
        if senha and len(senha) < 8:
            self.add_error("senha", "A senha deve ter pelo menos 8 caracteres.")

        # Confirmação de senha
        if senha and senha2 and senha != senha2:
            self.add_error("senha2", "As senhas não conferem.")

        return cleaned

    def save(self, commit=True):
        """
        Sobrescreve para criptografar a senha antes de salvar no banco.
        """
        raw_senha = self.cleaned_data.get("senha")
        if raw_senha:
            self.instance.senha = make_password(raw_senha)
        return super().save(commit=commit)


class TreinadorForm(PessoaForm):
    """
    Formulário específico para criação/edição de Treinador.
    Herdado de PessoaForm.
    """

    class Meta(PessoaForm.Meta):
        model = Treinador


class AlunoForm(PessoaForm):
    """
    Formulário para criação/edição de Aluno, exige CPF de treinador vinculável.
    """

    treinador = forms.CharField(
        max_length=11,
        label="CPF do Treinador",
        help_text="Informe o CPF do treinador responsável.",
    )

    class Meta(PessoaForm.Meta):
        model = Aluno
        fields = PessoaForm.Meta.fields + ["treinador"]

    def clean_treinador(self) -> Treinador:
        """
        Converte CPF de treinador em instância de Treinador, validando existência.
        """
        cpf_t = normalizar_cpf(self.cleaned_data.get("treinador", ""))
        try:
            return Treinador.objects.get(cpf=cpf_t)
        except Treinador.DoesNotExist:
            raise ValidationError("Treinador não encontrado para o CPF informado.")

    def save(self, commit=True):
        """
        Criptografa a senha e vincula a instância de treinador antes de salvar.
        """
        # Criptografa senha
        raw_senha = self.cleaned_data.get("senha")
        if raw_senha:
            self.instance.senha = make_password(raw_senha)

        # Atribui objeto Treinador ao aluno
        treinador_obj = self.cleaned_data.get("treinador")
        if isinstance(treinador_obj, Treinador):
            self.instance.treinador = treinador_obj

        return super().save(commit=commit)


class AlunoTrocaTreinadorForm(forms.ModelForm):
    """
    Formulário para que um Aluno selecione um novo treinador via ModelChoiceField.
    """

    treinador = forms.ModelChoiceField(
        queryset=Treinador.objects.all(),
        empty_label="Selecione um treinador",
        label="Novo Treinador",
        help_text="Escolha um treinador válido na lista.",
    )

    class Meta:
        model = Aluno
        fields = ["treinador"]
