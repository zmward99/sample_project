"""This file will hold all of the tests associated with the SMS simulation."""

import pytest
import re

import msg_producer
import sender_manager
import sim_manager


def test_sender_mgr_initialization():
    """
    Test all of the different ways that creating a sender manager object can
    fail.
    """
    dummy_msg = msg_producer.Message()
    # Test to make sure they check types correctly.
    with pytest.raises(TypeError):
        sender_manager.SenderManager("hello", 10, 10, [dummy_msg], 10, 10)
    with pytest.raises(TypeError):
        sender_manager.SenderManager(10, "hello", 10, [dummy_msg], 10, 10)
    with pytest.raises(TypeError):
        sender_manager.SenderManager(10, 10, 10, "hello", 10, 10)
    with pytest.raises(TypeError):
        sender_manager.SenderManager(10, 10, 10, [dummy_msg], "hello", 10)
    with pytest.raises(TypeError):
        sender_manager.SenderManager(10, 10, 10, [dummy_msg], 10, "hello")
    # Tests to make sure they check values correctly.
    with pytest.raises(ValueError):
        sender_manager.SenderManager(-10, 10, 10, [dummy_msg], 10, 10)
    with pytest.raises(ValueError):
        sender_manager.SenderManager(10, -10, 10, [dummy_msg], 10, 10)
    with pytest.raises(ValueError):
        sender_manager.SenderManager(10, 10, 10, [], 10, 10)
    with pytest.raises(ValueError):
        sender_manager.SenderManager(10, 10, 10, [dummy_msg], -10, 10)
    with pytest.raises(ValueError):
        sender_manager.SenderManager(10, 10, 10, [dummy_msg], 10, -10)


def test_msg_pool():
    """
    Collection of tests to make sure that things related to the message pool
    are working correctly.
    """
    with pytest.raises(TypeError):
        msg_producer.generate_msg_pool("hello")
    with pytest.raises(ValueError):
        msg_producer.generate_msg_pool(-10)

    msg_pool = msg_producer.generate_msg_pool(100)
    assert isinstance(msg_pool, list)
    assert len(msg_pool) == 100

    dummy_msg = msg_producer.generate_msg()
    assert isinstance(dummy_msg, msg_producer.Message)
    assert isinstance(dummy_msg.phone_number, str)
    assert isinstance(dummy_msg.msg_body, str)
    assert isinstance(dummy_msg.send_time, int)
    assert isinstance(dummy_msg.sent_status, bool)
    # Make sure that the phone number only has digits
    assert re.fullmatch(r"\d+", dummy_msg.phone_number)
    assert re.fullmatch(r"\D+", dummy_msg.msg_body)

    assert dummy_msg.send_time == 0
    assert not dummy_msg.sent_status


def test_sim_config_parser():
    """Test the that config parser is working correctly."""
    with pytest.raises(TypeError):
        sim_manager.parse_config_file(10)
    with pytest.raises(FileNotFoundError):
        sim_manager.parse_config_file("invalid_path")
    with pytest.raises(ValueError):
        sim_manager.parse_config_file("test_config.txt")

    # Test to make sure that we can correctly pull a few values from the dummy
    # config file.
    dummy_config = sim_manager.parse_config_file("test_config.toml")
    assert dummy_config["test_field1"]["val1"] == 1
    assert dummy_config["test_field2"]["val2"] == 2
