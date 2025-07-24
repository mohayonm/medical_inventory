from django import forms
from .models import Product
from django_jalali.forms import jDateField

class ProductForm(forms.ModelForm):
    expiration_date = jDateField(label="تاریخ انقضا")

    class Meta:
        model = Product
        fields = ['product_code', 'title', 'price', 'quantity', 'expiration_date']
        labels = {
            'product_code': 'کد محصول',
            'title': 'عنوان محصول',
            'price': 'قیمت (تومان)',
            'quantity': 'تعداد',
            'expiration_date': 'تاریخ انقضا',
        }