from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from .views import *
from django.utils.translation import gettext_lazy as _


urlpatterns = [
    path('', index, name='index'),  # Index sahifasi to'g'ri belgilanganmi?
    path('login', login, name='login'),
    path('signin', signin, name='signin'),
    path('courses', courses, name='courses'),
    path('course/<int:pk>', course, name='course'),
    path('maruza/<int:pk>', maruza, name='maruza'),
    path('video/<int:pk>', video, name='video'),
    path('taqdimot/<int:pk>', taqdimot, name='taqdimot'),
    path('logout', logout, name='logout'),
    path('test/<int:pk>', test, name='test'),
    path('scan_test', scan_test, name='scan_test'),
    path('scan_test/<int:pk>', scan_test, name='scan_test'),
    path('certificate/<int:user>/<int:pk>', certificate, name='certificate'),
]


# Media fayllarni xizmat qilish
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
