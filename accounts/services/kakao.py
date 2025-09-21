import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class KakaoOAuthService:
    """카카오 OAuth 처리 서비스"""
    
    KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
    KAKAO_USER_INFO_URL = "https://kapi.kakao.com/v2/user/me"
    
    def __init__(self):
        self.client_id = settings.KAKAO_CLIENT_ID
        self.client_secret = getattr(settings, 'KAKAO_CLIENT_SECRET', None)
        self.redirect_uri = settings.KAKAO_REDIRECT_URI
    
    def get_access_token(self, authorization_code):
        """인증 코드로 액세스 토큰 획득"""
        data = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'code': authorization_code
        }
        
        # client_secret이 있다면 추가
        if self.client_secret:
            data['client_secret'] = self.client_secret
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
        }
        
        try:
            response = requests.post(self.KAKAO_TOKEN_URL, data=data, headers=headers, timeout=10)
            token_data = response.json()
            
            if response.status_code != 200:
                logger.error(f"카카오 토큰 요청 실패: {token_data}")
                raise Exception(f"카카오 토큰 요청 실패: {token_data}")
            
            return token_data.get('access_token')
            
        except requests.RequestException as e:
            logger.error(f"카카오 토큰 요청 네트워크 오류: {e}")
            raise Exception(f"네트워크 오류: {str(e)}")
    
    def get_user_info(self, access_token):
        """액세스 토큰으로 사용자 정보 획득"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = requests.get(self.KAKAO_USER_INFO_URL, headers=headers, timeout=10)
            user_data = response.json()
            
            if response.status_code != 200:
                logger.error(f"카카오 사용자 정보 요청 실패: {user_data}")
                raise Exception(f"카카오 사용자 정보 요청 실패: {user_data}")
            
            return user_data
            
        except requests.RequestException as e:
            logger.error(f"카카오 사용자 정보 요청 네트워크 오류: {e}")
            raise Exception(f"네트워크 오류: {str(e)}")
    
    def get_or_create_user(self, user_data):
        """카카오 사용자 정보로 User 생성 또는 조회"""
        kakao_id = str(user_data['id'])
        kakao_account = user_data.get('kakao_account', {})
        profile = kakao_account.get('profile', {})
        
        # 이메일 정보 처리
        email = kakao_account.get('email')
        if not email:
            email = f"kakao_{kakao_id}@temp.local"
        
        # 1. 기존 카카오 사용자 찾기
        try:
            user = User.objects.get(social_provider='kakao', social_id=kakao_id)
            self._update_user_info(user, profile, email)
            logger.info(f"기존 카카오 사용자 로그인: {user.email}")
            return user, False
        except User.DoesNotExist:
            pass
        
        # 2. 이메일로 기존 사용자 찾기 (소셜 계정 연동)
        if email and not email.endswith('@temp.local'):
            try:
                user = User.objects.get(email=email)
                user.social_provider = 'kakao'
                user.social_id = kakao_id
                self._update_user_info(user, profile, email)
                logger.info(f"기존 사용자와 카카오 계정 연동: {user.email}")
                return user, False
            except User.DoesNotExist:
                pass
        
        # 3. 새 사용자 생성
        user = self._create_new_user(kakao_id, profile, email)
        logger.info(f"새 카카오 사용자 생성: {user.email}")
        return user, True
    
    def _update_user_info(self, user, profile, email):
        """사용자 정보 업데이트"""
        user.first_name = profile.get('nickname', '')[:30]
        user.profile_image = profile.get('profile_image_url')
        user.email = email
        user.save()
    
    def _create_new_user(self, kakao_id, profile, email):
        """새 카카오 사용자 생성"""
        nickname = profile.get('nickname', '')
        
        # username 생성 (이메일 기반, 중복 방지)
        base_username = email.split('@')[0] if email else f"kakao_{kakao_id}"
        username = self._get_unique_username(base_username)
        
        user = User.objects.create(
            username=username,
            email=email,
            first_name=nickname[:30],
            social_provider='kakao',
            social_id=kakao_id,
            profile_image=profile.get('profile_image_url'),
            is_verified=True,  # 카카오 인증된 사용자는 자동 인증
        )
        
        return user
    
    def _get_unique_username(self, base_username):
        """중복되지 않는 username 생성"""
        username = base_username
        counter = 1
        
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1
        
        return username
    
    def generate_jwt_tokens(self, user):
        """사용자에 대한 JWT 토큰 생성"""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }