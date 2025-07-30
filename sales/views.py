from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Sale, LogEntry
from inventory.models import Product
import jdatetime
import pandas as pd
from io import BytesIO

@login_required
def sale_list(request):
    search_query = request.GET.get('q', '')
    search_min_quantity = request.GET.get('min_quantity', '')
    search_max_quantity = request.GET.get('max_quantity', '')
    search_min_price = request.GET.get('min_price', '')
    search_max_price = request.GET.get('max_price', '')
    search_date_start = request.GET.get('date_start', '')
    search_date_end = request.GET.get('date_end', '')
    sort_by = request.GET.get('sort', 'sale_date')
    order = request.GET.get('order', 'desc')

    sales = Sale.objects.all()
    if search_query:
        sales = sales.filter(product__title__icontains=search_query)
    if search_min_quantity or search_max_quantity:
        sales = sales.filter(quantity__gte=search_min_quantity or 0, quantity__lte=search_max_quantity or float('inf'))
    if search_min_price or search_max_price:
        sales = sales.filter(sale_price__gte=search_min_price or 0, sale_price__lte=search_max_price or float('inf'))
    if search_date_start or search_date_end:
        from django.utils import timezone
        start_date = timezone.datetime.fromisoformat(search_date_start) if search_date_start else None
        end_date = timezone.datetime.fromisoformat(search_date_end) if search_date_end else None
        if start_date and end_date:
            sales = sales.filter(sale_date__range=(start_date, end_date))
        elif start_date:
            sales = sales.filter(sale_date__gte=start_date)
        elif end_date:
            sales = sales.filter(sale_date__lte=end_date)

    if sort_by in ['sale_date', 'quantity', 'sale_price']:
        if order == 'asc':
            sales = sales.order_by(sort_by)
        else:
            sales = sales.order_by(f'-{sort_by}')
    else:
        sales = sales.order_by('-sale_date')

    sales_with_jalali = []
    for sale in sales:
        jalali_date = jdatetime.datetime.fromgregorian(datetime=sale.sale_date).strftime('%Y/%m/%d %H:%M')
        sales_with_jalali.append({
            'sale': sale,
            'jalali_date': jalali_date
        })

    return render(request, 'sales/sale_list.html', {
        'sales_with_jalali': sales_with_jalali,
        'search_query': search_query,
        'search_min_quantity': search_min_quantity,
        'search_max_quantity': search_max_quantity,
        'search_min_price': search_min_price,
        'search_max_price': search_max_price,
        'search_date_start': search_date_start,
        'search_date_end': search_date_end,
        'sort_by': sort_by,
        'order': order,
    })

@login_required
def sale_create(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')
        sale_price = request.POST.get('sale_price')
        product = get_object_or_404(Product, id=product_id)
        if int(quantity) > product.quantity:
            messages.error(request, 'موجودی کافی نیست!')
        else:
            sale = Sale(product=product, quantity=quantity, sale_price=sale_price, sold_by=request.user)
            sale.save()
            LogEntry.objects.create(action="Sale created", details=f"Sold {quantity} units of {product.title}", user=request.user)
            messages.success(request, 'فروش با موفقیت ثبت شد.')
        return redirect('sale_list')
    products = Product.objects.all()
    return render(request, 'sales/sale_form.html', {'products': products})

@login_required
def backup_sales(request):
    if not request.user.is_authenticated:
        return redirect('sale_list')
    if request.GET.get('type') == 'excel':
        # بکاپ اکسل فروش‌ها
        sales = Sale.objects.all().values('product__title', 'quantity', 'sale_price', 'sale_date', 'sold_by__username')
        df = pd.DataFrame.from_records(sales)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Sales', index=False)
        output.seek(0)
        response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="backup_sales.xlsx"'
        return response
    else:
        # بکاپ JSON فروش‌ها
        data = serializers.serialize("json", Sale.objects.all())
        response = HttpResponse(data, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="backup_sales.json"'
        return response