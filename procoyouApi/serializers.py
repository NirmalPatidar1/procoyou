from rest_framework import serializers
from django.contrib.auth import get_user_model

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