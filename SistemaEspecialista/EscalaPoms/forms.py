from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from .models import Treinador, Aluno
from .utils import validar_cpf, validar_numero_telefone
import re

class PessoaForm(forms.ModelForm):
    senha2 = forms.CharField(widget=forms.PasswordInput, label="Confirmar Senha")

    class Meta:
        model = Treinador 
        fields = ['cpf', 'nome', 'email', 'senha', 'genero', 'num_telefone']
        widgets = {'senha': forms.PasswordInput()}

    def clean_cpf(self):
        cpf = re.sub(r'\D', '', self.cleaned_data['cpf'])
        if not validar_cpf(cpf):
            raise ValidationError("CPF inválido.")

        from .models import Treinador, Aluno

        if Treinador.objects.filter(cpf=cpf).exists() or Aluno.objects.filter(cpf=cpf).exists():
            raise ValidationError("Já existe um usuário com este CPF.")

        return cpf

    def clean_num_telefone(self):
        tel = re.sub(r'\D', '', self.cleaned_data.get('num_telefone',''))
        if tel and not validar_numero_telefone(tel):
            raise ValidationError("Telefone inválido.")
        return tel

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('senha') != cleaned.get('senha2'):
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

    def clean(self):
        cleaned = super().clean()
        cpf_t = cleaned.get('treinador')
        if not cpf_t:
            raise ValidationError({'treinador': "Informe o CPF do treinador."})
        try:
            cleaned['treinador'] = Treinador.objects.get(cpf=cpf_t)
        except Treinador.DoesNotExist:
            raise ValidationError({'treinador': "Treinador não encontrado."})
        return cleaned

class AlunoTrocaTreinadorForm(forms.ModelForm):
    treinador = forms.ModelChoiceField(
        queryset=Treinador.objects.all(),   
        empty_label="Selecione um treinador",
        label="Novo Treinador"
    )

    class Meta:
        model = Aluno
        fields = ['treinador']