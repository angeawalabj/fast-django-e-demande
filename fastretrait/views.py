from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.contrib import messages
import re
from .models import Etudiant, Demande, Message, Admin, PasswordResetToken
from uuid import UUID
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string

def inscription(request):
    erreur = False
    message = ''
    if request.method == 'POST':
        nom = request.POST.get('nom', '').strip().upper()
        prenoms = request.POST.get('prenom', '').strip().title()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        repassword = request.POST.get('repassword', '')
        matricule = request.POST.get('matricule', '').strip().upper()
        telephone = request.POST.get('phone', '').strip()
        carte = request.FILES.get('id_card', None)

        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            erreur = True
            message = 'Adresse e-mail invalide'
        elif User.objects.filter(username=email).exists():
            erreur = True
            message = 'Cet email est déjà utilisé'
        elif Etudiant.objects.filter(matricule=matricule).exists():
            erreur = True
            message = 'Ce matricule est déjà utilisé'
        elif password != repassword:
            erreur = True
            message = 'Les mots de passe ne correspondent pas'
        elif len(password) < 6:
            erreur = True
            message = 'Le mot de passe doit contenir au moins 6 caractères'
        elif not carte:
            erreur = True
            message = 'La carte d\'identité est requise'
        else:
            try:
                user = User.objects.create_user(username=email, email=email, password=password)
                etudiant = Etudiant(
                    user=user,
                    nom=nom,
                    prenom=prenoms,
                    email=email,
                    telephone=telephone,
                    carte_NIP=carte,
                    matricule=matricule
                )
                etudiant.full_clean()
                etudiant.save()
                messages.success(request, 'Inscription réussie. Veuillez vous connecter.')
                return redirect('connecter')
            except ValidationError as e:
                erreur = True
                message = str(e)
    context = {'message': message, 'erreur': erreur}
    return render(request, 'register.html', context)

def connexion(request):
    context = {}
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect")
            context['error'] = True
    return render(request, 'login.html', context)

@login_required(login_url='connecter')
def dashboard(request):
    etudiant = get_object_or_404(Etudiant, user=request.user)
    demandes_list = Demande.objects.filter(etudiant=etudiant).order_by('-date')
    paginator = Paginator(demandes_list, 5)
    page_number = request.GET.get('page')
    demandes = paginator.get_page(page_number)
    context = {'etudiant': etudiant, 'demandes': demandes}
    return render(request, 'dashboard.html', context)

@login_required(login_url='connecter')
def admin_dashboard(request):
    if not Admin.objects.filter(user=request.user).exists():
        messages.error(request, 'Accès non autorisé.')
        return redirect('connecter')
    demandes_list = Demande.objects.all().order_by('-date')
    paginator = Paginator(demandes_list, 10)
    page_number = request.GET.get('page')
    demandes = paginator.get_page(page_number)
    context = {'demandes': demandes}
    return render(request, 'admin_dashboard.html', context)

