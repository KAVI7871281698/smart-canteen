from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from .models import User, Category, MenuItem, Order, OrderItem, KOT, WalletTransaction
from .qr_utils import generate_qr_code
from .decorators import login_required, admin_required, staff_required
from django.core.files import File
import os
from django.conf import settings

# Authentication Views
def qr_login(request):
    # if request.user.is_authenticated:
    #     return redirect('qr_login')
    return render(request, 'qr_login.html')

def process_qr_login(request):
    if request.user.is_authenticated:
        return redirect('user_dashboard')
        
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        pin = request.POST.get('pin')
        
        try:
            user = User.objects.get(id=user_id)
            if user.pin == pin:
                login(request, user)
                return redirect('user_dashboard')
            messages.error(request, "Invalid PIN")
        except User.DoesNotExist:
            messages.error(request, "User not found")
        return redirect('login')
    
    return redirect('login')

def logout_view(request):
    logout(request)
    return redirect('login')

# User Views
@login_required
def user_dashboard(request):
    categories = Category.objects.all()
    return render(request, 'dashboard.html', {
        'categories': categories,
        'user': request.user,
    })

@login_required
def category_items(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    items = MenuItem.objects.filter(category=category, available=True)
    return render(request, 'category_items.html', {
        'category': category,
        'items': items
    })

@login_required
@require_POST
def add_to_cart(request):
    try:
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        
        item = MenuItem.objects.get(id=item_id)
        
        cart = request.session.get('cart', {})
        cart_item = cart.get(str(item_id), {'quantity': 0, 'price': str(item.price)})
        cart_item['quantity'] += quantity
        cart[str(item_id)] = cart_item
        request.session['cart'] = cart
        
        return JsonResponse({
            'success': True, 
            'cart_total': sum(item['quantity'] for item in cart.values())
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    
    for item_id, item_data in cart.items():
        try:
            menu_item = MenuItem.objects.get(id=item_id)
            quantity = item_data['quantity']
            price = float(item_data['price'])
            subtotal = quantity * price
            
            cart_items.append({
                'item': menu_item,
                'quantity': quantity,
                'subtotal': subtotal
            })
            total += subtotal
        except MenuItem.DoesNotExist:
            continue
    
    return render(request, 'cart.html', {
        'items': cart_items,
        'total': total
    })

@login_required
@transaction.atomic
def confirm_order(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        
        if not cart:
            messages.error(request, "Your cart is empty")
            return redirect('view_cart')
        
        # Calculate total
        total = sum(float(item['price']) * item['quantity'] for item in cart.values())
        
        # Check wallet balance
        if request.user.wallet_balance < total:
            messages.error(request, "Insufficient wallet balance")
            return redirect('view_cart')
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            total_amount=total
        )
        
        # Create order items
        for item_id, item_data in cart.items():
            menu_item = MenuItem.objects.get(id=item_id)
            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=item_data['quantity'],
                price=item_data['price']
            )
        
        # Update wallet
        request.user.wallet_balance -= total
        request.user.save()
        
        # Record transaction
        WalletTransaction.objects.create(
            user=request.user,
            amount=total,
            transaction_type='DEBIT',
            reference=f'Order #{order.id}'
        )
        
        # Generate KOT
        kot = KOT.objects.create(
            order=order,
            kot_number=f"KOT{order.id:05d}"
        )
        
        # Clear cart
        request.session['cart'] = {}
        
        return render(request, 'kot.html', {'kot': kot})
    
    return redirect('view_cart')

# Admin Views
@admin_required
def admin_dashboard(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'dashboard.html', {'users': users})

@admin_required
def create_user(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            pin = request.POST.get('pin')
            user_type = int(request.POST.get('user_type'))
            
            user = User.objects.create_user(
                username=username,
                pin=pin,
                user_type=user_type
            )
            
            # Generate and save QR code
            qr_path = generate_qr_code(user)
            user.qr_code.save(os.path.basename(qr_path), File(open(qr_path, 'rb')))
            user.save()
            
            messages.success(request, "User created successfully")
            return redirect('admin_dashboard')
        except Exception as e:
            messages.error(request, f"Error creating user: {str(e)}")
    
    return render(request, 'create_user.html')

@admin_required
def recharge_wallet(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        try:
            amount = float(request.POST.get('amount'))
            if amount <= 0:
                raise ValueError("Amount must be positive")
            
            user.wallet_balance += amount
            user.save()
            
            WalletTransaction.objects.create(
                user=user,
                amount=amount,
                transaction_type='CREDIT',
                reference='Admin recharge'
            )
            
            messages.success(request, f"Successfully recharged ₹{amount} to {user.username}'s wallet")
            return redirect('admin_dashboard')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    
    return render(request, 'recharge_wallet.html', {'user': user})

# Staff Views
@staff_required
def staff_dashboard(request):
    pending_kots = KOT.objects.filter(served=False).order_by('generated_at')
    return render(request, 'dashboard.html', {'kots': pending_kots})

@staff_required
@require_POST
def process_kot(request, kot_id):
    kot = get_object_or_404(KOT, id=kot_id)
    kot.served = True
    kot.save()
    
    messages.success(request, f"KOT #{kot.kot_number} marked as served")
    return redirect('staff_dashboard')

# Additional Utility Views
@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'order_history.html', {'orders': orders})

@login_required
def transaction_history(request):
    transactions = WalletTransaction.objects.filter(user=request.user).order_by('-transaction_date')
    return render(request, 'transaction_history.html', {'transactions': transactions})