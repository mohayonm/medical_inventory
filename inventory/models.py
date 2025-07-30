from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Product(models.Model):
    product_code = models.CharField(max_length=50, unique=True, verbose_name="کد محصول")
    title = models.CharField(max_length=200, verbose_name="عنوان محصول")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="قیمت (تومان)")
    quantity = models.PositiveIntegerField(verbose_name="تعداد")
    main_image = models.ImageField(upload_to='product_images/main/', null=True, blank=True, verbose_name="تصویر اصلی")
    additional_images = models.JSONField(default=list, blank=True, null=True, verbose_name="تصاویر اضافی")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش")

    def __str__(self):
        return f"{self.title} ({self.product_code})"

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="نام نقش")
    description = models.TextField(blank=True, verbose_name="توضیحات نقش")

    def __str__(self):
        return self.name

class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name="نقش")
    assigned_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ تخصیص")

    class Meta:
        unique_together = ('user', 'role')
        verbose_name = "نقش کاربر"
        verbose_name_plural = "نقش‌های کاربر"

    def __str__(self):
        return f"{self.user.username} - {self.role.name}"

class LogEntry(models.Model):
    action = models.CharField(max_length=100, verbose_name="عمل انجام‌شده")
    details = models.TextField(verbose_name="جزئیات")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inventory_log_entries', verbose_name="کاربر")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="زمان ثبت")

    def __str__(self):
        return f"{self.action} by {self.user.username} at {self.timestamp}"

    class Meta:
        verbose_name = "لاگ"
        verbose_name_plural = "لاگ‌ها"