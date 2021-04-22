from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from user.models import User
from user.serializers import UserSerializer
import redis
import uuid

# initializes the redis instance.
redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,
                                  port=settings.REDIS_PORT, db=0)

set_name = settings.REDIS_SET_NAME


class submit_score(APIView):

    # returns the user with the given user id.
    def get_user(self, id):
        try:
            try:
                uuid_is_valid = uuid.UUID(str(id))
            except ValueError:
                return Response({"message": "Please provide a valid UUID."}, status=status.HTTP_400_BAD_REQUEST)
            return User.objects.get(user_id=id)
        except User.DoesNotExist:
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    # submits the score.
    def post(self, request):

        data = request.data
        user = self.get_user(data['user_id'])
        if isinstance(user, Response):
            return user

        try: 
            int(data['score_worth'])
        except ValueError:
            return Response({'message': 'Invalid score type.'}, status=status.HTTP_400_BAD_REQUEST)

        if int(data['score_worth']) < 0:
            return Response({'message': 'Score can not be a negative number.'}, status=status.HTTP_400_BAD_REQUEST)

        # first submits the score, then calculates the new rank of the user 
        # and returns the updates values of the user.
        pipeline = redis_instance.pipeline()
        pipeline.zadd(set_name, {data['user_id']: data['score_worth']}, incr=True)
        pipeline.zrevrank(set_name, data['user_id'])
        pipeline.zadd(user.country, {data['user_id']: data['score_worth']}, incr=True)
        pipeline.zrevrank(user.country, data['user_id'])
        pipeline.zscore(user.country, data['user_id'])
        pipeline_values = pipeline.execute()
        data = {
            'rank': int(pipeline_values[1])+1,
            'points': int(pipeline_values[4]),
            'country_rank': int(pipeline_values[3])+1,
            }
        
        # saves the updated rank and score of the user to the database.
        serializer = UserSerializer(user, data=data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



