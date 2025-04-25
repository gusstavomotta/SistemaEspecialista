from django.contrib.auth.hashers import make_password
from .models import Treinador, Aluno
from django import forms

class CadastroForm(forms.Form):
    TIPO_CHOICES = (
        ('treinador', 'Treinador'),
        ('aluno', 'Aluno'),
    )
    
    TIPO_GENEROS =  (
            ('masculino', 'Masculino'),
            ('feminino', 'Feminino'),
    )
    
    cpf = forms.CharField(
        max_length=11,
        help_text="Digite somente os números do CPF"
    )
    nome = forms.CharField(max_length=100)
    email = forms.EmailField()
    senha = forms.CharField(widget=forms.PasswordInput)
    tipo_usuario = forms.ChoiceField(choices=TIPO_CHOICES, label="Tipo de usuário")
    genero = forms.ChoiceField(choices=TIPO_GENEROS, label="Gênero", required=False, initial='masculino', help_text="Selecione o gênero")
    num_telefone = forms.CharField(max_length=100)

    # Campo extra para quando o usuário for aluno
    treinador = forms.CharField(
        max_length=11,
        required=False,
        help_text="Digite o CPF do treinador (obrigatório se for aluno)"
    )

    def clean(self):
        cleaned_data = super().clean()
        
        tipo = cleaned_data.get('tipo_usuario')
        treinador_cpf = cleaned_data.get('treinador')
        
        # Se o tipo for aluno, é obrigatório informar o CPF do treinador.
        if tipo == 'aluno' and not treinador_cpf:
            raise forms.ValidationError("Para cadastro de aluno, informe o CPF do treinador.")
        
        return cleaned_data

    def save(self):
        """
        Salva o registro dependendo do tipo de usuário selecionado.
        Para o treinador, cria a instância da model Treinador.
        Para o aluno, busca o treinador informado e cria a instância da model Aluno.
        """
        cpf = self.cleaned_data['cpf']
        nome = self.cleaned_data['nome']
        email = self.cleaned_data['email']
        senha = make_password(self.cleaned_data['senha'])
        tipo = self.cleaned_data['tipo_usuario']
        genero = self.cleaned_data['genero']
        num_telefone = self.cleaned_data.get('num_telefone')

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
            t_cpf = self.cleaned_data['treinador']
            # Procura o treinador informado
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
