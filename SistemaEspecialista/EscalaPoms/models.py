from django.db import models

class Treinador(models.Model):
    """
    Modelo que representa um Treinador no sistema.

    Campos:
      - cpf: CPF do treinador (apenas números). É a chave primária única.
      - nome: Nome completo do treinador.
      - email: Email único do treinador.
      - senha: Senha criptografada do treinador.
      - genero: Gênero do treinador, com opções 'M' (Masculino) ou 'F' (Feminino).
      - num_telefone: Número de telefone do treinador (opcional).
    """
    cpf = models.CharField(
        max_length=11,
        primary_key=True,
        unique=True,
        help_text="Digite somente os números do CPF"
    )
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=128)
    genero = models.CharField(
        max_length=10,
        choices=[('M', 'Masculino'), ('F', 'Feminino')]
    )
    num_telefone = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Número de telefone"
    )

    def __str__(self):
        # Retorna o nome do treinador para facilitar a identificação em interfaces administrativas.
        return self.nome


class Aluno(models.Model):
    """
    Modelo que representa um Aluno no sistema.

    Cada aluno é vinculado a um treinador.

    Campos:
      - treinador: Chave estrangeira para o Treinador associado (com exclusão em cascata).
      - cpf: CPF do aluno (apenas números). É a chave primária única.
      - nome: Nome completo do aluno.
      - email: Email único do aluno.
      - senha: Senha criptografada do aluno.
      - genero: Gênero do aluno, com opções 'M' (Masculino) ou 'F' (Feminino).
      - num_telefone: Número de telefone do aluno (opcional).
    """
    treinador = models.ForeignKey(
        Treinador,
        on_delete=models.CASCADE,
        related_name='alunos'
    )
    cpf = models.CharField(
        max_length=11,
        primary_key=True,
        unique=True,
        help_text="Digite somente os números do CPF"
    )
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=128)
    genero = models.CharField(
        max_length=10,
        choices=[('M', 'Masculino'), ('F', 'Feminino')]
    )
    num_telefone = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Número de telefone"
    )

    def __str__(self):
        # Retorna o nome do aluno para facilitar a identificação.
        return self.nome


class EscalaPoms(models.Model):
    """
    Modelo que representa uma escala ou avaliação realizada por um aluno.

    Cada registro de escala está vinculado a um aluno e contém somatórios de indicadores 
    e outros dados relacionados, tais como:
      - somaTensao: Soma dos valores de tensão.
      - somaDepressao: Soma dos valores de depressão.
      - somaHostilidade: Soma dos valores de hostilidade.
      - somaFadiga: Soma dos valores de fadiga.
      - somaConfusao: Soma dos valores de confusão.
      - somaVigor: Soma dos valores de vigor.
      - somaDesajuste: Soma dos valores de desajuste.
      - pth: Valor calculado que utiliza os somatórios acima.
      - sono: Horas de sono registradas (opcional).
      - volume_treino: Volume de treino (por exemplo, carga ou repetições) (opcional).
      - freq_cardiaca_media: Frequência cardíaca média em BPM (opcional).
    """
    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.CASCADE,
        related_name='escalas'
    )
    data = models.DateField()

    somaTensao = models.IntegerField()
    somaDepressao = models.IntegerField()
    somaHostilidade = models.IntegerField()
    somaFadiga = models.IntegerField()
    somaConfusao = models.IntegerField()
    somaVigor = models.IntegerField()
    somaDesajuste = models.IntegerField()
    pth = models.IntegerField()

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

    def __str__(self):
        # Retorna uma string que relaciona o aluno e a data da escala, facilitando a identificação do registro.
        return f"Escala de {self.aluno.nome} em {self.data}"
