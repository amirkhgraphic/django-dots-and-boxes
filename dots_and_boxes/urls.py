from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path, include
from django.views.generic import TemplateView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include(('user.urls', 'user'), namespace='user')),
    path('game/', include(('game.urls', 'game'), namespace='game')),
    path('', login_required(TemplateView.as_view(template_name='home.html')), name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
