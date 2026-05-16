from .models import Course
import django_filters

class CourseFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    difficulty_level = django_filters.CharFilter(lookup_expr='exact')
    price = django_filters.NumberFilter(lookup_expr='gte')
    price__lte = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    
    class Meta:
        model = Course
        fields = ['title', 'difficulty_level', 'price']
