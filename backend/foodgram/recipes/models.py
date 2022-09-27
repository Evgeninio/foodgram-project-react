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
    id = models.AutoField(primary_key=True)
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


class Recipe(models.Model):
    id = models.AutoField(primary_key=True)
    tags = models.ManyToManyField(
        Tag,
        db_index=True,
        related_name='recipes',
        verbose_name='Тэг'
    )
    author = models.ForeignKey(
        CustomUser,
        verbose_name='user',
        related_name='recipes',
        on_delete=models.CASCADE,
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
        through='RecipeIngredient'
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
    id = models.AutoField(primary_key=True)
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='ingredient'
    )
    amount = models.PositiveIntegerField(verbose_name='Колличетсво')

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient'
            ),
        )


class Favourite(models.Model):
    id = models.AutoField(primary_key=True)
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='favourite_recipe'
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favourite_user'
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
    id = models.AutoField(primary_key=True)
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shoppingcart_recipe'
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='User_shopping_cart'
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
