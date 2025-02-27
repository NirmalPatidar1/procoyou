from django.urls import path
from .views import UserSignupView, OTPVerificationView, UserLoginView
from .views import *

urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('verify-otp/', OTPVerificationView.as_view(), name='verify-otp'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('userinfo/', UserInfoView.as_view(), name='user-info'),
    path('upload-profile-image/', ProfileImageUploadView.as_view(), name='upload-profile-image'),
]
