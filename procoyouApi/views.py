import random
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from .models import *
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from geopy.distance import geodesic

User = get_user_model()

# Helper function to generate OTP
def generate_otp():
    return str(random.randint(1000, 9999))

# User Signup
class UserSignupView(APIView):
    permission_classes = [AllowAny]
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
    permission_classes = [AllowAny]
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
                # refresh = RefreshToken.for_user(user)
                Token.objects.filter(user=user).delete()
                token, created = Token.objects.get_or_create(user=user)
                
                return Response({
                    "message": "OTP verified successfully",
                    "access_token": token.key
                })
            except User.DoesNotExist:
                return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# User Login
class UserLoginView(APIView):
    permission_classes = [AllowAny]
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
    
class UpdateLocationView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is logged in

    def post(self, request):
        user = request.user  # Get the currently logged-in user
        serializer = LocationUpdateSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Location updated successfully", "data": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UpdateRoleView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is logged in

    def post(self, request):
        user = request.user  # Get the currently logged-in user
        serializer = RoleUpdateSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User role updated successfully", "data": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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

class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user  # Get the logged-in user
        serializer = UpdateProfileSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PropertyCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
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
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        property = Property.objects.all()[:10]  

        return Response({
            "property": PropertySerializer(property, many=True).data,
        }, status=status.HTTP_200_OK)
   
    
class BuyerRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Ensure only logged-in users can create requests

    def post(self, request):
        serializer = BuyerRequestSerializer(data=request.data, context={"request": request})  # Pass request context
        if serializer.is_valid():
            serializer.save()  # No need to manually assign user here
            return Response(
                {"message": "Property request created successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class NotificationPagination(PageNumberPagination):
    page_size = 10  # Default notifications per page
    page_size_query_param = 'page_size'  # Optional: Allow dynamic page size
    max_page_size = 100  # Limit the max page size
    
class NotificationView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Only logged-in users can access
    pagination_class = NotificationPagination
    
    def get(self, request):
        notifications = Notification.objects.filter(user=request.user).order_by('-datetime')  
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(notifications, request)
        serializer = NotificationSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = NotificationSerializer(data=request.data)
        if serializer.is_valid():
            Notification.objects.create(
                user=request.user, 
                title=serializer.validated_data['title'], 
                description=serializer.validated_data['description']
            )
            return Response({"message": "Notification created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WishlistView(generics.ListCreateAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 0:  # Buyer should see only properties
            content_type = ContentType.objects.get(model='property')
        else:  # Seller should see only buyer requests
            content_type = ContentType.objects.get(model='buyerrequest')

        return Wishlist.objects.filter(user=user, content_type=content_type)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(
                {"message": "Added to wishlist successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class WishlistDeleteView(generics.DestroyAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)
    
class HomeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        # Ensure user has a location
        if not user.latitude or not user.longitude:
            return Response({"error": "User location is required"}, status=status.HTTP_400_BAD_REQUEST)

        user_location = (user.latitude, user.longitude)  # User's location as a tuple

        nearby_properties = []
        for property in Property.objects.all():  # Iterate over all properties
            if property.latitude and property.longitude:
                property_location = (property.latitude, property.longitude)
                distance = geodesic(user_location, property_location).km  # Calculate distance in km

                if distance <= 15:  # Only include properties within 5 km
                    nearby_properties.append((distance, property))
         # Sort properties by nearest distance
        nearby_properties.sort(key=lambda x: x[0])  # Sort by distance (first element in tuple)

        # Extract sorted property objects
        sorted_properties = [prop for _, prop in nearby_properties]
        if user.role == 0:  # Buyer
            recommended_property = Property.objects.all()[:10]  # Example condition
            category_property = Property.objects.all()[:10]

            return Response({
                "recommended_property": PropertySerializer(sorted_properties, many=True).data,
                "category_property": PropertySerializer(sorted_properties, many=True).data,
            }, status=status.HTTP_200_OK)

        elif user.role == 1:  # Seller
            #buyers_request = BuyerRequest.objects.all()[:10]  # Example: Show latest 10 buyer requests
            #recommended_property = Property.objects.all()[:10]  # Example: Seller’s properties
            nearby_buyers_request = []
            for buyers_request in BuyerRequest.objects.all():  # Iterate over all properties
                if buyers_request.latitude and buyers_request.longitude:
                    buyers_request_location = (buyers_request.latitude, buyers_request.longitude)
                    distance = geodesic(user_location, buyers_request_location).km  # Calculate distance in km

                    if distance <= 15:  # Only include properties within 5 km
                        nearby_buyers_request.append((distance, property))
            # Sort properties by nearest distance
            nearby_buyers_request.sort(key=lambda x: x[0])  # Sort by distance (first element in tuple)

            # Extract sorted property objects
            buyers_request = [prop for _, prop in nearby_buyers_request]

            return Response({
                "buyers_request": BuyerRequestSerializer(buyers_request, many=True).data,
                "recommended_property": PropertySerializer(sorted_properties, many=True).data,
            }, status=status.HTTP_200_OK)

        return Response({"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)
    
class PropertyDetailView(generics.RetrieveAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticated]  # Anyone can access this API
    lookup_field = "id"

    def get(self, request, id, *args, **kwargs):
        try:
            property_obj = Property.objects.get(id=id)
            serializer = PropertySerializer(property_obj)
            return Response({"message": "Success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Property.DoesNotExist:
            return Response({"error": "Property not found"}, status=status.HTTP_404_NOT_FOUND)
        
class ProposalListCreateView(generics.ListCreateAPIView):
    serializer_class = ProposalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 0:  # Buyer
            return Proposal.objects.filter(buyer_request__user=user)
        elif user.role == 1:  # Seller
            return Proposal.objects.filter(seller=user)
        return Proposal.objects.none()

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

class ProposalDetailView(generics.RetrieveAPIView):
    serializer_class = ProposalSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Proposal.objects.all()