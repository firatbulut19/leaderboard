from django.test import TestCase
from ..models import User


class UserTest(TestCase):

    def setUp(self):
        User.objects.create(
            display_name='firat')
        User.objects.create(
            display_name='faruk', points=15)

    def test_user_points(self):
        user_firat = User.objects.get(display_name='firat')
        user_faruk = User.objects.get(display_name='faruk')
        self.assertEqual(
            user_firat.get_points(), "firat has 0 points.")
        self.assertEqual(
            user_faruk.get_points(), "faruk has 15 points.")

    def test_user_rank(self):
        user_firat = User.objects.get(display_name='firat')
        user_faruk = User.objects.get(display_name='faruk')  
        self.assertEqual(
            user_firat.get_rank(), "firat is rank 0.")
        self.assertEqual(
            user_faruk.get_rank(), "faruk is rank 0.")
        