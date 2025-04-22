from .models import Item, Calculation

def normalize_item_name(name: str) -> str:
    return name.strip().capitalize()

def update_or_create_item_clean(name: str, price):
    name_clean = normalize_item_name(name)
    existing = Item.objects.filter(name__iexact=name_clean).first()

    if existing:
        if existing.price != price:
            existing.price = price
            existing.save()
            return existing, True
        return existing, False

    return Item.objects.create(name=name_clean, price=price), True

def calculate_total_price(calculation):
    """Возвращает сумму без наценки и с наценкой для расчёта."""
    total = sum(item.quantity * item.item.price for item in calculation.items.all())
    total_with_markup = total * (1 + calculation.markup / 100)
    return total, total_with_markup
