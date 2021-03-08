from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer
import uuid
import pycountry

def get_user_fields(data):
    fields = {}
    if 'country' in data.keys():
        fields['country'] = data['country']
    if 'display_name' in data.keys():
        fields['display_name'] = data['display_name']
    return fields    

class user_detail(APIView):

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
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request, id):

        if 'display_name' not in request.data.keys() and 'country' not in request.data.keys():
            return Response({'message': 'Please provide either "display_name" or "country" field.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if 'country' in request.data.keys() and not pycountry.countries.get(alpha_2=request.data['country']):
            return Response({'message': 'Invalid country ISO code. Please use ISO 3166-1 alpha-2 codes.'}, status=status.HTTP_400_BAD_REQUEST)

        user = self.get_user(id)
        data = get_user_fields(request.data)
        serializer = UserSerializer(user, data=data, context={'request': request}, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        user = self.get_user(id)
        if isinstance(user, Response):
            return user
        user.delete()
        return Response({'message': 'User successfully deleted.'}, status=status.HTTP_204_NO_CONTENT)



class create_user(APIView):

    def post(self, request):

        if 'country' in request.data.keys() and not pycountry.countries.get(alpha_2=request.data['country']):
            return Response({'message': 'Invalid country ISO code. Please use ISO 3166-1 alpha-2 codes.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_user_fields(request.data)
        serializer = UserSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class all_users(APIView):

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status.HTTP_200_OK)
    
    def delete(self, request):
        User.objects.all().delete()
        return Response({'message': 'All users successfully deleted.'}, status.HTTP_200_OK)

