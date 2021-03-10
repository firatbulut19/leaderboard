from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from user.models import User
from user.serializers import UserSerializer
import uuid

client = Client()

class SubmitScoreTest(TestCase):

    def setUp(self):
        self.firat = User.objects.create(display_name='firat')
        self.faruk = User.objects.create(display_name='faruk')
    
    def test_submit_score_valid(self):
        data = {
            'user_id': self.firat.user_id,
            'score_worth': 15,
        }
        response = client.post('/score/submit/', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_submit_invalid_score(self):
        data = {
            'user_id': self.faruk.user_id,
            'score_worth': 'asd',
        }
        response = client.post('/score/submit/', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_submit_invalid_user(self):
        data = {
            'user_id': uuid.uuid4(),
            'score_worth': 15,
        }
        response = client.post('/score/submit/', data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        