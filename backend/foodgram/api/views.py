from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Ingredient, Recipe, Tag
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import CustomUser

from .permissions import AuthorOrReadOnly, IsAdminOrReadOnly
from .serializers import (IngredientSerializer,
                          RecipeGetSerializer, TagSerializer,
                          CustomUserSerializer, RecipeCreateSerializer)
from djoser.views import UserViewSet


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


class CustomUserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (permissions.AllowAny, )


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all().order_by('name')
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly, )
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGetSerializer
        else:
            return RecipeCreateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context



# class FavouriteView(APIView):
#     permission_classes = [permissions.IsAuthenticated, ]
#
#     def post(self, request, id):
#         data = {
#             'user': request.user_id,
#             'recipe': id
#         }
#         if not Favourite.objects.filter(
#             user=request.user, recipe_id=id
#         ).exists():
#             serializer = FavouriteSerializer(
#                 data=data, context={'request': request}
#             )
#             if serializer.is_valid():
#                 return Response(
#                     serializer.data, status=status.HTTP_201_CREATED
#                 )
#         return Response(status=status.HTTP_400_BAD_REQUEST)
#
#     def delete(self, request, id):
#         recipe = get_object_or_404(Recipe, id=id)
#         if Favourite.objects.filter(user=request.user, recipe=recipe):
#             Favourite.objects.filter(user=request.user, recipe=recipe).delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         return Response(status=status.HTTP_400_BAD_REQUEST)
