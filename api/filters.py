from django_filters import FilterSet, CharFilter

from api.models import Titles


class TitleFilter(FilterSet):
    genre = CharFilter(field_name='genre__slug', lookup_expr='icontains')
    category = CharFilter(field_name='category__slug', lookup_expr='iexact')
    year = CharFilter(lookup_expr='iexact')
    name = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Titles
        fields = ('genre', 'category', 'year', 'name')
