from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from user.models import User
from user.serializers import UserSerializer
import time

client = Client()

class SubmitScoreTest(TestCase):

    def setUp(self):
        self.firat = User.objects.create(display_name='firat')
        self.faruk = User.objects.create(display_name='faruk')

    # test case doesnt work.
    '''
    def test_submit_score_valid(self):
        data = {
            'user_id': self.firat.user_id,
            'score_worth': 15,
        }
        response = client.post('/score/submit/', data=data)
        self.assertEqual(self.firat.get_points(), "firat has 15 points.")
    '''
    def test_submit_score_invalid(self):
        data = {
            'user_id': self.faruk.user_id,
            'score_worth': 'asd',
        }
        response = client.post('/score/submit/', data=data)
        self.assertEqual(self.faruk.get_points(), "faruk has 0 points.")
        