@login_required(login_url='connecter')
def manage_demande(request, demande_id):
    if not Admin.objects.filter(user=request.user).exists():
        messages.error(request, 'Accès non autorisé.')
        return redirect('connecter')
    demande = get_object_or_404(Demande, id=demande_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'accepter':
            demande.accept = True
            demande.traitement = True
            demande.status = 'Traitée'
        elif action == 'rejeter':
            demande.accept = False
            demande.traitement = True
            demande.status = 'Rejetée'
        demande.save()
        messages.success(request, f'Demande {demande.status} avec succès.')
        return redirect('admin_dashboard')
    context = {'demande': demande}
    return render(request, 'manage_demande.html', context)

@login_required(login_url='connecter')
def demande(request):
    etudiant = get_object_or_404(Etudiant, user=request.user)
    if request.method == 'POST':
        types = request.POST.get('type_document')
        annee_d_obtention = request.POST.get('obtention')
        filiere = request.POST.get('filiere')
        quittance = request.FILES.get('quittance', None)
        carte_etudiant = request.FILES.get('carte_et', None)

        if types not in ['attestation', 'diplome']:
            return render(request, 'demande.html', {'etudiant': etudiant, 'erreur': 'Type de document invalide'})
        if not re.match(r'^\d{4}-\d{4}$', annee_d_obtention):
            return render(request, 'demande.html', {'etudiant': etudiant, 'erreur': 'Année d\'obtention invalide (ex. 2022-2023)'})
        if not re.match(r'^[A-Za-z0-9]{2,}$', filiere):
            return render(request, 'demande.html', {'etudiant': etudiant, 'erreur': 'Filière invalide'})

        dem = Demande(
            etudiant=etudiant,
            types=types,
            annee_d_obtention=annee_d_obtention,
            filiere=filiere,
            quittance=quittance,
            carte_etudiant=carte_etudiant
        )
        dem.full_clean()
        dem.save()
        messages.success(request, 'Demande envoyée avec succès.')
        return redirect('dashboard')
    return render(request, 'demande.html', {'etudiant': etudiant})

def contact(request):
    ok = False
    message = ''
    if request.method == 'POST':
        nom = request.POST.get('nom', '').strip()
        email = request.POST.get('email', '').strip()
        sujet = request.POST.get('sujet', '').strip()
        message_text = request.POST.get('message', '').strip()

        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            message = 'Adresse e-mail invalide'
        elif not nom or not sujet or not message_text:
            message = 'Tous les champs sont requis'
        else:
            contact = Message(nom=nom, email=email, sujet=sujet, message=message_text)
            contact.full_clean()
            contact.save()
            ok = True
            message = 'Message envoyé avec succès'
    context = {'ok': ok, 'message': message}
    return render(request, 'contact.html', context)


def recuperation(request):
    erreur = False
    message = ''
    ok = False
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        user = User.objects.filter(email=email).first()
        if user:
            token = PasswordResetToken.objects.create(
                user=user,
                expires_at=timezone.now() + timedelta(hours=1)
            )
            reset_link = f"http://{request.get_host()}/reset/{token.token}/"
            email_body = render_to_string('reset_password_email.html', {
                'user': user,
                'reset_link': reset_link,
            })
            send_mail(
                subject='Réinitialisation de votre mot de passe',
                message='',
                from_email='from@example.com',  # Remplace par DEFAULT_FROM_EMAIL
                recipient_list=[email],
                html_message=email_body,
                fail_silently=False,
            )
            message = 'Un email de récupération a été envoyé.'
            ok = True
        else:
            erreur = True
            message = 'Aucun utilisateur trouvé avec cet email.'
    context = {'erreur': erreur, 'message': message, 'ok': ok}
    return render(request, 'recuperation.html', context)

def log_out(request):
    logout(request)
    messages.success(request, 'Déconnexion réussie.')
    return redirect('connecter')

def profil(request):
    etudiant = get_object_or_404(Etudiant, user=request.user)
    context = {'etudiant': etudiant}
    return render(request, 'profil.html', context)

def home(request):
    return render(request, 'accueil.html')

def reset_password(request, token):
    try:
        token_obj = PasswordResetToken.objects.get(token=token)
        if not token_obj.is_valid():
            messages.error(request, 'Ce lien de réinitialisation est expiré.')
            return redirect('connecter')
    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Lien de réinitialisation invalide.')
        return redirect('connecter')

    if request.method == 'POST':
        password = request.POST.get('password')
        repassword = request.POST.get('repassword')
        if password != repassword:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
        elif len(password) < 6:
            messages.error(request, 'Le mot de passe doit contenir au moins 6 caractères.')
        else:
            user = token_obj.user
            user.set_password(password)
            user.save()
            token_obj.delete()
            messages.success(request, 'Mot de passe réinitialisé avec succès. Veuillez vous connecter.')
            return redirect('connecter')
    return render(request, 'reset_password.html', {'token': token})