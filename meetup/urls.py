from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from meetup import settings

urlpatterns = [
                  path('admin/', admin.site.urls),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL,
                                                                                         document_root=settings.STATIC_URL)
