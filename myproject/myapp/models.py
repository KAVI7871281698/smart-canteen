from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import MinValueValidator
from django.utils import timezone
import os
from django.conf import settings

class User(AbstractUser):
    """
    Custom user model for the Smart Canteen System
    """
    STUDENT = 1
    STAFF = 2
    ADMIN = 3
    
    USER_TYPE_CHOICES = (
        (STUDENT, 'Student'),
        (STAFF, 'Staff'),
        (ADMIN, 'Admin'),
    )
    
    user_type = models.PositiveSmallIntegerField(
        choices=USER_TYPE_CHOICES,
        default=STUDENT
    )
    
    pin = models.CharField(
        max_length=4,
        help_text="4-digit PIN for authentication"
    )
    
    wallet_balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    
    qr_code = models.ImageField(
        upload_to='qr_codes/',
        blank=True,
        null=True
    )
    
    # Add these to resolve the reverse accessor conflicts
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="canteen_user_groups",
        related_query_name="canteen_user",
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="canteen_user_permissions",
        related_query_name="canteen_user",
    )
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    class Meta:
        # Add this to ensure unique username/email if needed
        constraints = [
            models.UniqueConstraint(fields=['username'], name='unique_username'),
            models.UniqueConstraint(fields=['email'], name='unique_email'),
        ]

class Category(models.Model):
    """
    Food category model (e.g., Drinks, Snacks, Breakfast)
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class MenuItem(models.Model):
    """
    Food item model with price and availability status
    """
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='menu_items'
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    available = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - ₹{self.price}"
    
    class Meta:
        unique_together = ('category', 'name')

class Order(models.Model):
    """
    Order model to track user purchases
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"
    
    class Meta:
        ordering = ['-order_date']

class OrderItem(models.Model):
    """
    Individual items within an order
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.PROTECT
    )
    
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    
    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"
    
    class Meta:
        verbose_name = "Order Item"

class KOT(models.Model):
    """
    Kitchen Order Ticket (KOT) model
    """
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='kot'
    )
    
    kot_number = models.CharField(
        max_length=10,
        unique=True
    )
    
    generated_at = models.DateTimeField(auto_now_add=True)
    served = models.BooleanField(default=False)
    served_at = models.DateTimeField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if self.served and not self.served_at:
            self.served_at = timezone.now()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"KOT #{self.kot_number}"
    
    class Meta:
        verbose_name = "KOT"
        ordering = ['-generated_at']

class WalletTransaction(models.Model):
    """
    Model to track all wallet transactions
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wallet_transactions'
    )
    
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    
    transaction_type = models.CharField(
        max_length=10,
        choices=(
            ('CREDIT', 'Credit'),
            ('DEBIT', 'Debit')
        )
    )
    
    transaction_date = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.transaction_type} of ₹{self.amount} for {self.user.username}"
    
    class Meta:
        ordering = ['-transaction_date']