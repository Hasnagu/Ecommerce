from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),

    path("client/dashboard/", views.client_dashboard, name="client_dashboard"),
    path("client/orders/", views.client_orders, name="client_orders"),

    path("edit-profile/", views.edit_profile, name="edit_profile"),

    path("admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin/orders/", views.admin_orders, name="admin_orders"),
    path("admin/users/", views.admin_manage_users, name="admin_manage_users"), path("admin/products/", views.admin_products, name="admin_products"),
    path("admin/product/add/", views.admin_add_product, name="admin_add_product"),
    path('admin/product/delete/<int:product_id>/', views.admin_delete_product, name='admin_delete_product'),
path("order/<int:order_id>/pdf/", views.order_pdf, name="order_pdf"),
   path("admin/orders/<int:order_id>/accept/", 
         views.admin_order_accept, 
         name="admin_order_accept"),

    path("admin/orders/<int:order_id>/reject/", 
         views.admin_order_reject, 
         name="admin_order_reject"),
    path("admin/product/edit/<int:product_id>/", views.admin_edit_product, name="admin_edit_product"),
]
