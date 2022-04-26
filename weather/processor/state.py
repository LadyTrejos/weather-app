from sawtooth_sdk.processor.exceptions import InternalError

from weather.utils import serialize, deserialize, make_weather_address


class Measure:
    def __init__(self, parameter, value, sensor, timestamp):
        self.parameter = parameter
        self.value = value
        self.sensor = sensor
        self.timestamp = timestamp


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
        address = make_weather_address(
            data["Parameter"], data["Sensor"], data["Timestamp"]
        )
        state_entries = {}
        del data["Verb"]
        state_entries[address] = serialize(data)
        return self._context.set_state(state_entries, timeout=self.TIMEOUT)

    @staticmethod
    def get_data(parameter, sensor, timestamp, context):
        address = make_weather_address(parameter, sensor, timestamp)

        state_entries = context.get_state([address])
        try:
            return deserialize(data=state_entries[0].data)
        except IndexError:
            return {}
        except Exception as e:
            raise InternalError("Failed to load state data") from e
