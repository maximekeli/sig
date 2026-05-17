import django_filters

from .models import SoilPoint


class SoilPointFilter(django_filters.FilterSet):
    ph_min = django_filters.NumberFilter(field_name='ph', lookup_expr='gte')
    ph_max = django_filters.NumberFilter(field_name='ph', lookup_expr='lte')
    soil_type = django_filters.CharFilter(field_name='soil_type')
    fertility_class = django_filters.CharFilter(field_name='fertility_class')
    collected_after = django_filters.DateFilter(field_name='collected_at', lookup_expr='gte')
    collected_before = django_filters.DateFilter(field_name='collected_at', lookup_expr='lte')
    is_validated = django_filters.BooleanFilter(field_name='is_validated')

    class Meta:
        model = SoilPoint
        fields = ['soil_type', 'fertility_class', 'is_validated', 'zone']
