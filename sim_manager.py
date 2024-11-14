"""
Manager for the SMS simulation.

This manager is responsible for setting up the simulation. It does this by
parsing the configuration file, setting up the initial message pool, and then
creating the jobs for each sender and the progress monitor.

It is also responsible for setting up the logger that will be used arcoss this
project.
"""
import msg_producer
import sender_manager

import toml
import asyncio
import os
import logging

logger = logging.getLogger(__name__)


def parse_config_file(path_to_config="simulation_config.toml"):
    """
    Parse the config file.

    Args:
      path_to_config: Path to the config file as a string.

    Returns:
      Simulation configuration as a dict.

    Raises:
      TypeError is the path_to_config is not a string.
      FileNotFoundError if the path_to_config is not a valid file.
    """
    if not isinstance(path_to_config, str):
        raise TypeError(f"path_to_config cannot be type {type(path_to_config)} must be str.")
    if not os.path.isfile(path_to_config):
        raise FileNotFoundError(f"Config file: {path_to_config} not found. Check that the correct config file was used.")
    elif path_to_config.split(".")[-1] != "toml":
        raise ValueError(f"Invalid file extension in config file: {path_to_config}, should be a toml file.")
    # Parse the simulation configuration file.
    with open(path_to_config, "r") as sim_config_file:
        config_file_contents = sim_config_file.read()

    sim_config = toml.loads(config_file_contents)

    return sim_config


def configure_logger():
    """Configure the logger that will be used across the project."""
    logging.basicConfig(filename="sms_msgs.log", level=logging.INFO, filemode="w",
                        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")


def start_sim():
    """Start the SMS simulation."""
    # Parse the config file to get the different simulation parameters.
    sim_config = parse_config_file()

    configure_logger()

    print("Starting Simulation...")

    # Setup the initial message pool.
    msg_pool = msg_producer.generate_msg_pool(sim_config["msg_producer"]["num_msgs_to_send"])

    # Setup the sender manager so that it can simulate sending the messages.
    sender_pool = sender_manager.SenderManager(sim_config["msg_sender"]["average_send_time"],
                                               sim_config["msg_sender"]["average_send_time_factor"],
                                               sim_config["msg_sender"]["failure_rate"],
                                               msg_pool,
                                               sim_config["msg_sender"]["num_senders"],
                                               sim_config["progress_monitor"]["refresh_rate"])

    asyncio.run(sender_pool.send_msgs())

    print("End of Simulation...")
