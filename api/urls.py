from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import (
    CategoriesViewSet, GenresViewSet, TitlesViewSet, ReviewsViewSet,
    CommentsViewSet, EmailRegistrationView, TokenObtainView, UsersViewSet)

router = DefaultRouter()
router.register(r'users', UsersViewSet, basename='Users')
router.register('categories', CategoriesViewSet)
router.register('genres', GenresViewSet)
router.register('titles', TitlesViewSet)
router.register(
    r'titles/(?P<title_id>[0-9]+)/reviews',
    ReviewsViewSet,
    basename='review_set')
router.register(
    r'titles/(?P<title_id>[0-9]+)/reviews/(?P<review_id>[0-9]+)/comments',
    CommentsViewSet,
    basename='comment_set')

auth_urlpatterns = [
    path('email/', EmailRegistrationView.as_view()),
    path('token/', TokenObtainView.as_view()),
]

urlpatterns = [
    path('v1/auth/', include(auth_urlpatterns)),
    path('v1/', include(router.urls)),
]
