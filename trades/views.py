from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import UserSettingsForm
from .models import Item, Calculation, CalculationItem, UserSettings
import pandas as pd
import decimal


# Главная страница: список товаров, редактирование, удаление и загрузка
def item_list(request):
    if request.method == "POST":
        # Добавление товара
        if "add_item" in request.POST:
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
        # Изменение шага изменения цены
        if "update_step" in request.POST:
            if request.user.is_authenticated:
                settings, created = UserSettings.objects.get_or_create(user=request.user)
                price_step = request.POST.get("price_step", "0.01")
                try:
                    settings.price_step = decimal.Decimal(price_step)
                    settings.save()
                    messages.success(request, "Шаг изменения цены успешно обновлён!")
                except decimal.InvalidOperation:
                    messages.error(request, "Введите корректное значение для шага.")
        # Обработка редактирования товара
        elif "edit_item" in request.POST:
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

        # Удаление товара
        elif "delete_item" in request.POST:
            item_id = request.POST.get("delete_item")
            try:
                item = Item.objects.get(id=item_id)
                item.delete()
                messages.success(request, "Товар успешно удалён!")
            except Item.DoesNotExist:
                messages.error(request, "Товар не найден!")
        # Загрузка товаров из файла
        elif "upload_file" in request.POST and request.FILES.get("file"):
            file = request.FILES["file"]
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

    # Получение всех товаров
    items = Item.objects.all()
    # Получение или создание настроек пользователя
    if request.user.is_authenticated:
        settings, created = UserSettings.objects.get_or_create(user=request.user)
    else:
        class DefaultSettings:
            price_step = 0.01

        settings = DefaultSettings()

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
            messages.error(request, "Выберите хотя бы один товар!")
            return redirect('create_calculation')

        calculation = Calculation.objects.create(title=title, markup=markup)
        for item_id in item_ids:
            quantity = int(request.POST.get(f"quantity_{item_id}", 1))
            item = Item.objects.get(id=item_id)
            CalculationItem.objects.create(calculation=calculation, item=item, quantity=quantity)

        return redirect('calculation_detail', pk=calculation.pk)

    items = Item.objects.all()
    return render(request, "trades/create_calculation.html", {"items": items})


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
    settings, created = UserSettings.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = UserSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            return redirect('item_list')  # Перенаправление на главную страницу
    else:
        form = UserSettingsForm(instance=settings)
    return render(request, 'trades/settings.html', {'form': form})
