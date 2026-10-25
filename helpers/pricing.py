"""Математика розрахунку з ТЗ. Усі суми в цілих копійках, як в API."""

STANDARD_SHIPPING = 8000
EXPRESS_SHIPPING = 15000
FREE_SHIPPING_FROM = 150000
COUPONS = {"WELCOME10": 10}  # промокод


def normalize_coupon(code):

    return code.strip().upper()


def subtotal(prices, items):
    """prices: {product_id: ціна}, items: [{"product_id", "quantity"}]."""
    return sum(prices[item["product_id"]] * item["quantity"] for item in items)


def discount(amount, coupon=""):
    """Рахуємо скільки абсолютно відняти з суми товарів за промокодом."""
    percent = COUPONS.get(normalize_coupon(coupon), 0)
    return amount * percent // 100


def shipping(amount, delivery="standard"):
    """Поріг безкоштовної доставки рахується від суми товарів до знижки."""
    if delivery == "express":
        return EXPRESS_SHIPPING
    return 0 if amount >= FREE_SHIPPING_FROM else STANDARD_SHIPPING


def expected_quote(prices, items, coupon="", delivery="standard"):
    goods = subtotal(prices, items)
    off = discount(goods, coupon)
    ship = shipping(goods, delivery)
    return {"subtotal": goods, "discount": off, "shipping": ship, "total": goods - off + ship}
