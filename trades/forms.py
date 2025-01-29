from django import forms
from .models import Item, Calculation, CalculationItem, UserSettings


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


class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = UserSettings
        fields = ['decimal_places_price', 'decimal_places_percentage', 'price_step', 'markup_step']
        labels = {
            'decimal_places_price': 'Знаков после запятой для цены',
            'decimal_places_percentage': 'Знаков после запятой для наценки',
            'price_step': 'Шаг изменения цены',
            'markup_step': 'Шаг изменения наценки',
        }
        widgets = {
            'decimal_places_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'decimal_places_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
            'price_step': forms.NumberInput(attrs={'class': 'form-control', 'step': 0.01}),
            'markup_step': forms.NumberInput(attrs={'class': 'form-control'}),
        }
