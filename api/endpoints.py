"""Одна функція на ендпоінт із ТЗ. Повертають Response: статус перевіряє тест."""


def line(product_id, quantity=1):
    """збираємо словник для кошика"""
    return {"product_id": product_id, "quantity": quantity}


def health(client):
    return client.request("GET", "/api/health")


def get_products(client, **filters):
    return client.request("GET", "/api/products", params=filters)


def get_product(client, product_id):
    return client.request("GET", f"/api/products/{product_id}")


def get_favorites(client):
    return client.request("GET", "/api/favorites")


def put_favorites(client, product_ids):
    return client.request("PUT", "/api/favorites", json={"product_ids": product_ids})


def get_review(client, product_id):
    return client.request("GET", f"/api/products/{product_id}/review")


def post_review(client, product_id, rating, text):
    return client.request("POST", f"/api/products/{product_id}/review", json={"rating": rating, "text": text})


def quote(client, items, coupon="", delivery="standard"):
    return client.request("POST", "/api/quote", json={"items": items, "coupon": coupon, "delivery": delivery})


def create_order(client, items, customer, coupon="", delivery="standard", payment="approved"):
    """customer: {"name", "email", "address"}."""
    payload = {"items": items, **customer, "coupon": coupon, "delivery": delivery, "payment": payment}
    return client.request("POST", "/api/orders", json=payload)


def get_orders(client, status="all"):
    return client.request("GET", "/api/orders", params={"status": status})


def get_order(client, order_id):
    return client.request("GET", f"/api/orders/{order_id}")


def cancel_order(client, order_id):
    return client.request("POST", f"/api/orders/{order_id}/cancel")
