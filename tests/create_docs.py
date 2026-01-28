"""
Script per generare 5 documenti di test per testare semantic, keyword e hybrid search.
Ogni documento ha contenuto diverso per testare vari scenari di ricerca.
"""

from pathlib import Path

# Directory dove salvare i file
OUTPUT_DIR = Path("test_documents")
OUTPUT_DIR.mkdir(exist_ok=True)

# Documento 1: Django Authentication Tutorial
doc1 = """Django Authentication and Authorization Guide

Introduction to Django Auth System

Django comes with a built-in authentication system that handles user accounts, groups, permissions, and cookie-based user sessions. The authentication system is located in django.contrib.auth.

Setting Up Authentication

To use Django's authentication system, you need to ensure these items are in your INSTALLED_APPS setting:
- django.contrib.auth (contains the core authentication framework)
- django.contrib.contenttypes (needed for permissions)

The authentication system also requires these middleware classes:
- SessionMiddleware (manages sessions across requests)
- AuthenticationMiddleware (associates users with requests)

User Model

Django provides a default User model with these fields:
- username: Required. 150 characters or fewer.
- password: Required. Hash of the password.
- email: Optional. Email address.
- first_name: Optional. 30 characters or fewer.
- last_name: Optional. 150 characters or fewer.

Creating Users

You can create users programmatically:

from django.contrib.auth.models import User

user = User.objects.create_user('john', 'john@example.com', 'password123')
user.first_name = 'John'
user.last_name = 'Doe'
user.save()

Login and Logout

Django provides views for handling login and logout. In your urls.py:

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

Password Management

Django includes views for password change and reset:
- PasswordChangeView: Allows users to change their password
- PasswordResetView: Sends password reset email
- PasswordResetConfirmView: Handles password reset confirmation

Permissions and Groups

Django's permission system provides a way to assign permissions to specific users and groups. Every model automatically gets create, read, update, and delete permissions.

You can check permissions in views:
if request.user.has_perm('app.add_model'):
    # User has permission
    pass

Custom Authentication Backends

You can customize the authentication process by creating a custom backend. Set it in settings.py:

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'myapp.backends.CustomBackend',
]

This allows you to authenticate users against different systems or add custom authentication logic.
"""

# Documento 2: JWT Authentication in Django REST Framework
doc2 = """JWT Authentication in Django REST Framework

What is JWT?

JSON Web Token (JWT) is an open standard (RFC 7519) for securely transmitting information between parties as a JSON object. JWTs are commonly used for authentication in modern web applications and APIs.

A JWT consists of three parts separated by dots:
- Header: Contains token type and hashing algorithm
- Payload: Contains claims (user data)
- Signature: Ensures token hasn't been tampered with

Installing JWT in Django

To use JWT authentication in Django REST Framework, install djangorestframework-simplejwt:

pip install djangorestframework-simplejwt

Configuration

Add the following to your settings.py:

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

URL Configuration

Add JWT token endpoints to your urls.py:

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]

Obtaining Tokens

Users can obtain tokens by sending POST request to /api/token/ with username and password:

POST /api/token/
{
    "username": "user@example.com",
    "password": "password123"
}

Response:
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Using Tokens

Include the access token in the Authorization header:

Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...

Token Refresh

When the access token expires, use the refresh token to get a new one:

POST /api/token/refresh/
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Custom Claims

You can add custom claims to the JWT payload by creating a custom serializer:

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['is_staff'] = user.is_staff
        return token

Security Best Practices

1. Always use HTTPS in production
2. Keep SECRET_KEY secure and never commit it
3. Set appropriate token lifetimes
4. Implement token blacklisting for logout
5. Validate tokens on every request
6. Store tokens securely on the client side
"""

