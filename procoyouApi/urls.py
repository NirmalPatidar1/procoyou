from django.urls import path
from .views import *

urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('verify-otp/', OTPVerificationView.as_view(), name='verify-otp'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('userinfo/', UserInfoView.as_view(), name='user-info'),
    path('upload-profile-image/', ProfileImageUploadView.as_view(), name='upload-profile-image'),
    path('update-profile/', UpdateProfileView.as_view(), name='update-profile'),
    path('add-property/', PropertyCreateView.as_view(), name='add-property'),
    path('list-properties/', PropertyListView.as_view(), name='list-properties'),
    path('buyer-request/', BuyerRequestView.as_view(), name='buyer-request'),
    path('notifications/', NotificationView.as_view(), name='notifications'),
    path('wishlist/', WishlistView.as_view(), name='wishlist-list'),
    path('wishlist/<int:pk>/', WishlistDeleteView.as_view(), name='wishlist-delete'),
]
