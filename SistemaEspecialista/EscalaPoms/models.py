from django.db import models


#aqui criamos as classes que representam as tabelas do banco de dados, e cada atributo da classe representa uma coluna da tabela.
class Personal (models.Model):
    
    nome = models.CharField(max_length=100)

class Aluno (models.Model):
    
    nome = models.CharField(max_length=100)

class EscalaPoms(models.Model):
    
    somaEmocoes = models.IntegerField()
    