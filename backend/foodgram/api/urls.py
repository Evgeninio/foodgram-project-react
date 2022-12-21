from django.urls import include, path
from rest_framework import routers

from .views import (CustomUserViewSet, FollowViewSet, IngredientViewSet,
                    RecipeViewSet, TagViewSet, UserViewSet)
# IngredientViewSet,
router = routers.DefaultRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register('users', UserViewSet, basename='users')
router.register(r'users', CustomUserViewSet)

urlpatterns = [
    path(
        'users/subscriptions/',
        FollowViewSet.as_view({'get': 'list'}),
        name='subscriptions',
    ),
    path(
        'users/<int:user_id>/subscribe/',
        FollowViewSet.as_view({'post': 'create', 'delete': 'delete'}),
        name='subscribe',
    ),
    path('', include(router.urls)),
]
