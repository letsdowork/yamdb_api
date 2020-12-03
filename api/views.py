from abc import ABC
from django.db.models import Avg, Func
from django.contrib.auth.tokens import default_token_generator
from django.utils.datetime_safe import datetime
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from django.conf import settings
from django.core.mail import send_mail
from rest_framework import status, viewsets
from rest_framework.mixins import (
    CreateModelMixin, ListModelMixin, DestroyModelMixin)
from rest_framework.permissions import (
    IsAuthenticated, IsAdminUser, AllowAny, IsAuthenticatedOrReadOnly)
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.serializers import RefreshToken
from api.filters import TitleFilter
from api.models import Categories, Genres, Titles, Reviews, User
from api.permissions import (
    IsAdminOrReadOnly, IsOwnerOrAdmin, IsOwnerOrAllStaff)
from api.serializers import (
    CategoriesSerializer, GenresSerializer, TitlesReadSerializer,
    ReviewsSerializer, CommentsSerializer, EmailRegistrationSerializer,
    TokenObtainSerializer, UsersSerializer, ProfileSerializer,
    TitlesWriteSerializer)

REVIEW_COMMENT_PERMISSIONS = {
    'create': (IsAuthenticatedOrReadOnly,),
    'retrieve': (AllowAny,),
    'list': (AllowAny,),
    'update': (IsOwnerOrAdmin,),
    'partial_update': (IsOwnerOrAdmin,),
    'destroy': (IsOwnerOrAllStaff,),
}


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (IsAdminUser,)
    lookup_field = 'username'

    def get_serializer_class(self):
        if self.request.user.is_superuser:
            return UsersSerializer
        return ProfileSerializer

    @action(methods=('GET', 'PATCH'), detail=False,
            permission_classes=(IsAuthenticated,), url_path='me')
    def profile(self, request):
        user = get_object_or_404(
            User, pk=self.request.user.pk)
        serializer = self.get_serializer(
            user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class EmailRegistrationView(GenericAPIView):
    serializer_class = EmailRegistrationSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = User.objects.create(
            username=email, email=email, last_login=datetime.now())
        confirmation_code = default_token_generator.make_token(user)
        user.set_password(confirmation_code)
        user.save()
        subject = 'Registration by e-mail'
        from_email = settings.EMAIL_HOST_USER
        to_email = [email]
        message_email = 'confirmation_code %s' % confirmation_code
        send_mail(subject, message_email, from_email, to_email,
                  fail_silently=True)
        return Response(serializer.data)


class TokenObtainView(GenericAPIView):
    serializer_class = TokenObtainSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = get_object_or_404(User, email=email)
        confirmation_code = serializer.validated_data['confirmation_code']
        if user.check_password(confirmation_code):
            token = RefreshToken.for_user(user=user)
            user.set_password(None)
            user.save()
            return Response(
                {'refresh': str(token), 'access': str(token.access_token)})
        confirmation_code = default_token_generator.make_token(user)
        user.set_password(confirmation_code)
        user.save()
        subject = 'a new confirmation_code'
        from_email = settings.EMAIL_HOST_USER
        to_email = [email]
        message_email = 'confirmation_code %s' % confirmation_code
        send_mail(subject, message_email, from_email, to_email,
                  fail_silently=True)

        return Response(
            data={'message': ' wrong or already used confirmation_code, '
                             'check your mail for a new confirmation_code'},
            status=status.HTTP_400_BAD_REQUEST)


class MainMixinClass(CreateModelMixin, ListModelMixin, DestroyModelMixin,
                     GenericViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoriesViewSet(MainMixinClass):
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer


class GenresViewSet(MainMixinClass):
    queryset = Genres.objects.all()
    serializer_class = GenresSerializer


class TitlesViewSet(viewsets.ModelViewSet):
    class Round(Func, ABC):
        function = 'ROUND'
        template = '%(function)s(%(expressions)s, 1)'

    queryset = Titles.objects.annotate(
        rating=Round(Avg('reviews__score')))
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    filterset_fields = ('genre', 'category', 'year', 'name',)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return TitlesWriteSerializer
        return TitlesReadSerializer


class ReviewsViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewsSerializer

    def get_permissions(self):
        self.permission_classes = REVIEW_COMMENT_PERMISSIONS[self.action]
        return super(self.__class__, self).get_permissions()

    def get_title_or_404(self):
        return get_object_or_404(Titles, id=self.kwargs['title_id'])

    def get_queryset(self):
        title = self.get_title_or_404()
        return title.reviews.all()

    def perform_create(self, serializer):
        title = self.get_title_or_404()
        serializer.save(author=self.request.user, title=title)


class CommentsViewSet(viewsets.ModelViewSet):
    serializer_class = CommentsSerializer

    def get_permissions(self):
        self.permission_classes = REVIEW_COMMENT_PERMISSIONS[self.action]
        return super(self.__class__, self).get_permissions()

    def get_review_or_404(self):
        review = get_object_or_404(
            Reviews, id=self.kwargs['review_id'],
            title__id=self.kwargs['title_id'])
        return review

    def get_queryset(self):
        review = self.get_review_or_404()
        return review.comments.all()

    def perform_create(self, serializer):
        review = self.get_review_or_404()
        serializer.save(author=self.request.user, review=review)
