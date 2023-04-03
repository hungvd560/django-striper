import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


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


def create_new_product(**kwargs):
    """
    # tạo sản phẩm và giá
    :return:
    """
    product = stripe.Product.create(
        name=kwargs.get('name'),
        description=kwargs.get('description'),
    )

    price = stripe.Price.create(
        unit_amount=kwargs.get('unit_amount'),
        currency=kwargs.get('currency'),
        product=product["id"],
    )

    return product


def create_new_charge(order, customer):
    """
    customer thanh toán order
    :param order:
    :param customer:
    :return:
    """
    charge = stripe.Charge.create(
        amount=order.amount,
        currency=order.currency,
        customer=customer.id,
        description='Example charge',
    )

    return charge


