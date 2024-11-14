"""
Collection of functions used to simulate message production.

Also, contains the definiton for the Message type.
"""

import random
import string
from dataclasses import dataclass


@dataclass
class Message:
    """Definition of a basic message type."""

    # Number to send the message to.
    phone_number: str = ""
    # Contents of the message.
    msg_body: str = ""
    # The time that it took to send the message.
    send_time: int = 0
    # Whether or not the message was sent correctly.
    sent_status: bool = False


def generate_msg_pool(msg_count=1000):
    """
    Generate a pool of messages.

    Args:
      msg_count: Number of messages contained in the pool. Default is 1000.

    Returns:
      List of messages, where the message are type Message.

    Raises:
      TypeError: When the msg_count is not an int.
      ValueError: When the msg_count less than or equal to 0.
    """
    # Need to make sure that we have a valid input for the number of message in
    # the pool.
    if not isinstance(msg_count, int):
        raise TypeError(
            f"msg_count cannot be type {type(msg_count)} must be int.")
    if msg_count < 1:
        raise ValueError(
            f"msg_count cannot be {msg_count}, must be 1 or greater.")

    return [generate_msg() for _ in range(msg_count)]


def generate_msg():
    """
    Generate an individual message.

    Returns:
      Message with a random msg_body, and random phone_number. All other fields
      are default.
    """
    MSG_LEN_LIMIT = 100

    msg = Message()

    # Generate a standard US phone number in length.
    msg.phone_number = "".join(random.choices(string.digits, k=10))

    # Generate a random string to simulate the message mody.
    msg_len = random.randint(1, MSG_LEN_LIMIT)
    msg.msg_body = "".join(random.choices(string.ascii_letters, k=msg_len))

    return msg
