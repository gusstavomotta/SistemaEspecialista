from django.db import models

class ActiveManager(models.Manager):
    """
    Manager customizado que retorna apenas objetos com o campo 'ativo=True'.
    Usado para filtrar usuários ativos automaticamente nas consultas padrão.
    """
    def get_queryset(self):
        return super().get_queryset().filter(ativo=True)


class Pessoa(models.Model):
    """
    Classe abstrata base para Treinador e Aluno.
    Contém campos comuns como CPF, nome, e-mail, senha, telefone, foto, etc.
    """
    cpf          = models.CharField(primary_key=True)
    nome         = models.CharField(max_length=100)
    email        = models.EmailField(unique=True)
    senha        = models.CharField(max_length=128)
    genero       = models.CharField(max_length=12, choices=[
                        ('masculino', 'Masculino'),
                        ('feminino', 'Feminino')
                  ])
    num_telefone = models.CharField(max_length=100, null=True, blank=True)
    foto         = models.ImageField(upload_to='fotos_perfil/', blank=True, null=True)
    ativo        = models.BooleanField(default=True)

    class Meta:
        abstract = True  # Não será criada tabela para Pessoa diretamente


class Treinador(Pessoa):
    """
    Representa um treinador do sistema, herda de Pessoa.
    Usa ActiveManager para filtrar apenas treinadores ativos.
    """
    objects = ActiveManager()

    def __str__(self):
        return self.nome


class Aluno(Pessoa):
    """
    Representa um aluno do sistema, vinculado a um treinador.
    Herda de Pessoa e também usa ActiveManager para filtrar ativos.
    """
    treinador = models.ForeignKey(
        Treinador,
        on_delete=models.CASCADE,
        related_name='alunos'
    )
    objects = ActiveManager()


class EscalaPoms(models.Model):
    """
    Representa uma avaliação POMS preenchida por um aluno em uma data específica.

    Armazena os valores somados dos domínios emocionais e dados adicionais como sono,
    volume de treino e frequência cardíaca.
    """
    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.CASCADE,
        related_name='escalas'
    )
    data = models.DateTimeField()

    # Domínios emocionais (somatórios das respostas)
    soma_tensao      = models.IntegerField()
    soma_depressao   = models.IntegerField()
    soma_hostilidade = models.IntegerField()
    soma_fadiga      = models.IntegerField()
    soma_confusao    = models.IntegerField()
    soma_vigor       = models.IntegerField()
    soma_desajuste   = models.IntegerField()
    pth              = models.IntegerField()  # Perfil Total de Humor

    # Dados complementares
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

    enviado = models.BooleanField(default=False)

    def __str__(self):
        return f"Escala de {self.aluno.nome} em {self.data}"


class ClassificacaoRecomendacao(models.Model):
    """
    Armazena os resultados da inferência baseada na EscalaPoms:
    - Níveis emocionais classificados (ex: nível_tensao = 'Alto')
    - Recomendações de treino específicas por domínio
    """
    escala = models.OneToOneField(
        EscalaPoms,
        on_delete=models.CASCADE,
        related_name='classificacao'
    )

    # Classificação dos níveis emocionais
    nivel_tensao      = models.CharField(max_length=20)
    nivel_depressao   = models.CharField(max_length=20)
    nivel_hostilidade = models.CharField(max_length=20)
    nivel_fadiga      = models.CharField(max_length=20)
    nivel_confusao    = models.CharField(max_length=20)
    nivel_vigor       = models.CharField(max_length=20)
    nivel_desajuste   = models.CharField(max_length=20)

    # Sugestões de treino baseadas na classificação
    sugestao_treino_tensao      = models.TextField(blank=True, null=True)
    sugestao_treino_depressao   = models.TextField(blank=True, null=True)
    sugestao_treino_hostilidade = models.TextField(blank=True, null=True)
    sugestao_treino_fadiga      = models.TextField(blank=True, null=True)
    sugestao_treino_confusao    = models.TextField(blank=True, null=True)
    sugestao_treino_vigor       = models.TextField(blank=True, null=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Classificação para {self.escala.aluno.nome} em {self.escala.data:%Y-%m-%d}"
