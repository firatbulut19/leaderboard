import json
import uuid

from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from ..models import User
from ..serializers import UserSerializer


# initialize the APIClient app
client = Client()

class UserTest(TestCase):

    def setUp(self):
        self.ahmet = User.objects.create(display_name='Ahmet')
        self.can = User.objects.create(display_name='Can')
        self.selin = User.objects.create(display_name='Selin')
        self.zeynep = User.objects.create(display_name='Zeynep')

    def test_get_all_users(self):
        response = client.get(reverse('get-users'))
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_single_user_valid(self):
        response = client.get('/user/profile/{}/'.format(self.selin.user_id))
        user_selin = User.objects.get(user_id=self.selin.user_id)
        serializer = UserSerializer(user_selin)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_single_user_invalid(self):
        response = client.get('/user/profile/{}/'.format(uuid.uuid4()))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_create_valid_user(self):
        response = client.post('/user/create/', {"display_name": "faruk"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_user(self):
        response = client.post('/user/create/', {"display_name": ""})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_valid(self):
        response = client.put('/user/profile/{}/'.format(self.can.user_id), data=json.dumps({"display_name": "firat"}), content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_user_invalid(self):
        response = client.put('/user/profile/{}/'.format(self.can.user_id), data=json.dumps({"display_name": ""}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_delete_user_valid(self):
        response = client.delete('/user/profile/{}/'.format(self.zeynep.user_id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_user_invalid(self):
        response = client.delete('/user/profile/{}/'.format(uuid.uuid4()))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        