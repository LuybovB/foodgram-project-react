from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


class Ingredient(models.Model):
    """
    Ингридиенты для рецепта.
    Связан с моделю Recipe через М2М - AmountIngredient.
    """
    name = models.CharField(
        'Ингредиент', max_length=200, db_index=True
    )
    measurement_unit = models.CharField(
        'Единица измерения', max_length=200,
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient'
            ),
        )

    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    Тэги для рецептов.
    Связан с моделю Recipe через М2М.
    """
    name = models.CharField(
        'Название',
        max_length=200,
        db_index=True,
        unique=True,
        help_text='Введите название тега',
    )
    color = models.CharField(
        'Цвет в формате HEX без "#"',
        max_length=6,
        unique=True,
        help_text='Цветовой HEX-код например, 49B64E, без "#"'
    )
    slug = models.SlugField(
        'Уникальный слаг',
        max_length=200,
        unique=True,
        db_index=True,
        help_text='Адрес для странице в браузере'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """
    Модель для рецептов.
    Автор (author) рецепта связан с моделю User.
    Тег (tags) связан с моделью Tag через M2M.
    Ингредиенты (ingredients) связаны с моделью Ingredient через M2M.
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    name = models.CharField(
        'Название',
        db_index=True,
        max_length=200,
        help_text='Название рецепта'
    )
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/images/',
        help_text='Изображение ингредиента'
    )
    text = models.TextField('Описание', help_text='Описание рецепта')
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        through='AmountIngredient',
        verbose_name='Список ингредиентов',
        help_text='Выберите ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тег',
        help_text='Выберите тег'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[MinValueValidator(
            1, 'Минимальное время приготовления 1 минута')],
        default=1,
        help_text='Время приготовления в минутах'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class AmountIngredient(models.Model):
    """
    Количество ингридиента в рецерте (гр, мл, шт и т.д.).
    Связан с моделю Recipe через М2М - AmountIngredient.
    """
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингридиент',
        help_text='Выберите ингредиенты',
        related_name='amount_ingredient',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='amount_ingredient',
    )
    amount = models.IntegerField(
        'Количество',
        validators=[MinValueValidator(
            1, 'Минимальное количество ингридеентов 1')],
        default=1,
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты рецепта'
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='unique_ingredients_recipe'
            ),
        )


class Cart(models.Model):
    """
    Список покупок (Продуктовая корзина).
    Пользователь (user) связан с моделю User.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Рецепт',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Корзина'
        verbose_name_plural = 'В корзине'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_for_carts'
            ),
        )


class Favorites(models.Model):
    """
    Список избранного.
    вязан с моделю Recipe через М2М.
    Пользователь (user) связан с моделю User.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ('user',)
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_for_favorite'
            ),
        )
