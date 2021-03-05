from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from user.models import User
from user.serializers import UserSerializer


class submit_score(APIView):

    def get_user(self, id):
        try:
            return User.objects.get(user_id=id)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

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

        new_points = user.points + int(data['score_worth'])
        score = {"points": new_points}
        serializer = UserSerializer(user, data=score, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



