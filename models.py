from dataclasses import dataclass, field
from enum import Enum


@dataclass
class Restaurant:
    name: str
    menu: dict
    available_capacity: int
    items_served: list = field(default_factory=list)


class OrderStatus(Enum):
    PLACED = "PLACED"
    FULFILLED = "FULFILLED"
    REJECTED = "REJECTED"


@dataclass
class Order:
    order_id: str
    status: OrderStatus = OrderStatus.PLACED
    reason: str = ""
    restaurant_for: dict = field(default_factory=dict)
    fulfilled_items: list = field(default_factory=list)

    def restaurants(self):
        return list(dict.fromkeys(self.restaurant_for.values()))

    def summary(self):
        if self.status is OrderStatus.REJECTED:
            return f"Order Id{self.order_id} : REJECTED ({self.reason})"
        names = " & ".join(f'"{name}"' for name in self.restaurants())
        return f"Order Id{self.order_id} : Ordered from {names}"
