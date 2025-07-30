from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from inventory.models import Product
from .models import Cart, CartItem, Order
import jdatetime

@login_required
def shop_home(request):
    products = Product.objects.all()
    return render(request, 'shop/shop_home.html', {'products': products})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    if product.quantity <= 0:
        messages.error(request, 'موجودی این محصول تمام شده است!')
    else:
        product.quantity -= 1
        product.save()
        messages.success(request, 'محصول به سبد خرید اضافه شد!')
    return redirect('shop_home')

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    total = sum(item.product.price * item.quantity for item in cart_items)
    # محاسبه جمع برای هر آیتم
    cart_items_with_total = [
        {
            'item': item,
            'subtotal': item.product.price * item.quantity
        }
        for item in cart_items
    ]
    return render(request, 'shop/cart.html', {
        'cart_items_with_total': cart_items_with_total,
        'total': total
    })

@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    if not cart_items.exists():
        messages.error(request, 'سبد خرید خالی است!')
        return redirect('cart_view')
    total = sum(item.product.price * item.quantity for item in cart_items)
    if request.method == 'POST':
        order = Order.objects.create(user=request.user, cart=cart, total_price=total)
        cart_items.delete()  # خالی کردن سبد بعد از سفارش
        messages.success(request, 'سفارش شما ثبت شد!')
        return redirect('shop_home')
    return render(request, 'shop/checkout.html', {'total': total})

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
            'description': product.description or 'توضیحاتی موجود نیست',
            'main_image': product.main_image.url if product.main_image else None,
            'additional_images': additional_images_urls
        })
    print(f"Products sent to template: {products_with_jalali}")  # برای دیباگ
    return render(request, 'inventory/shop.html', {'products_with_jalali': products_with_jalali})