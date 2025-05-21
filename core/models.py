from django.db import models
from django.contrib.auth.models import User

class AccessRight(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resource = models.CharField(max_length=100)  # Exemple : 'transactions'
    can_access = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'resource')

    def __str__(self):
        return f"{self.user.username} - {self.resource} : {'✅' if self.can_access else '❌'}"

class Transaction(models.Model):
    row_id = models.IntegerField(unique=True)  # ← Row.ID
    order_id = models.CharField(max_length=100)  # ← Order.ID
    order_date = models.DateTimeField()  # ← Order.Date
    customer_name = models.CharField(max_length=100)  # ← Customer.Name
    country = models.CharField(max_length=100)
    product_category = models.CharField(max_length=100)  # ← Sub.Category
    payment_method = models.CharField(max_length=100)  # ← Payment_Method
    status = models.CharField(max_length=100)
    amount = models.FloatField()  # ← Sales
    customer_rating = models.FloatField()  # ← Customer_Rating

    def __str__(self):
        return f"{self.row_id} - {self.customer_name}"

class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    method = models.CharField(max_length=10)
    path = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    body = models.TextField(blank=True)

    def __str__(self):
        return f"[{self.timestamp}] {self.user} → {self.method} {self.path}"
