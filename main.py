from .service import OrderService, RestaurantService


def print_stats(restaurants):
    for name, (capacity, served) in restaurants.stats().items():
        print(f"{name}: {capacity}  (served: {', '.join(served) or '-'})")


def main():
    restaurants = RestaurantService()
    orders = OrderService(restaurants)
    restaurants.onboard_restaurant("A2B", {"Idly": 40, "Vada": 30, "Paper Plain Dosa": 50}, 4)
    restaurants.onboard_restaurant("Rasaganga", {"Idly": 45, "Set Dosa": 60, "Poori": 25}, 6)
    restaurants.onboard_restaurant("Eat Fit", {"Idly": 30, "Vada": 40}, 2)

    print(orders.place_order(["Idly", "Poori"], "lowest_price").summary())
    print(orders.place_order(["Idly", "Vada"], "lowest_price").summary())
    print_stats(restaurants)
    print(orders.place_order(["Idly"], "lowest_price").summary())
    orders.mark_order_fulfilled("#1")
    orders.mark_order_fulfilled("#2")
    print(orders.place_order(["Idly"], "lowest_price").summary())
    print_stats(restaurants)


if __name__ == "__main__":
    main()
