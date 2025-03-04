from rest_framework import serializers
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import *

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
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'mobile_number', 'role', 'profile_image']
        
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