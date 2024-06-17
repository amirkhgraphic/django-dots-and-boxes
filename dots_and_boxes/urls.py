from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from dots_and_boxes.local_settings import ADMIN_URL


urlpatterns = [
    path(f'{ADMIN_URL}/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
