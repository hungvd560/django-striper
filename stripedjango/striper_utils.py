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


def create_new_charge(amount, order_id, customer_id):
    """
    customer thanh toán order
    :param amount:
    :param order_id:
    :param customer_id:
    :return:
    """
    charge = stripe.Charge.create(
        amount=amount, # đơn vị tính là cent
        currency="usd",
        customer=customer_id,
        description="Payment for Order #{}".format(order_id),
    )

    return charge


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
        email='customer@example.com',
        items=line_items,
    )
    return order.id, order.currency, total_amount

