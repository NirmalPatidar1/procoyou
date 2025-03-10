from django.contrib.auth.models import BaseUserManager,AbstractUser
from django.db import models
from rest_framework import permissions
from django.utils.timezone import now
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class CustomUserManager(BaseUserManager):
    def create_user(self, email, mobile_number, password=None, name=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        if not mobile_number:
            raise ValueError("The Mobile Number field must be set")
        
        email = self.normalize_email(email)
        user = self.model(email=email, mobile_number=mobile_number, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, mobile_number, password=None, name=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, mobile_number, password, name, **extra_fields)

class CustomUser(AbstractUser):
    username = None  # Remove the username field
    mobile_number = models.CharField(max_length=15, unique=True)
    otp = models.CharField(max_length=6, blank=True, null=True)  # Store OTP temporarily
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    ROLE_CHOICES = (
        (0, 'Buyer'),
        (1, 'Seller'),
    )
    role = models.IntegerField(choices=ROLE_CHOICES, default=0, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['mobile_number', 'name']

    objects = CustomUserManager()  # Use CustomUserManager instead of default manager

    def __str__(self):
        return self.email

class Property(models.Model):
    PROPERTY_TYPE_CHOICES = [
        ('Villa', 'Villa'),
        ('Apartment', 'Apartment'),
        ('House', 'House'),
    ]
    
    title = models.CharField(max_length=255)
    address = models.TextField()
    price = models.CharField(max_length=50)
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPE_CHOICES)
    size = models.CharField(max_length=50)
    furniture_status = models.CharField(max_length=50, choices=[('Furnished', 'Furnished'), ('Unfurnished', 'Unfurnished')])
    bhk_type = models.CharField(max_length=50)
    contact_number = models.CharField(max_length=15)
    Looking_For_Type = [
        ('Sell', 'Sell'),
        ('Rent', 'Rent'),
        ('PG', 'PG'),
    ]
    looking_for = models.CharField(max_length=50, default="Sell", choices=Looking_For_Type)
    # Top Amenities
    cctv = models.BooleanField(default=False)
    lift = models.BooleanField(default=False)
    park = models.BooleanField(default=False)
    swimming_pool = models.BooleanField(default=False)

    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

class PropertyMedia(models.Model):
    PROPERTY_MEDIA_TYPE = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="media")
    media_type = models.CharField(max_length=10, choices=PROPERTY_MEDIA_TYPE)
    file = models.FileField(upload_to='property_media/')

    def __str__(self):
        return f"{self.property.title} - {self.media_type}"
    
class BuyerRequest(models.Model):
    PROPERTY_TYPE_CHOICES = [
        ('Villa', 'Villa'),
        ('Apartment', 'Apartment'),
        ('House', 'House'),
    ]
    
    FURNITURE_STATUS_CHOICES = [
        ('Furnished', 'Furnished'),
        ('Semi-furnished', 'Semi-furnished'),
        ('Unfurnished', 'Unfurnished'),
    ]
    
    LOOKING_FOR_CHOICES = [
        ('Buy', 'Buy'),
        ('Rent', 'Rent'),
        ('PG', 'PG'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE) 
    address = models.TextField()
    price = models.CharField(max_length=50)
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPE_CHOICES)
    size = models.CharField(max_length=50)
    furniture_status = models.CharField(max_length=50, choices=FURNITURE_STATUS_CHOICES)
    bhk_type = models.CharField(max_length=50)
    looking_for = models.CharField(max_length=50, choices=LOOKING_FOR_CHOICES, default="Buy")
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.property_type} - {self.address}"

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Links to the user receiving the notification
    title = models.CharField(max_length=255)
    description = models.TextField()
    datetime = models.DateTimeField(default=now)  # Auto set when notification is created

    def __str__(self):
        return f"{self.title} - {self.user.username}"

class Wishlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)  # Property or BuyerRequest
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')  # Links to actual Property or BuyerRequest
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.item}"
  
class Proposal(models.Model):
    PROPERTY_TYPE_CHOICES = [
        ('Villa', 'Villa'),
        ('Apartment', 'Apartment'),
        ('House', 'House'),
    ]
    
    FURNITURE_STATUS_CHOICES = [
        ('Furnished', 'Furnished'),
        ('Semi-furnished', 'Semi-furnished'),
        ('Unfurnished', 'Unfurnished'),
    ]

    buyer_request = models.ForeignKey("BuyerRequest", on_delete=models.CASCADE, related_name="proposals")
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="seller_proposals")
    
    title = models.CharField(max_length=255)
    address = models.TextField()
    price = models.CharField(max_length=50)
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPE_CHOICES)
    size = models.CharField(max_length=50)
    furniture_status = models.CharField(max_length=50, choices=FURNITURE_STATUS_CHOICES)
    bhk_type = models.CharField(max_length=50)
    top_amenities = models.TextField(help_text="Comma-separated list of amenities")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Proposal by {self.seller} for {self.buyer_request}"

class ProposalMedia(models.Model):
    PROPERTY_MEDIA_TYPE = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name="media")
    media_type = models.CharField(max_length=10, choices=PROPERTY_MEDIA_TYPE)
    file = models.FileField(upload_to="proposal_media/")  # Supports both image and video

    def __str__(self):
        return f"Media for {self.proposal.title} - {self.media_type}"