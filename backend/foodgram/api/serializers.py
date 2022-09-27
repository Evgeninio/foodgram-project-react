import base64

from recipes.models import (CHOICES, Favourite, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)
from rest_framework import serializers
from users.models import CustomUser
from django.core.files.base import ContentFile


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
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class RecipeIngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = RecipeIngredient
        fields = '__all__'
        read_only_fields = ('recipe',)


class FavouriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favourite
        fields = ('user', 'recipe')

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipe = data['recipe']
        if Favourite.objects.filter(user=request.user, recipe=recipe).exists():
            raise serializers.ValidationError({
                'status': 'Рецепт уже в избранном'
            })
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializer(
            instance.recipe, context=context).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializer(instance.recipe, context=context).data


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(
        many=True,
        read_only=True,
        source='recipe_ingredients'
    )
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    image = Base64ImageField(required=False, allow_null=True)
    is_favourited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favourited', 'is_in_shopping_cart',
                  'name', 'text', 'cooking_time')
        model = Recipe

    def get_is_favourited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favourite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj).exists()

    def update(self, instance, validated_data):
        instance.author = validated_data.get('author', instance.author)
        instance.tags = validated_data.get('tags', instance.tags)
        instance.is_favourited = validated_data.get(
            'is_favourited', instance.is_favourited
            )
        instance.is_in_shopping_cart = validated_data.get(
            'is_in_shopping_cart', instance.is_in_shopping_cart
        )
        instance.image = validated_data.get('image', instance.image)
        if 'ingredients' in validated_data:
            ingredients_data = validated_data.pop('ingredients')
            lst = []
            for ingredient in ingredients_data:
                current_ingredient, status = Ingredient.objects.get_or_create(
                    **ingredient
                    )
                lst.append(current_ingredient)
            instance.ingredients.set(lst)

        instance.save()
        return instance

    def validate(self, data):
        ingredients = data.get('ingredients')
        for ingredient in ingredients:
            if not Ingredient.objects.filter(
                    id=ingredient['id']).exists():
                raise serializers.ValidationError({
                    'ingredients': f'Ингредиента с id - {ingredient["id"]} нет'
                })
        if len(ingredients) != len(set([item['id'] for item in ingredients])):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться!')
        tags = data.get('tags')
        if len(tags) != len(set([item for item in tags])):
            raise serializers.ValidationError({
                'tags': 'Тэги не должны повторяться!'})
        amounts = data.get('ingredients')
        if [item for item in amounts if item['amount'] < 1]:
            raise serializers.ValidationError({
                'amount': 'Минимальное количество ингредиента 1'
            })
        cooking_time = data.get('cooking_time')
        if cooking_time < 1:
            raise serializers.ValidationError({
                'cooking_time': 'Минимальное время приготовления 1 минута'
            })
        return data
