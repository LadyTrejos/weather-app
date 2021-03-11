import cbor
import hashlib

from sawtooth_sdk.processor.exceptions import InternalError


WEATHER_NAMESPACE = hashlib.sha512('weather'.encode("utf-8")).hexdigest()[0:6]


class Measure:
    def __init__(self, parameter, value, sensor, timestamp):
        self.parameter = parameter
        self.value = value
        self.sensor = sensor
        self.timestamp = timestamp


def _make_weather_address(parameter, sensor, timestamp):
    name = parameter + sensor + timestamp
    return WEATHER_NAMESPACE + \
        hashlib.sha512(name.encode('utf-8')).hexdigest()[:64]


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


class WeatherState:

    TIMEOUT = 3

    def __init__(self, context):
        """Constructor.
        Args:
            context (sawtooth_sdk.processor.context.Context): Access to
                validator state from within the transaction processor.
        """
        self._context = context

    def set_data(self, data):
        address = _make_weather_address(
            data['Parameter'], data['Sensor'], data['Timestamp'])
        state_entries = {}
        del data['Verb']
        state_entries[address] = self._serialize(data)
        print("state entries: ", state_entries)
        return self._context.set_state(state_entries, timeout=self.TIMEOUT)

    def get_data(self, parameter, sensor, timestamp, context):
        address = _make_weather_address(parameter, sensor, timestamp)

        state_entries = context.get_state([address])
        try:
            return deserialize(data=state_entries[0].data)
        except IndexError:
            return {}
        except Exception as e:
            raise InternalError('Failed to load state data') from e

    def _serialize(self, data):
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
        print("fin serialize", "|".join(sorted(data_strs)).encode())
        return "|".join(sorted(data_strs)).encode()
