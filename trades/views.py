from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import UserSettingsForm
from .models import Item, Calculation, CalculationItem, UserSettings, PriceHistory
import pandas as pd
import decimal


# Главная страница: список товаров, редактирование, удаление и загрузка
# Вспомогательные функции
def handle_add_item(request):
    """Обработка добавления товара."""
    name = request.POST.get("name")
    price = request.POST.get("price")
    if name and price:
        try:
            item, created = Item.objects.update_or_create(
                name=name.strip(),
                defaults={'price': price}
            )
            if created:
                messages.success(request, "Товар успешно добавлен!")
            else:
                messages.success(request, "Товар уже существовал, цена обновлена!")
        except Exception as e:
            messages.error(request, f"Ошибка добавления товара: {e}")
    else:
        messages.error(request, "Введите название и цену!")


def handle_edit_item(request):
    """Обработка редактирования товара."""
    item_id = request.POST.get("edit_item")
    name = request.POST.get(f"name_{item_id}")
    price = request.POST.get(f"price_{item_id}")
    try:
        item = Item.objects.get(id=item_id)
        item.name = name
        item.price = price
        item.save()
        messages.success(request, "Товар успешно обновлён!")
    except Item.DoesNotExist:
        messages.error(request, "Товар не найден!")


def handle_delete_item(request):
    """Обработка удаления товара."""
    item_id = request.POST.get("delete_item")
    try:
        item = Item.objects.get(id=item_id)
        item.delete()
        messages.success(request, "Товар успешно удалён!")
    except Item.DoesNotExist:
        messages.error(request, "Товар не найден!")


def handle_upload_file(request):
    """Обработка загрузки товаров из файла."""
    file = request.FILES.get("file")
    try:
        df = pd.read_excel(file)
        if 'Наименование комплектующей' not in df.columns or 'Цена' not in df.columns:
            messages.error(request, "Файл должен содержать столбцы 'Наименование комплектующей' и 'Цена'.")
        else:
            for _, row in df.iterrows():
                name = row.get('Наименование комплектующей')
                price = row.get('Цена')
                if name and price:
                    Item.objects.update_or_create(name=name.strip(), defaults={'price': price})
            messages.success(request, "Товары загружены!")
    except Exception as e:
        messages.error(request, f"Ошибка загрузки файла: {e}")


# Главная страница: список товаров, редактирование, удаление и загрузка
def item_list(request):
    if request.method == "POST":
        if "add_item" in request.POST:
            handle_add_item(request)
        elif "edit_item" in request.POST:
            handle_edit_item(request)
        elif "delete_item" in request.POST:
            handle_delete_item(request)
        elif "upload_file" in request.POST:
            handle_upload_file(request)

    # Получение всех товаров
    items = Item.objects.all()
    settings, _ = UserSettings.objects.get_or_create(id=1)

    return render(request, "trades/item_list.html", {
        "items": items,
        "user_settings": settings,
    })


def calculations_list(request):
    if request.method == "POST":
        # Обработка удаления расчёта
        if "delete_calc" in request.POST:
            calc_id = request.POST.get("delete_calc")
            try:
                calculation = get_object_or_404(Calculation, id=calc_id)
                calculation.delete()
                messages.success(request, "Расчёт успешно удалён!")
            except Exception as e:
                messages.error(request, f"Ошибка при удалении расчёта: {e}")

    calculations = Calculation.objects.all()
    return render(request, "trades/calculations_list.html", {"calculations": calculations})


def create_calculation(request):
    if request.method == "POST":
        title = request.POST.get("title")
        markup = request.POST.get("markup", 0)
        item_ids = request.POST.getlist("items")
        if not item_ids:
            messages.error(request, "Выберите хотя бы один товар для расчёта!")
            return redirect('create_calculation')

        calculation = Calculation.objects.create(title=title, markup=markup)
        for item_id in item_ids:
            quantity = int(request.POST.get(f"quantity_{item_id}", 1))
            item = Item.objects.get(id=item_id)
            CalculationItem.objects.create(calculation=calculation, item=item, quantity=quantity)
        return redirect('calculation_detail', pk=calculation.pk)

    search_query = request.GET.get('search', '')
    if search_query:
        items = Item.objects.filter(name__icontains=search_query)
    else:
        items = Item.objects.all()

    return render(request, "trades/create_calculation.html", {"items": items, "search_query": search_query})


