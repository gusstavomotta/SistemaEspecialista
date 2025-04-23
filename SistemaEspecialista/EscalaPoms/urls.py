from django.urls import path
from .views import *

#Aqui definimos as urls que serão utilizadas no projeto e associamos a uma função que será chamada quando a url for acessada.
urlpatterns = [
    path('alunos/', listar_alunos, name='listar_alunos'),
    path('personal/', listar_personal, name='listar_personal'),
    path('escalas/', lista_escalas, name='lista_escalas')
]
