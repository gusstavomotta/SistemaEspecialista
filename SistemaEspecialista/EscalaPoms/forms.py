from django.contrib.auth.hashers import make_password
from django import forms
from .models import Treinador, Aluno
from .utils import validar_cpf, validar_numero_telefone
from django.core.exceptions import ValidationError
import re

class CadastroForm(forms.Form):
    """
    Formulário para cadastro de usuários (Treinador e Aluno).

    Este formulário recebe os dados necessários para o cadastro, realiza a 
    validação do CPF e do número de telefone usando funções auxiliares e 
    determina, com base no tipo de usuário, se será criado um registro de 
    Treinador ou de Aluno.
    """
    TIPO_CHOICES = (
        ('treinador', 'Treinador'),
        ('aluno', 'Aluno'),
    )
    
    TIPO_GENEROS = (
        ('masculino', 'Masculino'),
        ('feminino', 'Feminino'),
    )
    
    cpf = forms.CharField(
        max_length=11,
        help_text="Digite somente os números do CPF"
    )
    nome = forms.CharField(max_length=100)
    email = forms.EmailField()
    
    senha = forms.CharField(widget=forms.PasswordInput,label="Senha")
    senha2 = forms.CharField(widget=forms.PasswordInput,label="Confirmar Senha")
    
    tipo_usuario = forms.ChoiceField(choices=TIPO_CHOICES, label="Tipo de usuário")
    genero = forms.ChoiceField(
        choices=TIPO_GENEROS,
        label="Gênero",
        required=False,
        initial='masculino',
        help_text="Selecione o gênero"
    )
    num_telefone = forms.CharField(
        max_length=100,
        help_text="Digite o número de telefone com DDD"
    )
    treinador = forms.CharField(
        max_length=11,
        required=False,
        help_text="Digite o CPF do treinador (obrigatório se for aluno)"
    )

    def clean(self):
        cleaned = super().clean()
        senha, senha2 = cleaned.get('senha'), cleaned.get('senha2')
        if senha and senha2 and senha != senha2:
            self.add_error('senha2', 'As senhas não coincidem.')
        if cleaned.get('tipo_usuario') == 'aluno' and not cleaned.get('treinador'):
            self.add_error('treinador', 'Para se cadastrar, selecione um treinador.')
        return cleaned
    
    def clean_cpf(self):
        cpf = re.sub(r'\D', '', self.cleaned_data['cpf'])
        if not validar_cpf(cpf):
            raise forms.ValidationError("CPF inválido.")
        return cpf
    
    def clean_num_telefone(self):
        tel = re.sub(r'\D', '', self.cleaned_data['num_telefone'])
        if not validar_numero_telefone(tel):
            raise forms.ValidationError("Telefone inválido.")
        return tel
    
    def save(self):
        """
        Salva o cadastro do usuário no banco de dados.

        Este método verifica o tipo de cadastro (Treinador ou Aluno) e cria o objeto
        correspondente. Em caso de cadastro de aluno, busca o treinador associado por CPF.
        Utiliza make_password para criptografar a senha antes de salvá-la.
        """
        cpf = self.cleaned_data['cpf']
        nome = self.cleaned_data['nome']
        email = self.cleaned_data['email']
        senha = make_password(self.cleaned_data['senha'])
        tipo = self.cleaned_data['tipo_usuario']
        genero = self.cleaned_data['genero']
        num_telefone = self.cleaned_data.get('num_telefone')

        # Se o cadastro for de Treinador, cria o objeto correspondente
        if tipo == 'treinador':
            usuario = Treinador.objects.create(
                cpf=cpf,
                nome=nome,
                email=email,
                senha=senha,
                genero=genero,
                num_telefone=num_telefone
            )
        else:
            # Cadastro para aluno: busca o treinador pelo CPF informado
            t_cpf = self.cleaned_data['treinador']
            try:
                treinador_obj = Treinador.objects.get(cpf=t_cpf)
            except Treinador.DoesNotExist:
                raise forms.ValidationError("O treinador informado não foi encontrado.")
            usuario = Aluno.objects.create(
                cpf=cpf,
                nome=nome,
                email=email,
                senha=senha,
                treinador=treinador_obj,
                genero=genero,
                num_telefone=num_telefone
            )
        return usuario
