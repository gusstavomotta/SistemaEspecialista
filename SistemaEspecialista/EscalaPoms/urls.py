from django.urls import path
from .views import *

#Aqui definimos as urls que serão utilizadas no projeto e associamos a uma função que será chamada quando a url for acessada.
urlpatterns = [
    path('', login_view, name='login'),
        path('logout/', logout_view, name='logout'),
    path('cadastro/', cadastro, name='cadastro'),
    path('dashboard/', dashboard, name='dashboard'),
    path('escala/', escala, name='escala'),
    path('perfil/', perfil, name='perfil'),
    path('relatorio/', relatorio, name='relatorio'),
    path('meus_alunos/', meus_alunos, name='meus_alunos'),

]
