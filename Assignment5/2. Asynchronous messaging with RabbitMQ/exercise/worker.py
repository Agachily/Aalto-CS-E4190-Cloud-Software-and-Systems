from types import SimpleNamespace

import pika
import json
import dateutil.parser
import time
from db_and_event_definitions import customers_database, cost_per_unit, number_of_units, BillingEvent, ProductEvent
from xprint import xprint

class ShoppingWorker:

    def __init__(self, worker_id, queue, weight="1"):
        # Do not edit the init method.
        # Set the variables appropriately in the methods below.
        self.connection = None
        self.channel = None
        self.worker_id = worker_id
        self.queue = queue
        self.weight = weight
        self.shopping_state = {}
        self.shopping_events = []
        self.billing_event_producer = None
        self.customer_app_event_producer = None

    def initialize_rabbitmq(self):
        # To implement - Initialize the RabbitMQ connection, channel, exchange and queue here
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='shopping_events_exchange', exchange_type='x-consistent-hash')
        self.channel.exchange_declare(exchange='deadland', exchange_type='direct')
        self.channel.queue_declare(queue='shopping_events_dead_letter_queue')
        self.channel.queue_declare(queue=self.queue, arguments={
            'x-dead-letter-exchange': 'deadland',
            'x-dead-letter-routing-key': 'deadlandroute'
        })
        self.channel.queue_bind(queue='shopping_events_dead_letter_queue', exchange='deadland', routing_key='deadlandroute')
        self.channel.queue_bind(exchange='shopping_events_exchange', queue=self.queue, routing_key=self.weight)

        # Also initialize the channels for the billing_event_producer and customer_app_event_producer
        # connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.customer_app_event_producer = CustomerEventProducer(self.connection, self.worker_id)
        self.billing_event_producer = BillingEventProducer(self.connection, self.worker_id)
        self.customer_app_event_producer.initialize_rabbitmq()
        self.billing_event_producer.initialize_rabbitmq()
        xprint("ShoppingWorker {}: initialize_rabbitmq() called".format(self.worker_id))

    def handle_shopping_event(self, ch, method, properties, body):
        # To implement - This is the callback that is passed to "on_message_callback" when a message is received
        xprint("ShoppingWorker {}: handle_event() called".format(self.worker_id))
        # Handle the application logic and the publishing of events here
        info = json.loads(body.decode('utf-8'))
        # get the product event
        productEvent = ProductEvent(**info)
        # On receiving a pick up or purchase shopping event, the worker looks up the customer associated with the product number.
        customer_id = self.get_customer_id_from_shopping_event(productEvent)

        # Reject the message is customer_id is illegle
        if customer_id is None:
            ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
        else:
            # add the event
            self.shopping_events.append(productEvent)
            # publish the event
            self.customer_app_event_producer.publish_shopping_event(customer_id=customer_id, shopping_event=productEvent)
            if productEvent.event_type== 'pick up':
                self.shopping_state[productEvent.product_number] = productEvent.timestamp
            else:
                pickUpTime = self.shopping_state.pop(productEvent.product_number)
                purchaseTime = info.get('timestamp')
                cost = round(cost_per_unit * number_of_units * 0.8)
                billEvent = BillingEvent(customer_id=customer_id, product_number=info.get('product_number'), pickup_time=pickUpTime,
                            purchase_time=purchaseTime, shopping_cost=cost)
                self.billing_event_producer.publish(billEvent)
                self.customer_app_event_producer.publish_billing_event(billEvent)

    # Utility function to get the customer_id from a shopping event
    def get_customer_id_from_shopping_event(self, shopping_event):
        customer_id = [customer_id for customer_id, product_number in customers_database.items()
                       if shopping_event.product_number == product_number]
        if len(customer_id) == 0:
            xprint("{}: Customer Id for product number {} Not found".format(self.worker_id, shopping_event.product_number))
            return None
        return customer_id[0]

    def start_consuming(self):
        # To implement - Start consuming from Rabbit
        xprint("ShoppingWorker {}: start_consuming() called".format(self.worker_id))
        self.channel.basic_consume(self.queue, on_message_callback=self.handle_shopping_event)
        self.channel.start_consuming()

    def close(self):
        # Do not edit this method
        try:
            xprint("Closing worker with id = {}".format(self.worker_id))
            self.channel.stop_consuming()
            time.sleep(1)
            self.channel.close()
            self.billing_event_producer.close()
            self.customer_app_event_producer.close()
            time.sleep(1)
            self.connection.close()
        except Exception as e:
            print("Exception {} when closing worker with id = {}".format(e, self.worker_id))


class BillingEventProducer:

    def __init__(self, connection, worker_id):
        # Do not edit the init method.
        self.worker_id = worker_id
        # Reusing connection created in ShoppingWorker
        self.channel = connection.channel()

    def initialize_rabbitmq(self):
        # To implement - Initialize the RabbitMq connection, channel, exchange and queue here
        xprint("BillingEventProducer {}: initialize_rabbitmq() called".format(self.worker_id))
        self.channel.queue_declare('billing_events')

    def publish(self, billing_event):
        xprint("BillingEventProducer {}: Publishing billing event {}".format(
            self.worker_id,
            vars(billing_event)))
        # To implement - publish a message to the Rabbitmq here
        # Use json.dumps(vars(billing_event)) to convert the shopping_event object to JSON
        message = json.dumps(vars(billing_event))
        self.channel.basic_publish(exchange='', routing_key='billing_events', body=message)

    def close(self):
        # Do not edit this method
        self.channel.close()


class CustomerEventProducer:

    def __init__(self, connection, worker_id):
        # Do not edit the init method.
        self.worker_id = worker_id
        # Reusing connection created in ShoppingWorker
        self.channel = connection.channel()

    def initialize_rabbitmq(self):
        # To implement - Initialize the RabbitMq connection, channel, exchange and queue here
        xprint("CustomerEventProducer {}: initialize_rabbitmq() called".format(self.worker_id))
        self.channel.exchange_declare('customer_app_events', exchange_type='topic')

    def publish_billing_event(self, billing_event):
        xprint("{}: CustomerEventProducer: Publishing billing event {}"
              .format(self.worker_id, vars(billing_event)))
        # To implement - publish a message to the Rabbitmq here
        # Use json.dumps(vars(billing_event)) to convert the shopping_event object to JSON
        message = json.dumps(vars(billing_event))
        self.channel.basic_publish(exchange='customer_app_events', routing_key=billing_event.customer_id,
                                   body=message)

    def publish_shopping_event(self, customer_id, shopping_event):
        xprint("{}: CustomerEventProducer: Publishing shopping event {} {}"
              .format(self.worker_id, customer_id, vars(shopping_event)))
        # To implement - publish a message to the Rabbitmq here
        # Use json.dumps(vars(shopping_event)) to convert the shopping_event object to JSON
        message = json.dumps(vars(shopping_event))
        self.channel.basic_publish(exchange='customer_app_events', routing_key=customer_id, body=message)


    def close(self):
        # Do not edit this method
        self.channel.close()