def calculation_detail(request, pk):
    calculation = get_object_or_404(Calculation, pk=pk)

    if request.method == "POST":
        # Удаление товара из расчёта
        if "delete_item" in request.POST:
            item_id = request.POST.get("delete_item")
            try:
                calculation_item = calculation.items.get(id=item_id)
                calculation_item.delete()
                messages.success(request, "Товар успешно удалён из расчёта!")
            except CalculationItem.DoesNotExist:
                messages.error(request, "Товар не найден в расчёте!")
                # Изменение количества товара
                if "update_quantity" in request.POST:
                    item_id = request.POST.get("update_quantity")
                    quantity = request.POST.get(f"quantity_{item_id}")
                    try:
                        calculation_item = calculation.items.get(id=item_id)
                        calculation_item.quantity = int(quantity)
                        calculation_item.save()
                        messages.success(request, "Количество успешно обновлено!")
                    except CalculationItem.DoesNotExist:
                        messages.error(request, "Товар не найден в расчёте!")
                    except ValueError:
                        messages.error(request, "Введите корректное количество!")

        # Изменение количества товара
        if "update_quantity" in request.POST:
            item_id = request.POST.get("update_quantity")
            quantity = request.POST.get(f"quantity_{item_id}")
            try:
                calculation_item = calculation.items.get(id=item_id)
                calculation_item.quantity = int(quantity)
                calculation_item.save()
                messages.success(request, "Количество успешно обновлено!")
            except CalculationItem.DoesNotExist:
                messages.error(request, "Товар не найден в расчёте!")
            except ValueError:
                messages.error(request, "Введите корректное количество!")
        # Добавление товара в расчёт
        elif "add_item" in request.POST:
            item_id = request.POST.get("item_id")
            quantity = int(request.POST.get("quantity", 1))
            item = Item.objects.get(id=item_id)
            CalculationItem.objects.create(calculation=calculation, item=item, quantity=quantity)
            messages.success(request, "Товар успешно добавлен в расчёт!")

        # Изменение наценки
        elif "update_markup" in request.POST:
            markup = request.POST.get("markup", 0)
            try:
                # Преобразование в Decimal
                calculation.markup = decimal.Decimal(markup)
                calculation.save()
                messages.success(request, "Наценка успешно обновлена!")
            except (ValueError, decimal.InvalidOperation):
                messages.error(request, "Введите корректное значение наценки!")

    items = Item.objects.exclude(id__in=calculation.items.values_list('item_id', flat=True))
    return render(request, "trades/calculation_detail.html", {
        "calculation": calculation,
        "items": items,
    })


def update_settings(request):
    settings, created = UserSettings.objects.get_or_create(id=1)

    if request.method == "POST":
        form = UserSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, "Настройки успешно сохранены!")
            return redirect('update_settings')
        else:
            # Лог отладки: выводим ошибки формы
            print("Ошибки формы:", form.errors)
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = UserSettingsForm(instance=settings)

    return render(request, 'trades/settings.html', {
        'form': form,
        'user_settings': settings,
    })


def handle_edit_item(request):
    item_id = request.POST.get("edit_item")
    name = request.POST.get(f"name_{item_id}")
    new_price = request.POST.get(f"price_{item_id}")

    try:
        item = Item.objects.get(id=item_id)
        old_price = item.price  # Сохраняем старую цену

        if old_price != new_price:
            # Создаём запись в истории цен
            PriceHistory.objects.create(item=item, old_price=old_price, new_price=new_price)

        item.name = name
        item.price = new_price
        item.save()
        messages.success(request, "Товар успешно обновлён!")

    except Item.DoesNotExist:
        messages.error(request, "Товар не найден!")


def price_history_view(request):
    price_history = PriceHistory.objects.all().order_by('-changed_at')  # Сортируем по дате (новые сверху)
    return render(request, "trades/price_history.html", {"price_history": price_history})
