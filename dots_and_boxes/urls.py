from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path, include
from django.views.generic import TemplateView

from dots_and_boxes.local_settings import ADMIN_URL

urlpatterns = [
    path(f'{ADMIN_URL}/', admin.site.urls),
    path('', login_required(TemplateView.as_view(template_name='home.html')), name='home'),
    path('user/', include(('user.urls', 'user'), namespace='user'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
