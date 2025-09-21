from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegistrationSerializer, UserSerializer
import logging
import urllib.parse
from django.conf import settings
from .services.kakao import KakaoOAuthService

logger = logging.getLogger(__name__)
User = get_user_model()


# ==================== 기본 인증 뷰 ====================

class RegisterView(generics.CreateAPIView):
    """사용자 회원가입"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """사용자 프로필 조회"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


class LogoutView(APIView):
    """사용자 로그아웃 (토큰 무효화)"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            
            if refresh_token:
                try:
                    # 리프레시 토큰을 블랙리스트에 추가
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                    
                    return Response({
                        'status': 'success',
                        'message': '성공적으로 로그아웃되었습니다.'
                    })
                except Exception as e:
                    logger.error(f"토큰 블랙리스트 처리 오류: {e}")
                    return Response({
                        'status': 'success',
                        'message': '로그아웃되었습니다.'
                    })
            else:
                return Response({
                    'status': 'success',
                    'message': '로그아웃되었습니다.'
                })
                
        except Exception as e:
            logger.error(f"로그아웃 처리 오류: {e}")
            return Response({
                'status': 'error',
                'message': '로그아웃 처리 중 오류가 발생했습니다.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def health_check(request):
    """서버 상태 확인"""
    return Response({'status': 'healthy'})


# ==================== 카카오 OAuth 뷰 ====================

class KakaoLoginURLView(APIView):
    """카카오 로그인 URL 반환"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """카카오 OAuth URL 생성"""
        try:
            params = {
                'client_id': settings.KAKAO_CLIENT_ID,
                'redirect_uri': settings.KAKAO_REDIRECT_URI,
                'response_type': 'code',
                'scope': 'profile,account_email'
            }
            
            base_url = "https://kauth.kakao.com/oauth/authorize"
            login_url = f"{base_url}?{urllib.parse.urlencode(params)}"
            
            return Response({
                'status': 'success',
                'login_url': login_url,
                'redirect_uri': settings.KAKAO_REDIRECT_URI,
                'scope': 'profile,account_email'
            })
            
        except Exception as e:
            logger.error(f"카카오 로그인 URL 생성 실패: {e}")
            return Response({
                'status': 'error',
                'message': f'로그인 URL 생성 실패: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class KakaoCallbackView(APIView):
    """카카오 OAuth 콜백 처리"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """카카오 콜백 처리"""
        try:
            # 에러 체크
            error = request.GET.get('error')
            if error:
                logger.error(f"카카오 OAuth 에러: {error}")
                return Response({
                    'status': 'error',
                    'error': error,
                    'error_description': request.GET.get('error_description')
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 인증 코드 확인
            authorization_code = request.GET.get('code')
            if not authorization_code:
                return Response({
                    'status': 'error',
                    'message': '인증 코드가 없습니다'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 카카오 OAuth 처리
            kakao_service = KakaoOAuthService()
            
            # 1단계: 액세스 토큰 획득
            access_token = kakao_service.get_access_token(authorization_code)
            
            # 2단계: 사용자 정보 조회
            user_data = kakao_service.get_user_info(access_token)
            
            # 3단계: 사용자 생성/조회
            user, created = kakao_service.get_or_create_user(user_data)
            
            # 4단계: JWT 토큰 생성
            tokens = kakao_service.generate_jwt_tokens(user)

            # 프론트엔드로 리다이렉트 (토큰 포함)
            frontend_url = f"http://localhost:3000/auth/kakao/callback"
            params = urllib.parse.urlencode({
                'access_token': tokens['access'],
                'refresh_token': tokens['refresh'],
                'user_id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'is_new_user': str(created).lower()
            })

            return redirect(f"{frontend_url}?{params}")
            
        except Exception as e:
            logger.error(f"카카오 콜백 처리 오류: {e}")
            return Response({
                'status': 'error',
                'message': f'로그인 처리 중 오류가 발생했습니다: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class KakaoTokenLoginView(APIView):
    """카카오 액세스 토큰으로 직접 로그인 (프론트엔드용)"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """카카오 액세스 토큰으로 로그인"""
        try:
            access_token = request.data.get('access_token')
            
            if not access_token:
                return Response({
                    'status': 'error',
                    'message': 'access_token이 필요합니다'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 카카오 OAuth 서비스
            kakao_service = KakaoOAuthService()
            
            # 1단계: 사용자 정보 조회
            user_data = kakao_service.get_user_info(access_token)
            
            # 2단계: 사용자 생성/조회
            user, created = kakao_service.get_or_create_user(user_data)
            
            # 3단계: JWT 토큰 생성
            tokens = kakao_service.generate_jwt_tokens(user)
            
            return Response({
                'status': 'success',
                'message': '카카오 로그인 성공',
                'tokens': tokens,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'profile_image': user.profile_image,
                    'is_new_user': created
                }
            })
            
        except Exception as e:
            logger.error(f"카카오 토큰 로그인 오류: {e}")
            return Response({
                'status': 'error',
                'message': f'로그인 처리 중 오류가 발생했습니다: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)