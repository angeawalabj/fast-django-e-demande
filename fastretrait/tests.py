from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail
from .models import Etudiant, Demande, Admin, PasswordResetToken
import uuid
from django.test.utils import override_settings

class FastRetraitTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {
            'email': 'test@example.com',
            'password': 'password123',
            'nom': 'Test',
            'prenom': 'User',
            'matricule': 'TEST123',
            'phone': '+22912345678',
        }
        self.admin_user = User.objects.create_user(
            username='admin@example.com',
            email='admin@example.com',
            password='adminpass'
        )
        Admin.objects.create(user=self.admin_user, email='admin@example.com')
        self.user = User.objects.create_user(
            username=self.user_data['email'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        self.etudiant = Etudiant.objects.create(
            user=self.user,
            nom=self.user_data['nom'],
            prenom=self.user_data['prenom'],
            email=self.user_data['email'],
            matricule=self.user_data['matricule'],
            telephone=self.user_data['phone'],
            carte_NIP='test.jpg'
        )

    def test_register_success(self):
        response = self.client.post(reverse('inscription'), {
            'nom': 'New',
            'prenom': 'User',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'repassword': 'newpass123',
            'matricule': 'NEW123',
            'phone': '+22987654321',
            'id_card': self._create_test_file('test.jpg')
        })
        self.assertRedirects(response, reverse('connecter'))
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())
        self.assertTrue(Etudiant.objects.filter(matricule='NEW123').exists())

    def test_register_invalid_email(self):
        response = self.client.post(reverse('inscription'), {
            'nom': self.user_data['nom'],
            'prenom': self.user_data['prenom'],
            'email': 'invalid_email',
            'password': self.user_data['password'],
            'repassword': self.user_data['password'],
            'matricule': 'NEW456',
            'phone': self.user_data['phone'],
            'id_card': self._create_test_file('test.jpg')
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Adresse e-mail invalide')

    @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
    def test_login_success(self):
        response = self.client.post(reverse('connecter'), {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        })
        self.assertRedirects(response, reverse('dashboard'))

    @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
    def test_login_invalid_credentials(self):
        response = self.client.post(reverse('connecter'), {
            'email': self.user_data['email'],
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nom d\'utilisateur ou mot de passe incorrect')

    @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
    def test_create_demande(self):
        self.client.login(username=self.user_data['email'], password=self.user_data['password'])
        response = self.client.post(reverse('demande'), {
            'type_document': 'attestation',
            'filiere': 'MI2',
            'obtention': '2022-2023',
            'quittance': self._create_test_file('quittance.pdf')
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(Demande.objects.filter(etudiant=self.etudiant, types='attestation').exists())

    @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
    def test_admin_dashboard_access(self):
        self.client.login(username='admin@example.com', password='adminpass')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)

    @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
    def test_admin_dashboard_no_access(self):
        self.client.login(username=self.user_data['email'], password=self.user_data['password'])
        response = self.client.get(reverse('admin_dashboard'))
        self.assertRedirects(response, reverse('connecter'))

    def test_password_reset_request(self):
        response = self.client.post(reverse('recuperation'), {
            'email': self.user_data['email']
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Un email de récupération a été envoyé')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Réinitialisation de votre mot de passe', mail.outbox[0].subject)

    def test_password_reset_valid_token(self):
        token = PasswordResetToken.objects.create(user=self.user)
        response = self.client.post(reverse('reset_password', args=[token.token]), {
            'password': 'newpass123',
            'repassword': 'newpass123'
        })
        self.assertRedirects(response, reverse('connecter'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass123'))

    def test_password_reset_invalid_token(self):
        response = self.client.get(reverse('reset_password', args=[uuid.uuid4()]))
        self.assertRedirects(response, reverse('connecter'))

    def _create_test_file(self, filename):
        from io import BytesIO
        from django.core.files.uploadedfile import SimpleUploadedFile
        content = b'Test content'
        return SimpleUploadedFile(filename, content)