from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Item, Calculation, CalculationItem, CustomUser

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'price']
    
    def clean_price(self):
        """Валидация цены - должна быть положительной"""
        price = self.cleaned_data.get('price')
        if price and price <= 0:
            raise forms.ValidationError("Цена должна быть больше нуля")
        return price
    
    def clean_name(self):
        """Валидация названия - минимум 2 символа"""
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            if len(name) < 2:
                raise forms.ValidationError("Название должно содержать минимум 2 символа")
        return name


class CalculationForm(forms.ModelForm):
    """Форма для создания расчёта."""
    class Meta:
        model = Calculation
        fields = ['title', 'markup']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название расчёта'}),
            'markup': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Наценка (%)'}),
        }
    
    def clean_markup(self):
        """Валидация наценки - от 0 до 1000%"""
        markup = self.cleaned_data.get('markup')
        if markup is not None:
            if markup < 0 or markup > 1000:
                raise forms.ValidationError("Наценка должна быть от 0% до 1000%")
        return markup
    
    def clean_title(self):
        """Валидация названия - минимум 3 символа"""
        title = self.cleaned_data.get('title')
        if title:
            title = title.strip()
            if len(title) < 3:
                raise forms.ValidationError("Название должно содержать минимум 3 символа")
        return title


class CalculationItemForm(forms.ModelForm):
    """Форма для добавления товаров в расчёт."""
    class Meta:
        model = CalculationItem
        fields = ['item', 'quantity']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }


class UploadPricesForm(forms.Form):
    """Форма для загрузки товаров из файла Excel."""
    file = forms.FileField(
        label="Выберите файл Excel",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    
    def clean_file(self):
        """Валидация загружаемого файла - размер и формат"""
        file = self.cleaned_data.get('file')
        if file:
            # Проверка размера файла (максимум 10MB)
            max_size = 10 * 1024 * 1024
            if file.size > max_size:
                raise forms.ValidationError("Файл слишком большой. Максимальный размер: 10MB")
            
            # Проверка расширения файла
            if not file.name.endswith(('.xlsx', '.xls')):
                raise forms.ValidationError("Поддерживаются только файлы Excel (.xlsx, .xls)")
        return file


class UserCreateForm(UserCreationForm):
    """Форма для создания нового пользователя."""
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'is_admin']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя пользователя'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите email'
            }),
            'is_admin': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'username': 'Имя пользователя',
            'email': 'Электронная почта',
            'is_admin': 'Роль - Администратор?',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Отключаем вспомогательный текст для всех полей
        for field in self.fields.values():
            field.help_text = ''
        # Настраиваем виджеты для полей с паролями
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Повторите пароль'
        })


class UserEditForm(UserChangeForm):
    """Форма для редактирования существующего пользователя."""
    password = None  # Отключаем отображение пароля

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'is_active', 'is_admin']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя пользователя'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите email'
            }),
            'is_admin': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            # Можно добавить виджет для is_active, если требуется редактирование
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'username': 'Имя пользователя',
            'email': 'Электронная почта',
            'is_active': 'Активен',
            'is_admin': 'Администратор',
        }
        help_texts = {
            'username': '',
            'email': '',
            'is_active': '',
            'is_admin': '',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Удаляем стандартные подсказки для всех полей
        for field in self.fields.values():
            field.help_text = ''
        # Добавляем класс form-control для всех полей, кроме чекбоксов
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'form-control')
