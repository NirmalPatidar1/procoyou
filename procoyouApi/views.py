import random
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from .models import *
from rest_framework import generics

User = get_user_model()

# Helper function to generate OTP
def generate_otp():
    return str(random.randint(1000, 9999))

# User Signup
class UserSignupView(APIView):
    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            otp = generate_otp()
            user.otp = otp
            user.save()
            # Send OTP via SMS (Integration required)
            return Response({"message": "OTP sent to mobile", "otp": otp})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# OTP Verification
class OTPVerificationView(APIView):
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            mobile_number = serializer.validated_data['mobile_number']
            otp = serializer.validated_data['otp']
            try:
                user = User.objects.get(mobile_number=mobile_number, otp=otp)
                user.otp = None  # Clear OTP after successful verification
                user.save()
                
                # Generate JWT Token
                refresh = RefreshToken.for_user(user)
                return Response({
                    "message": "OTP verified successfully",
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh)
                })
            except User.DoesNotExist:
                return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# User Login
class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            mobile_number = serializer.validated_data['mobile_number']
            try:
                user = User.objects.get(mobile_number=mobile_number)
                otp = generate_otp()
                user.otp = otp
                user.save()
                # Send OTP via SMS (Integration required)
                return Response({"message": "OTP sent to mobile", "otp": otp})
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# User Info
class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]  
    def get(self, request):
        user = request.user
        serializer = UserInfoSerializer(user)
        return Response(serializer.data)
    
# User profile image upload
class ProfileImageUploadView(APIView):
    permission_classes = [IsAuthenticated]  
    parser_classes = [MultiPartParser, FormParser]  

    def post(self, request):
        user = request.user
        serializer = ProfileImageUploadSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile image updated successfully", "profile_image": user.profile_image.url})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PropertyCreateView(generics.CreateAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    parser_classes = (MultiPartParser, FormParser)  # Ensures file uploads are parsed

    def post(self, request, *args, **kwargs):
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            property_instance = serializer.save()
            return Response({"message": "Property created successfully!", "property": PropertySerializer(property_instance).data}, status=201)
        return Response(serializer.errors, status=400)

class PropertyListView(generics.ListAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer