import base64

from django.core.files.base import ContentFile
from recipes.models import (CHOICES, Ingredient, Recipe,
                            RecipeIngredient, Tag)
from rest_framework import serializers
from users.models import CustomUser
from djoser.serializers import UserCreateSerializer, UserSerializer


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    color = serializers.ChoiceField(choices=CHOICES)

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientGetSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'amount', 'measurement_unit')


class RecipeIngredientPostSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


# class FavouriteSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Favourite
#         fields = ('user', 'recipe')
#
#     def validate(self, data):
#         request = self.context.get('request')
#         if not request or request.user.is_anonymous:
#             return False
#         recipe = data['recipe']
#         if Favourite.objects.filter(user=request.user, recipe=recipe).exists():
#             raise serializers.ValidationError({
#                 'status': 'Рецепт уже в избранном'
#             })
#         return data
#
#     def to_representation(self, instance):
#         request = self.context.get('request')
#         context = {'request': request}
#         return RecipeSerializer(
#             instance.recipe, context=context).data
#
#
# class ShoppingCartSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ShoppingCart
#         fields = ('user', 'recipe')
#
#     def to_representation(self, instance):
#         request = self.context.get('request')
#         context = {'request': request}
#         return RecipeSerializer(instance.recipe, context=context).data


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        extra_kwargs = {'password': {'write_only': True}}

        def create(self, validated_data):
            user = CustomUser.objects.create(
                email=validated_data['email'],
                username=validated_data['username'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
            )
            user.set_password(validated_data['password'])
            user.save()
            return user


class CustomUserSerializer(UserSerializer):

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name'
        )


class RecipeGetSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField(
        method_name='get_ingredients'
    )
    tags = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField(required=False, allow_null=True)
    # is_favourited = serializers.SerializerMethodField()
    # is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'tags', 'author', 'image', 'ingredients',
                  'name', 'text', 'cooking_time')
        #'is_favourited', 'is_in_shopping_cart',
        model = Recipe

    def get_ingredients(self, recipe):
        return RecipeIngredientGetSerializer(
            RecipeIngredient.objects.filter(recipe=recipe),
            many=True
        ).data

    # def get_is_favourited(self, obj):
    #     request = self.context.get('request')
    #     if not request or request.user.is_anonymous:
    #         return False
    #     return Favourite.objects.filter(user=request.user, recipe=obj).exists()
    #
    # def get_is_in_shopping_cart(self, obj):
    #     request = self.context.get('request')
    #     if not request or request.user.is_anonymous:
    #         return False
    #     return ShoppingCart.objects.filter(
    #         user=request.user, recipe=obj).exists()

    # def validate(self, data):
    #     ingredients = data.get('ingredients')
    #     for ingredient in ingredients:
    #         if not Ingredient.objects.filter(
    #                 id=ingredient['id']).exists():
    #             raise serializers.ValidationError({
    #                 'ingredients': f'Ингредиента с id - {ingredient["id"]} нет'
    #             })
    #     if len(ingredients) != len(set([item['id'] for item in ingredients])):
    #         raise serializers.ValidationError(
    #             'Ингредиенты не должны повторяться!')
    #     tags = data.get('tags')
    #     if len(tags) != len(set([item for item in tags])):
    #         raise serializers.ValidationError({
    #             'tags': 'Тэги не должны повторяться!'})
    #     amounts = data.get('ingredients')
    #     if [item for item in amounts if item['amount'] < 1]:
    #         raise serializers.ValidationError({
    #             'amount': 'Минимальное количество ингредиента 1'
    #         })
    #     cooking_time = data.get('cooking_time')
    #     if cooking_time < 1:
    #         raise serializers.ValidationError({
    #             'cooking_time': 'Минимальное время приготовления 1 минута'
    #         })
    #     return data


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Используется на запись и редактирование рецепта."""

    author = CustomUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = RecipeIngredientPostSerializer(many=True)
    image = Base64ImageField(required=True)

    @staticmethod
    def create_ingredients(ingredients, recipe):
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                amount=ingredient['amount'],
                #ingredient=Ingredient.objects.get(id=ingredient['id']),
                ingredient=ingredient['id'],
            ) for ingredient in ingredients
        ])

    @staticmethod
    def create_tags(tags, recipe):
        for tag in tags:
            recipe.tags.add(tag)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user,
            **validated_data
        )
        self.create_ingredients(ingredients, recipe)
        self.create_tags(tags, recipe)
        return recipe

    # def update(self, recipe, validated_data):
    #     recipe.tags.clear()
    #     RecipeIngredient.objects.filter(recipe=recipe).delete()
    #     ingredients = validated_data.pop('ingredients')
    #     tags = validated_data.pop('tags')
    #     self.create_ingredients_tags(recipe, ingredients, tags)
    #     return super().update(recipe, validated_data)

    class Meta:
        model = Recipe
        fields = (
            'author', 'name', 'cooking_time',
            'tags', 'text', 'ingredients',
            'image'
        )
