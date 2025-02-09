from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import UserCreateForm, UserEditForm
from .models import Item, Calculation, CalculationItem, PriceHistory, CustomUser
import pandas as pd
import decimal
import io
import zipfile

# Фиксированные настройки (шаг цены и наценки)
PRICE_STEP = 0.01
MARKUP_STEP = 1
DECIMAL_PLACES = 1


def handle_add_item(request):
    """Обработка добавления товара."""
    name = request.POST.get("name")
    price = request.POST.get("price")
    if name and price:
        try:
            # Приводим цену к Decimal
            price = decimal.Decimal(price)
        except (decimal.InvalidOperation, TypeError):
            messages.error(request, "Введите корректное значение цены!")
            return

        try:
            item, created = Item.objects.update_or_create(
                name=name.strip(),
                defaults={'price': price}
            )
            if created:
                messages.success(request, "Товар успешно добавлен!")
            else:
                messages.success(request, "Товар уже существовал, цена обновлена!")
        except IntegrityError as e:
            messages.error(request, f"Ошибка добавления товара: {e}")
    else:
        messages.error(request, "Введите название и цену!")


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
    """Главная страница: список товаров, редактирование, удаление и загрузка"""
    if request.method == "POST":
        if "add_item" in request.POST:
            handle_add_item(request)
        elif "edit_item" in request.POST:
            handle_edit_item(request)
        elif "delete_item" in request.POST:
            handle_delete_item(request)
        elif "upload_file" in request.POST:
            handle_upload_file(request)

    items = Item.objects.all()

    return render(request, "trades/item_list.html", {
        "items": items,
        "price_step": PRICE_STEP
    })


def calculations_list(request):
    """Страница списка расчётов с возможностью экспорта в Excel (каждый расчёт – отдельный файл в ZIP‑архиве)"""
    if request.method == "POST":
        if "delete_calc" in request.POST:
            calc_id = request.POST.get("delete_calc")
            try:
                calculation = get_object_or_404(Calculation, id=calc_id)
                calculation.delete()
                messages.success(request, "Расчёт успешно удалён!")
            except Exception as e:
                messages.error(request, f"Ошибка при удалении расчёта: {e}")
        elif "export_excel" in request.POST:
            # Получаем список выбранных расчётов
            calc_ids = request.POST.getlist("calc_ids")
            if calc_ids:
                calculations = Calculation.objects.filter(id__in=calc_ids)
                # Создаем буфер для ZIP‑архива
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for calc in calculations:
                        # Вычисляем итоговые суммы для расчёта
                        total, total_with_markup = calculate_total_price(calc)

                        # Формируем данные для DataFrame
                        calc_data = {
                            "ID": [calc.id],
                            "Название": [calc.title],
                            "Наценка (%)": [calc.markup],
                            "Стоимость": [total],
                            "Стоимость с наценкой": [total_with_markup]
                        }
                        df_calc = pd.DataFrame(calc_data)

                        # Создаем Excel‑файл для этого расчёта
                        excel_buffer = io.BytesIO()
                        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                            df_calc.to_excel(writer, index=False, sheet_name="Информация о расчёте")

                            # Если расчет содержит товары, добавляем дополнительный лист
                            calc_items = calc.items.all().select_related("item")
                            if calc_items.exists():
                                items_data = []
                                for ci in calc_items:
                                    items_data.append({
                                        "ID товара": ci.item.id,
                                        "Наименование товара": ci.item.name,
                                        "Цена": ci.item.price,
                                        "Количество": ci.quantity,
                                        "Итого": ci.quantity * ci.item.price
                                    })
                                df_items = pd.DataFrame(items_data)
                                df_items.to_excel(writer, index=False, sheet_name="Товары")
                        # Задаем имя файла для каждого расчёта
                        excel_filename = f"calculation_{calc.id}.xlsx"
                        # Добавляем Excel‑файл в ZIP‑архив
                        zip_file.writestr(excel_filename, excel_buffer.getvalue())
                # Возвращаем ZIP‑архив как ответ
                zip_buffer.seek(0)
                response = HttpResponse(
                    zip_buffer.getvalue(),
                    content_type="application/zip"
                )
                response["Content-Disposition"] = 'attachment; filename="calculations.zip"'
                return response
            else:
                messages.error(request, "Выберите хотя бы один расчёт для экспорта!")

    calculations = Calculation.objects.all()
    return render(request, "trades/calculations_list.html", {"calculations": calculations})


