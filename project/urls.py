from django.contrib import admin
from django.urls import path,include
from django.urls import re_path as url
from django.views.static import serve
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import gettext_lazy as _

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  # Tilni o‘zgartirish uchun
]

# Barcha URL lar i18n_patterns ichida bo‘lishi kerak
urlpatterns += i18n_patterns(
    path(_('admin/'), admin.site.urls),
    path('', include('app.urls')),  # Bu yerda i18n_patterns ishlatilmayapti
)

if not settings.DEBUG:
    urlpatterns += url(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    urlpatterns += url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
