from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

from .models import CustomUser, Order, OrderItem
from shop.models import Product
from .forms import RegisterForm


# =====================================================
# ADMIN CHECK
# =====================================================
def admin_required(view_func):
    return user_passes_test(lambda u: u.is_staff)(view_func)


# =====================================================
# REGISTER
# =====================================================
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            role = form.cleaned_data.get("role")
            user.is_staff = True if role == "admin" else False

            user.save()
            login(request, user)

            return redirect('admin_dashboard' if user.is_staff else 'client_dashboard')

        messages.error(request, "Veuillez corriger les erreurs.")
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


# =====================================================
# LOGIN
# =====================================================
def login_view(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password"),
        )

        if user:
            login(request, user)
            return redirect('admin_dashboard' if user.is_staff else 'client_dashboard')
        else:
            messages.error(request, "Identifiants incorrects.")

    return render(request, 'accounts/login.html')


# =====================================================
# LOGOUT
# =====================================================
def logout_view(request):
    logout(request)
    return redirect('login')


# =====================================================
# CLIENT DASHBOARD
# =====================================================
@login_required
def client_dashboard(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')

    products = Product.objects.all()

    recent_ids = request.session.get("recently_viewed", [])
    recently_viewed = Product.objects.filter(id__in=recent_ids)

    return render(request, "accounts/client_dashboard.html", {
        "products": products,
        "recently_viewed": recently_viewed,
    })


# =====================================================
# ADMIN DASHBOARD
# =====================================================
@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('client_dashboard')

    return render(request, "accounts/admin_dashboard.html")


# =====================================================
# EDIT PROFILE
# =====================================================
@login_required
def edit_profile(request):
    user = request.user

    if request.method == 'POST':
        user.username = request.POST.get("username")
        user.email = request.POST.get("email")
        user.save()

        messages.success(request, "Profil mis à jour.")
        return redirect('client_dashboard')

    return render(request, "accounts/edit_profile.html")


# =====================================================
# CLIENT ORDERS
# =====================================================
@login_required
def client_orders(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')

    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'accounts/client_orders.html', {'orders': orders})


# =====================================================
# ADMIN : LIST ALL ORDERS
# =====================================================
@admin_required
def admin_orders(request):
    orders = Order.objects.all().order_by("-created_at")
    return render(request, 'accounts/admin_orders.html', {'orders': orders})


# =====================================================
# ADMIN ORDER ACCEPT
# =====================================================
@admin_required
def admin_order_accept(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = "Accepted"
    order.save()
    messages.success(request, f"Commande #{order.id} acceptée.")
    return redirect("admin_orders")


# =====================================================
# ADMIN ORDER REJECT
# =====================================================
@admin_required
def admin_order_reject(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = "Rejected"
    order.save()
    messages.error(request, f"Commande #{order.id} refusée.")
    return redirect("admin_orders")


# =====================================================
# ADMIN : USERS LIST
# =====================================================
@admin_required
def admin_manage_users(request):
    users = CustomUser.objects.all()
    return render(request, 'accounts/admin_manage_users.html', {'users': users})


# =====================================================
# ADMIN : ADD PRODUCT
# =====================================================
@admin_required
def admin_add_product(request):
    if request.method == 'POST':
        Product.objects.create(
            name=request.POST.get("name"),
            price=request.POST.get("price"),
            description=request.POST.get("description"),
            image=request.FILES.get("image"),
        )
        messages.success(request, "Produit ajouté.")
        return redirect('admin_dashboard')

    return render(request, 'accounts/admin_add_product.html')


# =====================================================
# ADMIN : EDIT PRODUCT
# =====================================================
@admin_required
def admin_edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product.name = request.POST.get("name")
        product.price = request.POST.get("price")
        product.description = request.POST.get("description")

        if request.FILES.get("image"):
            product.image = request.FILES.get("image")

        product.save()

        messages.success(request, "Produit modifié.")
        return redirect('admin_products')

    return render(request, 'accounts/admin_edit_product.html', {'product': product})


# =====================================================
# ADMIN : LIST PRODUCTS
# =====================================================
@admin_required
def admin_products(request):
    products = Product.objects.all()
    return render(request, "accounts/admin_products.html", {"products": products})


# =====================================================
# ADMIN : DELETE PRODUCT
# =====================================================
@admin_required
def admin_delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('admin_products')


# =====================================================
# PDF GENERATION
# =====================================================
@login_required
def order_pdf(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_{order.id}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 2 * cm

    # TITLE
    p.setFont("Helvetica-Bold", 20)
    p.drawString(2 * cm, y, f"Facture - Commande #{order.id}")
    y -= 1.5 * cm

    # USER INFO
    p.setFont("Helvetica-Bold", 14)
    p.drawString(2 * cm, y, "Informations du client :")
    y -= 0.8 * cm

    p.setFont("Helvetica", 12)
    p.drawString(2 * cm, y, f"Nom : {order.user.username}")
    y -= 1.2 * cm

    # ORDER DETAILS
    p.setFont("Helvetica-Bold", 14)
    p.drawString(2 * cm, y, "Détails de la commande :")
    y -= 1 * cm

    p.setFont("Helvetica-Bold", 12)
    p.drawString(2 * cm, y, "Produit")
    p.drawString(10 * cm, y, "Quantité")
    p.drawString(14 * cm, y, "Total")
    y -= 0.8 * cm

    p.setFont("Helvetica", 12)

    for item in order.items.all():
        p.drawString(2 * cm, y, f"{item.product.name}")
        p.drawString(10 * cm, y, f"{item.quantity}")
        p.drawString(14 * cm, y, f"{item.subtotal:.2f} €")
        y -= 0.6 * cm

    # TOTAL
    y -= 1 * cm
    p.setFont("Helvetica-Bold", 14)
    p.drawString(2 * cm, y, f"Total : {order.total_price:.2f} €")

    p.showPage()
    p.save()

    return response
