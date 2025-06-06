from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('inscription', views.inscription, name="inscription"),
    path('login', views.connexion, name="connecter"),
    path('Tableau_de_bord', views.dashboard, name="dashboard"),
    path('admin_dashboard', views.admin_dashboard, name="admin_dashboard"),
    path('manage_demandes/<int:demande_id>', views.manage_demande, name="manage_demande"),
    path('demandeur', views.demande, name="demande"),
    path('recuperation', views.recuperation, name="recuperation"),
    path('reset/<uuid:token>/', views.reset_password, name='reset_password'),
    path('logout', views.log_out, name="log_out"),
    path('contacter', views.contact, name='contact'),
    path('profil', views.profil, name='profil'),
    path('reset/<uuid:token>/', views.reset_password, name='reset_password'),
]