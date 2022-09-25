from django.core.validators import MinValueValidator
from django.db import models
from users.models import CustomUser

CHOICES = (
        ('Gray', 'Серый'),
        ('Black', 'Чёрный'),
        ('White', 'Белый')
)


class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(
        'Название',
        max_length=256
    )
    color = models.CharField(max_length=16)
    slug = models.SlugField(
        'slug',
        max_length=50,
        unique=True,
        db_index=True
    )

    def __str__(self):
        return f'{self.id}, {self.name}, {self.color}, {self.slug}'


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


class Recipe(models.Model):
    id = models.AutoField(primary_key=True)
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        db_index=True,
        related_name='recipes',
        verbose_name='Тэг'
    )
    author = models.ForeignKey(
        CustomUser,
        verbose_name='user',
        related_name='recipes',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    name = models.TextField(
        max_length=256
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


class RecipeIngredient(models.Model):
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


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_tags'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тэг',
        related_name='tag'
    )


class Favourite(models.Model):
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
        related_name='Favourite_user'
    )


class ShoppingCart(models.Model):
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
