from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password

from .models import Treinador, Aluno
from .validators import validar_cpf, validar_numero_telefone, normalizar_cpf

class PessoaForm(forms.ModelForm):
    senha2 = forms.CharField(widget=forms.PasswordInput, label="Confirmar Senha")

    class Meta:
        model = Treinador 
        fields = ['cpf', 'nome', 'email', 'senha', 'genero', 'num_telefone']
        widgets = {'senha': forms.PasswordInput()}

    def clean_cpf(self):
        cpf = self.cleaned_data['cpf']
        cpf_normalizado = validar_cpf(cpf)
        
        # Verifica se o CPF já está em uso
        if Treinador.objects.filter(cpf=cpf_normalizado).exists() or Aluno.objects.filter(cpf=cpf_normalizado).exists():
            raise ValidationError("Já existe um usuário com este CPF.")
        
        return cpf_normalizado

    def clean_email(self):
        email = self.cleaned_data['email']
        # Verifica se o e-mail já está cadastrado
        if Treinador.objects.filter(email=email).exists() or Aluno.objects.filter(email=email).exists():
            raise ValidationError("Este e-mail já está cadastrado.")
        return email

    def clean_num_telefone(self):
        tel = self.cleaned_data.get('num_telefone', '')
        tel_normalizado = validar_numero_telefone(tel)

        if not tel_normalizado:
            raise ValidationError("Telefone inválido.")

        # Verifica se já existe um usuário com esse número de telefone
        if Treinador.objects.filter(num_telefone=tel_normalizado).exists() or Aluno.objects.filter(num_telefone=tel_normalizado).exists():
            raise ValidationError("Este número de telefone já está em uso.")

    def clean(self):
        cleaned = super().clean()
        senha = cleaned.get('senha')
        senha2 = cleaned.get('senha2')

        # Validação da senha
        if senha and len(senha) < 8:
            raise ValidationError({'senha': "A senha deve ter pelo menos 8 caracteres."})

        # Verifica se as senhas coincidem
        if senha != senha2:
            raise ValidationError({'senha2': "As senhas não conferem."})

        return cleaned

    def save(self, commit=True):
        self.instance.senha = make_password(self.cleaned_data['senha'])
        return super().save(commit=commit)

class TreinadorForm(PessoaForm):
    class Meta(PessoaForm.Meta):
        model = Treinador


class AlunoForm(PessoaForm):
    treinador = forms.CharField(
        max_length=11,
        help_text="CPF do treinador (obrigatório para aluno)"
    )

    class Meta(PessoaForm.Meta):
        model = Aluno
        fields = PessoaForm.Meta.fields + ['treinador']

    def clean_treinador(self):
        cpf_t = self.cleaned_data.get('treinador')
        if not cpf_t:
            raise ValidationError("Informe o CPF do treinador.")
        try:
            return Treinador.objects.get(cpf=cpf_t)
        except Treinador.DoesNotExist:
            raise ValidationError("Treinador não encontrado.")

    def save(self, commit=True):
        # Criptografa a senha
        self.instance.senha = make_password(self.cleaned_data['senha'])

        # Atribui o treinador como instância, não como string
        treinador = self.cleaned_data.get('treinador')
        if isinstance(treinador, Treinador):
            self.instance.treinador = treinador

        return super().save(commit=commit)


class AlunoTrocaTreinadorForm(forms.ModelForm):
    treinador = forms.ModelChoiceField(
        queryset=Treinador.objects.all(),   
        empty_label="Selecione um treinador",
        label="Novo Treinador"
    )

    class Meta:
        model = Aluno
        fields = ['treinador']