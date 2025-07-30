from django.db import models
from inventory.models import Product
from django.contrib.auth.models import User

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales')
    quantity = models.PositiveIntegerField()
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_date = models.DateTimeField(auto_now_add=True)
    sold_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.product.title} - {self.quantity} واحد"

    def save(self, *args, **kwargs):
        self.quantity = int(self.quantity)
        self.product.quantity -= self.quantity
        if self.product.quantity < 0:
            raise ValueError("موجودی کافی نیست!")
        self.product.save()
        super().save(*args, **kwargs)

class LogEntry(models.Model):
    action = models.CharField(max_length=200)  # مثلاً "Sale created", "Product updated"
    details = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales_log_entries')

    def __str__(self):
        return f"{self.action} - {self.timestamp}"