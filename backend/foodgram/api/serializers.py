import base64

from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipes.models import (CHOICES, Favorite, Recipe, Ingredient, RecipeIngredient,
                             ShoppingCart, Tag)
from users.models import CustomUser, Follow

# Ingredient, RecipeIngredient, в импорт моделей


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
        fields = ('id', 'name')
        # 'measurement_unit')


class RecipeIngredientGetSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    # measurement_unit = serializers.ReadOnlyField(
    #     source='ingredient.measurement_unit'
    # )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'amount')
                  # 'measurement_unit')


class RecipeIngredientPostSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class ShortRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        if Favorite.objects.filter(
                user=self.context.get('request').user,
                recipe=data['recipe']
        ).exists():
            raise serializers.ValidationError({
                'status': 'Уже добавлен'
            })
        return data

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


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
        method_name='get_ingredients', read_only=True
    )
    tags = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField(required=False, allow_null=True)
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited',
        read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id',
            'tags',
            'author',
            'image',
            'name',
            'text',
            'is_favorited',
            'ingredients',
            'cooking_time',
            'is_in_shopping_cart'
        )
        # 'ingredients',
        model = Recipe

    def get_ingredients(self, recipe):
        return RecipeIngredientGetSerializer(
            RecipeIngredient.objects.filter(recipe=recipe),
            many=True
        ).data

    def get_is_favorited(self, recipe):
        if self.context.get('request').user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=self.context.get('request').user,
            recipe=recipe
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj).exists()

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

    author = CustomUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = RecipeIngredientPostSerializer(
        many=True
    )
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'author', 'name', 'cooking_time',
            'tags', 'text',
            'image',
            'ingredients'
        )
        # 'ingredients',

    # def validate(self, data):
    #     ingredients = self.initial_data['ingredients']
    #     ingredients_list = []
    #     if not ingredients:
    #         raise serializers.ValidationError({
    #             'ingredients': 'Добавьте ингредиенты'})
    #     for ingredient in ingredients:
    #         current_ingredient = get_object_or_404(
    #             Ingredient, id=ingredient['id']
    #         )
    #         if current_ingredient in ingredients_list:
    #             raise serializers.ValidationError({
    #                 'ingredients': 'Ингредиенты должны быть уникальными'
    #             })
    #         if int(ingredient['amount']) < 0:
    #             raise serializers.ValidationError({
    #                 'amount': 'Количество ингредиента '
    #                           'не может быть меньше нуля!'
    #             })
    #         ingredients_list.append(current_ingredient)
    #     tags = data['tags']
    #     if not tags:
    #         raise serializers.ValidationError({
    #             'tags': 'Нужно выбрать хотя бы один тег!'
    #         })
    #     tags_list = []
    #     for tag in tags:
    #         if tag in tags_list:
    #             raise serializers.ValidationError({
    #                 'tags': 'Теги должны быть уникальными!'
    #             })
    #         tags_list.append(tag)
    #     cooking_time = self.initial_data['cooking_time']
    #     if int(cooking_time) <= 0:
    #         raise serializers.ValidationError({
    #             'cooking_time': 'Время приготовления должно быть больше 0!'
    #         })
    #     return data

    @staticmethod
    def create_ingredients(recipe, ingredients):
        for ingredient in ingredients:
            RecipeIngredient.objects.bulk_create([RecipeIngredient(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                amount=ingredient.get('amount'))

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
        self.create_tags(tags, recipe)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, recipe, validated_data):
        recipe.tags.clear()
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        self.create_tags(tags, recipe)
        self.create_ingredients(recipe, ingredients)
        return super().update(recipe, validated_data)


class FollowListSerializer(serializers.ModelSerializer):
    """ Сериализация списка на кого подписан пользователь"""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_recipes_count(self, following):
        return Recipe.objects.filter(author=following).count()

    def get_recipes(self, following):
        queryset = self.context.get('request')
        recipes_limit = queryset.query_params.get('recipes_limit')
        if not recipes_limit:
            return ShortRecipeSerializer(
                following.author.all(),
                many=True, context={'request': queryset}
            ).data
        return ShortRecipeSerializer(
            following.author.all()[:int(recipes_limit)], many=True,
            context={'request': queryset}
        ).data

    def get_is_subscribed(self, following):
        return Follow.objects.filter(
            user=self.context.get('request').user,
            following=following
        ).exists()


class FollowSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField(
        method_name='get_recipes',
        read_only=True
    )
    recipes_count = serializers.ReadOnlyField(source='recipes.count')
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed',
        read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        ]

    def get_recipes(self, obj):
        request = self.context.get('request')
        if request.GET.get('recipes_limit'):
            recipes_limit = int(request.GET.get('recipes_limit'))
            queryset = Recipe.objects.filter(
                author__id=obj.id).order_by('id')[:recipes_limit]
        else:
            queryset = Recipe.objects.filter(
                following__id=obj.id).order_by('id')
        return ShortRecipeSerializer(queryset, many=True).data

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user, following=obj).exists()


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, data):
        if ShoppingCart.objects.filter(
                user=self.context['request'].user,
                recipe=data['recipe']
        ):
            raise serializers.ValidationError('Уже добавлен')
        return data

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
