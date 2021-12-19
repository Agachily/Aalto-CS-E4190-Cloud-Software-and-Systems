from concurrent import futures
import grpc
import sys
from proto import restaurant_pb2
from proto import restaurant_pb2_grpc

RESTAURANT_ITEMS_FOOD = ["chips", "fish", "burger", "pizza", "pasta", "salad"]
RESTAURANT_ITEMS_DRINK = ["water", "fizzy drink", "juice", "smoothie", "coffee", "beer"]
RESTAURANT_ITEMS_DESSERT = ["ice cream", "chocolate cake", "cheese cake", "brownie", "pancakes", "waffles"]

class Restaurant(restaurant_pb2_grpc.RestaurantServicer):
    # Logic goes here
    def FoodOrder(self, request, context):
        # Get the order
        food_orderID = request.orderID
        # Get the order content
        items = request.items
        food_status = restaurant_pb2.RestaurantResponse.Status.ACCEPTED
        for i in items:
            if i not in RESTAURANT_ITEMS_FOOD:
                food_status = restaurant_pb2.RestaurantResponse.Status.REJECTED
        return restaurant_pb2.RestaurantResponse(orderID=food_orderID, status=food_status)

    def DrinkOrder(self, request, context):
        # Get the order
        drink_orderID = request.orderID
        # Get the order content
        items = request.items
        drink_status = restaurant_pb2.RestaurantResponse.Status.ACCEPTED
        for i in items:
            if i not in RESTAURANT_ITEMS_DRINK:
                drink_status = restaurant_pb2.RestaurantResponse.Status.REJECTED
        return restaurant_pb2.RestaurantResponse(orderID=drink_orderID, status=drink_status)

    def DessertOrder(self, request, context):
        # Get the order
        dessert_orderID = request.orderID
        # Get the order content
        items = request.items
        dessert_status = restaurant_pb2.RestaurantResponse.Status.ACCEPTED
        for i in items:
            if i not in RESTAURANT_ITEMS_DESSERT:
                dessert_status = restaurant_pb2.RestaurantResponse.Status.REJECTED
        return restaurant_pb2.RestaurantResponse(orderID=dessert_orderID, status=dessert_status)



def serve():
    # Logic goes here
    # Remember to start the server on localhost and a port defined by the first command line argument
    port = sys.argv[1]
    str = 'localhost:{0}'.format(port)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    restaurant_pb2_grpc.add_RestaurantServicer_to_server(Restaurant(), server)
    server.add_insecure_port(str)
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
