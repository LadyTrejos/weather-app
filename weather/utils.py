import hashlib

from sawtooth_sdk.processor.exceptions import InternalError

WEATHER_NAMESPACE = hashlib.sha512("weather".encode("utf-8")).hexdigest()[0:6]


def serialize(data):
    """Takes a dict of sensor data objects and serializes them into bytes.
    Args:
        data (dict): sensor data
    Returns:
        (bytes): The UTF-8 encoded string stored in state.
    """
    data_strs = []
    for item in data.items():
        data_str = ",".join(map(str, item))
        data_strs.append(data_str)
    return "|".join(sorted(data_strs)).encode()


def deserialize(data):
    """Take bytes and deserialize them into Python string
    Args:
        data (bytes): The UTF-8 encoded string stored in state.
    Returns:
        (dict): sensor data
    """
    try:
        dictionary = {}
        for measure in data.decode().split("|"):
            key, value = measure.split(",")
            dictionary[key] = value
    except ValueError as e:
        raise InternalError("Failed to deserialize sensor data") from e

    return dictionary


def make_weather_address(parameter, sensor, timestamp):
    name = parameter + sensor + timestamp
    return WEATHER_NAMESPACE + hashlib.sha512(name.encode("utf-8")).hexdigest()[:64]
