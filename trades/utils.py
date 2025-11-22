from decimal import Decimal
from django.core.paginator import Paginator


def normalize_item_name(name: str) -> str:
    """Убирает лишние пробелы и возвращает название в «чистом» виде."""
    return name.strip()


def update_or_create_item_clean(name: str, price):
    """
    Возвращает кортеж (item, created, updated).
    created: создан ли новый товар.
    updated: изменена ли цена существующего товара.
    """
    from .models import Item

    name_clean = normalize_item_name(name)
    existing = Item.objects.filter(name__iexact=name_clean).first()

    if existing:
        if existing.price != price:
            existing.price = price
            existing.save()
            return existing, False, True
        return existing, False, False

    return Item.objects.create(name=name_clean, price=price), True, False


def calculate_total_price(calculation):
    """Считает сумму расчёта и сумму с наценкой на основании текущих позиций."""
    items = calculation.items.all()
    if hasattr(items, "select_related"):
        items = items.select_related("item")

    total = sum(
        (item.quantity * item.item.price for item in items),
        Decimal("0"),
    )

    markup_multiplier = (Decimal("100") + calculation.markup) / Decimal("100")
    total_with_markup = total * markup_multiplier
    return total, total_with_markup


def paginate_queryset(queryset, request, page_size_options=None):
    """
    Helper функция для пагинации queryset.
    
    Args:
        queryset: QuerySet для пагинации
        request: HTTP request с параметрами page и page_size
        page_size_options: Список доступных размеров страницы (по умолчанию [10, 25, 50, 100, 200])
    
    Returns:
        tuple: (page_obj, page_range, page_size, page_size_options)
    """
    if page_size_options is None:
        page_size_options = [10, 25, 50, 100, 200]
    
    try:
        page_size = int(request.GET.get("page_size", page_size_options[0]))
    except (TypeError, ValueError):
        page_size = page_size_options[0]
    
    if page_size not in page_size_options:
        page_size = page_size_options[0]
    
    paginator = Paginator(queryset, page_size)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    page_range = paginator.get_elided_page_range(page_obj.number, on_each_side=1, on_ends=1)
    
    return page_obj, page_range, page_size, page_size_options
