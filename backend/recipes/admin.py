from django.contrib import admin
from foodgram.settings import VALUE_DISPLAY
from recipes.models import AmountIngredient, Favorites, Ingredient, Recipe, Tag
from users.models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Отображает пользователей в панели администратора."""
    list_display = ('username', 'first_name', 'last_name', 'email')
    list_filter = ('email', 'username', )
    empty_value_display = VALUE_DISPLAY


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Отображает подписки на авторов в панели администратора."""
    list_display = ('user', 'author')
    search_fields = ('user',)
    list_filter = ('user', )
    empty_value_display = VALUE_DISPLAY


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Отображает ингредиенты в панели администратора."""
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('name', 'measurement_unit')
    empty_value_display = VALUE_DISPLAY


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Отображает теги в панели администратора."""
    list_display = ('name', 'slug', 'color')
    search_fields = ('name',)
    empty_value_display = VALUE_DISPLAY


class IngredientLnline(admin.TabularInline):
    model = AmountIngredient
    extra = 10


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    from django.contrib import admin
    from django.contrib.admin import display

    from .models import (Favourite, Ingredient, IngredientInRecipe, Recipe,
                         ShoppingCart, Tag)

    @admin.register(Recipe)
    class RecipeAdmin(admin.ModelAdmin):
        list_display = ('name', 'id', 'author', 'added_in_favorites')
        readonly_fields = ('added_in_favorites',)
        list_filter = ('author', 'name', 'tags',)

        @display(description='Количество в избранных')
        def added_in_favorites(self, obj):
            return obj.favorites.count()

    @admin.register(Ingredient)
    class IngredientAdmin(admin.ModelAdmin):
        list_display = ('name', 'measurement_unit',)
        list_filter = ('name',)

    @admin.register(Tag)
    class TagAdmin(admin.ModelAdmin):
        list_display = ('name', 'color', 'slug',)

    @admin.register(ShoppingCart)
    class ShoppingCartAdmin(admin.ModelAdmin):
        list_display = ('user', 'recipe',)

    @admin.register(Favourite)
    class FavouriteAdmin(admin.ModelAdmin):
        list_display = ('user', 'recipe',)

    @admin.register(IngredientInRecipe)
    class IngredientInRecipe(admin.ModelAdmin):
        list_display = ('recipe', 'ingredient', 'amount',)
