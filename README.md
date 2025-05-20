# 🧠 Sistema Especialista - Umore

Sistema especialista desenvolvido em parceria com o curso de Educação Física da UNISC. O objetivo do projeto é auxiliar na avaliação do humor de atletas e pacientes a partir da aplicação da Escala POMS (Profile of Mood States), gerando recomendações automáticas com base nas emoções relatadas.

Acesse pela URL: sistemaumore.com.br

---

## 📌 Sobre o Projeto

Este sistema utiliza regras de inferência para classificar o estado emocional do usuário com base nos seis fatores da Escala POMS Reduzida:

- Tensão
- Depressão
- Hostilidade
- Fadiga
- Confusão
- Vigor
- Desajuste ao Treino

Com esses valores, o sistema calcula o índice de Perturbação Total do Humor (PTH) e, a partir de um motor de inferência baseado em regras (sistema especialista), classifica o nível de cada emoção e oferece recomendações de treinos.

---

## 🎯 Objetivos

- Automatizar a análise da Escala POMS.
- Fornecer feedback baseado em regras especializadas.
- Facilitar o acompanhamento psicológico e físico de usuários.
- Criar uma interface acessível e responsiva para profissionais da saúde.

---

## 🧩 Tecnologias Utilizadas

| Tecnologia | Finalidade |
|-----------|------------|
| **Python** | Backend e motor de inferência |
| **Django** | Framework web |
| **HTML/CSS** | Interface do sistema |
| **JavaScript** | Criação de gráficos |
| **Bootstrap** | Layout responsivo |
| **PostgreSQL** | Banco de dados |

---

## ⚙️ Instalação e Execução

### 🔧 Requisitos

- Python 3.10+
- PostgreSQL 13+
- `pip` instalado
- Ambiente virtual: `venv`

### 📥 Passos para rodar localmente

```bash
# Banco de dados
Instale o PostgreSql
Crie um database com o nome de sua escolha
Acesse o arquivo .env e preencha com as informações do database e do e-mail (crie uma senha de app)

# Clone o repositório
git clone https://github.com/gusstavomotta/SistemaEspecialista.git
cd SistemaEspecialista (2x)

# Crie e ative o ambiente virtual (opcional, mas recomendado)
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação (se for um script simples com Flask ou Django)
python manage.py collectstatic
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

### 📥 Passos para rodar com Docker
```bash
Instalar Docker Desktop - Windows
Instalar Docker Engine e Docker Compose - Linux

# Clone o repositório
git clone https://github.com/gusstavomotta/SistemaEspecialista.git
cd SistemaEspecialista (2x)

# Acessar a pasta raiz e rodar o comando:
docker-compose up --build
```

