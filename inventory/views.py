import json
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from .models import Product, Role, UserRole
from .forms import ProductForm
from django.db.models import Q, Sum
import jdatetime
import base64
from django.contrib import messages
import pandas as pd
from io import BytesIO
from sales.models import Sale
from django.conf import settings

class CustomLoginView(LoginView):
    template_name = 'inventory/login.html'
    redirect_authenticated_user = True
    success_url = '/dashboard/'

def login_redirect(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/?next=/dashboard/')
    return HttpResponseRedirect('/dashboard/')

@login_required
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    roles = UserRole.objects.filter(user=request.user)
    context = {
        'username': request.user.username,
        'roles': [role.role.name for role in roles],
        'sections': [
            {'name': 'مدیریت انبار', 'url': '/inventory/', 'icon': 'fa-box'},
            {'name': 'بکاپ‌گیری', 'url': '/backup/', 'icon': 'fa-download'},
            {'name': 'تنظیم دسترسی', 'url': '/manage-roles/', 'icon': 'fa-lock'},
            {'name': 'آپلود اکسل', 'url': '#', 'form_id': 'excel-upload-form', 'icon': 'fa-file-excel'},
            {'name': 'مدیریت فروش', 'url': '/sales/', 'icon': 'fa-cart-plus'},
            {'name': 'درآمد', 'url': '/income/', 'icon': 'fa-money-bill'},
            {'name': 'فروشگاه', 'url': '/shop/', 'icon': 'fa-store'},
        ]
    }
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        file_content = excel_file.read()
        encoded_content = base64.b64encode(file_content).decode('utf-8')
        context['message'] = 'فایل با موفقیت آپلود شد، در حال پردازش...'
    return render(request, 'inventory/dashboard.html', context)

@login_required
def product_list(request):
    search_query = request.GET.get('q', '')
    search_code = request.GET.get('code', '')
    search_title = request.GET.get('title', '')
    search_min_price = request.GET.get('min_price', '')
    search_max_price = request.GET.get('max_price', '')
    search_min_quantity = request.GET.get('min_quantity', '')
    search_max_quantity = request.GET.get('max_quantity', '')
    search_created_start = request.GET.get('created_start', '')
    search_created_end = request.GET.get('created_end', '')
    search_updated_start = request.GET.get('updated_start', '')
    search_updated_end = request.GET.get('updated_end', '')
    sort_by = request.GET.get('sort', 'created_at')
    order = request.GET.get('order', 'desc')

    products = Product.objects.all()
    if search_query:
        products = products.filter(
            Q(product_code__icontains=search_query) |
            Q(title__icontains=search_query) |
            Q(price__icontains=search_query) |
            Q(quantity__icontains=search_query)
        )
    if search_code:
        products = products.filter(product_code__icontains=search_code)
    if search_title:
        products = products.filter(title__icontains=search_title)
    if search_min_price or search_max_price:
        products = products.filter(price__gte=search_min_price or 0, price__lte=search_max_price or float('inf'))
    if search_min_quantity or search_max_quantity:
        products = products.filter(quantity__gte=search_min_quantity or 0, quantity__lte=search_max_quantity or float('inf'))
    if search_created_start or search_created_end:
        from django.utils import timezone
        start_date = timezone.datetime.fromisoformat(search_created_start) if search_created_start else None
        end_date = timezone.datetime.fromisoformat(search_created_end) if search_created_end else None
        if start_date and end_date:
            products = products.filter(created_at__range=(start_date, end_date))
        elif start_date:
            products = products.filter(created_at__gte=start_date)
        elif end_date:
            products = products.filter(created_at__lte=end_date)
    if search_updated_start or search_updated_end:
        from django.utils import timezone
        start_date = timezone.datetime.fromisoformat(search_updated_start) if search_updated_start else None
        end_date = timezone.datetime.fromisoformat(search_updated_end) if search_updated_end else None
        if start_date and end_date:
            products = products.filter(updated_at__range=(start_date, end_date))
        elif start_date:
            products = products.filter(updated_at__gte=start_date)
        elif end_date:
            products = products.filter(updated_at__lte=end_date)

    if sort_by in ['product_code', 'title', 'price', 'quantity', 'created_at', 'updated_at']:
        if order == 'asc':
            products = products.order_by(sort_by)
        else:
            products = products.order_by(f'-{sort_by}')
    else:
        products = products.order_by('-created_at')

    products_with_jalali = []
    for product in products:
        jalali_created = jdatetime.datetime.fromgregorian(datetime=product.created_at).strftime('%Y/%m/%d %H:%M')
        jalali_updated = jdatetime.datetime.fromgregorian(datetime=product.updated_at).strftime('%Y/%m/%d %H:%M')
        products_with_jalali.append({
            'product': product,
            'jalali_created': jalali_created,
            'jalali_updated': jalali_updated
        })

    return render(request, 'inventory/product_list.html', {
        'products_with_jalali': products_with_jalali,
        'search_query': search_query,
        'search_code': search_code,
        'search_title': search_title,
        'search_min_price': search_min_price,
        'search_max_price': search_max_price,
        'search_min_quantity': search_min_quantity,
        'search_max_quantity': search_max_quantity,
        'search_created_start': search_created_start,
        'search_created_end': search_created_end,
        'search_updated_start': search_updated_start,
        'search_updated_end': search_updated_end,
        'sort_by': sort_by,
        'order': order,
    })

@login_required
def shop(request):
    products = Product.objects.all()
    products_with_jalali = []
    for product in products:
        jalali_created = jdatetime.datetime.fromgregorian(datetime=product.created_at).strftime('%Y/%m/%d %H:%M')
        jalali_updated = jdatetime.datetime.fromgregorian(datetime=product.updated_at).strftime('%Y/%m/%d %H:%M')
        # ساخت URL برای additional_images (فرض می‌کنیم تو media/product_images/additional/ ذخیره می‌شن)
        additional_images_urls = [f"{settings.MEDIA_URL}product_images/additional/{img}" for img in product.additional_images] if product.additional_images else []
        products_with_jalali.append({
            'product': product,
            'jalali_created': jalali_created,
            'jalali_updated': jalali_updated,
            'description': product.description,
            'main_image': product.main_image.url if product.main_image else None,
            'additional_images': additional_images_urls
        })
    return render(request, 'inventory/shop.html', {'products_with_jalali': products_with_jalali})

@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product_code = form.cleaned_data['product_code']
            if Product.objects.filter(product_code=product_code).exists():
                messages.error(request, 'کد محصول باید یکتا باشد!')
                return render(request, 'inventory/product_form.html', {'form': form})
            product = form.save()
            content_type = ContentType.objects.get_for_model(Product)
            LogEntry.objects.create(
                user=request.user,
                content_type=content_type,
                object_id=product.id,
                object_repr=product.title,
                action_flag=1,  # 1 برای ایجاد (ADD)
                change_message=f"Created product {product.title}"
            )
            messages.success(request, f'محصول {product.title} با موفقیت اضافه شد.')
            return redirect('product_list')
        else:
            print(form.errors)
            messages.error(request, 'خطا در ثبت محصول، کد محصول باید یکتا باشد')
            return render(request, 'inventory/product_form.html', {'form': form})
    else:
        form = ProductForm()
    return render(request, 'inventory/product_form.html', {'form': form})

@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product_code = form.cleaned_data['product_code']
            if Product.objects.exclude(pk=pk).filter(product_code=product_code).exists():
                messages.error(request, 'کد محصول باید یکتا باشد!')
                return render(request, 'inventory/product_form.html', {'form': form})
            product = form.save()
            content_type = ContentType.objects.get_for_model(Product)
            LogEntry.objects.create(
                user=request.user,
                content_type=content_type,
                object_id=product.id,
                object_repr=product.title,
                action_flag=2,  # 2 برای به‌روزرسانی (CHANGE)
                change_message=f"Updated product {product.title}"
            )
            messages.success(request, f'محصول {product.title} با موفقیت به‌روزرسانی شد.')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'inventory/product_form.html', {'form': form})

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        title = product.title
        product.delete()
        content_type = ContentType.objects.get_for_model(Product)
        LogEntry.objects.create(
            user=request.user,
            content_type=content_type,
            object_id=product.id,
            object_repr=title,
            action_flag=3,  # 3 برای حذف (DELETE)
            change_message=f"Deleted product {title}"
        )
        messages.success(request, f'محصول {title} با موفقیت حذف شد.')
        return redirect('product_list')
    return render(request, 'inventory/product_delete.html', {'product': product})

