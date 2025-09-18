from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from drf_spectacular.views import SpectacularSwaggerView
import yaml
import os
from django.conf import settings

def custom_schema_view(request):
    """커스텀 OpenAPI 스키마를 반환하는 뷰"""
    yaml_path = os.path.join(settings.BASE_DIR, 'doc', 'openapi.yaml')
    with open(yaml_path, 'r', encoding='utf-8') as file:
        schema = yaml.safe_load(file)
    return JsonResponse(schema)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/schema/', custom_schema_view, name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]