from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('', views.qr_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('process-qr-login/', views.process_qr_login, name='process_qr_login'),
    
    # User routes
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('category/<int:category_id>/', views.category_items, name='category_items'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('confirm-order/', views.confirm_order, name='confirm_order'),
    
    # Admin routes
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/create-user/', views.create_user, name='create_user'),
    path('admin/recharge-wallet/<int:user_id>/', views.recharge_wallet, name='recharge_wallet'),
    
    # Staff routes
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/process-kot/<int:kot_id>/', views.process_kot, name='process_kot'),
]