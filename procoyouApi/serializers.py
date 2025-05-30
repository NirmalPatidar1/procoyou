from rest_framework import serializers
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import *
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import localtime
from datetime import timedelta

User = get_user_model()

class UserSignupSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['name', 'email', 'mobile_number']

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            mobile_number=validated_data['mobile_number'],
            name=validated_data.get('name')  # Name is optional
        )
        return user

class OTPVerificationSerializer(serializers.Serializer):
    mobile_number = serializers.CharField()
    otp = serializers.CharField()

class UserLoginSerializer(serializers.Serializer):
    mobile_number = serializers.CharField()

class UserInfoSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'mobile_number', 'role', 'profile_image']
    def get_profile_image(self, obj):
        if obj.profile_image:
            return f"{settings.BASE_URL}{settings.MEDIA_URL}{obj.profile_image.name}"
        return None

class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'email', 'mobile_number']
    
    def validate_email(self, value):
        """Ensure email is unique if changed."""
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def validate_mobile_number(self, value):
        """Ensure mobile number is unique if changed."""
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(mobile_number=value).exists():
            raise serializers.ValidationError("This mobile number is already in use.")
        return value
 
class LocationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['latitude', 'longitude', 'address']
    
class RoleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['role']
        
class ProfileImageUploadSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['profile_image']
        
class PropertyMediaSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    def get_file(self, obj):
        return f"{settings.BASE_URL}{settings.MEDIA_URL}{obj.file.name}"
    class Meta:
        model = PropertyMedia
        fields = ['id', 'media_type', 'file']

class PropertySerializer(serializers.ModelSerializer):
    media_files = serializers.ListField(
        child=serializers.FileField(), write_only=True, required=False
    )
    media = PropertyMediaSerializer(many=True, read_only=True)  # To return media files in response

    class Meta:
        model = Property
        fields = '__all__'

    def create(self, validated_data):
        media_files = validated_data.pop('media_files', [])
        property_instance = Property.objects.create(**validated_data)

        # Save media files
        for file in media_files:
            media_type = 'image' if file.content_type.startswith('image') else 'video'
            PropertyMedia.objects.create(property=property_instance, media_type=media_type, file=file)

        return property_instance
    
class BuyerRequestSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)  # Include user ID in the response

    class Meta:
        model = BuyerRequest
        fields = ['user_id', 'address', 'price', 'property_type', 'size', 'furniture_status', 'bhk_type', 'looking_for', 'description']
        read_only_fields = ['user_id']

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["user"] = request.user  # Set the logged-in user
        return super().create(validated_data)
        
class NotificationSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = Notification
        fields = ['user_id', 'title', 'description', 'datetime']
        
class WishlistSerializer(serializers.ModelSerializer):
    content_type = serializers.SerializerMethodField()  # Convert ContentType to string
    created_at = serializers.SerializerMethodField()  # Format datetime
    object_details = serializers.SerializerMethodField()  # Fetch object details

    class Meta:
        model = Wishlist
        fields = ['id', 'content_type', 'object_id', 'object_details', 'created_at']

    def get_content_type(self, obj):
        return obj.content_type.model  # Return 'property' or 'buyerrequest'

    def get_created_at(self, obj):
        dt = obj.created_at  # Use stored datetime without conversion
        today = now().date()  # Get today’s date in system's local time

        if dt.date() == today:
            return f"Today {dt.strftime('%I:%M %p')}"
        elif dt.date() == today - timedelta(days=1):
            return f"Yesterday {dt.strftime('%I:%M %p')}"
        else:
            return dt.strftime('%b %d %I:%M %p')  # Example: Feb 05 05:10 PM

    def get_object_details(self, obj):
        if obj.content_type.model == 'property':
            try:
                property_obj = Property.objects.get(id=obj.object_id)
                return PropertySerializer(property_obj).data 
            except Property.DoesNotExist:
                return None
        elif obj.content_type.model == 'buyerrequest':
            try:
                buyer_request = BuyerRequest.objects.get(id=obj.object_id)
                return {
                    "id": buyer_request.id,
                    "address": buyer_request.address,
                    "price": buyer_request.price,
                    "looking_for": buyer_request.looking_for
                }
            except BuyerRequest.DoesNotExist:
                return None
        return None

    def validate(self, data):
        user = self.context['request'].user
        content_type_str = self.initial_data.get('content_type')  # 'property' or 'buyerrequest'
        object_id = data.get('object_id')

        if content_type_str == 'property':
            if user.role != 0:  # Only buyers can add properties
                raise serializers.ValidationError({"error": "Only buyers can add properties to wishlist"})
            model = Property
        elif content_type_str == 'buyerrequest':
            if user.role != 1:  # Only sellers can add buyer requests
                raise serializers.ValidationError({"error": "Only sellers can add buyer requests to wishlist"})
            model = BuyerRequest
        else:
            raise serializers.ValidationError({"error": "Invalid content_type"})

        if not model.objects.filter(id=object_id).exists():
            raise serializers.ValidationError({"error": f"{content_type_str} does not exist"})

        return data

    def create(self, validated_data):
        content_type_str = self.initial_data.get('content_type')
        model = Property if content_type_str == 'property' else BuyerRequest

        validated_data['content_type'] = ContentType.objects.get_for_model(model)
        return super().create(validated_data)
    
class ProposalMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProposalMedia
        fields = ['id', 'media_type', 'file']

class ProposalSerializer(serializers.ModelSerializer):
    seller_id = serializers.IntegerField(source='seller.id', read_only=True)  # Read-only seller ID
    media = ProposalMediaSerializer(many=True, read_only=True)
    uploaded_files = serializers.ListField(
        child=serializers.FileField(), write_only=True, required=False
    )  # Accept multiple file uploads

    class Meta:
        model = Proposal
        fields = [
            'id', 'buyer_request', 'seller_id', 'title', 'address', 'price', 'property_type',
            'size', 'furniture_status', 'bhk_type', 'top_amenities', 'description', 'created_at',
            'media', 'uploaded_files'
        ]

    def validate(self, data):
        seller = self.context['request'].user
        buyer_request = data['buyer_request']

        # Ensure a seller submits only one proposal per BuyerRequest
        if Proposal.objects.filter(seller=seller, buyer_request=buyer_request).exists():
            raise serializers.ValidationError({"error": "You have already submitted a proposal for this BuyerRequest"})

        return data

    def create(self, validated_data):
        uploaded_files = validated_data.pop('uploaded_files', [])
        proposal = Proposal.objects.create(**validated_data)

        # Save uploaded media files
        for file in uploaded_files:
            media_type = 'video' if file.name.lower().endswith(('mp4', 'avi', 'mov')) else 'image'
            ProposalMedia.objects.create(proposal=proposal, file=file, media_type=media_type)

        return proposal