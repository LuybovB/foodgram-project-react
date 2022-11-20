from django.urls import include, path
from recipes import views
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register("tags", views.TagsViewSet, "tags")
router.register("recipes", views.RecipeViewSet, "recipes")
router.register("ingredients", views.IngredientsViewSet, "ingredients")


urlpatterns = [
    path("", include(router.urls)),
]
