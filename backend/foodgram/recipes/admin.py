from django.contrib import admin

from .models import (Favourite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class RecipeIngredientAdmin(admin.TabularInline):
    model = RecipeIngredient
    autocomplete_fields = ('ingredient', )
    list_display = (
        'name', 'measurement_unit', 'amount'
    )
    search_fields = ('name', )


class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientAdmin, ]
    list_display = (
        'id', 'name', 'author', 'text', 'count_favourites'
    )
    list_filter = ('author', 'name', 'tags')
    readonly_fields = ('count_favourites', )
    filter_vertical = ('tags', )
    search_fields = ('name', )
    empty_value_display = 'пусто'

    @staticmethod
    def count_favourites(obj):
        return obj.favourite_recipe.count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'measurement_unit'
    )
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


class FavouriteAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'recipe'
    )
    search_fields = ('favourited_recipe', )
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
admin.site.register(Favourite, FavouriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)

