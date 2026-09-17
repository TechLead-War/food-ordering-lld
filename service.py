import threading

from .models import Order, OrderStatus, Restaurant
from .strategies import LowestPriceRestaurantSelectionStrategy


class RestaurantService:
    def __init__(self):
        self.lock = threading.RLock()
        self.restaurants = {}

    def onboard_restaurant(self, name, menu, max_capacity):
        with self.lock:
            if name in self.restaurants:
                raise ValueError(f"restaurant already onboarded: {name}")
            self.restaurants[name] = Restaurant(name, dict(menu), max_capacity)

    def add_or_update_menu_item(self, restaurant_name, item, price):
        with self.lock:
            self.restaurants[restaurant_name].menu[item] = price

    def remove_menu_item(self, restaurant_name, item):
        with self.lock:
            self.restaurants[restaurant_name].menu.pop(item, None)

    def get_available_capacity(self, restaurant_name):
        with self.lock:
            return self.restaurants[restaurant_name].available_capacity

    def stats(self):
        with self.lock:
            return {r.name: (r.available_capacity, list(r.items_served)) for r in self.restaurants.values()}


class OrderService:
    def __init__(self, restaurant_service):
        self.restaurants = restaurant_service.restaurants
        self.lock = restaurant_service.lock
        self.strategies = {"lowest_price": LowestPriceRestaurantSelectionStrategy()}
        self.orders = {}
        self.next_order_id = 1

    def register_selection_strategy(self, name, strategy):
        with self.lock:
            self.strategies[name] = strategy

    def place_order(self, items, strategy_name):
        if not items or len(set(items)) != len(items):
            raise ValueError(f"order must list each item exactly once: {items}")
        with self.lock:
            strategy = self.strategies[strategy_name]
            order = Order(f"#{self.next_order_id}")
            self.next_order_id += 1

            for item in items:
                candidates = [r for r in self.restaurants.values() if item in r.menu and r.available_capacity > 0]
                chosen = strategy.select_restaurant(item, candidates)
                if chosen is None:
                    for name in order.restaurant_for.values():
                        self.restaurants[name].available_capacity += 1
                    order.restaurant_for.clear()
                    order.status = OrderStatus.REJECTED
                    order.reason = f"no restaurant can serve {item}"
                    return order
                chosen.available_capacity -= 1
                order.restaurant_for[item] = chosen.name

            self.orders[order.order_id] = order
            return order

    def mark_item_fulfilled(self, order_id, item):
        with self.lock:
            order = self.orders[order_id]
            restaurant = self.restaurants[order.restaurant_for[item]]
            if item in order.fulfilled_items:
                raise ValueError(f"already fulfilled: {order_id} {item}")
            order.fulfilled_items.append(item)
            restaurant.available_capacity += 1
            restaurant.items_served.append(item)
            if len(order.fulfilled_items) == len(order.restaurant_for):
                order.status = OrderStatus.FULFILLED

    def mark_order_fulfilled(self, order_id):
        with self.lock:
            order = self.orders[order_id]
            for item in order.restaurant_for:
                if item not in order.fulfilled_items:
                    self.mark_item_fulfilled(order_id, item)
