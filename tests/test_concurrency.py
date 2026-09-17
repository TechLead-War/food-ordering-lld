import threading
import unittest

from food_ordering.models import OrderStatus
from food_ordering.service import OrderService, RestaurantService


class TestConcurrency(unittest.TestCase):
    def test_parallel_orders_never_exceed_capacity(self):
        restaurants = RestaurantService()
        orders = OrderService(restaurants)
        restaurants.onboard_restaurant("Solo", {"X": 1}, 3)
        results = []
        threads = [threading.Thread(target=lambda: results.append(orders.place_order(["X"], "lowest_price").status))
                   for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(results.count(OrderStatus.PLACED), 3)
        self.assertEqual(restaurants.get_available_capacity("Solo"), 0)
