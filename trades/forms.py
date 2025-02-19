from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Item, Calculation, CalculationItem, CustomUser

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'price']


class CalculationForm(forms.ModelForm):
    """Форма для создания расчёта."""
    class Meta:
        model = Calculation
        fields = ['title', 'markup']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название расчёта'}),
            'markup': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Наценка (%)'}),
        }


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
