import datetime
from pickle import TRUE
import jwt
import re

from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import User
from .serializer import UserSerializer


class UserRegisterView(APIView):
    def post(self, request):
        try:
            if 'email' in request.data:
                email = request.data['email'].lower().strip()
                if User.objects.filter(email=email).exists():
                    return Response(
                        {'error': 'This email is already registered'},
                        status=status.HTTP_409_CONFLICT
                    )
                
                # Handle date_of_birth formatting
                if 'date_of_birth' in request.data and request.data['date_of_birth']:
                    try:
                        # Parse date_of_birth in whatever format it comes in
                        dob_string = request.data['date_of_birth']
                        
                        # Try different date formats
                        import datetime
                        date_formats = [
                            '%Y-%m-%d',      # 1999-06-21
                            '%d-%m-%Y',      # 21-06-1999
                            '%m-%d-%Y',      # 06-21-1999
                            '%d/%m/%Y',      # 21/06/1999
                            '%m/%d/%Y',      # 06/21/1999
                            '%d.%m.%Y',      # 21.06.1999
                            '%Y/%m/%d',      # 1999/06/21
                        ]
                        
                        parsed_date = None
                        for date_format in date_formats:
                            try:
                                parsed_date = datetime.datetime.strptime(dob_string, date_format).date()
                                break
                            except ValueError:
                                continue
                        
                        if parsed_date:
                            # Convert to YYYY-MM-DD format
                            request.data['date_of_birth'] = parsed_date.strftime('%Y-%m-%d')
                        else:
                            return Response({'error': 'Invalid date format for date_of_birth'}, 
                                           status=status.HTTP_400_BAD_REQUEST)
                    except Exception as e:
                        return Response({'error': f'Error processing date_of_birth: {str(e)}'}, 
                                       status=status.HTTP_400_BAD_REQUEST)
                
                # Allow partial updates
                serializer = UserSerializer(data=request.data, partial=True)
                if serializer.is_valid():
                    user = serializer.save()
                    user.is_active = True
                    user.save()
                    return Response({'message': "Registration successful"}, status=status.HTTP_201_CREATED)
                else:
                    # Return validation errors without raising exceptions
                    return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



class LoginUserView(APIView):
    def post(self, request):
        
        if 'email' not in request.data or 'password' not in request.data:
            return Response({'message': 'Both email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            return Response({'message': 'User not found'},status=status.HTTP_404_NOT_FOUND)

        if not user.check_password(password):
            return Response({'message': 'Incorrect password.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        tokens = user.token() 

        response = Response()
        response.set_cookie(key='jwt', value=tokens['access'], httponly=True)
        response.data = {
            'message': 'Success',
            'access_token': tokens['access'],
            'refresh_token': tokens['refresh']
        }
        return response
    

class ViewProfile(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # If the user is authenticated, request.user contains the authenticated user instance
            user = request.user
            serializer = UserSerializer(user)
            response_data = {
                'username': serializer.data['first_name'],
            }
            return Response(response_data)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

class LogoutView(APIView):
    def post(self,request):
        response =Response()
        response.delete_cookie('jwt')
        response.data={
            'message':'Logout Success'
        }
        
        return response