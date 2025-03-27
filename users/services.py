import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product(course_title, course_price):
    """Создает продукт в Stripe"""
    product = stripe.Product.create(name=course_title)
    return product.id


def create_stripe_price(product_id, course_price):
    """Создает цену для продукта в Stripe"""
    price = stripe.Price.create(
        unit_amount=int(course_price * 100),  # Цена в копейках
        currency='usd',
        product=product_id
    )
    return price.id


def create_stripe_checkout_session(price_id):
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': price_id,
            'quantity': 1,
        }],
        mode='payment',
        success_url='http://localhost:8000/success/',
        cancel_url='http://localhost:8000/cancel/',
    )
    return session.id  # Возвращаем только session_id
