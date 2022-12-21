from django.contrib import admin

from .models import Favorite, Recipe, Ingredient, ShoppingCart, Tag

# Ingredient,


class RecipeIngredientAdmin(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 1
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientAdmin]
    list_display = (
        'id', 'name', 'author', 'text'
    )
    list_filter = ('author', 'name', 'tags')
    filter_vertical = ('tags', )
    search_fields = ('name', )
    empty_value_display = 'пусто'


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name'
    )
    # 'measurement_unit'
    search_fields = ('name', )
    list_filter = ('name', )
    empy_value_display = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'color', 'slug'
    )
    search_fields = ('name', 'slug')
    list_filter = ('name', 'slug')
    empy_value_display = '-пусто-'


class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'recipe'
    )
    search_fields = ('favorited_recipe', )
    list_filter = ('id', 'user', 'recipe')
    empy_value_display = '-пусто-'


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    empy_value_display = '-пусто-'


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
