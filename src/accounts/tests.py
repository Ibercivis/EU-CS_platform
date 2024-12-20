from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

class DeleteAccountTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="testuser@email.com",
            password='testpassword',
            name='testuser'
        )
        self.user.is_active = True
        self.user.save()

        self.url = reverse('accounts:delete_account')
        self.client.login(email='testuser@email.com', password='testpassword')

    def test_get_request(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/delete_account.html")
    
    def test_post_with_wrong_password(self):
        response = self.client.post(self.url, {'password': 'wrongpassword'})

        self.assertTrue(get_user_model().objects.filter(id=self.user.id).exists())

        self.assertContains(response, 'Incorrect password')
    
    def test_post_with_correct_password(self):
        reponse = self.client.post(self.url, {'password': 'testpassword'})

        self.assertFalse(get_user_model().objects.filter(id=self.user.id).exists())

        self.assertEqual(reponse.status_code, 202)