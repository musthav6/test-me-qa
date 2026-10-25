"""пошук товарів для тестів"""
from itertools import combinations

from api.endpoints import get_products, line

MAX_QUANTITY = 10 
PAGE_LIMIT = 20 


def load_catalog(client):
    """Усі товари"""
    products, page = [], 1
    while True:
        resp = get_products(client, page=page, limit=PAGE_LIMIT)
        assert resp.status_code == 200, resp.text
        body = resp.json()
        products += body["items"]
        if not body["items"] or len(products) >= body["total"]:
            return products
        page += 1


def prices(products):
    """{product_id: ціна} для helpers.pricing."""
    return {p["id"]: p["price"] for p in products}


def find(products, condition, description):
    for product in products:
        if condition(product):
            return product
    raise LookupError(f"У каталозі немає товару: {description}")


def in_stock(products, min_stock=1):
    return find(products, lambda p: p["stock"] >= min_stock, f"stock >= {min_stock}")


def out_of_stock(products):
    return find(products, lambda p: p["stock"] == 0, "stock = 0")


def limited_stock(products):
    """stock менший за ліміт 10 для отримання валідної помилки при замовленні більшої кількості."""
    return find(products, lambda p: 0 < p["stock"] < MAX_QUANTITY, "0 < stock < 10")


def short_name(product):
    """Назва в лапках для пошуку: «Бездротові навушники «Орбіта»» → Орбіта."""
    return product["name"].split("«")[1].rstrip("»")


def items_totaling(products, amount):
    """Кошик рівно на amount копійок: один товар у потрібній кількості або два різні."""
    available = [p for p in products if p["stock"] > 0]
    for p in available:
        quantity, rest = divmod(amount, p["price"])
        if rest == 0 and 1 <= quantity <= min(p["stock"], MAX_QUANTITY):
            return [line(p["id"], quantity)]
    for a, b in combinations(available, 2):
        if a["price"] + b["price"] == amount:
            return [line(a["id"]), line(b["id"])]
    raise LookupError(f"Не вдалося зібрати кошик рівно на {amount} коп.")