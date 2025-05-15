from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import *

# URLs principais da aplicação

urlpatterns = [
    # Acesso inicial e cadastro
    path('', login_view, name='login'),
    path('cadastro/', cadastro, name='cadastro'),

    # Redefinição de senha
    path('redefinir_senha/', redefinir_senha, name='redefinir_senha'),
    path('confirmar-codigo/', confirmar_codigo, name='confirmar_codigo'),

    # Dashboard principal
    path('home/', home, name='home'),

    # Escala POMS
    path('escala/', escala, name='escala'),
    path('minhas_escalas/', minhas_escalas, name='minhas_escalas'),

    # Visualização de alunos (para treinadores)
    path('meus_alunos/', meus_alunos, name='meus_alunos'),
    path('historico_aluno/<str:aluno_cpf>/', historico_aluno, name='historico_aluno'),

    # Perfil e gerenciamento de conta
    path('perfil/', perfil, name='perfil'),
    path('solicitar_exclusao/', solicitar_exclusao, name='solicitar_exclusao'),
    path('confirmar_exclusao/', confirmar_exclusao, name='confirmar_exclusao'),

    # Página institucional
    path('sobre/', sobre, name='sobre'),
    path("termo_uso/", termo_uso, name="termo_uso"),

    # Logout
    path('logout/', logout_view, name='logout'),

    # Trocar treinador (aluno)
    path('trocar_treinador/', trocar_treinador, name='trocar_treinador'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
