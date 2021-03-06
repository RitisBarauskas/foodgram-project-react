from typing import Optional

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Exists, OuterRef
from django.utils.text import slugify

User = get_user_model()


class Ingredient(models.Model):

    """
    Модель ингредиентов, используемых в рецептах
    """

    name = models.CharField(
        max_length=150,
        verbose_name='Название ингредиента'
    )

    measurement_unit = models.CharField(
        max_length=150,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} - {self.measurement_unit}'


class Tag(models.Model):

    """
    Модель тегов, отвечающая за уникальную сортировку
    """

    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Имя тега'
    )

    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name='Цвет тега'
    )

    slug = models.SlugField(
        max_length=150,
        unique=True,
        verbose_name='Слаг тега'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class RecipeQuerySet(models.QuerySet):
    def add_user_annotation(self, user_id: Optional[int]):
        return self.annotate(
            is_favorited=Exists(
                Favorite.objects.filter(
                    user_id=user_id, recipe__pk=OuterRef('pk')
                )
            ),
            is_in_shopping_cart=Exists(
                ShoppingCart.objects.filter(
                    user_id=user_id, recipe__pk=OuterRef('pk')
                )
            ),
        )


class Recipe(models.Model):

    """
    Модель рецептов
    """

    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='ingredients',
        through='IngredientInRecipe',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Ингредиенты рецепта',
    )

    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги рецепта',
    )

    image = models.ImageField(
        upload_to='recipes/images',
        verbose_name='Иллюстрация рецепта',
    )

    text = models.TextField(
        verbose_name='Описание рецепта',
        blank=False,
        null=False,
    )

    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Время приготовления (мин)',
    )

    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    objects = RecipeQuerySet.as_manager()

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not kwargs.pop('from_admin', False):
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class IngredientInRecipe(models.Model):

    """
    Ингредиенты для конкретного рецепта
    """

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_amount',
        verbose_name='Ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_amount',
        verbose_name='Рецепт',
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        unique_together = ('ingredient', 'recipe')
        ordering = ('recipe__name',)

    def __str__(self):
        return f'{self.recipe}: {self.ingredient} в объеме: {self.amount}'


class Favorite(models.Model):

    """
    Модель избранных рецептов
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата любви',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        ordering = ('recipe__name',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'Рецепт {self.recipe} нравится {self.user}'


class ShoppingCart(models.Model):

    """
    Список необходимых покупок
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт для покупки',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзины покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]
