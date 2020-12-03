from django.contrib import admin
from .models import User, Categories, Genres, Titles, Reviews, Comments


class UserAdmin(admin.ModelAdmin):
    fields = ('email', 'username', 'role', 'is_superuser')
    list_display = ('email', 'username', 'role', 'is_superuser')
    search_fields = ('username', 'email')
    list_filter = ('is_superuser', 'role')


class CategoriesGenresAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('name', 'slug')


class TitlesAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'description', 'category', 'genres')
    search_fields = ('name', 'year', 'category__name', 'genre__name')
    list_filter = ('year', 'category__name', 'genre__name')
    empty_value_display = '-пусто-'

    def genres(self, title):
        return ', '.join([genre.name for genre in title.genre.all()])


class ReviewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'text', 'author', 'score', 'pub_date')
    search_fields = ('text', 'author__username')
    list_filter = ('score', 'pub_date')


class CommentsAdmin(admin.ModelAdmin):
    list_display = ('review', 'text', 'author', 'pub_date')
    search_fields = ('text', 'author__username')
    list_filter = ('pub_date',)


admin.site.register(User, UserAdmin)
admin.site.register(Genres, CategoriesGenresAdmin)
admin.site.register(Categories, CategoriesGenresAdmin)
admin.site.register(Titles, TitlesAdmin)
admin.site.register(Reviews, ReviewsAdmin)
admin.site.register(Comments, CommentsAdmin)
