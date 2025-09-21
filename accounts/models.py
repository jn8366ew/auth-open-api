from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

        # 카카오 OAuth 관련 필드 추가
    social_provider = models.CharField(max_length=20, null=True, blank=True)  # 'kakao', 'google' 등
    social_id = models.CharField(max_length=100, null=True, blank=True)       # 카카오 고유 ID
    profile_image = models.URLField(null=True, blank=True)  


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        unique_together = ('social_provider', 'social_id')