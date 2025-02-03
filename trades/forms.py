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

class UserEditForm(UserChangeForm):
    """Форма для редактирования существующего пользователя."""
    password = None  # Отключаем отображение пароля в форме редактирования

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'is_active', 'is_admin']