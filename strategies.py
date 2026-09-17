from abc import ABC, abstractmethod


class RestaurantSelectionStrategy(ABC):
    @abstractmethod
    def select_restaurant(self, item, candidates):
        ...


class LowestPriceRestaurantSelectionStrategy(RestaurantSelectionStrategy):
    def select_restaurant(self, item, candidates):
        return min(candidates, key=lambda r: r.menu[item], default=None)