def create_calculation(request):
    """Создание нового расчёта"""
    if request.method == "POST":
        title = request.POST.get("title")
        markup = request.POST.get("markup", 0)  # Получаем наценку, по умолчанию 0
        item_ids = request.POST.getlist("items")

        if not item_ids:
            messages.error(request, "Выберите хотя бы один товар для расчёта!")
            return redirect('create_calculation')

        try:
            # Преобразуем наценку в Decimal
            markup = decimal.Decimal(markup)
        except decimal.InvalidOperation:
            messages.error(request, "Наценка должна быть числовым значением!")
            return redirect('create_calculation')

        # Создание объекта расчета
        try:
            calculation = Calculation.objects.create(title=title, markup=markup)
        except IntegrityError:
            messages.error(request, "Ошибка при создании расчета!")
            return redirect('create_calculation')

        # Добавляем товары в расчет
        for item_id in item_ids:
            quantity = int(request.POST.get(f"quantity_{item_id}", 1))  # Устанавливаем количество товара
            try:
                item = Item.objects.get(id=item_id)
                CalculationItem.objects.create(calculation=calculation, item=item, quantity=quantity)
            except Item.DoesNotExist:
                messages.error(request, f"Товар с id {item_id} не найден!")
                continue

        messages.success(request, "Расчёт успешно создан!")
        return redirect('calculation_detail', pk=calculation.pk)

    # Поиск по товарам
    search_query = request.GET.get('search', '')
    items = Item.objects.filter(name__icontains=search_query) if search_query else Item.objects.all()

    return render(request, "trades/create_calculation.html", {"items": items, "search_query": search_query})


def calculate_total_price(calculation):
    """Функция для вычисления общей стоимости расчёта с учётом наценки."""
    total = sum(item.quantity * item.item.price for item in
                calculation.items.all())  # Суммируем цену всех товаров с их количеством
    total_with_markup = total + (total * calculation.markup / 100)  # Применяем наценку
    return total, total_with_markup


def calculation_detail(request, pk):
    """Просмотр и редактирование сохранённого расчёта"""
    calculation = get_object_or_404(Calculation, pk=pk)

    if request.method == "POST":
        # Удаление товара из расчёта
        if "delete_item" in request.POST:
            item_id = request.POST.get("delete_item")
            try:
                calculation_item = calculation.items.get(id=item_id)
                calculation_item.delete()
                messages.success(request, "Товар удалён из расчёта!")
            except CalculationItem.DoesNotExist:
                messages.error(request, "Товар не найден в расчёте!")

        # Обновление количества товара
        elif "update_quantity" in request.POST:
            item_id = request.POST.get("update_quantity")
            quantity = request.POST.get(f"quantity_{item_id}")
            try:
                calculation_item = calculation.items.get(id=item_id)
                calculation_item.quantity = int(quantity)
                calculation_item.save()
                messages.success(request, "Количество обновлено!")
            except (CalculationItem.DoesNotExist, ValueError):
                messages.error(request, "Ошибка обновления количества!")

        # Добавление товара в расчёт
        elif "add_item" in request.POST:
            item_id = request.POST.get("item_id")
            quantity = int(request.POST.get("quantity", 1))
            item = Item.objects.get(id=item_id)
            CalculationItem.objects.create(calculation=calculation, item=item, quantity=quantity)
            messages.success(request, "Товар добавлен в расчёт!")

        # Обновление наценки
        elif "update_markup" in request.POST:
            markup = request.POST.get("markup", 0)
            try:
                calculation.markup = decimal.Decimal(markup)
                calculation.save()
                messages.success(request, "Наценка обновлена!")
            except (ValueError, decimal.InvalidOperation):
                messages.error(request, "Введите корректное значение наценки!")

        # Сохранение расчёта (привязано к кнопке "Сохранить расчет")
        elif "save_calculation" in request.POST:
            # Обновляем количество для всех позиций расчёта
            for calc_item in calculation.items.all():
                new_quantity = request.POST.get(f"quantity_{calc_item.id}")
                if new_quantity:
                    try:
                        calc_item.quantity = int(new_quantity)
                        calc_item.save()
                    except ValueError:
                        messages.error(request, f"Некорректное количество для товара {calc_item.item.name}.")
            # Обновляем наценку, если она передана в форме
            if "markup" in request.POST:
                markup = request.POST.get("markup")
                try:
                    calculation.markup = decimal.Decimal(markup)
                except (ValueError, decimal.InvalidOperation):
                    messages.error(request, "Введите корректное значение наценки!")
            calculation.save()  # Сохраняем объект расчёта
            messages.success(request, "Расчёт успешно сохранён!")

        # Пересчитываем общую стоимость с учётом наценки
        total, total_with_markup = calculate_total_price(calculation)
        calculation.total_price = total
        calculation.total_price_with_markup = total_with_markup
        calculation.save()

    # Получение товаров, которые еще не добавлены в расчёт
    items = Item.objects.exclude(id__in=calculation.items.values_list('item_id', flat=True))

    return render(request, "trades/calculation_detail.html", {
        "calculation": calculation,
        "items": items,
        "markup_step": MARKUP_STEP
    })


