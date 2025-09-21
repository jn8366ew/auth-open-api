# 🔐 Auth Open API - Project Template

> This document contains project structure and context information for smooth collaboration with Claude AI.

## 📋 Project Overview

**Project Name**: Auth Open API
**Development Environment**: Python 3.12+, Django 5.2, MariaDB, UV venv
**Local Development**: Windows 10

## 🏗️ Architecture Structure

```
auth-open-api/
├── 🔧 Project Configuration
│   ├── auth_project/           # Django main project
│   │   ├── settings.py         # Project settings (JWT, CORS, DB)
│   │   ├── urls.py            # Main URL routing
│   │   ├── wsgi.py            # WSGI configuration
│   │   └── asgi.py            # ASGI configuration
│   ├── manage.py              # Django management commands
│   └── main.py                # Project entry point
│
├── 👤 Authentication App
│   └── accounts/              # User authentication related app
│       ├── models.py          # Custom User model (social login support)
│       ├── serializers.py     # DRF serializers
│       ├── views.py           # API views (registration, profile, Kakao OAuth)
│       ├── urls.py            # Authentication related URL patterns
│       ├── admin.py           # Django admin configuration
│       ├── services/          # Business logic services
│       │   ├── __init__.py
│       │   └── kakao.py       # Kakao OAuth service
│       └── migrations/        # Database migrations
│
├── 📚 Documentation
│   └── doc/
│       └── openapi.yaml       # OpenAPI 3.0 spec
│
├── 🐳 Infrastructure
│   ├── docker-compose.yml     # MariaDB container configuration
│   ├── pyproject.toml         # Python dependency management (uv)
│   └── uv.lock               # Dependency lock file
│
└── 📖 Documentation
    ├── README.md             # Basic project description
    └── PROJECT_TEMPLATE.md   # This file
```

## 🔑 Core Features

### 1. API Endpoints
```
# Basic Authentication
POST /api/auth/register/         # User registration
POST /api/auth/login/            # Login (JWT token issuance)
POST /api/auth/token/refresh/    # Token refresh
POST /api/auth/logout/           # Logout (token invalidation)
GET  /api/auth/profile/          # User profile retrieval
GET  /api/auth/health/           # Server health check

# Kakao OAuth
GET  /api/auth/kakao/            # Return Kakao login URL
GET  /api/auth/kakao/callback/   # Kakao OAuth callback handling
POST /api/auth/kakao/token/      # Direct login with Kakao access token
```

### 2. Data Model
```python
# accounts.models.User
class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Kakao OAuth related fields
    social_provider = models.CharField(max_length=20, null=True, blank=True)
    social_id = models.CharField(max_length=100, null=True, blank=True)
    profile_image = models.URLField(null=True, blank=True)

    USERNAME_FIELD = 'email'

    class Meta:
        unique_together = ('social_provider', 'social_id')
```

## ⚙️ Technology Stack

### Backend Framework
- **Django 5.2.6** - Main web framework
- **Django REST Framework 3.16.1** - API development
- **SimpleJWT 5.5.1** - JWT token authentication

### Database
- **MariaDB** - Main database (Docker)
- **mysqlclient 2.2.7** - Python MySQL driver

### Dependencies
- **drf-spectacular 0.28.0** - OpenAPI schema generation
- **django-cors-headers 4.8.0** - CORS handling
- **python-dotenv 1.0.0** - Environment variable management
- **requests 2.32.5** - HTTP requests for Kakao API
- **uv** - Package manager

## 🔧 Configuration

### Environment Variables (.env)
```env
# Django settings
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# JWT settings
JWT_ACCESS_TOKEN_LIFETIME=60      # 60 minutes
JWT_REFRESH_TOKEN_LIFETIME=1440   # 24 hours
JWT_SECRET_KEY=your-jwt-secret

# Database
DB_ENGINE=django.db.backends.mysql
DB_NAME=localDB
DB_USER=root
DB_PASSWORD=1234
DB_HOST=localhost
DB_PORT=3308

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Kakao OAuth
KAKAO_CLIENT_ID=your-kakao-client-id
KAKAO_CLIENT_SECRET=your-kakao-client-secret
KAKAO_REDIRECT_URI=http://localhost:8000/api/auth/kakao/callback/
SITE_URL=http://localhost:8000
```

### JWT Configuration
- Access token lifetime: 60 minutes
- Refresh token lifetime: 24 hours
- Token rotation: Enabled
- Blacklist after rotation: Enabled

### CORS Configuration
- Allowed origins: localhost:3000, 127.0.0.1:3000
- Allow credentials: True

## 📊 Database Structure

### accounts_user Table
```sql
CREATE TABLE accounts_user (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(150) NOT NULL UNIQUE,
    email VARCHAR(254) NOT NULL UNIQUE,
    first_name VARCHAR(30) NOT NULL,
    last_name VARCHAR(30) NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    password VARCHAR(128) NOT NULL,
    is_staff BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    date_joined DATETIME(6) NOT NULL,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    last_login DATETIME(6),
    social_provider VARCHAR(20),
    social_id VARCHAR(100),
    profile_image VARCHAR(200),

    UNIQUE KEY unique_social (social_provider, social_id)
);
```

## 🔍 Code Structure

### Views
```python
# accounts/views.py
# Basic Authentication
- RegisterView: CreateAPIView for user registration
- profile_view: Function-based view for user profile
- LogoutView: APIView for token invalidation
- health_check: Function-based view for server status

# Kakao OAuth
- KakaoLoginURLView: APIView returning Kakao login URL
- KakaoCallbackView: APIView handling OAuth callback
- KakaoTokenLoginView: APIView for direct token login
```

### Services
```python
# accounts/services/kakao.py
- KakaoOAuthService: Kakao OAuth processing service
  - get_access_token(): Get access token with authorization code
  - get_user_info(): Get user info with access token
  - get_or_create_user(): Create or retrieve Kakao user
  - generate_jwt_tokens(): Generate JWT tokens
```

### Serializers
```python
# accounts/serializers.py
- UserRegistrationSerializer: User registration
- UserSerializer: User information serialization
```

## 🚀 Development Commands

### Start Development
```bash
# Start database
docker-compose up -d

# Start Django server
python manage.py runserver
```

### API Documentation
- **Swagger UI**: http://127.0.0.1:8000/api/docs/
- **OpenAPI Schema**: http://127.0.0.1:8000/api/schema/

---

**Last Updated**: September 21, 2025
**Git Branch**: prod