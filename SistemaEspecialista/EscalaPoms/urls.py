from django.urls import path
from .views import *


urlpatterns = [
    path('', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('cadastro/', cadastro, name='cadastro'),
    path('home/', home, name='home'),
    path('escala/', escala, name='escala'),
    path('perfil/', perfil, name='perfil'),
    path('minhas_escalas/', minhas_escalas, name='minhas_escalas'),
    path('meus_alunos/', meus_alunos, name='meus_alunos'),
    path('historico_aluno/<str:aluno_cpf>/', historico_aluno, name='historico_aluno'),
    path('redefinir_senha/', redefinir_senha, name='redefinir_senha'),
    path('sobre/' , sobre, name='sobre'),
]
