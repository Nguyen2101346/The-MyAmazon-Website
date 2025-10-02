from django import template
from django.utils.safestring import mark_safe
register = template.Library()

@register.filter
def format_price(value, suffix='đ'):
    try:
        value = int(value) * 1000  # vì bạn lưu theo đơn vị nghìn
        formatted = f"{value:,}".replace(",", ".")
        return mark_safe(f"{formatted}<sup>{suffix}</sup>")
    except (ValueError, TypeError):
        return value