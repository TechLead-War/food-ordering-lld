import unittest

from food_ordering.models import OrderStatus
from food_ordering.service import OrderService, RestaurantService
from food_ordering.strategies import RestaurantSelectionStrategy


class HighestPrice(RestaurantSelectionStrategy):
    def select_restaurant(self, item, candidates):
        return max(candidates, key=lambda r: r.menu[item], default=None)


class TestOrder(unittest.TestCase):
    def setUp(self):
        self.restaurants = RestaurantService()
        self.orders = OrderService(self.restaurants)
        self.restaurants.onboard_restaurant("A2B", {"Idly": 40, "Vada": 30}, 4)
        self.restaurants.onboard_restaurant("Rasaganga", {"Idly": 45, "Poori": 25}, 6)
        self.restaurants.onboard_restaurant("Eat Fit", {"Idly": 30, "Vada": 40}, 2)

    def order(self, *items, strategy="lowest_price"):
        return self.orders.place_order(list(items), strategy)

    def chosen(self, *items, strategy="lowest_price"):
        return self.order(*items, strategy=strategy).restaurants()

    def capacity(self, *names):
        return [self.restaurants.get_available_capacity(n) for n in names]

    def test_sample_flow(self):
        self.assertEqual(self.chosen("Idly", "Poori"), ["Eat Fit", "Rasaganga"])
        self.assertEqual(self.chosen("Idly", "Vada"), ["Eat Fit", "A2B"])
        self.assertEqual(self.capacity("A2B", "Rasaganga", "Eat Fit"), [3, 5, 0])
        self.assertEqual(self.chosen("Idly"), ["A2B"])
        self.orders.mark_order_fulfilled("#1")
        self.orders.mark_order_fulfilled("#2")
        self.assertEqual(self.chosen("Idly"), ["Eat Fit"])

    def test_summary(self):
        self.assertEqual(self.order("Idly", "Poori").summary(), 'Order Id#1 : Ordered from "Eat Fit" & "Rasaganga"')

    def test_rejected_order_reserves_nothing(self):
        order = self.order("Vada", "Biryani")
        self.assertIs(order.status, OrderStatus.REJECTED)
        self.assertEqual(order.reason, "no restaurant can serve Biryani")
        self.assertEqual(order.restaurants(), [])
        self.assertEqual(self.capacity("A2B"), [4])

    def test_duplicate_or_empty_items_raise(self):
        with self.assertRaises(ValueError):
            self.order("Idly", "Idly")
        with self.assertRaises(ValueError):
            self.order()
        self.assertEqual(self.capacity("Eat Fit"), [2])

    def test_item_fulfilment_frees_only_that_restaurant(self):
        order = self.order("Vada", "Poori")
        self.orders.mark_item_fulfilled("#1", "Vada")
        self.assertEqual(self.capacity("A2B", "Rasaganga"), [4, 5])
        self.assertIs(order.status, OrderStatus.PLACED)
        self.orders.mark_item_fulfilled("#1", "Poori")
        self.assertIs(order.status, OrderStatus.FULFILLED)

    def test_double_fulfilment_raises(self):
        self.order("Idly")
        self.orders.mark_item_fulfilled("#1", "Idly")
        with self.assertRaises(ValueError):
            self.orders.mark_item_fulfilled("#1", "Idly")

    def test_unknown_item_fulfilment_leaves_order_untouched(self):
        order = self.order("Idly", "Vada")
        with self.assertRaises(KeyError):
            self.orders.mark_item_fulfilled("#1", "Biryani")
        self.assertEqual(order.fulfilled_items, [])
        self.assertEqual(self.restaurants.stats()["Eat Fit"], (1, []))

    def test_items_served(self):
        self.order("Idly")
        self.order("Idly")
        self.orders.mark_order_fulfilled("#1")
        self.assertEqual(self.restaurants.stats()["Eat Fit"], (1, ["Idly"]))

    def test_menu_change(self):
        self.restaurants.add_or_update_menu_item("Rasaganga", "Idly", 10)
        self.assertEqual(self.chosen("Idly"), ["Rasaganga"])

    def test_custom_strategy(self):
        self.orders.register_selection_strategy("highest_price", HighestPrice())
        self.assertEqual(self.chosen("Idly", strategy="highest_price"), ["Rasaganga"])
