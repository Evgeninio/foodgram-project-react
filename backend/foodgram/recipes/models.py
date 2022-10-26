from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from users.models import CustomUser

BREAKFAST = '#FBCEB1'
LUNCH = '#FAE7B5'
DINNER = '#9ACEEB'

CHOICES = (
    (BREAKFAST, 'Абрикосовый'),
    (LUNCH, 'Бананамания'),
    (DINNER, 'СинийВасилек')
)


class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(
        'Название',
        max_length=256
    )
    color = models.CharField(
        max_length=16,
        unique=True,
        choices=CHOICES
    )
    slug = models.SlugField(
        'slug',
        max_length=50,
        unique=True,
        db_index=True
    )

    def __str__(self):
        return f'{self.id}, {self.name}, {self.color}, {self.slug}'

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'


class Ingredient(models.Model):
    name = models.TextField(
        'Название ингредиента',
        max_length=256
    )
    measurement_unit = models.TextField(
        'Единица измерения',
        max_length=256
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

        constraints = (
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='ingredient'
            ),
        )


class Recipe(models.Model):

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    tags = models.ManyToManyField(
        Tag,
        db_index=True,
        related_name='recipes',
        verbose_name='Тэг'
    )
    name = models.TextField(
        max_length=256
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        default=None
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                1,
                message='Время готовки не может быть меньше одной минуты'
            )
        ]
    )
    text = models.TextField(
        'Текст рецепта'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='recipe_ingredients'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_ingredients'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Колличетсво',
        validators=(MinValueValidator(
            1, message='Количество ингредиентов не может быть меньше нуля'),)
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'ingredient'],
            name='unique_recipe_ingredients'),
            models.CheckConstraint(
                check=models.Q(amount=1),
                name='amount_1')
        ]
        verbose_name = 'Ингредиент в рецептах'
        verbose_name_plural = 'Ингредиенты в рецептах'
        ordering = ['id']

    def __str__(self):
        return f'{self.ingredient} in {self.recipe}'


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='favorite'
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorite'
    )

    class Meta:
        verbose_name = 'Избранный'
        verbose_name_plural = 'Избранные'
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            ),
        )


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shopping_cart'
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_cart'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            ),
        )
