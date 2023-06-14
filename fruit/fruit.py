# File name: fruit.py

import ray
from ray import serve
from ray.serve.drivers import DAGDriver
from ray.serve.deployment_graph import InputNode
from ray.serve.handle import RayServeDeploymentHandle
from ray.serve.http_adapters import json_request

# These imports are used only for type hints:
from typing import Dict

@serve.deployment(num_replicas=2)
class FruitMarket:
    def __init__(
        self,
        mango_stand: RayServeDeploymentHandle,
        orange_stand: RayServeDeploymentHandle,
        pear_stand: RayServeDeploymentHandle,
    ):
        self.directory = {
            "MANGO": mango_stand,
            "ORANGE": orange_stand,
            "PEAR": pear_stand,
        }

    # async def check_price(self, fruit: str, amount: float) -> float:
    #     if fruit not in self.directory:
    #         return -1
    #     else:
    #         fruit_stand = self.directory[fruit]
    #         ref: ray.ObjectRef = await fruit_stand.check_price.remote(amount)
    #         result = await ref
    #         return result
    
    async def print_input(self, fruit: str, amount: float) -> str:
        if fruit not in self.directory:
            return ""
        else:
            fruit_stand = self.directory[fruit]
            ref: ray.ObjectRef = await fruit_stand.print_input.remote(amount)
            result = await ref
            return result

@serve.deployment(user_config={"price": 3})
class MangoStand:

    DEFAULT_PRICE = 1

    def __init__(self):
        # This default price is overwritten by the one specified in the
        # user_config through the reconfigure() method.
        self.price = self.DEFAULT_PRICE
        self.input = "hello world"

    def reconfigure(self, config: Dict):
        self.price = config.get("price", self.DEFAULT_PRICE)

    # def check_price(self, amount: float) -> float:
    #     return self.price * amount + 1
    
    def print_input(self, amount: float) -> str:
        print("hello world")
        return amount


@serve.deployment(user_config={"price": 2})
class OrangeStand:

    DEFAULT_PRICE = 0.5

    def __init__(self):
        # This default price is overwritten by the one specified in the
        # user_config through the reconfigure() method.
        self.price = self.DEFAULT_PRICE
        self.input = "hello world"

    def reconfigure(self, config: Dict):
        self.price = config.get("price", self.DEFAULT_PRICE)

    # def check_price(self, amount: float) -> float:
    #     return self.price * amount + 1

    def print_input(self, amount: float) -> str:
        print("hello world")
        return amount


@serve.deployment(user_config={"price": 4})
class PearStand:

    DEFAULT_PRICE = 0.75

    def __init__(self):
        # This default price is overwritten by the one specified in the
        # user_config through the reconfigure() method.
        self.price = self.DEFAULT_PRICE
        self.input = "hello world"

    def reconfigure(self, config: Dict):
        self.price = config.get("price", self.DEFAULT_PRICE)

    # def check_price(self, amount: float) -> float:
    #     return self.price * amount + 1

    def print_input(self, amount: float) -> str:
        print("hello world")
        return amount

print("OUTSIDE PLEASE PRINT\n")

with InputNode() as query:
    fruit, amount = query[0], query[1]

    mango_stand = MangoStand.bind()
    orange_stand = OrangeStand.bind()
    pear_stand = PearStand.bind()

    fruit_market = FruitMarket.bind(mango_stand, orange_stand, pear_stand)

    # net_price = fruit_market.check_price.bind(fruit, amount)
    statement = fruit_market.print_input.bind(fruit, amount)
    print(statement)

# deployment_graph = DAGDriver.bind(net_price, http_adapter=json_request)
deployment_graph = DAGDriver.bind(statement, http_adapter=json_request)

# SAMPLE QUERY
# kubectl port-forward service/rayservice-sample-serve-svc 8000
# curl -X POST -H 'Content-Type: application/json' localhost:8000 -d '["MANGO", 2]'
# curl -X GET -H 'Content-Type: application/json' localhost:8000 -d '["MANGO", 2]'
# curl -X GET -H 'Content-Type: application/json' localhost:8000 -d '["PEAR", 2]'
# curl -X GET -H 'Content-Type: application/json' localhost:8000'