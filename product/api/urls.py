from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.urls import include, path

app_name = 'api'

urlpatterns = [
    path('api/v1/', include('api.v1.urls')),
]

if settings.DEBUG:
    urlpatterns += debug_toolbar_urls()