@login_required
def backup(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.GET.get('type') == 'excel_products':
        products = Product.objects.all().values('product_code', 'title', 'price', 'quantity', 'created_at', 'updated_at')
        df = pd.DataFrame.from_records(products)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Products', index=False)
        output.seek(0)
        response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="backup_products.xlsx"'
        return response
    elif request.GET.get('type') == 'json_products':
        data = serializers.serialize("json", Product.objects.all())
        response = HttpResponse(data, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="backup_products.json"'
        return response
    elif request.GET.get('type') == 'excel_sales':
        sales = Sale.objects.all().values('product__title', 'quantity', 'sale_price', 'sale_date', 'sold_by__username')
        df = pd.DataFrame.from_records(sales)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Sales', index=False)
        output.seek(0)
        response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="backup_sales.xlsx"'
        return response
    elif request.GET.get('type') == 'json_sales':
        data = serializers.serialize("json", Sale.objects.all())
        response = HttpResponse(data, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="backup_sales.json"'
        return response
    return render(request, 'inventory/backup.html')

@login_required
def manage_roles(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        if 'add_role' in request.POST:
            user_id = request.POST.get('user_id')
            role_id = request.POST.get('role_id')
            try:
                user = get_object_or_404(User, id=user_id)
                role = get_object_or_404(Role, id=role_id)
                UserRole.objects.get_or_create(user=user, role=role)
                content_type = ContentType.objects.get_for_model(UserRole)
                LogEntry.objects.create(
                    user=request.user,
                    content_type=content_type,
                    object_id=user.id,
                    object_repr=f"Assigned {role.name} to {user.username}",
                    action_flag=1,
                    change_message=f"Assigned role {role.name} to {user.username}"
                )
                messages.success(request, 'نقش با موفقیت اضافه شد.')
            except Exception as e:
                messages.error(request, f'خطا: {str(e)}')
        elif 'add_user' in request.POST:
            username = request.POST.get('new_username')
            password = request.POST.get('new_password')
            if username and password:
                try:
                    user = User.objects.create_user(username=username, password=password)
                    content_type = ContentType.objects.get_for_model(User)
                    LogEntry.objects.create(
                        user=request.user,
                        content_type=content_type,
                        object_id=user.id,
                        object_repr=username,
                        action_flag=1,
                        change_message=f"Created user {username}"
                    )
                    messages.success(request, f'کاربر {username} با موفقیت اضافه شد.')
                except Exception as e:
                    messages.error(request, f'خطا: {str(e)}')
        elif 'add_role_new' in request.POST:
            new_role_name = request.POST.get('new_role_name')
            if new_role_name:
                try:
                    role = Role.objects.get_or_create(name=new_role_name)[0]
                    content_type = ContentType.objects.get_for_model(Role)
                    LogEntry.objects.create(
                        user=request.user,
                        content_type=content_type,
                        object_id=role.id,
                        object_repr=new_role_name,
                        action_flag=1,
                        change_message=f"Created role {new_role_name}"
                    )
                    messages.success(request, f'نقش {new_role_name} با موفقیت ایجاد شد.')
                except Exception as e:
                    messages.error(request, f'خطا: {str(e)}')
        return redirect('manage_roles')
    roles = Role.objects.all()
    users = User.objects.all()
    user_roles = UserRole.objects.all()
    return render(request, 'inventory/manage_roles.html', {'roles': roles, 'users': users, 'user_roles': user_roles})

@login_required
def income(request):
    from django.utils import timezone

    today = timezone.now().date()
    this_week_start = today - timezone.timedelta(days=today.weekday())
    this_month_start = today.replace(day=1)
    this_year_start = today.replace(month=1, day=1)

    total_income = Sale.objects.aggregate(Sum('sale_price'))['sale_price__sum'] or 0
    today_income = Sale.objects.filter(sale_date__date=today).aggregate(Sum('sale_price'))['sale_price__sum'] or 0
    week_income = Sale.objects.filter(sale_date__date__gte=this_week_start).aggregate(Sum('sale_price'))['sale_price__sum'] or 0
    month_income = Sale.objects.filter(sale_date__date__gte=this_month_start).aggregate(Sum('sale_price'))['sale_price__sum'] or 0
    year_income = Sale.objects.filter(sale_date__date__gte=this_year_start).aggregate(Sum('sale_price'))['sale_price__sum'] or 0

    sales_by_product = Sale.objects.values('product__title').annotate(total_quantity=Sum('quantity'), total_price=Sum('sale_price')).order_by('-total_price')

    context = {
        'total_income': total_income,
        'today_income': today_income,
        'week_income': week_income,
        'month_income': month_income,
        'year_income': year_income,
        'sales_by_product': sales_by_product,
    }
    return render(request, 'inventory/income.html', context)

@login_required
def add_product(request):
    if request.method == 'POST':
        title = request.POST['title']
        product_code = request.POST['product_code']
        price = request.POST['price']
        quantity = request.POST['quantity']
        description = request.POST.get('description', '')  # اختیاری
        main_image = request.FILES.get('main_image')  # اختیاری
        additional_images = request.FILES.getlist('additional_images')  # لیست عکس‌های اضافی

        if Product.objects.filter(product_code=product_code).exists():
            messages.error(request, 'کد محصول تکراری است!')
            return redirect('add_product')

        product = Product(
            title=title,
            product_code=product_code,
            price=price,
            quantity=quantity,
            description=description
        )
        if main_image:
            product.main_image = main_image
        if additional_images:
            product.additional_images = [img.name for img in additional_images]  # فقط نام‌ها رو ذخیره می‌کنیم
        product.save()

        content_type = ContentType.objects.get_for_model(Product)
        LogEntry.objects.create(
            user=request.user,
            content_type=content_type,
            object_id=product.id,
            object_repr=product.title,
            action_flag=1,  # 1 برای ایجاد (ADD)
            change_message=f"Created product {product.title}"
        )
        messages.success(request, 'محصول با موفقیت اضافه شد!')
        return redirect('dashboard')
    return render(request, 'inventory/product_form.html')

@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    jalali_created = jdatetime.datetime.fromgregorian(datetime=product.created_at).strftime('%Y/%m/%d %H:%M')
    jalali_updated = jdatetime.datetime.fromgregorian(datetime=product.updated_at).strftime('%Y/%m/%d %H:%M')
    additional_images_urls = [f"{settings.MEDIA_URL}product_images/additional/{img}" for img in product.additional_images] if product.additional_images else []
    print(f"Product detail: {product}, Main Image: {product.main_image}, Description: {product.description}")  # دیباگ
    return render(request, 'inventory/product_detail.html', {
        'product': product,
        'jalali_created': jalali_created,
        'jalali_updated': jalali_updated,
        'additional_images': additional_images_urls
    })