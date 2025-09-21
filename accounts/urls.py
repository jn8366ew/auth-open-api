from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', views.profile_view, name='profile'),
    path('health/', views.health_check, name='health'),


    # 카카오 OAuth 관련 URL
    path('kakao/login/', views.KakaoLoginURLView.as_view(), name='kakao_login'),
    path('kakao/callback/', views.KakaoCallbackView.as_view(), name='kakao_callback'), 
    path('kakao/token/', views.KakaoTokenLoginView.as_view(), name='kakao_token'),
]