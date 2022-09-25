from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Favourite, Ingredient, Recipe, Tag
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import CustomUser

from .permissions import AuthorOrReadOnly, IsAdminOrReadOnly, ReadOnly
from .serializers import (FavouriteSerializer, IngredientSerializer,
                          RecipeSerializer, TagSerializer, UserSerializer)


class ListCreateDeleteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    lookup_field = 'slug'
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=name',)


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all().order_by('name')
    serializer_class = IngredientSerializer
    permissions = (permissions.IsAuthenticated, )
    pagination_class = None


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly, )
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = [DjangoFilterBackend]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_permissions(self):
        if self.action == 'retrieve':
            return (ReadOnly(),)
        return super().get_permissions()


class FavouriteView(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def post(self, request, id):
        data = {
            'user': request.user_id,
            'recipe': id
        }
        if not Favourite.objects.filter(
            user=request.user, recipe_id=id
        ).exists():
            serializer = FavouriteSerializer(
                data=data, context={'request': request}
            )
            if serializer.is_valid():
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        if Favourite.objects.filter(
            user=request.user, recipe=recipe
        ).exists():
            Favourite.objects.filter(user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)



