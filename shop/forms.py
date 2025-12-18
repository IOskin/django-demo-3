from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Product


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Логин",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "image",
            "name",
            "category",
            "description",
            "manufacturer",
            "supplier",
            "price",
            "unit",
            "stock_quantity",
            "discount_percent",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "manufacturer": forms.Select(attrs={"class": "form-select"}),
            "supplier": forms.Select(attrs={"class": "form-select"}),
            "price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "unit": forms.Select(attrs={"class": "form-select"}),
            "stock_quantity": forms.NumberInput(attrs={"class": "form-control"}),
            "discount_percent": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price < 0:
            raise forms.ValidationError("Цена не может быть отрицательной.")
        return price

    def clean_stock_quantity(self):
        quantity = self.cleaned_data["stock_quantity"]
        if quantity < 0:
            raise forms.ValidationError("Количество на складе не может быть отрицательным.")
        return quantity

    def clean_discount_percent(self):
        discount = self.cleaned_data["discount_percent"]
        if discount < 0:
            raise forms.ValidationError("Скидка не может быть отрицательной.")
        if discount > 100:
            raise forms.ValidationError("Скидка не может превышать 100%.")
        return discount