# Documento 3: Django Performance Optimization
doc3 = """Django Performance Optimization Techniques

Database Query Optimization

Use select_related for Foreign Keys

select_related() performs a SQL join and includes related object data in a single query:

# Bad - causes N+1 queries
books = Book.objects.all()
for book in books:
    print(book.author.name)  # Separate query for each book

# Good - single query with join
books = Book.objects.select_related('author').all()
for book in books:
    print(book.author.name)

Use prefetch_related for Many-to-Many

prefetch_related() performs separate queries but does the joining in Python:

# Bad
authors = Author.objects.all()
for author in authors:
    for book in author.books.all():  # Query for each author
        print(book.title)

# Good
authors = Author.objects.prefetch_related('books').all()
for author in authors:
    for book in author.books.all():
        print(book.title)

Database Indexing

Add indexes to frequently queried fields:

class Article(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    created_at = models.DateTimeField(db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['title', 'created_at']),
            models.Index(fields=['-created_at']),
        ]

Query Optimization

Use only() and defer() to limit fields:

# Only fetch specific fields
users = User.objects.only('id', 'username')

# Defer loading of large fields
articles = Article.objects.defer('content', 'metadata')

Use values() and values_list() for dictionaries:

# Returns list of dictionaries
users = User.objects.values('id', 'username')

# Returns list of tuples
user_ids = User.objects.values_list('id', flat=True)

Caching Strategies

Django supports multiple cache backends:

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'myapp',
        'TIMEOUT': 300,
    }
}

Per-View Caching

from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # Cache for 15 minutes
def my_view(request):
    # Expensive operations
    return render(request, 'template.html')

Template Fragment Caching

{% load cache %}
{% cache 500 sidebar %}
    <!-- Expensive sidebar rendering -->
{% endcache %}

Low-Level Cache API

from django.core.cache import cache

# Set cache
cache.set('my_key', 'my_value', 300)

# Get cache
value = cache.get('my_key')

# Delete cache
cache.delete('my_key')

Static Files Optimization

Use WhiteNoise for static files in production:

pip install whitenoise

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ...
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

Enable compression and caching:

WHITENOISE_COMPRESS_OFFLINE = True
WHITENOISE_MANIFEST_STRICT = False

Async Views and Database Operations

Django 4.1+ supports async views and database queries:

from django.http import JsonResponse
import asyncio

async def my_async_view(request):
    # Async database query
    users = await User.objects.filter(is_active=True).acount()

    # Concurrent operations
    results = await asyncio.gather(
        fetch_data_from_api(),
        process_background_task(),
    )

    return JsonResponse({'count': users})

Middleware Optimization

Remove unnecessary middleware and order them correctly. Put lightweight middleware first.

Connection Pooling

Use persistent database connections:

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'CONN_MAX_AGE': 600,  # Keep connections for 10 minutes
    }
}

Use Persistent Connections with pgBouncer for PostgreSQL.
"""

# Documento 4: Django Security Best Practices
doc4 = """Django Security Best Practices and Configuration

Security Settings

Essential Security Settings in settings.py

# HTTPS Settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookie Security
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SAMESITE = 'Strict'

# Content Security
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

Secret Key Management

Never hardcode SECRET_KEY in settings.py. Use environment variables:

import os
from pathlib import Path

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY environment variable not set")

Generate strong secret keys:

from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())

Database Security

Use parameterized queries (Django ORM does this automatically):

# Safe - parameterized
User.objects.filter(username=user_input)

# Dangerous - SQL injection risk
User.objects.raw(f"SELECT * FROM users WHERE username='{user_input}'")

Encrypt sensitive data at rest:

from django.contrib.postgres.fields import CICharField
from encrypted_model_fields.fields import EncryptedCharField

class UserProfile(models.Model):
    ssn = EncryptedCharField(max_length=11)
    credit_card = EncryptedCharField(max_length=16)

Password Security

Configure password validators:

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

Use Argon2 for password hashing:

pip install django[argon2]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

CSRF Protection

Django's CSRF protection is enabled by default. Ensure you:

1. Include {% csrf_token %} in all forms
2. Use @csrf_protect decorator for function views
3. Configure CSRF_TRUSTED_ORIGINS for cross-domain requests:

CSRF_TRUSTED_ORIGINS = [
    'https://example.com',
    'https://subdomain.example.com',
]

XSS Prevention

Django templates auto-escape by default. Be careful with:

# Safe
{{ user_input }}

# Dangerous - disables escaping
{{ user_input|safe }}

# Use format_html for mixing HTML and variables
from django.utils.html import format_html
output = format_html('<a href="{}">{}</a>', url, text)

Clickjacking Protection

X_FRAME_OPTIONS = 'DENY'  # Never allow framing

# Or allow only same origin
X_FRAME_OPTIONS = 'SAMEORIGIN'

# Or specify allowed domains
from django.middleware.clickjacking import XFrameOptionsMiddleware

Rate Limiting and DDoS Protection

Install django-ratelimit:

pip install django-ratelimit

from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m', method='POST')
def login_view(request):
    # Login logic
    pass

Use django-axes for login attempt tracking:

pip install django-axes

INSTALLED_APPS = [
    'axes',
    # ...
]

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesBackend',
    'django.contrib.auth.backends.ModelBackend',
]

AXES_FAILURE_LIMIT = 5
AXES_LOCK_OUT_AT_FAILURE = True
AXES_COOLOFF_TIME = 1  # Hours

File Upload Security

Limit file upload size:

DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880

Validate file types:

from django.core.exceptions import ValidationError

def validate_file_extension(value):
    valid_extensions = ['.pdf', '.doc', '.docx']
    if not any(value.name.endswith(ext) for ext in valid_extensions):
        raise ValidationError('Unsupported file extension.')

class Document(models.Model):
    file = models.FileField(
        upload_to='documents/',
        validators=[validate_file_extension]
    )

Security Headers with django-csp

pip install django-csp

MIDDLEWARE = [
    'csp.middleware.CSPMiddleware',
    # ...
]

CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "https://cdn.example.com")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:", "https:")

Logging and Monitoring

Configure security logging:

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'security_file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/security.log',
        },
    },
    'loggers': {
        'django.security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

Monitor for security events and set up alerts for suspicious activity.
"""

