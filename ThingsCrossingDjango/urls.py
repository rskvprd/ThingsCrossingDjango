from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
import ThingsCrossing.views as views
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token

router = routers.DefaultRouter()
router.register(r"advertisement", views.AdvertisementViewSet)
router.register(r"pictures", views.PicturesViewSet)
# router.register(r"users", views.)

urlpatterns = [
    path("", include(router.urls)),
    path("admin/", admin.site.urls),
    path("auth/", include('rest_framework.urls', namespace='rest_framework')),
    path("obtain-auth-token/", obtain_auth_token, name="obtain_auth_token")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
