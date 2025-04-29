from django.db import models

#Aqui criamos as classes que são as tabelas do banco também
#Cada atributo é uma coluna
class Treinador(models.Model):
    cpf = models.CharField(
        max_length=11,
        primary_key=True,
        unique=True,
        help_text="Digite somente os números do CPF"
    )
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=128)
    genero = models.CharField(max_length=10, choices=[('M', 'Masculino'), ('F', 'Feminino')])
    num_telefone = models.CharField(null=True, blank=True, help_text="Número de telefone")
    
class Aluno(models.Model):
    treinador = models.ForeignKey(Treinador, on_delete=models.CASCADE, related_name='alunos')

    cpf = models.CharField(
        max_length=11,
        primary_key=True,
        unique=True,
        help_text="Digite somente os números do CPF"
    )
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=128)
    genero = models.CharField(max_length=10, choices=[('M', 'Masculino'), ('F', 'Feminino')])
    num_telefone = models.CharField(null=True, blank=True, help_text="Número de telefone")

class EscalaPoms(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='escalas')
    data = models.DateField()
    
    somaTensao = models.IntegerField()
    somaDepressao = models.IntegerField()
    somaHostilidade = models.IntegerField()
    somaFadiga = models.IntegerField()
    somaConfusao = models.IntegerField()
    somaVigor = models.IntegerField()
    somaDesajuste = models.IntegerField()
    pth = models.IntegerField()
    
    sono = models.IntegerField(null=True, blank=True, help_text="Horas de sono")
    volume_treino = models.IntegerField(null=True, blank=True, help_text="Volume de treino (ex: carga, repetições ou outro critério)")
    freq_cardiaca_media = models.IntegerField(null=True, blank=True, help_text="Frequência cardíaca média (BPM)")
    

    