def handle_edit_item(request):
    """Обработка редактирования товара."""
    item_id = request.POST.get("edit_item")
    name = request.POST.get(f"name_{item_id}")
    price = request.POST.get(f"price_{item_id}")

    try:
        price = decimal.Decimal(price)
    except (decimal.InvalidOperation, TypeError):
        messages.error(request, "Введите корректное значение цены!")
        return

    try:
        item = Item.objects.get(id=item_id)
        old_price = item.price  # Сохраняем старую цену

        if old_price != price:
            # Создаём запись в истории цен
            PriceHistory.objects.create(item=item, old_price=old_price, new_price=price)

        item.name = name
        item.price = price
        item.save()
        messages.success(request, "Товар успешно обновлён!")
    except Item.DoesNotExist:
        messages.error(request, "Товар не найден!")


def price_history_view(request):
    price_history = PriceHistory.objects.all().order_by('-changed_at')  # Сортируем по дате (новые сверху)
    return render(request, "trades/price_history.html", {"price_history": price_history})


@login_required
def manage_users(request):
    """Страница управления пользователями"""
    users = CustomUser.objects.all()
    return render(request, 'trades/manage_users.html', {'users': users})


@login_required
def create_user(request):
    """Создание нового пользователя"""
    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Пользователь успешно создан!")
            return redirect('manage_users')
    else:
        form = UserCreateForm()
    return render(request, 'trades/create_user.html', {'form': form})


@login_required
def edit_user(request, user_id):
    """Редактирование пользователя"""
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == "POST":
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Пользователь успешно обновлён!")
            return redirect('manage_users')
    else:
        form = UserEditForm(instance=user)
    return render(request, 'trades/edit_user.html', {'form': form, 'user': user})


@login_required
def delete_user(request, user_id):
    """Удаление пользователя"""
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == "POST":
        user.delete()
        messages.success(request, "Пользователь успешно удалён!")
        return redirect('manage_users')
    return render(request, 'trades/delete_user.html', {'user': user})


def download_import_template(request):
    """
    Создает Excel-шаблон для импорта товаров и возвращает его как файл для скачивания.
    Шаблон содержит заголовки: 'Наименование комплектующей' и 'Цена'.
    """
    # Формируем DataFrame с необходимыми столбцами (без строк данных)
    data = {
        "Наименование комплектующей": [],
        "Цена": []
    }
    df = pd.DataFrame(data)

    # Создаем буфер для записи Excel-файла
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Импорт")
    output.seek(0)

    # Формируем HTTP-ответ с нужным content-type и заголовком для скачивания
    response = HttpResponse(
        output.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="import_template.xlsx"'
    return response