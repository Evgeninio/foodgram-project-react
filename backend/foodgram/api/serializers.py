from recipes.models import (CHOICES, Favourite, Ingredient, Recipe,
                            RecipeIngredient, RecipeTag, ShoppingCart, Tag)
from rest_framework import serializers
from users.models import CustomUser


class TagSerializer(serializers.ModelSerializer):
    color = serializers.ChoiceField(choices=CHOICES)

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class RecipeTagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = RecipeTag


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
    tags = serializers.StringRelatedField(many=True)
    author = UserSerializer(read_only=True)
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
