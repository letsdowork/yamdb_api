from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class Roles(models.TextChoices):
        USER = 'user', _('user')
        MODERATOR = 'moderator', _('moderator')
        ADMIN = 'admin', _('admin')
    role = models.CharField(
        max_length=10, choices=Roles.choices, default=Roles.USER)
    bio = models.CharField(max_length=320, blank=True)

    def is_moderator(self):
        return self.role == self.Roles.MODERATOR

    def is_admin(self):
        return self.role == self.Roles.ADMIN


class Genres(models.Model):
    name = models.CharField(max_length=200, verbose_name='Genre name')
    slug = models.SlugField(unique=True, verbose_name='Genre slug')

    class Meta:
        verbose_name = 'Genre'
        verbose_name_plural = 'Genres'

    def __str__(self):
        return self.name


class Categories(models.Model):
    name = models.CharField(max_length=200, verbose_name='Category name')
    slug = models.SlugField(unique=True, verbose_name='Category slug')

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Titles(models.Model):
    name = models.CharField(
        max_length=200, verbose_name='Title')
    year = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(2100)],
        verbose_name='Year', null=True, blank=True, db_index=True)
    description = models.TextField(verbose_name='Description', null=True)
    category = models.ForeignKey(
        Categories, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='category_titles', verbose_name='Category')
    genre = models.ManyToManyField(Genres)

    class Meta:
        verbose_name = 'Title'
        verbose_name_plural = 'Titles'
        ordering = ['id']

    def __str__(self):
        return self.name


class Reviews(models.Model):
    title = models.ForeignKey(
        Titles, on_delete=models.CASCADE, related_name='reviews',
        null=True)
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)])
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Publication date')

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:50] + '...'


class Comments(models.Model):
    review = models.ForeignKey(
        Reviews, on_delete=models.CASCADE, related_name='comments', null=True)
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Publication date')

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:50] + '...'
