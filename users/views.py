import datetime
from rest_framework import status, generics, filters
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .models import User
from .serializer import UserSerializer, UserUpdateSerializer
from dateutil import parser as date_parser
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from .serializer import PasswordResetRequestSerializer, PasswordResetSerializer
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class UserRegisterView(generics.CreateAPIView):
    """
    API view for user registration. No authentication required.
    """
    permission_classes = [AllowAny]
    serializer_class = UserSerializer
    
    @swagger_auto_schema(
        operation_description="Register a new user",
        request_body=UserSerializer,
        responses={
            201: openapi.Response(
                description="Created - Registration successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: "Bad Request",
            409: "Conflict - Email already registered"
        },
        tags=['Authentication'],
        operation_summary="Register a new user"
    )
    def post(self, request):
        try:
            if 'email' in request.data:
                email = request.data['email'].lower().strip()
                if User.objects.filter(email=email).exists():
                    return Response(
                        {'error': 'This email is already registered'},
                        status=status.HTTP_409_CONFLICT
                    )
                
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
    """
    API view for user login. No authentication required.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Log in a user and return authentication tokens",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
                'password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD),
            }
        ),
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'email': openapi.Schema(type=openapi.TYPE_STRING),
                        'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'access_token': openapi.Schema(type=openapi.TYPE_STRING),
                        'refresh_token': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: "Bad Request - Missing email or password",
            401: "Unauthorized - Incorrect password",
            404: "Not Found - User not found"
        },
        tags=['Authentication'],
        operation_summary="Log in a user"
    )
    def post(self, request):
        if 'email' not in request.data or 'password' not in request.data:
            return Response({'message': 'Both email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if not user.check_password(password):
            return Response({'message': 'Incorrect password.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        tokens = user.token() 

        response = Response()
        response.set_cookie(key='jwt', value=tokens['access'], httponly=True)
        response.data = {
            'message': 'Success',
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'access_token': tokens['access'],
            'refresh_token': tokens['refresh']
        }
        return response


class UserListView(generics.ListAPIView):
    """
    API view for admin to list all users. Admin authentication required.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'first_name', 'last_name', 'phone_number']
    ordering_fields = ['id', 'email', 'first_name', 'last_name', 'date_joined']
    ordering = ['id']
    
    @swagger_auto_schema(
        operation_description="List all users. Only accessible by admin users.",
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, 
                              description="Search in email, first_name, last_name, phone_number", 
                              type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, 
                              description="Order by field (prefix with - for descending)", 
                              type=openapi.TYPE_STRING),
        ],
        responses={
            200: UserSerializer(many=True),
            401: "Unauthorized - Authentication credentials not provided",
            403: "Forbidden - Not an admin user"
        },
        tags=['User Management'],
        operation_summary="List all users (Admin only)",
 
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class UserDetailView(generics.RetrieveAPIView):
    """
    API view to retrieve a specific user's details.
    Admin can access any user, regular users can only access their own profile.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    
    @swagger_auto_schema(
        operation_description="Get specific user details. Admin can access any user, regular users can only access their own profile.",
        responses={
            200: UserSerializer(),
            401: "Unauthorized - Authentication credentials not provided",
            403: "Forbidden - Not authorized to view this profile",
            404: "Not Found - User not found"
        },
        tags=['User Management'],
        operation_summary="Get user details"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_object(self):
        user_id = self.kwargs.get('pk')
        user = get_object_or_404(User, pk=user_id)
        
        # Check if the requesting user has permission to view this profile
        if self.request.user.is_staff or self.request.user.id == user.id:
            return user
        else:
            raise PermissionDenied("You don't have permission to access this profile")


class UserProfileView(APIView):
    """
    API view for authenticated users to view their own profile.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Get the authenticated user's profile information",
        responses={
            200: UserSerializer(),
            401: "Unauthorized - Authentication credentials not provided"
        },
        tags=['User Profile'],
        operation_summary="View own profile"
    )
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)


class UserUpdateView(generics.UpdateAPIView):
    """
    API view for users to update their profile.
    Admin can update any user, regular users can only update their own profile.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserUpdateSerializer
    queryset = User.objects.all()
    
    def get_object(self):
        user_id = self.kwargs.get('pk')
        user = get_object_or_404(User, pk=user_id)
        
        # Check if the requesting user has permission to update this profile
        if self.request.user.is_staff or self.request.user.id == user.id:
            return user
        else:
            raise PermissionDenied("You don't have permission to update this profile")
    
    @swagger_auto_schema(
        operation_description="Update a user profile. Admin can update any user, regular users can only update their own profile.",
        request_body=UserUpdateSerializer,
        responses={
            200: UserUpdateSerializer,
            400: "Bad Request - Validation error",
            401: "Unauthorized - Authentication credentials not provided",
            403: "Forbidden - Not authorized to update this profile",
            404: "Not Found - User not found"
        },
        tags=['User Profile'],
        operation_summary="Update user profile"
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Partially update a user profile. Admin can update any user, regular users can only update their own profile.",
        request_body=UserUpdateSerializer,
        responses={
            200: UserUpdateSerializer,
            400: "Bad Request - Validation error",
            401: "Unauthorized - Authentication credentials not provided", 
            403: "Forbidden - Not authorized to update this profile",
            404: "Not Found - User not found"
        },
        tags=['User Profile'],
        operation_summary="Partially update user profile"
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    API view for user logout.
    """
    @swagger_auto_schema(
        operation_description="Logout a user by removing their JWT cookie",
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        },
        tags=['Authentication'],
        operation_summary="Logout"
    )
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'Logout Success'
        }
        return response


class PasswordResetRequestView(APIView):
    """
    API view for requesting a password reset. No authentication required.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Request a password reset email",
        request_body=PasswordResetRequestSerializer,
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: "Bad Request - Email not found or invalid"
        },
        tags=['Password Management'],
        operation_summary="Request password reset"
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            
            # Generate token and uid
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Construct reset URL
            reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"
            
            # Send email
            send_mail(
                subject='Password Reset Request',
                message=f'Click the link to reset your password: {reset_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            
            return Response(
                {"message": "Password reset email has been sent"},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """
    API view for confirming password reset. No authentication required.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Confirm password reset with token and set new password",
        request_body=PasswordResetSerializer,
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: "Bad Request - Invalid token or uidb64"
        },
        tags=['Password Management'],
        operation_summary="Confirm password reset"
    )
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Password has been reset successfully"},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)