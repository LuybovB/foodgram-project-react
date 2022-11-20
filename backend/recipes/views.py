from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes import serializers
from recipes.filters import IngredientSearchFilter, RecipeFilterSet
from recipes.models import (AmountIngredient, Cart, Favorites, Ingredient,
                            Recipe, Tag)
from recipes.pagination import CustomPagination
from recipes.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import User


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """Работает с тегами. Теги может создавать только админ"""
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """Работает с ингредиентами. Ингредиенты может создавать только админ"""
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    permission_classes = (IsAdminOrReadOnly,)
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Работает с рецептами."""
    queryset = Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer
    pagination_class = CustomPagination
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilterSet

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def __get_add_delete_recipe(self, model, request, pk):
        """
        Вызывается методом: favorite, shopping_cart.
        Проверяет наличие рецепта в избранных или корзине
        после добавляет или удаляет его.
        """
        user = get_object_or_404(User, username=request.user)
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            model.objects.get_or_create(user=user, recipe=recipe)
            serializer = serializers.FavoritesSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        get_object_or_404(model, user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=('post', 'delete'),
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        """Добавляет или удаляет рецепт из избранного."""
        return self.__get_add_delete_recipe(Favorites, request, pk)

    @action(detail=True, methods=('post', 'delete'),
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        """Добавляет или удаляет рецепт из корзины."""
        return self.__get_add_delete_recipe(Cart, request, pk)

    @action(detail=False, methods=('get',),
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        """
        Список покупок скачивается в формате .txt.
        Пользователь получает файл с суммированным перечнем
        и количеством необходимых ингредиентов для всех рецептов.
        """
        carts = get_object_or_404(User, username=request.user).cart.all()
        ingredients_set = {}

        for item in carts:
            ingredients = AmountIngredient.objects.filter(recipe=item.recipe)

            for ingredient in ingredients:
                amount = ingredient.amount
                name = ingredient.ingredient.name
                measurement_unit = ingredient.ingredient.measurement_unit
                if name not in ingredients_set:
                    ingredients_set[name] = {
                        'amount': amount,
                        'measurement_unit': measurement_unit,
                    }
                else:
                    ingredients_set[name]['amount'] += amount

        cart_list = ['{} - {} {}.\n'.format(
            name, ingredients_set[name]['amount'],
            ingredients_set[name]['measurement_unit'],
        ) for name in ingredients_set]

        return HttpResponse(cart_list, content_type='text/plain')
