from django.urls import include, path
from recipes import views
from rest_framework.routers import SimpleRouter

router = SimpleRouter()

urlpatterns = [
    path("", include(router.urls)),
]
