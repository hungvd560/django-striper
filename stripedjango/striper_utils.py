from django.http import HttpResponseServerError
from rest_framework import generics, status
from rest_framework.response import Response
from stripe.error import StripeError
import stripe
from django.conf import settings
from users.models import ProductType, ProductInterval

stripe.api_key = settings.STRIPE_SECRET_KEY


def stripe_error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except StripeError as e:
            print('Stripe error:', str(e))
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return wrapper


@stripe_error_handler
def check_customer_exist(customer_id):
    """
    :param customer_id:
    :return:
    """
    try:
        token = stripe.Customer.retrieve(customer_id)
        return True
    except stripe.error.InvalidRequestError:
        # customer does not exist
        return False


@stripe_error_handler
def create_new_customer(email):
    """
    Tạo customer và thông tin thanh toán
    :param email:
    :param card:
    example : {
            "number": "4242424242424242",
            "exp_month": 12,
            "exp_year": 22,
            "cvc": "123"
        }
    :return:
    """
    customer = stripe.Customer.create(
        email=email
    )
    return customer


@stripe_error_handler
def add_payment_method(card, customer_id):
    """
    Tạo customer và thông tin thanh toán
    :param customer_id:
    :param card:
    example : {
            "number": "4242424242424242",
            "exp_month": 12,
            "exp_year": 22,
            "cvc": "123"
        }
    :return:
    """
    payment_method = stripe.PaymentMethod.create(
        type="card",
        card=card,
    )
    payment_method.attach(customer=customer_id)
    stripe.Customer.modify(
        customer_id,
        invoice_settings={
            'default_payment_method': payment_method.id
        }
    )
    return payment_method


@stripe_error_handler
def create_new_product(**kwargs):
    """
    # tạo sản phẩm và giá
    :return:
    """
    product = stripe.Product.create(
        name=kwargs.get('name'),
        description=kwargs.get('description'),
    )

    if kwargs.get('type') and kwargs.get('type') == ProductType.RECURRING:
        plan = stripe.Plan.create(
            amount=kwargs.get('unit_amount'),  # Số tiền thanh toán (tính bằng cents)
            currency=kwargs.get('currency'),
            interval=kwargs.get('interval', ProductInterval.MONTH),  # Chu kỳ thanh toán hàng tháng
            product=product["id"],
        )

    else:
        price = stripe.Price.create(
            unit_amount=kwargs.get('unit_amount'),
            currency=kwargs.get('currency'),
            product=product["id"],
        )

    return product


@stripe_error_handler
def create_new_payment_intent(amount, payment_method_id, customer_id, currency='usd'):
    """
    customer thanh toán order
    :param amount:
    :param currency:
    :param payment_method_id:
    :param customer_id:
    :return:
    """
    intent = stripe.PaymentIntent.create(
        amount=amount,
        currency=currency,
        customer=customer_id,
        payment_method=payment_method_id,
        confirm=True
    )
    return intent


# @stripe_error_handler
# def create_order(order, user_email):
#     """
#     customer thanh toán order
#     :param order:
#     :param customer:
#     :return:
#     """
#     # get product info
#     order_detail = order.order_details.all()
#     line_items = []
#     total_amount = 0
#     for item in order_detail:
#         product = stripe.Product.retrieve(item.product.product_id)
#         prices = stripe.Price.list(product=product)
#         price = next((p for p in prices.data if p.currency == item.product.currency), None)
#         if price:
#             line_items.append({
#                 'price': price.id,
#                 'quantity': item.quantity,
#             })
#             total_amount += (price.unit_amount*item.quantity)
#     order = stripe.Order.create(
#         currency='usd',
#         email=user_email,
#         items=line_items
#     )
#     return order.id, order.currency, total_amount


@stripe_error_handler
def create_subscription(product, customer_id):
    """
    customer thanh toán order
    :param product:
    :param customer_id:
    :return:
    """
    # get product info
    plans = stripe.Plan.list(product=product.product_id)
    plan_id = plans.data[0].id
    subscription = stripe.Subscription.create(
        customer=customer_id,
        items=[
            {
                "plan": plan_id
            }
        ]
        # trial_period_days=7
    )
    return subscription


@stripe_error_handler
def create_checkout_session(order, customer_id):
    """
    customer thanh toán order
    :param order:
    :param customer_id:
    :return:
    """
    # get product info
    order_detail = order.order_details.all()
    line_items = []
    total_amount = 0
    for item in order_detail:
        product = stripe.Product.retrieve(item.product.product_id)
        prices = stripe.Price.list(product=product)
        price = next((p for p in prices.data if p.currency == item.product.currency), None)
        if price:
            line_items.append({
                'price': price.id,
                'quantity': item.quantity,
            })
            total_amount += (price.unit_amount * item.quantity)

    # # get default payment method
    # customer = stripe.Customer.retrieve(customer_id)
    # if customer.invoice_settings.default_payment_method is None:
    #     payment_methods = stripe.PaymentMethod.list(customer=customer_id, type='card')
    #     payment_method_id = payment_methods.data[0].id if payment_methods else ''
    # else:
    #     payment_methods = stripe.PaymentMethod.retrieve(customer.invoice_settings.default_payment_method)
    #     payment_method_id = payment_methods.id if payment_methods else ''
    #
    # # create payment intent
    # payment_intent = create_new_payment_intent(amount=total_amount, payment_method_id=payment_method_id,
    #                                            customer_id=customer_id)

    # create session
    checkout_session = stripe.checkout.Session.create(
        success_url=settings.CHECKOUT_SUCCESS_URL,
        cancel_url=settings.CHECKOUT_FAILED_URL,
        payment_method_types=['card'],
        mode='payment',
        line_items=line_items,
        metadata={
            'order_id': order.id,
        }
    )
    return checkout_session
