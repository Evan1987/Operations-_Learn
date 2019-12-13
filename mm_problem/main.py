
import math
import pandas as pd
from collections import namedtuple
from mm_problem.core import ConstantConsumer, Shop, Manager
from typing import List, Tuple


LOG = namedtuple("LOG", ["week", "start_inventory", "requirement", "sold",
                         "end_inventory", "replenish", "opportunity_loss",
                         "insurance_cost", "travel_cost"])

UNIT_PROFIT = 200
UNIT_TRAVEL_COST = 2000
UNIT_INSURANCE_COST = 3.5

MEAN_REQUIREMENT = 55
TRAVEL_COST_WEEKS = 1
MIN_REPLENISH_AMOUNT = 100
INIT_INVENTORY = 100
TEST_WEEKS = 52

R = TRAVEL_COST_WEEKS * MEAN_REQUIREMENT
Q = int(math.sqrt(2 * UNIT_TRAVEL_COST * MEAN_REQUIREMENT / UNIT_INSURANCE_COST))


def simulate(r: int, q: int) -> Tuple[pd.DataFrame, float]:
    if q < MIN_REPLENISH_AMOUNT:
        raise ValueError(f"`q` should not be smaller than {MIN_REPLENISH_AMOUNT}")
    consumer = ConstantConsumer(MEAN_REQUIREMENT)
    shop = Shop(INIT_INVENTORY)
    manager = Manager(trigger_inventory=r, replenish_amount=q,
                      cost_weeks=TRAVEL_COST_WEEKS, unit_travel_cost=UNIT_TRAVEL_COST)

    logs: List[LOG] = []

    for week in range(1, TEST_WEEKS + 1):
        start_inventory = shop.inventory
        requirement = consumer.requirement
        sold = shop.sell(requirement)
        end_inventory = shop.inventory

        opportunity_loss = UNIT_PROFIT * (requirement - sold)
        insurance_cost = (start_inventory + end_inventory) / 2 * UNIT_INSURANCE_COST
        manager.on_turn(shop)
        replenish = shop.inventory - end_inventory
        travel_cost = manager.loss
        manager.reset_loss()

        log = LOG(week, start_inventory, requirement, sold, end_inventory,
                  replenish, opportunity_loss, insurance_cost, travel_cost)
        logs.append(log)
    schema = {
        "week": "int", "start_inventory": "int", "requirement": "int",
        "sold": "int", "end_inventory": "int", "replenish": "int"
    }
    data_log = pd.DataFrame(logs).astype(schema)
    data_log["total_loss"] = data_log["opportunity_loss"] + data_log["insurance_cost"] + data_log["travel_cost"]
    total_cost = data_log["total_loss"].sum()
    print(f"Test for r={r}, q={q}, total_cost={total_cost}")
    return data_log, total_cost


if __name__ == '__main__':
    data, cost = simulate(R, Q)


