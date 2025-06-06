from django.contrib import admin
from .models import Etudiant, Demande, Message, Admin

@admin.register(Etudiant)
class EtudiantAdmin(admin.ModelAdmin):
    list_display = ['nom', 'prenom', 'email', 'matricule', 'telephone']
    search_fields = ['nom', 'prenom', 'email', 'matricule']
    list_filter = ['nom', 'prenom', 'email']
    fields = ['nom', 'prenom', 'email', 'matricule', 'telephone', 'carte_NIP']

@admin.register(Demande)
class DemandeAdmin(admin.ModelAdmin):
    list_display = ['etudiant', 'types', 'annee_d_obtention', 'accept', 'traitement', 'status']
    list_filter = ['types', 'accept', 'traitement', 'status']
    search_fields = ['etudiant__nom', 'etudiant__prenom', 'etudiant__email']
    fields = ['etudiant', 'types', 'annee_d_obtention', 'filiere', 'quittance', 'carte_etudiant', 'accept', 'traitement', 'status', 'notified']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['nom', 'email', 'sujet']
    search_fields = ['nom', 'email', 'sujet']

@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = ['email']
    search_fields = ['email']