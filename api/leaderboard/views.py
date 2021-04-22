from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from user.models import User
from user.serializers import UserSerializer

import redis
import uuid
import pycountry

# initiates the redis instance.
redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
set_name = settings.REDIS_SET_NAME

# returns the top 50 users of the corresponding redis table. 
def get_top_users(country, size):

    top_users = redis_instance.zrevrange(country, 0, size-1, withscores=True)
    IDs = []
    points = []
    for i in range(len(top_users)):
        ID_str = top_users[i][0].decode('utf-8')
        IDs.append(uuid.UUID(ID_str))
        points.append(top_users[i][1])
    return IDs, points

# Returns the individual country ranks of top users if the user requested global 
# leaderboard, and returns the global ranks of the top users if the user requested
# country leaderboard.
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
        # gets the IDs and points of the top 50 users globally. 
        IDs, points = get_top_users(set_name, leaderboard_size)
        users = User.objects.filter(user_id__in=IDs)
        # gets the individual country ranks of those users, stores them in 'country_ranks'
        # variable.
        country_ranks = get_ranking(users, IDs, False)
        
        # creates a list of users to be updated in the database. This list contains 
        # the most up to date values of those users, freshly received from the redis 
        # table. 
        for user in users:
            user_index = IDs.index(user.user_id)
            user.rank = user_index+1
            user.points = points[user_index]
            user.country_rank = country_ranks[user_index]+1

        # updates the values of those users in the database.
        User.objects.bulk_update(users, ['points', 'rank', 'country_rank'])
        serializer = UserSerializer(users, many=True)
        data = list(serializer.data)
        data.reverse()
        return Response(data, status=status.HTTP_200_OK)


# Follows a similar procedure to the global leaderboard class.
class country_leaderboard(APIView):

    def get(self, request, country):

        if not pycountry.countries.get(alpha_2=country):
            return Response({'message': 'Invalid country ISO code. Please use ISO 3166-1 alpha-2 codes.'}, status=status.HTTP_400_BAD_REQUEST)

        leaderboard_size = 50
        IDs, points = get_top_users(country, leaderboard_size)
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