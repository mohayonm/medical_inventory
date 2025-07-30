from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_code', 'title', 'price', 'quantity']
        labels = {
            'product_code': 'کد محصول',
            'title': 'عنوان محصول',
            'price': 'قیمت (تومان)',
            'quantity': 'تعداد',
        }
        widgets = {
            'product_code': forms.TextInput(attrs={'placeholder': 'مثال: P001'}),
            'title': forms.TextInput(attrs={'placeholder': 'مثال: سرنگ'}),
            'price': forms.NumberInput(attrs={'placeholder': 'مثال: 10000'}),
            'quantity': forms.NumberInput(attrs={'placeholder': 'مثال: 50'}),
        }