from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from user.models import User
from user.serializers import UserSerializer

import redis
import uuid
import pycountry

redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
set_name = settings.REDIS_SET_NAME

def get_top_50(country, size):

    top_50 = redis_instance.zrevrange(country, 0, size-1, withscores=True)
    IDs = []
    points = []
    for i in range(len(top_50)):
        ID_str = top_50[i][0].decode('utf-8')
        IDs.append(uuid.UUID(ID_str))
        points.append(top_50[i][1])
    return IDs, points

def get_ranking(users, ID_list, is_global_ranking):
    
    pipeline = redis_instance.pipeline()
    for user_id in ID_list:
        user = users.get(user_id=user_id)
        pipeline.zrevrank(set_name if is_global_ranking else user.country, str(user_id))
    pipeline_values = pipeline.execute()
    return pipeline_values

class global_leaderboard(APIView):

    def get(self, request):

        leaderboard_size = 50
        IDs, points = get_top_50(set_name, leaderboard_size)
        users = User.objects.filter(user_id__in=IDs)
        country_ranks = get_ranking(users, IDs, False)
        
        for user in users:
            user_index = IDs.index(user.user_id)
            user.rank = user_index+1
            user.points = points[user_index]
            user.country_rank = country_ranks[user_index]+1

        User.objects.bulk_update(users, ['points', 'rank', 'country_rank'])
        serializer = UserSerializer(users, many=True)
        data = list(serializer.data)
        data.reverse()
        return Response(data, status=status.HTTP_200_OK)


class country_leaderboard(APIView):

    def get(self, request, country):

        if not pycountry.countries.get(alpha_2=country):
            return Response({'message': 'Invalid country ISO code. Please use ISO 3166-1 alpha-2 codes.'}, status=status.HTTP_400_BAD_REQUEST)

        leaderboard_size = 50
        IDs, points = get_top_50(country, leaderboard_size)
        users = User.objects.filter(user_id__in=IDs)
        global_ranks = get_ranking(users, IDs, True)

        for user in users:
            user_index = IDs.index(user.user_id)
            user.country_rank = user_index+1
            user.points = points[user_index]
            user.rank = global_ranks[user_index]+1

        User.objects.bulk_update(users, ['points', 'rank', 'country_rank'])
        serializer = UserSerializer(users, many=True)
        data = list(serializer.data)
        data.reverse()
        return Response(data, status=status.HTTP_200_OK)