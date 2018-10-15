"""
SUMMARY:
    attempts to answer basic questions using dictionary definitions

INPUT EXCHANGE:
    model_speech

OUTPUT EXCHANGE:
    action_speech
"""

import json
import pika
import tensorflow as tf
import tensorflow_hub as hub
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import re
import seaborn as sns

input_exchange = 'text_sensor'
output_exchange = 'semantic_vector'
module_url = "https://tfhub.dev/google/universal-sentence-encoder-large/3"


def maragi_publish(message):
    credentials = pika.PlainCredentials('guest', 'guest')
    parameters = pika.ConnectionParameters('maragi-rabbit', 5672, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.basic_publish(exchange=output_exchange, body=message, routing_key='')
    channel.close()
    connection.close()


def encode_sentence(ch, method, properties, body):
    payload = json.loads(body)
    messages = [payload['data']]
    embed = hub.Module(module_url)
    tf.logging.set_verbosity(tf.logging.ERROR)
    with tf.Session() as session:
        session.run([tf.global_variables_initializer(), tf.tables_initializer()])
        message_embeddings = session.run(embed(messages))
        arr = message_embeddings[0]
        maragi_publish()

def maragi_subscribe():
    parameters = pika.URLParameters('amqp://guest:guest@maragi-rabbit:5672/%2F')
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.exchange_declare(exchange=input_exchange, exchange_type='fanout')
    result = channel.queue_declare(exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=input_exchange, queue=queue_name)
    channel.basic_consume(encode_sentence, queue=queue_name, no_ack=True)
    channel.start_consuming()


if __name__ == "__main__":
    while True:
        try:
            maragi_subscribe()
        except Exception as oops:
            print('ERROR:', oops)