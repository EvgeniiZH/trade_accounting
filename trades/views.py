from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import UserCreateForm, UserEditForm, AdminSetPasswordForm
from .models import Item, Calculation, CalculationItem, PriceHistory, CustomUser, CalculationSnapshot, \
    CalculationSnapshotItem
import pandas as pd
import decimal
import io
import zipfile
from django.urls import reverse
from django.db.models import Count
from django.db.models.functions import Collate
from django.core.paginator import Paginator
from functools import wraps

from .utils import update_or_create_item_clean, calculate_total_price, paginate_queryset


# Фиксированные настройки (шаг цены и наценки)
PRICE_STEP = 0.01
MARKUP_STEP = 1
DECIMAL_PLACES = 1
PAGE_SIZE_OPTIONS = [10, 25, 50, 100, 200]


def admin_required(view_func):
    """Декоратор для проверки прав администратора."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not (request.user.is_admin or request.user.is_superuser):
            raise PermissionDenied("Только администраторы имеют доступ к этой странице")
        return view_func(request, *args, **kwargs)
    return wrapper


def handle_add_item(request):
    """Обработка добавления товара с проверкой дубликатов и форматированием имени."""
    name = request.POST.get("name")
    price = request.POST.get("price")

    if name and price:
        try:
            price = decimal.Decimal(price)
        except (decimal.InvalidOperation, TypeError):
            messages.error(request, "Введите корректное значение цены!")
            return

        item, updated = update_or_create_item_clean(name, price)
        if updated:
            messages.success(request, f"Товар «{item.name}» успешно добавлен или обновлён!")
            return redirect(reverse('item_list') + f'?new_item={item.id}')
        else:
            messages.info(request, f"Товар «{item.name}» уже существует и совпадает по цене.")
    else:
        messages.error(request, "Введите название и цену!")


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
            # Создаём запись в истории цен с указанием пользователя, изменившего цену.
            PriceHistory.objects.create(
                item=item,
                old_price=old_price,
                new_price=price,
                changed_by=request.user  # Здесь передаем текущего пользователя
            )

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


@login_required(login_url='/login/')
def edit_item_ajax(request):
    """Обработка редактирования товара через AJAX."""
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        item_id = request.POST.get("edit_item")
        name = request.POST.get(f"name_{item_id}")
        price = request.POST.get(f"price_{item_id}")
        try:
            price = decimal.Decimal(price)
        except (decimal.InvalidOperation, TypeError):
            return JsonResponse({"success": False, "error": "Введите корректное значение цены!"})
        try:
            item = Item.objects.get(id=item_id)
            old_price = item.price
            if old_price != price:
                PriceHistory.objects.create(
                    item=item,
                    old_price=old_price,
                    new_price=price,
                    changed_by=request.user
                )
            item.name = name
            item.price = price
            item.save()
            return JsonResponse({"success": True, "item_id": item.id, "message": "Товар успешно обновлён"})
        except Item.DoesNotExist:
            return JsonResponse({"success": False, "error": "Товар не найден!"})
    return JsonResponse({"success": False, "error": "Неверный запрос."})


@login_required(login_url='/login/')
def delete_item_ajax(request):
    """Обработка удаления товара через AJAX."""
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        item_id = request.POST.get("delete_item")
        try:
            item = Item.objects.get(id=item_id)
            item.delete()
            return JsonResponse({"success": True, "item_id": item_id, "message": "Товар успешно удалён"})
        except Item.DoesNotExist:
            return JsonResponse({"success": False, "error": "Товар не найден!"})
    return JsonResponse({"success": False, "error": "Неверный запрос."})


def handle_upload_file(request):
    """Обработка загрузки товаров из файла с проверкой дубликатов и форматированием имен."""
    file = request.FILES.get("file")
    updated, created, skipped = 0, 0, 0

    try:
        df = pd.read_excel(file)
        if 'Наименование комплектующей' not in df.columns or 'Цена' not in df.columns:
            messages.error(request, "Файл должен содержать столбцы 'Наименование комплектующей' и 'Цена'.")
        else:
            for _, row in df.iterrows():
                name = row.get('Наименование комплектующей')
                price = row.get('Цена')
                if name and price:
                    try:
                        price = decimal.Decimal(str(price))
                        item, changed = update_or_create_item_clean(name, price)
                        if changed:
                            updated += 1 if Item.objects.filter(pk=item.pk).exists() else 0
                            created += 0 if Item.objects.filter(pk=item.pk).exists() else 1
                        else:
                            skipped += 1
                    except decimal.InvalidOperation:
                        continue

            messages.success(request,
                             f"Импорт завершён: обновлено — {updated}, добавлено — {created}, пропущено — {skipped}")
    except Exception as e:
        messages.error(request, f"Ошибка загрузки файла: {e}")


# Главная страница: список товаров, редактирование, удаление и загрузка
@login_required(login_url='/login/')
def item_list(request):
    """Главная страница: список товаров, редактирование, удаление и загрузка"""
    if request.method == "POST":
        if "add_item" in request.POST:
            response = handle_add_item(request)
            if response:
                return response
        elif "edit_item" in request.POST:
            handle_edit_item(request)
        elif "delete_item" in request.POST:
            handle_delete_item(request)
        elif "upload_file" in request.POST:
            handle_upload_file(request)

    # Поиск и сортировка
    search = request.GET.get("search", "").strip()
    sort_by = request.GET.get("sort", "name")
    direction = request.GET.get("direction", "asc")
    order = sort_by if direction == "asc" else f"-{sort_by}"

    # Применяем фильтр только если есть поисковый запрос
    items_qs = Item.objects.filter(name__icontains=search).order_by(order) if search else Item.objects.all().order_by(order)

    # Пагинация
    page_obj, page_range, page_size, page_size_options = paginate_queryset(items_qs, request)

    # Статистика по текущему фильтру (без учёта пагинации)
    total_items = items_qs.count()
    total_price = sum(item.price for item in items_qs)
    avg_price = total_price / total_items if total_items else 0

    context = {
        "items": page_obj.object_list,
        "page_obj": page_obj,
        "page_range": page_range,
        "page_size": page_size,
        "page_size_options": page_size_options,
        "price_step": PRICE_STEP,
        "search": search,
        "sort_by": sort_by,
        "direction": direction,
        "total_items": total_items,
        "total_price": total_price,
        "avg_price": avg_price,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, "trades/includes/item_list_content.html", context)

    return render(request, "trades/item_list.html", context)


from pyuca import Collator

collator = Collator()


@login_required(login_url='/login/')
def calculations_list(request):
    updated_calc_id = request.GET.get("updated_calc")
    sort_by = request.GET.get("sort", "title")
    direction = request.GET.get("direction", "asc")
    reverse = direction == "desc"
    
    # Разрешенные поля для сортировки
    allowed_sort_fields = ['title', 'created_at', 'total_price', 'total_price_with_markup', 'user']
    if sort_by not in allowed_sort_fields:
        sort_by = 'title'

    if request.method == "POST":
        if "delete_calc" in request.POST:
            calc_id = request.POST.get("delete_calc")
            calculation = get_object_or_404(Calculation, id=calc_id)
            if calculation.user == request.user or request.user.is_admin or request.user.is_superuser:
                calculation.delete()
                messages.success(request, "Расчёт успешно удалён!")
            else:
                messages.error(request, "У вас нет прав для удаления этого расчёта.")
            return redirect('calculations_list')

        elif "export_excel" in request.POST:
            calc_ids = request.POST.getlist("calc_ids")
            if calc_ids:
                calculations_for_export = (
                    Calculation.objects
                    .filter(id__in=calc_ids)
                    .select_related('user')
                    .prefetch_related('items__item')
                )
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for calc in calculations_for_export:
                        total = calc.total_price
                        total_with_markup = calc.total_price_with_markup
                        
                        # Общая информация о расчёте
                        df_calc = pd.DataFrame({
                            "ID": [calc.id],
                            "Создал": [calc.user.username if calc.user else "Не указан"],
                            "Название": [calc.title],
                            "Наценка (%)": [calc.markup],
                            "Стоимость": [total],
                            "Стоимость с наценкой": [total_with_markup],
                            "Дата создания": [calc.created_at.strftime("%d.%m.%Y %H:%M")]
                        })
                        
                        # Детальный список товаров
                        items_data = []
                        for idx, calc_item in enumerate(calc.items.all(), start=1):
                            item_total = calc_item.item.price * calc_item.quantity
                            item_total_with_markup = item_total * (1 + calc.markup / 100)
                            items_data.append({
                                "№": idx,
                                "Наименование": calc_item.item.name,
                                "Цена за ед.": float(calc_item.item.price),
                                "Количество": calc_item.quantity,
                                "Сумма": float(item_total),
                                f"Сумма с наценкой ({calc.markup}%)": float(item_total_with_markup)
                            })
                        
                        df_items = pd.DataFrame(items_data) if items_data else pd.DataFrame()
                        
                        # Сохраняем в Excel с двумя листами
                        excel_buffer = io.BytesIO()
                        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                            df_calc.to_excel(writer, index=False, sheet_name="Информация")
                            if not df_items.empty:
                                df_items.to_excel(writer, index=False, sheet_name="Позиции")
                                
                                # Форматирование для красоты
                                workbook = writer.book
                                worksheet = writer.sheets["Позиции"]
                                
                                # Форматы
                                money_format = workbook.add_format({'num_format': '#,##0.00 ₽'})
                                header_format = workbook.add_format({
                                    'bold': True,
                                    'bg_color': '#4472C4',
                                    'font_color': 'white',
                                    'align': 'center'
                                })
                                
                                # Применяем форматы к столбцам с ценами
                                worksheet.set_column('C:C', 15, money_format)  # Цена за ед.
                                worksheet.set_column('E:F', 18, money_format)  # Сумма и Сумма с наценкой
                                worksheet.set_column('A:A', 5)   # №
                                worksheet.set_column('B:B', 40)  # Наименование
                                worksheet.set_column('D:D', 12)  # Количество
                        
                        zip_file.writestr(f"calculation_{calc.id}_{calc.title[:30]}.xlsx", excel_buffer.getvalue())
                zip_buffer.seek(0)
                return HttpResponse(
                    zip_buffer.getvalue(),
                    content_type="application/zip",
                    headers={"Content-Disposition": 'attachment; filename="calculations.zip"'}
                )
            else:
                messages.error(request, "Выберите хотя бы один расчёт для экспорта!")
                return redirect('calculations_list')

        return redirect('calculations_list')

    # Получаем поисковый запрос
    search = request.GET.get("search", "").strip()
    
    base_queryset = (
        Calculation.objects
        .select_related('user')
        .prefetch_related('items__item')
        .annotate(items_count=Count('items', distinct=True))
    )
    
    # Применяем поиск если есть
    if search:
        base_queryset = base_queryset.filter(title__icontains=search)

    # 🔠 Локализованная сортировка по title через Python
    if sort_by == "title":
        calculations_list = sorted(
            base_queryset,
            key=lambda c: collator.sort_key(c.title),
            reverse=reverse
        )
    else:
        order = sort_by if not reverse else f"-{sort_by}"
        calculations_list = list(base_queryset.order_by(order))

    page_obj, page_range, page_size, page_size_options = paginate_queryset(calculations_list, request)

    context = {
        "page_obj": page_obj,
        "page_range": page_range,
        "page_size": page_size,
        "page_size_options": page_size_options,
        "sort_by": sort_by,
        "direction": direction,
        "updated_calc_id": updated_calc_id,
        "search": search,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, "trades/includes/calculations_list_content.html", context)

    return render(request, "trades/calculations_list.html", context)


@login_required(login_url='/login/')
def create_calculation(request):
    """Создание нового расчёта (с возможностью предзаполнения через GET)"""
    if request.method == "POST":
        title = request.POST.get("title")
        markup = request.POST.get("markup", 0)  # По умолчанию 0
        item_ids = request.POST.getlist("items")

        try:
            markup = decimal.Decimal(markup)
        except decimal.InvalidOperation:
            messages.error(request, "Неверное значение наценки. Она должна быть числовым значением!")
            return redirect('create_calculation')

        if not item_ids:
            messages.error(request, "Выберите хотя бы один товар для расчёта!")
            return redirect('create_calculation')

        calculation = Calculation.objects.create(title=title, markup=markup, user=request.user)

        calculation_items = []
        for item_id in item_ids:
            try:
                quantity = int(request.POST.get(f"quantity_{item_id}", 1))
            except ValueError:
                quantity = 1
            try:
                item = Item.objects.get(id=item_id)
                calculation_items.append(
                    CalculationItem(calculation=calculation, item=item, quantity=quantity)
                )
            except Item.DoesNotExist:
                messages.error(request, f"Товар с id {item_id} не найден!")
                continue

        if calculation_items:
            CalculationItem.objects.bulk_create(calculation_items)

        total, total_with_markup = calculate_total_price(calculation)
        calculation.total_price = total
        calculation.total_price_with_markup = total_with_markup
        calculation.save()

        snapshot = CalculationSnapshot.objects.create(
            calculation=calculation,
            frozen_total_price=total,
            frozen_total_price_with_markup=total_with_markup,
            created_by=request.user
        )

        snapshot_items = []
        for calc_item in calculation.items.all():
            snapshot_items.append(
                CalculationSnapshotItem(
                    snapshot=snapshot,
                    item_name=calc_item.item.name,
                    item_price=calc_item.item.price,
                    quantity=calc_item.quantity,
                    total_price=calc_item.total_price()
                )
            )
        if snapshot_items:
            CalculationSnapshotItem.objects.bulk_create(snapshot_items)

        messages.success(request, "Расчёт успешно создан!")
        return redirect(reverse('calculations_list') + f'?new_calc={calculation.id}')

    # Обработка GET-запроса с возможностью копирования
    title = request.GET.get("title", "")
    markup = request.GET.get("markup", "0")
    selected_items_ids = request.GET.getlist("items")
    initial_quantities = {}
    for key in request.GET:
        if key.startswith("quantity_"):
            item_id = key.replace("quantity_", "")
            initial_quantities[item_id] = request.GET.get(key)

    search_query = request.GET.get('search', '')
    items_qs = Item.objects.filter(name__icontains=search_query) if search_query else Item.objects.all()

    # Сортировка
    sort_by = request.GET.get('sort_by', 'name')
    direction = request.GET.get('direction', 'asc')
    
    if sort_by in ['name', 'price']:
        order_field = f"{'-' if direction == 'desc' else ''}{sort_by}"
        items_qs = items_qs.order_by(order_field)
    
    # Пагинация для списка товаров при создании расчёта
    page_obj, page_range, page_size, page_size_options = paginate_queryset(items_qs, request)

    context = {
        "items": page_obj.object_list,
        "page_obj": page_obj,
        "page_range": page_range,
        "page_size": page_size,
        "page_size_options": page_size_options,
        "search_query": search_query,
        "title": title,
        "markup": markup,
        "selected_items_ids": selected_items_ids,
        "initial_quantities": initial_quantities,
        "sort_by": sort_by,
        "direction": direction,
        "user_settings": {
            "markup_step": 1  # или получи из профиля пользователя
        },
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, "trades/includes/create_calculation_content.html", context)

    return render(request, "trades/create_calculation.html", context)


@login_required(login_url='/login/')
def save_calculation_snapshot(request, pk):
    """
    Создаёт снимок расчёта с id=pk, сохраняя данные товаров,
    итоговые суммы и дату создания, затем перенаправляет на детальный просмотр.
    """
    calculation = get_object_or_404(Calculation, pk=pk)
    # Подготавливаем данные товаров
    items_data = []
    for ci in calculation.items.all():
        items_data.append({
            'id': ci.item.id,
            'name': ci.item.name,
            'price': float(ci.item.price),
            'quantity': ci.quantity,
            'total': float(ci.total_price())
        })
    total, total_with_markup = calculate_total_price(calculation)
    snapshot = CalculationSnapshot.objects.create(
        calculation=calculation,
        frozen_total_price=total,
        frozen_total_price_with_markup=total_with_markup,
        snapshot_data={'items': items_data}
    )
    messages.success(request, "Снимок расчёта успешно создан!")
    return redirect('calculation_snapshot_detail', snapshot_id=snapshot.id)


@login_required(login_url='/login/')
def calculation_snapshot_list(request):
    """Страница списка снимков расчётов."""
    snapshots_qs = CalculationSnapshot.objects.select_related('calculation', 'created_by').order_by('-created_at')
    page_obj, page_range, page_size, page_size_options = paginate_queryset(snapshots_qs, request)

    return render(request, 'trades/calculation_snapshot_list.html', {
        'page_obj': page_obj,
        'page_range': page_range,
        'page_size': page_size,
        'page_size_options': page_size_options,
    })


@login_required(login_url='/login/')
def calculation_snapshot_detail(request, snapshot_id):
    """Детальный просмотр снимка расчёта, включая список товаров."""
    snapshot = get_object_or_404(CalculationSnapshot, id=snapshot_id)
    items_qs = snapshot.items.all().order_by('item_name')
    page_obj, page_range, page_size, page_size_options = paginate_queryset(items_qs, request)

    return render(request, 'trades/calculation_snapshot_detail.html', {
        'snapshot': snapshot,
        'page_obj': page_obj,
        'page_range': page_range,
        'page_size': page_size,
        'page_size_options': page_size_options,
    })
@login_required(login_url='/login/')
def calculation_detail(request, pk):
    calculation = get_object_or_404(Calculation, pk=pk)

    if request.method == "POST":
        if "delete_item" in request.POST:
            item_id = request.POST.get("delete_item")
            try:
                calculation.items.get(id=item_id).delete()
                messages.success(request, "Товар удалён из расчёта!")
            except CalculationItem.DoesNotExist:
                messages.error(request, "Товар не найден в расчёте!")
            return redirect(request.path)  # Вернуться на ту же страницу после удаления

        elif "save_calculation" in request.POST:
            selected_raw_ids = request.POST.getlist("items")
            selected_item_ids = set()
            for raw_id in selected_raw_ids:
                try:
                    selected_item_ids.add(int(raw_id))
                except (TypeError, ValueError):
                    continue

            # Обновление количества и удаление снятых товаров
            existing_items = {
                calc_item.item_id: calc_item
                for calc_item in calculation.items.select_related("item")
            }

            for item_id, calc_item in list(existing_items.items()):
                if item_id not in selected_item_ids:
                    calc_item.delete()
                    continue

                quantity_value = request.POST.get(f"quantity_{item_id}")
                if quantity_value is None:
                    continue
                try:
                    quantity_int = int(quantity_value)
                    if quantity_int < 1:
                        raise ValueError
                    calc_item.quantity = quantity_int
                    calc_item.save(update_fields=["quantity"])
                except ValueError:
                    messages.error(request, f"Ошибка количества у {calc_item.item.name}")

            # Обновление названия
            title = request.POST.get("title", "").strip()
            if title:
                calculation.title = title

            # Обновление наценки
            markup = request.POST.get("markup", "0")
            try:
                calculation.markup = decimal.Decimal(markup)
                calculation.save(update_fields=["markup", "title"])
            except decimal.InvalidOperation:
                messages.error(request, "Введите корректную наценку!")

            # Добавление новых товаров
            for item_id in selected_item_ids:
                if item_id in existing_items:
                    continue
                quantity_value = request.POST.get(f"quantity_{item_id}", 1)
                try:
                    quantity_int = int(quantity_value)
                    if quantity_int < 1:
                        raise ValueError
                except ValueError:
                    messages.error(request, f"Ошибка количества у товара ID={item_id}")
                    continue

                try:
                    item = Item.objects.get(id=item_id)
                except Item.DoesNotExist:
                    messages.error(request, f"Товар с ID={item_id} не найден!")
                    continue

                CalculationItem.objects.create(
                    calculation=calculation,
                    item=item,
                    quantity=quantity_int
                )

            # Обновление сумм
            calculation.refresh_totals()

            messages.success(request, "Расчёт успешно обновлён!")
            return redirect(reverse("calculations_list") + f"?updated_calc={calculation.id}")

    # GET-запрос
    selected_items_ids = []
    initial_quantities = {}
    for ci in calculation.items.all():
        selected_items_ids.append(str(ci.item.id))
        initial_quantities[str(ci.item.id)] = ci.quantity

    # Поиск
    search_query = request.GET.get('search', '')
    items_qs = Item.objects.filter(name__icontains=search_query) if search_query else Item.objects.all()
    
    # Сортировка
    sort_by = request.GET.get('sort_by', 'name')
    direction = request.GET.get('direction', 'asc')
    
    if sort_by in ['name', 'price']:
        order_field = f"{'-' if direction == 'desc' else ''}{sort_by}"
        items_qs = items_qs.order_by(order_field)
    
    # Пагинация для списка товаров при редактировании расчёта
    page_obj, page_range, page_size, page_size_options = paginate_queryset(items_qs, request)

    return render(request, "trades/calculation_detail.html", {
        "calculation": calculation,
        "items": page_obj.object_list,
        "page_obj": page_obj,
        "page_range": page_range,
        "page_size": page_size,
        "page_size_options": page_size_options,
        "markup_step": 1,
        "initial_quantities": initial_quantities,
        "selected_items_ids": selected_items_ids,
        "sort_by": sort_by,
        "direction": direction,
        "search_query": search_query,
        "initial_totals": {
            "without_markup": calculation.total_price,
            "with_markup": calculation.total_price_with_markup,
        }
    })


@login_required(login_url='/login/')
def price_history_view(request):
    price_history_qs = PriceHistory.objects.select_related('item', 'changed_by').order_by('-changed_at')
    page_obj, page_range, page_size, page_size_options = paginate_queryset(price_history_qs, request)

    return render(request, "trades/price_history.html", {
        "page_obj": page_obj,
        "page_range": page_range,
        "page_size": page_size,
        "page_size_options": page_size_options,
    })


@login_required(login_url='/login/')
@admin_required
def manage_users(request):
    """Страница управления пользователями (только для администраторов)"""
    users_qs = CustomUser.objects.all().order_by('username')
    page_obj, page_range, page_size, page_size_options = paginate_queryset(users_qs, request)

    return render(request, 'trades/manage_users.html', {
        'page_obj': page_obj,
        'page_range': page_range,
        'page_size': page_size,
        'page_size_options': page_size_options,
    })


@login_required(login_url='/login/')
@admin_required
def create_user(request):
    """Создание нового пользователя (только для администраторов)"""
    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Пользователь успешно создан!")
            return redirect('manage_users')
    else:
        form = UserCreateForm()
    return render(request, 'trades/create_user.html', {'form': form})


@login_required(login_url='/login/')
@admin_required
def edit_user(request, user_id):
    """Редактирование пользователя (только для администраторов)"""
    user = get_object_or_404(CustomUser, id=user_id)
    action = request.POST.get('action')

    if request.method == "POST" and action == 'update_user':
        form = UserEditForm(request.POST, instance=user)
        password_form = AdminSetPasswordForm(user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль пользователя обновлён.")
            return redirect('manage_users')
    elif request.method == "POST" and action == 'change_password':
        form = UserEditForm(instance=user)
        password_form = AdminSetPasswordForm(user, request.POST)
        if password_form.is_valid():
            password_form.save()
            messages.success(request, f"Пароль пользователя «{user.username}» обновлён.")
            return redirect('manage_users')
    else:
        form = UserEditForm(instance=user)
        password_form = AdminSetPasswordForm(user)

    return render(request, 'trades/edit_user.html', {
        'form': form,
        'password_form': password_form,
        'user_obj': user
    })


@login_required(login_url='/login/')
@admin_required
def delete_user(request, user_id):
    """Удаление пользователя (только для администраторов)"""
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


@login_required(login_url='/login/')
def copy_calculation(request, calculation_id):
    original_calc = get_object_or_404(Calculation, id=calculation_id)

    # Формируем параметры для передачи в GET-запрос
    params = {
        'title': f"{original_calc.title} (копия)",
        'markup': original_calc.markup,
    }

    for ci in original_calc.items.all():
        params[f'quantity_{ci.item.id}'] = ci.quantity
        params.setdefault('items', []).append(str(ci.item.id))

    # Создаём URL с параметрами
    base_url = reverse('create_calculation')
    query_string = '&'.join([f"{key}={value}" for key, value in params.items() if key != 'items'])
    items_string = '&'.join([f"items={item_id}" for item_id in params['items']])
    redirect_url = f"{base_url}?{query_string}&{items_string}"

    return redirect(redirect_url)


@login_required(login_url='/login/')
def edit_item_page(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")

        try:
            price = decimal.Decimal(price)
            item.name = name
            item.price = price
            item.save()
            messages.success(request, "Товар успешно обновлён!")
            return redirect('item_list')
        except decimal.InvalidOperation:
            messages.error(request, "Некорректная цена!")

    return render(request, "trades/edit_item.html", {"item": item})


class CustomLoginView(LoginView):
    """Кастомный вид входа с поддержкой username или email через UsernameOrEmailBackend"""
    template_name = 'trades/login.html'
    redirect_authenticated_user = True
