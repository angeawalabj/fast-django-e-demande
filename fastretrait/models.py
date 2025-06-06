from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, FileExtensionValidator
from django.core.mail import send_mail
import uuid
from datetime import timedelta
from django.utils import timezone

class Etudiant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100, validators=[RegexValidator(r'^[A-Za-z\s-]+$', 'Nom invalide')])
    prenom = models.CharField(max_length=100, validators=[RegexValidator(r'^[A-Za-z\s-]+$', 'Prénom invalide')])
    email = models.EmailField(max_length=100, unique=True)
    matricule = models.CharField(max_length=20, unique=True, validators=[RegexValidator(r'^[A-Za-z0-9-]+$', 'Matricule invalide')])
    telephone = models.CharField(max_length=20, validators=[RegexValidator(r'^\+?\d{9,15}$', 'Numéro de téléphone invalide')])
    carte_NIP = models.ImageField(upload_to='photos_carte_NIP/', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])])

    def __str__(self):
        return f"{self.prenom} {self.nom}"

class Demande(models.Model):
    STATUS_CHOICES = [
        ('En attente', 'En attente'),
        ('Traitée', 'Traitée'),
        ('Rejetée', 'Rejetée'),
    ]

    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    types = models.CharField(max_length=20, choices=[('attestation', 'Attestation'), ('diplome', 'Diplôme')])
    date = models.DateField(auto_now_add=True)
    annee_d_obtention = models.CharField(max_length=50, validators=[RegexValidator(r'^\d{4}-\d{4}$', 'Format : AAAA-AAAA')])
    filiere = models.CharField(max_length=50, validators=[RegexValidator(r'^[A-Za-z0-9]{2,}$', 'Filière invalide')])
    quittance = models.FileField(upload_to='quittance/', validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])], blank=True, null=True)
    carte_etudiant = models.FileField(upload_to='carte_etudiant/', validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])], blank=True, null=True)
    accept = models.BooleanField(default=False)
    traitement = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='En attente')
    notified = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.pk:
            old_instance = Demande.objects.get(pk=self.pk)
            if old_instance.status != self.status and not self.notified:
                self.send_notification()
                self.notified = True
        super().save(*args, **kwargs)

    def send_notification(self):
        subject = f'Mise à jour de votre demande de {self.types}'
        message = f"""
        Bonjour {self.etudiant.prenom} {self.etudiant.nom},
        
        Votre demande de {self.types} pour l'année {self.annee_d_obtention} a été mise à jour.
        Statut actuel : {self.status}.
        
        Connectez-vous à la plateforme pour plus de détails : http://localhost:8000/dashboard
        
        Cordialement,
        L'équipe Fast Natitingou
        """
        send_mail(
            subject,
            message,
            'from@example.com',
            [self.etudiant.email],
            fail_silently=False,
        )

    def __str__(self):
        return f"Demande de {self.etudiant} - {self.types}"

class Message(models.Model):
    nom = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    sujet = models.CharField(max_length=100)
    message = models.TextField()

    def __str__(self):
        return f"Message de {self.nom}"

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(max_length=100, unique=True)

    def __str__(self):
        return f"Admin: {self.email}"

class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=2)  # Token valide pendant 2 heures
        super().save(*args, **kwargs)

    def is_valid(self):
        return timezone.now() <= self.expires_at

    def __str__(self):
        return f"Token pour {self.user.email}"