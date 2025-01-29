from django import template
from decimal import Decimal, ROUND_HALF_UP
from trades.models import UserSettings

register = template.Library()

@register.filter
def format_price(value):
    try:
        settings = UserSettings.objects.first()
        decimal_places = settings.decimal_places_price if settings else 2
        formatted_value = Decimal(value).quantize(Decimal(f'1.{"0" * decimal_places}'), rounding=ROUND_HALF_UP)
        return f"{formatted_value}"
    except Exception:
        return value

@register.filter
def format_percentage(value):
    try:
        settings = UserSettings.objects.first()
        decimal_places = settings.decimal_places_percentage if settings else 2
        formatted_value = Decimal(value).quantize(Decimal(f'1.{"0" * decimal_places}'), rounding=ROUND_HALF_UP)
        return f"{formatted_value}%"
    except Exception:
        return value
