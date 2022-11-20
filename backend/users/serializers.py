from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import Recipe
from rest_framework.serializers import (ModelSerializer, ReadOnlyField,
                                        SerializerMethodField, ValidationError)
from users.models import Follow, User


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для djoser для создания пользователя."""

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'password'
        )

    def validate(self, data):
        """Проверяет введенные данные."""
        username = data.get('username')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        if username == 'me':
            raise ValidationError(
                {'username': 'Нельзя создать пользователя с никнеймом - "me"'}
            )
        if not first_name:
            raise ValidationError({'first_name': 'Имя обязательное поле'})
        if not last_name:
            raise ValidationError({'last_name': 'Фамилия обязательное поле'})
        return data


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователя."""
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, author):
        """Проверяет подписан ли текущий пользователь на автора."""
        user = self.context.get('request').user
        return not user.is_anonymous and Follow.objects.filter(
            user=user, author=author).exists()


class FollowRecipeSerializer(ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(ModelSerializer):
    """Сериализатор для вывода авторов на которых подписан пользователь."""
    id = ReadOnlyField(source='author.id')
    username = ReadOnlyField(source='author.username')
    first_name = ReadOnlyField(source='author.first_name')
    last_name = ReadOnlyField(source='author.last_name')
    is_subscribed = SerializerMethodField()
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, author):
        """Проверяет подписан ли текущий пользователь на автора."""
        user = self.context.get('request').user
        return not user.is_anonymous and Follow.objects.filter(
            user=user, author=author.author).exists()

    def get_recipes(self, author):
        """Отображает рецепты в мои подписки."""
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        limit = request.query_params.get('recipes_limit')
        recipes = Recipe.objects.filter(author=author.author)
        if limit:
            recipes = recipes.all()[:int(limit)]
        return FollowRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, author):
        """Показывает количество рецептов у автора."""
        return Recipe.objects.filter(author=author.author).count()
