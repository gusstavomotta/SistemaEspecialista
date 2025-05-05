from django.db import models

class Pessoa(models.Model):
    cpf         = models.CharField(max_length=11, primary_key=True, help_text="…")
    nome        = models.CharField(max_length=100)
    email       = models.EmailField(unique=True)
    senha       = models.CharField(max_length=128)
    genero      = models.CharField(max_length=12, choices=[('masculino','Masculino'),('feminino','Feminino')])
    num_telefone= models.CharField(max_length=100, null=True, blank=True)
    foto = models.ImageField(upload_to='fotos_perfil/', blank=True, null=True)

    class Meta:
        abstract = True

class Treinador(Pessoa):
    pass

class Aluno(Pessoa):
    
    treinador = models.ForeignKey(Treinador, on_delete=models.CASCADE, related_name='alunos')

class EscalaPoms(models.Model):

    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.CASCADE,
        related_name='escalas'
    )
    data = models.DateField()

    soma_tensao      = models.IntegerField()
    soma_depressao   = models.IntegerField()
    soma_hostilidade = models.IntegerField()
    soma_fadiga      = models.IntegerField()
    soma_confusao    = models.IntegerField()
    soma_vigor       = models.IntegerField()
    soma_desajuste   = models.IntegerField()
    pth              = models.IntegerField()

    sono = models.IntegerField(
        null=True,
        blank=True,
        help_text="Horas de sono"
    )
    volume_treino = models.IntegerField(
        null=True,
        blank=True,
        help_text="Volume de treino (ex: carga, repetições ou outro critério)"
    )
    freq_cardiaca_media = models.IntegerField(
        null=True,
        blank=True,
        help_text="Frequência cardíaca média (BPM)"
    )
    observacoes = models.TextField(
        null=True,
        blank=True,
        help_text="Informações complementares (ex: tomando remédio, acontecimentos da semana)"
    )

    def __str__(self):
        # Retorna uma string que relaciona o aluno e a data da escala, facilitando a identificação do registro.
        return f"Escala de {self.aluno.nome} em {self.data}"

class ClassificacaoRecomendacao(models.Model):
    escala = models.OneToOneField(
        'EscalaPoms',
        on_delete=models.CASCADE,
        related_name='classificacao'
    )

    nivel_tensao      = models.CharField(max_length=20)
    nivel_depressao   = models.CharField(max_length=20)
    nivel_hostilidade = models.CharField(max_length=20)
    nivel_fadiga      = models.CharField(max_length=20)
    nivel_confusao    = models.CharField(max_length=20)
    nivel_vigor       = models.CharField(max_length=20)
    nivel_desajuste   = models.CharField(max_length=20)

    # Campo opcional para recomendação textual baseada nos níveis
    recomendacao = models.TextField(blank=True, null=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Classificação para {self.escala.aluno.nome} em {self.escala.data}"