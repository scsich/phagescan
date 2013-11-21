
from django.template import Library

register = Library()

@register.filter(name="order_by_engine")
def order_by_engine(queryset):
	return queryset.order_by("scanner_type__name")

