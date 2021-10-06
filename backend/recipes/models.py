from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db.models import (CASCADE, CharField, DateTimeField, ForeignKey,
                              ImageField, ManyToManyField, Model,
                              PositiveIntegerField, PositiveSmallIntegerField,
                              SlugField, TextField, UniqueConstraint)

User = get_user_model()


class Ingredient(Model):

    """
    Модель ингредиентов, используемых в рецептах
    """

    name = CharField(
        max_length=150,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Название ингредиента'
    )

    measurement_unit = CharField(
        max_length=150,
        blank=False,
        null=False,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} - {self.measurement_unit}'


class Tag(Model):

    """
    Модель тегов, отвечающая за уникальную сортировку
    """

    name = CharField(
        max_length=150,
        unique=True,
        null=False,
        blank=False,
        verbose_name='Имя тега'
    )

    color_hex = CharField(
        max_length=10,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Цвет тега'
    )

    slug = SlugField(
        max_length=150,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Слаг тега'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(Model):

    """
    Модель рецептов
    """

    name = CharField(
        max_length=150,
        verbose_name='Название рецепта',
        null=False,
        blank=False
    )

    author = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )

    ingredients = ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Ингредиенты рецепта'
    )

    tags = ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги рецепта'
    )

    image = ImageField(
        blank=True,
        null=True,
        upload_to='media/',
        verbose_name='Иллюстрация рецепта'
    )

    text = TextField(
        verbose_name='Описание рецепта',
        blank=False,
        null=False
    )

    cooking_time = PositiveSmallIntegerField(
        blank=False,
        null=False,
        validators=[MinValueValidator(1)],
        verbose_name='Время приготовления (мин)'
    )

    pub_date = DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class IngredientInRecipe(Model):

    """
    Ингредиенты для конкретного рецепта
    """

    ingredient = ForeignKey(
        Ingredient,
        on_delete=CASCADE,
        verbose_name='Ингредиент',
    )
    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        verbose_name='Рецепт'
    )
    amount = PositiveIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1)],
    )

    def __str__(self):
        return f'{self.recipe}: {self.ingredient} в объеме: {self.amount}'

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        unique_together = ('ingredient', 'recipe')
        ordering = ('recipe__name',)


class Favorite(Model):

    """
    Модель избранных рецептов
    """

    user = ForeignKey(
        User,
        on_delete=CASCADE,
        verbose_name='Пользователь'
    )

    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    pub_date = DateTimeField(
        auto_now_add=True,
        verbose_name='Дата любви',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        ordering = ('recipe__name',)
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'Рецепт {self.recipe} нравится {self.user}'


class Cart(Model):

    """
    Список необходимых покупок
    """

    user = ForeignKey(
        User,
        on_delete=CASCADE,
        verbose_name='Пользователь'
    )
    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        related_name='cart',
        verbose_name='Рецепт для покупки'
    )
    pub_date = DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзины покупок'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_cart'
            )
        ]
