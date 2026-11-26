import json
import re
from decimal import Decimal
from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Product, Order, OrderItem
from .mpesa import stk_push, MpesaError


def cart_data(request):
    cart = request.session.get('cart', {})
    rows, total, count = [], Decimal('0.00'), 0
    for product_id, qty in cart.items():
        try:
            product = Product.objects.get(pk=int(product_id), active=True)
            quantity = min(int(qty), product.stock)
            if quantity < 1:
                continue
            subtotal = product.price * quantity
            rows.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})
            total += subtotal
            count += quantity
        except (Product.DoesNotExist, ValueError, TypeError):
            continue
    return rows, total, count

def base_context(request):
    _, _, count = cart_data(request)
    return {'cart_count': count}

def home(request):
    products = Product.objects.filter(active=True)
    category = request.GET.get('category', '')
    query = request.GET.get('q', '').strip()
    if category:
        products = products.filter(category=category)
    if query:
        products = products.filter(name__icontains=query) | products.filter(description__icontains=query)
    context = base_context(request)
    context.update({'products': products, 'categories': Product.CATEGORY_CHOICES,
                    'selected_category': category, 'query': query,
                    'featured': Product.objects.filter(active=True, featured=True)[:4]})
    return render(request, 'home.html', context)

def add_to_cart(request, product_id):
    if request.method != 'POST':
        return redirect('home')
    product = get_object_or_404(Product, pk=product_id, active=True)
    cart = request.session.get('cart', {})
    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        quantity = 1
    quantity = max(1, quantity)
    current = int(cart.get(str(product.id), 0))
    if current + quantity > product.stock:
        messages.error(request, f'Only {product.stock} unit(s) of {product.name} are available.')
    else:
        cart[str(product.id)] = current + quantity
        request.session['cart'] = cart
        messages.success(request, f'{product.name} added to your cart.')
    return redirect(request.META.get('HTTP_REFERER', 'home'))

def cart_view(request):
    rows, total, _ = cart_data(request)
    context = base_context(request)
    context.update({'cart_items': rows, 'total': total})
    return render(request, 'cart.html', context)

@require_POST
def update_cart(request, product_id):
    cart = request.session.get('cart', {})
    product = get_object_or_404(Product, pk=product_id)
    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        quantity = 1
    if quantity <= 0:
        cart.pop(str(product_id), None)
    elif quantity <= product.stock:
        cart[str(product_id)] = quantity
    else:
        messages.error(request, f'Only {product.stock} unit(s) available.')
    request.session['cart'] = cart
    return redirect('cart')

@require_POST
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart.pop(str(product_id), None)
    request.session['cart'] = cart
    return redirect('cart')

def checkout(request):
    rows, total, _ = cart_data(request)
    if not rows:
        messages.info(request, 'Your cart is empty.')
        return redirect('home')
    context = base_context(request)
    context.update({'cart_items': rows, 'total': total})
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone_raw = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        phone = normalize_phone(phone_raw)
        if not all([name, email, phone, address]):
            messages.error(request, 'Please complete all checkout fields and enter a valid Kenyan M-Pesa number.')
            return render(request, 'checkout.html', context)
        with transaction.atomic():
            # Re-check stock at checkout to avoid overselling.
            for row in rows:
                product = Product.objects.select_for_update().get(pk=row['product'].pk)
                if product.stock < row['quantity']:
                    messages.error(request, f'{product.name} no longer has enough stock. Please update your cart.')
                    return redirect('cart')
            order = Order.objects.create(customer_name=name, email=email, phone=phone,
                                         delivery_address=address, total=total)
            for row in rows:
                product = Product.objects.get(pk=row['product'].pk)
                OrderItem.objects.create(order=order, product=product, product_name=product.name,
                                         quantity=row['quantity'], unit_price=product.price)
        try:
            response = stk_push(phone, total, f'AGRO{order.pk}')
            order.mpesa_checkout_request_id = response.get('CheckoutRequestID', '')
            order.mpesa_merchant_request_id = response.get('MerchantRequestID', '')
            order.mpesa_result_description = response.get('CustomerMessage', 'STK Push sent.')
            order.save(update_fields=['mpesa_checkout_request_id', 'mpesa_merchant_request_id', 'mpesa_result_description'])
            request.session['cart'] = {}
            return redirect('order_status', order_id=order.pk)
        except MpesaError as exc:
            order.status = 'FAILED'
            order.mpesa_result_description = str(exc)
            order.save(update_fields=['status', 'mpesa_result_description'])
            context['payment_error'] = str(exc)
            context['order_id'] = order.pk
            return render(request, 'checkout.html', context)
    return render(request, 'checkout.html', context)

def normalize_phone(value):
    digits = re.sub(r'\D', '', value)
    if digits.startswith('0') and len(digits) == 10:
        digits = '254' + digits[1:]
    elif digits.startswith('7') or digits.startswith('1'):
        digits = '254' + digits
    return digits if re.fullmatch(r'254[17]\d{8}', digits) else ''

def order_status(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'order_status.html', {**base_context(request), 'order': order})

@csrf_exempt
@require_POST
def mpesa_callback(request):
    """Daraja callback endpoint. Safaricom calls this URL after the customer responds."""
    try:
        payload = json.loads(request.body.decode('utf-8'))
        callback = payload['Body']['stkCallback']
        checkout_id = callback.get('CheckoutRequestID', '')
        order = Order.objects.filter(mpesa_checkout_request_id=checkout_id).first()
        if order:
            result_code = callback.get('ResultCode')
            order.mpesa_result_description = callback.get('ResultDesc', '')
            if str(result_code) == '0':
                # Safaricom may retry callbacks. A repeated success must not
                # decrement stock twice or change an already-paid order.
                if order.status != 'PAID':
                    metadata = callback.get('CallbackMetadata', {}).get('Item', [])
                    values = {item.get('Name'): item.get('Value') for item in metadata}
                    order.status = 'PAID'
                    order.mpesa_receipt = str(values.get('MpesaReceiptNumber', ''))
                    with transaction.atomic():
                        order.save(update_fields=['status', 'mpesa_receipt', 'mpesa_result_description'])
                        for item in order.items.select_related('product'):
                            product = Product.objects.select_for_update().get(pk=item.product_id)
                            product.stock = max(0, product.stock - item.quantity)
                            product.save(update_fields=['stock'])
            elif order.status != 'PAID':
                order.status = 'FAILED'
                order.save(update_fields=['status', 'mpesa_result_description'])
        return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})
    except (ValueError, KeyError, TypeError):
        return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Invalid callback payload'}, status=400)
