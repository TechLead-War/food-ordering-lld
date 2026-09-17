import unittest

from food_ordering.service import OrderService, RestaurantService


class TestRestaurant(unittest.TestCase):
    def setUp(self):
        self.restaurants = RestaurantService()
        self.orders = OrderService(self.restaurants)
        self.restaurants.onboard_restaurant("A2B", {"Idly": 40, "Vada": 30}, 4)

    def test_duplicate_onboarding_raises(self):
        with self.assertRaises(ValueError):
            self.restaurants.onboard_restaurant("A2B", {}, 1)

    def test_menu_add_and_remove(self):
        self.restaurants.add_or_update_menu_item("A2B", "Poori", 25)
        self.assertEqual(self.orders.place_order(["Poori"], "lowest_price").restaurants(), ["A2B"])
        self.restaurants.remove_menu_item("A2B", "Poori")
        self.assertEqual(self.orders.place_order(["Poori"], "lowest_price").reason, "no restaurant can serve Poori")
