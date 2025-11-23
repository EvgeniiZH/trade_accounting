from django import template
from decimal import Decimal, ROUND_HALF_UP
from urllib.parse import urlencode
from collections import OrderedDict

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

@register.filter
def add_class(field, css):
    """
    Добавляет CSS-класс к полю формы.
    Использование: {{ form.field|add_class:"form-control" }}
    """
    try:
        return field.as_widget(attrs={"class": css})
    except AttributeError:
        return field

@register.simple_tag(takes_context=True)
def querystring(context, **kwargs):
    """
    Создаёт query string из текущих GET параметров, обновляя указанные значения.
    Использование: {% querystring page=2 %}
    """
    request = context.get('request')
    if not request:
        return urlencode(kwargs)
    
    # Получаем текущие GET параметры как словарь
    # QueryDict можно итерировать, но для urlencode нужен обычный dict
    params = {}
    for key in request.GET:
        # Для параметров с несколькими значениями берем все
        values = request.GET.getlist(key)
        if len(values) == 1:
            params[key] = values[0]
        else:
            # Для множественных значений создаём список
            params[key] = values
    
    # Обновляем указанными значениями
    for key, value in kwargs.items():
        params[key] = str(value)
    
    # Обрабатываем множественные значения для urlencode
    query_parts = []
    for key, value in params.items():
        if isinstance(value, list):
            for v in value:
                query_parts.append((key, v))
        else:
            query_parts.append((key, value))
    
    return urlencode(query_parts)
