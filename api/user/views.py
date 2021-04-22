from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer

import redis
import uuid
import pycountry
import random
import time

# initiates the redis instance.
redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,
                                  port=settings.REDIS_PORT, db=0)
set_name = settings.REDIS_SET_NAME

# this function is only used while updating a user's info. The function checks
# the incoming data, finds out which fields of the user instance are supposed to be
# updated and returns those fields.
def get_user_fields(data):
    fields = {}
    if 'country' in data.keys():
        fields['country'] = data['country']
    if 'display_name' in data.keys():
        fields['display_name'] = data['display_name']
    return fields    

# this class is responsible for populating the database.
class populate_db(APIView):

    # checks the incoming data, finds out if floor and ceiling values for score 
    # generation are specified. Returns the floor and ceil values.
    def get_score_range(self, request, floor, ceil):

        if request.data['random_score'] == True:
            if 'score_floor' in request.data.keys():
                if request.data['score_floor'].isnumeric():
                    floor = request.data['score_floor']
                else:
                    return Response({'message': 'Wrong score_floor type.'}, status=status.HTTP_400_BAD_REQUEST), 0
            if 'score_ceil' in request.data.keys():
                if request.data['score_ceil'].isnumeric():
                    ceil = request.data['score_ceil']
                else:
                    return Response({'message': 'Wrong score_ceil type.'}, status=status.HTTP_400_BAD_REQUEST), 0
            if floor > ceil:
                return Response({'message': 'Invalid score range.'}, status=status.HTTP_400_BAD_REQUEST), 0
        
        return floor, ceil

    # Returns a random number between floor and ceil values.
    def get_random_score(self, floor, ceil):
        return random.randint(floor, ceil)

    # Trivial function that returns 0.
    def get_zero(self, floor, ceil):
        return 0

    # populates the database.
    def post(self, request):

        start = time.time()
        if 'count' not in request.data.keys():
            return Response({'message': 'Please specify amount of users to create. Use \'count\' field.'}, status=status.HTTP_400_BAD_REQUEST)

        count = request.data['count']
        floor, ceil = self.get_score_range(request, 0, 100000)
        if isinstance(floor, Response):
            return floor

        user_list = []
        pipeline = redis_instance.pipeline()
        countries = list(pycountry.countries)
        get_score = self.get_random_score if request.data['random_score'] else self.get_zero

        # generates random users. Amount is specified in 'count' variable.
        for i in range(count):
            score = get_score(floor, ceil)
            country = random.choice(countries).alpha_2.lower()
            new_user = User(points=score, country=country)
            user_list.append(new_user)
            pipeline.zadd(set_name, {str(new_user.user_id): new_user.points})
            pipeline.zadd(new_user.country, {str(new_user.user_id): new_user.points})

            # redis pipeline is executed and the django database is updated 
            # once in every 10000 entries, in order to speed up the process.
            if (i+1) % 10000 == 0 or i+1 == count:
                print("start of pipeline exec: ", time.time()-start)
                pipeline.execute()
                print("end of pipeline exec: ", time.time()-start)
                pipeline = redis_instance.pipeline()
                print("start of bulk create: ", time.time()-start)
                User.objects.bulk_create(user_list)
                print("end of bulk create: ", time.time()-start)
                user_list.clear()

        
        return Response({'message': 'Users successfully created.'}, status=status.HTTP_201_CREATED)


class user_detail(APIView):

    # Returns the user object with the given user id.
    def get_user(self, id):
        try:
            try:
                uuid_is_valid = uuid.UUID(str(id))
            except ValueError:
                return Response({'message': 'Please provide a valid UUID.'}, status=status.HTTP_400_BAD_REQUEST)
            return User.objects.get(user_id=id)
        except User.DoesNotExist:
            return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, id):
        user = self.get_user(id)
        if isinstance(user, Response):
            return user
        
        # checks the redis database for the current rank and points of the user, 
        # updates the user object in the database afterwards.
        pipeline = redis_instance.pipeline()
        pipeline.zrevrank(set_name, str(id))
        pipeline.zscore(user.country, str(id))
        pipeline.zrevrank(user.country, str(id))
        pipeline_values = pipeline.execute()
        data = {
            'rank': pipeline_values[0]+1,
            'points': pipeline_values[1],
            'country_rank': pipeline_values[2]+1,
            }
        
        # updates the user instance in the database. 
        serializer = UserSerializer(user, data=data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # updates the user info.
    def put(self, request, id):

        if 'display_name' not in request.data.keys() and 'country' not in request.data.keys():
            return Response({'message': 'Please provide either "display_name" or "country" field.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if 'country' in request.data.keys() and not pycountry.countries.get(alpha_2=request.data['country']):
            return Response({'message': 'Invalid country ISO code. Please use ISO 3166-1 alpha-2 codes.'}, status=status.HTTP_400_BAD_REQUEST)

        user = self.get_user(id)
        data = get_user_fields(request.data)
        if 'country' in data.keys():
            pipeline = redis_instance.pipeline()
            pipeline.zrem(user.country, id)
            pipeline.zadd(data.country, {id: user.points})
            pipeline.execute()

        serializer = UserSerializer(user, data=data, context={'request': request}, partial=True)
            

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # deletes the user from the database as well as from the redis tables.
    def delete(self, request, id):
        user = self.get_user(id)
        if isinstance(user, Response):
            return user
        pipeline = redis_instance.pipeline()
        pipeline.zrem(user.country, str(id))
        pipeline.zrem(set_name, str(id))
        pipeline.execute()
        redis_instance.save()
        user.delete()
        return Response({'message': 'User successfully deleted.'}, status=status.HTTP_204_NO_CONTENT)


# creates the user instances.
class create_user(APIView):

    def post(self, request):

        if 'country' in request.data.keys() and not pycountry.countries.get(alpha_2=request.data['country']):
            return Response({'message': 'Invalid country ISO code. Please use ISO 3166-1 alpha-2 codes.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_user_fields(request.data)
        serializer = UserSerializer(data=data)

        # adds the user instance to redis tables.
        if serializer.is_valid():
            serializer.save()
            start = time.time()
            pipeline = redis_instance.pipeline()
            pipeline.zadd(serializer.data['country'], {serializer.data['user_id']: 0})
            pipeline.zadd(set_name, {serializer.data['user_id']: 0})
            pipeline.execute()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# returns all users in the database. Usage is not recommended if there are 
# large number of entries in the database. 
class all_users(APIView):

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        print("type: ", type(serializer.data))
        print("serializer data: ", serializer.data)

        return Response(serializer.data, status.HTTP_200_OK)
    
    # deletes all users from the database as well as from the redis tables. 
    # It is a secure way of cleaning the database.
    def delete(self, request):
        User.objects.all().delete()
        redis_instance.flushall()
        redis_instance.save()
        return Response({'message': 'All users successfully deleted.'}, status.HTTP_200_OK)

