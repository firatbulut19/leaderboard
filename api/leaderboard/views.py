from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from user.models import User
from user.serializers import UserSerializer

import uuid
import pycountry

leaderboard_size = 5

class global_leaderboard(APIView):

    def get(self, request):

        top_users = User.objects.order_by('-points')[:leaderboard_size]
        serializer = UserSerializer(top_users, many=True)
        return Response(serializer.data)


class country_leaderboard(APIView):

    def get(self, request, country):

        if not pycountry.countries.get(alpha_2=country):
            return Response({'message': 'Invalid country ISO code. Please use ISO 3166-1 alpha-2 codes.'}, status=status.HTTP_400_BAD_REQUEST)

        top_users = User.objects.filter(country=country).order_by('-points')[:leaderboard_size]
        serializer = UserSerializer(top_users, many=True)
        return Response(serializer.data)