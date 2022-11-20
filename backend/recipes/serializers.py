from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (AmountIngredient, Cart, Favorites, Ingredient,
                            Recipe, Tag)
from rest_framework.serializers import (ModelSerializer, ReadOnlyField,
                                        SerializerMethodField, ValidationError)
from users.serializers import CustomUserSerializer


class TagSerializer(ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class AmountIngredientSerializer(ModelSerializer):
    """Сериализатор количества ингредиентов в рецепте."""
    id = ReadOnlyField(source='ingredient.id')
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = AmountIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class FavoritesSerializer(ModelSerializer):
    """Сериализатор рецепта в подписках."""
    image = Base64ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeSerializer(ModelSerializer):
    """Сериализатор рецептов."""
    image = Base64ImageField()
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = AmountIngredientSerializer(
        source='amount_ingredient', read_only=True, many=True
    )
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'tags', 'author', 'ingredients',
            'text', 'cooking_time', 'is_favorited', 'is_in_shopping_cart'
        )

    def __get_check(self, recipe, model):
        """Из get_is_favorited, get_is_in_shopping_cart."""
        user = self.context.get('request').user
        return not user.is_anonymous and model.objects.filter(
            user=user, recipe=recipe).exists()

    def get_is_favorited(self, recipe):
        """Проверяет добавлен ли пользователем рецепт в избранное."""
        return self.__get_check(recipe, Favorites)

    def get_is_in_shopping_cart(self, recipe):
        """Проверяет добавлен ли пользователем рецепт в корзину."""
        return self.__get_check(recipe, Cart)

    def validate(self, data):
        """Проверяет входные данные при создании и редактировании рецепта."""
        if data['cooking_time'] < 1:
            raise ValidationError('Минимальное время приготовления 1 минута')

        name = self.initial_data.get('name')
        if not name:
            raise ValidationError('Нет названия рецепта.')
        if self.context.get('request').method == 'POST':
            user = self.context.get('request').user
            if Recipe.objects.filter(author=user, name=name).exists():
                raise ValidationError(f'Рецепт {name} уже существует.')

        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise ValidationError('В рецепте нет ингредиентов.')
        ingredients_set = set()
        for ingredient in ingredients:
            ingredient = get_object_or_404(Ingredient, id=ingredient['id'])
            if ingredient in ingredients_set:
                raise ValidationError('Ингридиенты повторяются')
            ingredients_set.add(ingredient)
        data['ingredients'] = ingredients
        return data

    def __create_ingredients(self, ingredients, recipe):
        """Записывает количество ингредиентов в рецепте."""
        for ingredient in ingredients:
            AmountIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )

    def create(self, validated_data):
        """Создаёт рецепт."""
        image = validated_data.pop('image')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(image=image, **validated_data)
        recipe.tags.set(self.initial_data.get('tags'))
        self.__create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Редактирует рецепт."""
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        ingredients = validated_data.pop('ingredients')
        instance.tags.clear()
        instance.ingredients.clear()
        instance.tags.set(self.initial_data.get('tags'))
        self.__create_ingredients(ingredients, instance)
        instance.save()
        return instance