# Documento 5: Django REST Framework API Development
doc5 = """Django REST Framework API Development Guide

Setting Up Django REST Framework

Installation

pip install djangorestframework

Add to INSTALLED_APPS in settings.py:

INSTALLED_APPS = [
    # ...
    'rest_framework',
]

Basic Configuration

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
}

Serializers

Serializers convert complex data types (like Django models) to native Python datatypes that can be rendered into JSON.

Basic ModelSerializer

from rest_framework import serializers
from .models import Article

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'author', 'created_at']
        read_only_fields = ['created_at']

Custom Validation

class ArticleSerializer(serializers.ModelSerializer):
    def validate_title(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("Title must be at least 10 characters")
        return value

    def validate(self, data):
        if data['title'] == data['content']:
            raise serializers.ValidationError("Title and content cannot be the same")
        return data

Nested Serializers

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name', 'email']

class ArticleSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'author']

Views and ViewSets

Function-Based Views

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET', 'POST'])
def article_list(request):
    if request.method == 'GET':
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

Class-Based Views

from rest_framework import generics

class ArticleListCreateView(generics.ListCreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

ViewSets

from rest_framework import viewsets

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def get_queryset(self):
        queryset = Article.objects.all()
        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author__username=author)
        return queryset

Routers

from rest_framework.routers import DefaultRouter
from .views import ArticleViewSet

router = DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='article')

urlpatterns = [
    path('api/', include(router.urls)),
]

Authentication and Permissions

Configure Authentication

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

Token Authentication

Add to INSTALLED_APPS:
INSTALLED_APPS = [
    'rest_framework.authtoken',
]

Generate tokens:
from rest_framework.authtoken.models import Token
token = Token.objects.create(user=user)

Custom Permissions

from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user

Use in views:
class ArticleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthorOrReadOnly]

Filtering and Search

Install django-filter:
pip install django-filter

Add to INSTALLED_APPS:
INSTALLED_APPS = [
    'django_filters',
]

Configure:
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

Use in ViewSet:
class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    filterset_fields = ['author', 'status']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'title']

Pagination

Configure globally in settings.py:

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}

Custom Pagination:

from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

Throttling

Limit request rates:

REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
    }
}

Versioning

REST_FRAMEWORK = {
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
}

urlpatterns = [
    path('api/v1/', include('myapp.urls')),
    path('api/v2/', include('myapp.v2.urls')),
]

Testing APIs

from rest_framework.test import APITestCase
from rest_framework import status

class ArticleAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test123')
        self.client.force_authenticate(user=self.user)

    def test_create_article(self):
        data = {'title': 'Test Article', 'content': 'Test content'}
        response = self.client.post('/api/articles/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_articles(self):
        response = self.client.get('/api/articles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
"""

# Salva tutti i documenti
documents = {
    "django_authentication.txt": doc1,
    "jwt_authentication.txt": doc2,
    "performance_optimization.txt": doc3,
    "security_best_practices.txt": doc4,
    "rest_framework_api.txt": doc5,
}

for filename, content in documents.items():
    filepath = OUTPUT_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Creato: {filepath}")

print(f"\n🎉 Tutti i {len(documents)} documenti sono stati creati nella cartella '{OUTPUT_DIR}'")
print("\nDocumenti creati:")
print("1. django_authentication.txt - Django auth system, user model, permissions")
print("2. jwt_authentication.txt - JWT setup, configuration, token management")
print("3. performance_optimization.txt - Database queries, caching, async views")
print("4. security_best_practices.txt - Security settings, CSRF, XSS, rate limiting")
print("5. rest_framework_api.txt - DRF serializers, views, authentication, filtering")
print("\nQuery di test suggerite:")
print("- 'how to configure JWT in Django' (hybrid dovrebbe essere ottimo)")
print("- 'AUTHENTICATION_BACKENDS settings.py' (keyword eccelle)")
print("- 'improve application performance' (semantic eccelle)")
print("- 'password security best practices' (hybrid bilancia bene)")
print("- 'API authentication methods' (tutti e tre funzionano)")

