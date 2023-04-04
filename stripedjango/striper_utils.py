from django.http import HttpResponseServerError
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
            return HttpResponseServerError()
    return wrapper


@stripe_error_handler
def create_new_token(**kwargs):
    """
    :param kwargs: card info
        example : card={
            "number": "4242424242424242",
            "exp_month": 12,
            "exp_year": 22,
            "cvc": "123"
        }
    :return:
    """
    token = stripe.Token.create(
        card={**kwargs}
    )
    return token


@stripe_error_handler
def create_new_customer(email, payment_token):
    """
    Tạo customer và thông tin thanh toán
    :param email:
    :param payment_token:
    :return:
    """
    customer = stripe.Customer.create(
        email=email,
        source=payment_token
    )
    return customer


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

    if kwargs.get('type') and kwargs.get('type') == ProductType.DIRECT:

        price = stripe.Price.create(
            unit_amount=kwargs.get('unit_amount'),
            currency=kwargs.get('currency'),
            product=product["id"],
        )
    else:
        plan = stripe.Plan.create(
            amount=kwargs.get('unit_amount'),  # Số tiền thanh toán (tính bằng cents)
            currency=kwargs.get('currency'),
            interval=kwargs.get('interval', ProductInterval.MONTH),  # Chu kỳ thanh toán hàng tháng
            product=product["id"],
        )

    return product


@stripe_error_handler
def create_new_payment_intent(amount, currency, order_id, customer_id):
    """
    customer thanh toán order
    :param amount:
    :param currency:
    :param order_id:
    :param customer_id:
    :return:
    """
    intent = stripe.PaymentIntent.create(
        amount=amount,
        currency=currency,
        customer=customer_id,
        metadata={"order_id": order_id},
    )
    # Xác nhận thanh toán
    intent.confirm()
    return intent.status


@stripe_error_handler
def create_order(order, user_email):
    """
    customer thanh toán order
    :param order:
    :param customer:
    :return:
    """
    # get product info
    order_detail = order.order_details.all()
    line_items = []
    total_amount = 0
    for item in order_detail:
        product = stripe.Product.retrieve(item.product.product_id)
        price = stripe.Price.retrieve(product.price)
        line_items.append({
            'price': product.price,
            'quantity': item.quantity,
        })
        total_amount += (price.unit_amount*item.quantity)
    order = stripe.Order.create(
        currency='usd',
        email=user_email,
        items=line_items,
    )
    return order.id, order.currency, total_amount

