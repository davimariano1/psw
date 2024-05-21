from django.contrib import admin
from django.urls import path, include
from usuarios.views import login_view, redirect
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls')),
    path('medico/', include('medico.urls')),
    path('paciente/', include('paciente.urls')),
    path('', lambda request: redirect('/usuarios/login'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
