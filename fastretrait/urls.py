from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name="home"),
    path('inscription', inscription, name="inscription"),
    path('login', connexion, name="connecter"),
    path('Tableau_de_bord', dashboard, name="dashboard"),
    path('admin_dashboard', admin_dashboard, name="admin_dashboard"),
    path('manage_demande/<int:demande_id>', manage_demande, name="manage_demande"),
    path('demande', demande, name="demande"),
    path('recuperation', recuperation, name="recuperation"),
    path("logout", log_out, name="log_out"),
    path('contact', contact, name='contact'),
    path('profil', profil, name='profil'),
]