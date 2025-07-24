from django.db import models
import jdatetime

class Product(models.Model):
    product_code = models.CharField(max_length=50, unique=True, verbose_name="کد محصول")
    title = models.CharField(max_length=100, verbose_name="عنوان محصول")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="قیمت (تومان)")
    quantity = models.PositiveIntegerField(verbose_name="تعداد")
    expiration_date = models.DateField(verbose_name="تاریخ انقضا", default=jdatetime.date.today)
    created_at = models.DateField(auto_now_add=True, verbose_name="تاریخ ثبت")

    def __str__(self):
        return f"{self.title} ({self.product_code})"

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"