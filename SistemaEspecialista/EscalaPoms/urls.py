from django.urls import path
from .views import *

urlpatterns = [
    path('', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('cadastro/', cadastro, name='cadastro'),
    path('home_treinador/', home_treinador, name='home_treinador'),
    path('home_alunno/', home_aluno, name='home_aluno'),
    path('escala/', escala, name='escala'),
    path('perfil/', perfil, name='perfil'),
    path('relatorio/', relatorio, name='relatorio'),
    path('meus_alunos/', meus_alunos, name='meus_alunos'),
    path('historico_aluno/<str:aluno_cpf>/', historico_aluno, name='historico_aluno'),
    path('esqueceu_senha/', esqueceu_senha, name='esqueceu_senha'),

]
