"""Class the defines the sender manager for the SMS simulation."""

import asyncio
import random
import logging

logger = logging.getLogger(__name__)


class SenderManager:
    """
    Sender manager class.

    The sender manager will be responsible for handling each of the inidivdual
    message senders. Ensuring that they are synchronized, as well as handling
    the statistics collection across all senders.

    Attributes:
      avg_send_time: The average time that it takes a sender to send a
                     message. Defined in terms of seconds from 2 - N.
      avg_send_time_factor: This factor will randomly add or subtract time to
                            the avg_send_time. Defined in terms of
                            seconds from 0 - N.
      failure_rate: The approximate failure rate of a sender. Defined as a
                    percent from 0 - 100.
      lock: The lock used to control access to the message pool.
      msg_pool: The pool of messages that need to be sent.
      num_senders: The number of individual message senders that will be used
                   should be 1 - N.
      progress_monitor_refresh_rate: How often to update the progress monitor
                                     and display statistics. Should be 1 - N.
      stats: Dictionary to keep track of different stats during the simulation.
    """

    def __init__(self, avg_send_time, avg_send_time_factor, failure_rate, msg_pool, num_senders, progress_monitor_refresh_rate):
        """
        Initialize an instance of the MsgSender class.

        Args:
          avg_send_time: The average time that it takes a sender to send a
                         message. Defined in terms of seconds from 2 - N.
          avg_send_time_factor: This factor will randomly add or subtract time to
                                the avg_send_time. Defined in terms of
                                seconds from 0 - N.
          failure_rate: The approximate failure rate of a sender. Defined as a
                        percent from 0 - 100.
          msg_pool: The pool of messages that need to be sent.
          num_senders: The number of individual senders that will be used
                       Should be 1 - N.
          progress_monitor_refresh_rate: The rate in seconds to display the
                                         progress monitor. Should be 1 - N.

        Raises:
          TypeError if the type of the argumnet is wrong.
          ValueError if the value of the argument is not within correct limits.
        """
        # Need to error handle the passed in parameters.
        if not isinstance(avg_send_time, int):
            raise TypeError(f"avg_send_time cannot be type {type(avg_send_time)} must be int.")
        if avg_send_time < 2:
            raise ValueError(
                f"avg_send_time cannot be {avg_send_time}, must be 2 or greater.")

        if not isinstance(avg_send_time_factor, int):
            raise TypeError(f"avg_send_time_factor cannot be type {type(avg_send_time_factor)} must be int.")
        if avg_send_time_factor < 0:
            raise ValueError(
                f"avg_send_time_factor cannot be {avg_send_time_factor}, must be 0 or greater.")

        if not isinstance(failure_rate, int):
            raise TypeError(f"failure_rate cannot be type {type(failure_rate)} must be int.")
        if failure_rate < 0 or failure_rate > 100:
            raise ValueError(
                f"failure_rate cannot be {failure_rate}, must be in the range of 0 - 100.")

        if not isinstance(msg_pool, list):
            raise TypeError(f"msg_pool cannot be type {type(msg_pool)} must be list.")
        if len(msg_pool) < 1:
            raise ValueError(
                f"msg_pool length cannot be {msg_pool}, must be greater than 1.")

        if not isinstance(num_senders, int):
            raise TypeError(f"num_senders cannot be type {type(num_senders)} must be int.")
        if num_senders < 1:
            raise ValueError(
                f"num_senders cannot be {num_senders}, must be greater than 1.")

        if not isinstance(progress_monitor_refresh_rate, int):
            raise TypeError(f"progress_monitor_refresh_rate cannot be type {type(progress_monitor_refresh_rate)} must be int.")
        if progress_monitor_refresh_rate < 1:
            raise ValueError(
                f"progress_monitor_refresh_rate cannot be {progress_monitor_refresh_rate}, must be 1 or greater.")

        self.avg_send_time = avg_send_time
        self.avg_send_time_factor = avg_send_time_factor
        self.failure_rate = failure_rate
        self.msg_pool = msg_pool
        self.num_senders = num_senders
        self.progress_monitor_refresh_rate = progress_monitor_refresh_rate

        # Need to make sure that we can lock the message pool to keep data from
        # being modified incorrectly.
        self.lock = asyncio.Lock()

        self.stats = {"messages_sent": 0,
                      "messages_failed": 0,
                      # Make this a float for easier math. This is also the
                      # total time, we can calcutale the overall average
                      # whenever we need to.
                      "total_send_time": 0.0
                      }

    async def send_msgs(self):
        """
        Send all messages from a given message pool.

        Setup the workloads for the progress monitor and sending messages and
        then start them.

        This is an asynchronous routine.
        """
        sender_pool = [self.send_msg() for _ in range(1, self.num_senders + 1)]
        sender_pool.append(self.progress_monitor())

        await asyncio.gather(*sender_pool)

    async def send_msg(self):
        """
        Send an individual message until there are no more messages in the pool.

        Workload to continuously get messages from the message pool and "send"
        them.

        This is an asynchronous routine.
        """
        # Adjust the failure rate and success rate to use as weights for
        # `random.choices`.
        try:
            failure_rate_as_percent = self.failure_rate / 100
        except ZeroDivisionError:
            failure_rate_as_percent = 0.00
        pass_rate_as_percent = 1.00 - failure_rate_as_percent

        while self.msg_pool:
            # Make sure that we don't go lower than 1 second on the time
            # distribution.
            send_time = random.randint(max(self.avg_send_time - self.avg_send_time_factor, 1), self.avg_send_time + self.avg_send_time_factor)
            msg_state = random.choices([True, False], weights=[pass_rate_as_percent, failure_rate_as_percent])[0]
            await asyncio.sleep(send_time)
            async with self.lock:
                if self.msg_pool:
                    current_msg = self.msg_pool.pop()
                    current_msg.sent_status = msg_state
                    current_msg.send_time = send_time
                    logger.info(f"Phone number: {current_msg.phone_number}, Message body: {current_msg.msg_body}, Time to send: {current_msg.send_time}s, Message sent correctly: {current_msg.sent_status}")
                    if current_msg.sent_status:
                        self.stats["messages_sent"] += 1
                        self.stats["total_send_time"] += send_time
                    else:
                        self.stats["messages_failed"] += 1

    async def progress_monitor(self):
        """
        Report stats about the current messages sent.

        The reported stats will be the number of successful message sent, the
        average time to send those messages, and the number of messages that
        failed to send.

        This is an asynchronous routine.
        """
        while self.msg_pool:
            await asyncio.sleep(self.progress_monitor_refresh_rate)
            # Get the lock so we can ensure we get the most accurate data.
            async with self.lock:
                # Calculate the average time to send from the running total of
                # time and number of messages sent.
                try:
                    average_send_time = self.stats["total_send_time"] / self.stats["messages_sent"]
                # We haven't sent any messages yet, so we can't calculate the average.
                except ZeroDivisionError:
                    average_send_time = 0.0
                # Print the stats in a nicer format.
                print("\nProgress Monitor")
                print("-------------------------------------------------------------")
                print(f"Messages Sent: {self.stats['messages_sent']}")
                print(f"Average Message Send Time: {average_send_time:.2f}s")
                print(f"Messages Failed: {self.stats['messages_failed']}")
                print("-------------------------------------------------------------")
