
import abc
from random import Random


class AbstractConsumer(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def requirement(self) -> int:
        """The demand amount"""
        raise NotImplementedError


class RandomGaussConsumer(AbstractConsumer):
    def __init__(self, mean: float, std: float, seed: int, min_requirement: int = 10):
        """To initialize a consumer with amount in gaussian distribution"""
        self._mean = mean
        self._std = std
        self._seed = seed
        self._min_requirement = min_requirement
        self._rng = Random(self._seed)

    @property
    def requirement(self) -> int:
        r = self._rng.gauss(self._mean, self._std)
        if r < 0:
            return self._min_requirement
        return int(r)


class ConstantConsumer(AbstractConsumer):
    def __init__(self, r: int):
        self._r = r

    @property
    def requirement(self) -> int:
        return self._r


class Shop(object):
    def __init__(self, inventory: int):
        self._inventory = inventory

    @property
    def inventory(self):
        return self._inventory

    def sell(self, amount: int) -> int:
        sold = min(self._inventory, amount)
        self._inventory -= sold
        return sold

    def replenish(self, amount: int):
        """Replenish to increase the inventory"""
        self._inventory += amount


class Manager(object):
    def __init__(self, *, trigger_inventory: int, replenish_amount: int, cost_weeks: int, unit_travel_cost: float):
        self.trigger_inventory = trigger_inventory
        self.replenish_amount = replenish_amount
        self.cost_weeks = cost_weeks
        self.unit_travel_cost = unit_travel_cost
        self._travel_cost = 0.
        self._out = False
        self._out_count = 0

    @property
    def loss(self):
        return self._travel_cost

    def reset_loss(self):
        self._travel_cost = 0.

    def __repr__(self):
        return f"Out: {self._out}, Out weeks: {self._out_count}"

    @property
    def out(self):
        return self._out

    def on_turn(self, shop: Shop):
        if not self._out:   # Not travel
            if shop.inventory <= self.trigger_inventory:
                self._out = True
                self._out_count = 0
        else:               # travel out already
            self._out_count += 1
            if self._out_count == self.cost_weeks:  # Be BACK!!!
                self._out = False
                self._out_count = 0
                self._travel_cost += self.unit_travel_cost
                shop.replenish(self.replenish_amount)
            # Not back yet
