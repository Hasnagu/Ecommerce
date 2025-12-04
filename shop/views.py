from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Product, ProductImage, Cart, Coupon
from accounts.models import Order, OrderItem


# ============================
# PRODUITS
# ============================

@login_required
def product_list(request):
    products = Product.objects.all()

    search = request.GET.get('search', '')
    category = request.GET.get('category', '')
    max_price = request.GET.get('max_price', '')

    if search:
        products = products.filter(name__icontains=search)
    if category:
        products = products.filter(category__icontains=category)
    if max_price:
        try:
            max_price = float(max_price)
            products = products.filter(price__lte=max_price)
        except ValueError:
            pass

    return render(request, 'accounts/client_dashboard.html', {
        'products': products,
        'search': search,
        'category': category,
        'max_price': max_price,
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, id=pk)
    gallery = ProductImage.objects.filter(product=product)

    recently = request.session.get('recently_viewed', [])
    if pk in recently:
        recently.remove(pk)
    recently.insert(0, pk)
    request.session['recently_viewed'] = recently[:6]

    return render(request, "shop/product_detail.html", {
        "product": product,
        "gallery": gallery
    })


# ============================
# PANIER
# ============================

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart_item.quantity += 1

    cart_item.save()
    return redirect('cart')


@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)

    subtotal = sum(item.total_price() for item in cart_items)

    discount = request.session.get('coupon_discount', 0)
    shipping = 5
    total_with_shipping = subtotal - discount + shipping

    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'total': subtotal,
        'discount': discount,
        'shipping': shipping,
        'total_with_shipping': total_with_shipping,
        'expected_delivery': "3-5 jours ouvrés"
    })


@login_required
def cart_increase(request, product_id):
    cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('cart')


@login_required
def cart_decrease(request, product_id):
    cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('cart')


@login_required
def cart_remove(request, product_id):
    cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)
    cart_item.delete()
    return redirect('cart')


# ============================
# COUPONS
# ============================

@login_required
def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('coupon_code', '').strip()

        try:
            coupon = Coupon.objects.get(code__iexact=code, active=True)
            request.session['coupon_discount'] = float(coupon.discount_amount)
            request.session['coupon_code'] = coupon.code
        except Coupon.DoesNotExist:
            request.session['coupon_discount'] = 0
            request.session['coupon_code'] = ''

    return redirect('cart')


# ============================
# CHECKOUT
# ============================

@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items.exists():
        messages.error(request, "Votre panier est vide.")
        return redirect("cart")

    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    discount = request.session.get('coupon_discount', 0)
    shipping = 5
    total_with_shipping = subtotal - discount + shipping

    coupon_code = request.session.get('coupon_code', '')

    if request.method == "POST":
        order = Order.objects.create(
            user=request.user,
            payment_method=request.POST.get("payment_method", "cash"),
            status="Pending"
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
            )

        cart_items.delete()

        request.session['coupon_discount'] = 0
        request.session['coupon_code'] = ''

        return render(request, "shop/checkout_done.html", {
            "order": order
        })

    return render(request, "shop/checkout.html", {
        "cart_items": cart_items,
        "total": subtotal,
        'discount': discount,
        "shipping": shipping,
        "total_with_shipping": total_with_shipping,
        "coupon_code": coupon_code,
        "expected_delivery": "3-5 jours ouvrés",
    })


# ============================
# COMMANDES CLIENT
# ============================

@login_required
def client_orders(request):
    orders = Order.objects.filter(user=request.user)

    return render(request, "accounts/client_orders.html", {
        "orders": orders
    })
