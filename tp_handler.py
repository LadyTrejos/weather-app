import cbor
import hashlib
from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from state import WeatherState


def _decode_transaction(transaction):
    try:
        content = cbor.loads(transaction.payload)
    except Exception as e:
        raise InvalidTransaction('Invalid payload serialization') from e
    return content


class WeatherHandler(TransactionHandler):
    def __init__(self, namespace_prefix):
        self._namespace_prefix = namespace_prefix

    @property
    def family_name(self):
        return 'weather'

    @property
    def family_versions(self):
        return ['1.0']

    @property
    def namespaces(self):
        return [self._namespace_prefix]

    def apply(self, transaction, context):
        print("i'm inside handler print")
        # payload = {Verb: verb, Parameter: parameter, Value: value, Sensor: sensor, Timestamp: timestamp}
        payload = _decode_transaction(transaction)

        weather_state = WeatherState(context)

        if payload['Verb'] == 'set':
            return weather_state.set_data(payload)
        else:
            raise InvalidTransaction('Unhandled verb: {}'.format(
                payload['Verb']))
