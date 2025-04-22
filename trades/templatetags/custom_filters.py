from django import template
from decimal import Decimal, ROUND_HALF_UP

register = template.Library()

@register.filter
def format_price(value):
    try:
        # Убедимся, что значение не пустое и является числом
        if value is None or value == '':
            return value
        # Устанавливаем фиксированное количество знаков после запятой
        decimal_places = 1  # 1 знак после запятой
        formatted_value = Decimal(value).quantize(Decimal(f'1.{"0" * decimal_places}'), rounding=ROUND_HALF_UP)
        return f"{formatted_value}"
    except (ValueError, TypeError):
        # Если значение некорректное, возвращаем исходное
        return value

@register.filter
def format_percentage(value):
    try:
        if value is None or value == '':
            return value
        # Устанавливаем фиксированное количество знаков после запятой для наценки
        decimal_places = 1  # 1 знак после запятой
        formatted_value = Decimal(value).quantize(Decimal(f'1.{"0" * decimal_places}'), rounding=ROUND_HALF_UP)
        return f"{formatted_value}%"
    except (ValueError, TypeError):
        return value


@register.filter
def get_item(dictionary, key):
    try:
        return dictionary.get(str(key))
    except (AttributeError, TypeError):
        return ''

@register.filter
def mul(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''
