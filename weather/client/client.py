import base64
import random
import hashlib
import time
import cbor
import requests
import yaml
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey
from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_signing import ParseError

from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchList
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
from sawtooth_sdk.protobuf.batch_pb2 import Batch

WEATHER_NAMESPACE = hashlib.sha512('weather'.encode("utf-8")).hexdigest()[0:6]


def _sha512(data):
    return hashlib.sha512(data).hexdigest()

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

class Client:
    def __init__(self, url, keyfile=None):
        self.url = url

        if keyfile is None:
            self._signer = None
            return

        try:
            with open(keyfile) as fd:
                private_key_str = fd.read().strip()
        except OSError as err:
            raise Exception(
                'Failed to read private key {}: {}'.format(
                    keyfile, str(err))) from err

        try:
            private_key = Secp256k1PrivateKey.from_hex(private_key_str)
        except ParseError as e:
            raise Exception(
                'Unable to load private key: {}'.format(str(e))) from e

        self._signer = CryptoFactory(create_context('secp256k1')) \
            .new_signer(private_key)

    def set(self, parameter, value, sensor, timestamp, wait=None):
        return self._send_transaction('set', parameter, value, sensor, timestamp, wait=wait)

    def show(self, parameter, sensor, timestamp):
        address = _make_weather_address(parameter, sensor, timestamp)

        result = self._send_request(
            "state/{}".format(address), parameter=parameter, sensor=sensor, timestamp=timestamp)

        try:
            return deserialize(base64.b64decode(yaml.safe_load(result)["data"]))['Value']
        except BaseException:
            return None

    def list(self):
        result = self._send_request(
            "state?address={}".format(
                self._get_prefix()))

        try:
            encoded_entries = yaml.safe_load(result)["data"]

            return [
                deserialize(base64.b64decode(entry["data"]))
                for entry in encoded_entries
            ]

        except BaseException:
            return None

    def _get_prefix(self):
        return _sha512('weather'.encode('utf-8'))[0:6]

    def _get_status(self, batch_id, wait):
        try:
            result = self._send_request(
                'batch_statuses?id={}&wait={}'.format(batch_id, wait),)
            return yaml.safe_load(result)['data'][0]['status']
        except BaseException as err:
            raise Exception(err) from err

    def _send_request(self, suffix, data=None, content_type=None, parameter=None, sensor=None, timestamp=None):
        if self.url.startswith("http://"):
            url = "{}/{}".format(self.url, suffix)
        else:
            url = "http://{}/{}".format(self.url, suffix)

        headers = {}

        if content_type is not None:
            headers['Content-Type'] = content_type

        try:
            if data is not None:
                result = requests.post(url, headers=headers, data=data)
            else:
                result = requests.get(url, headers=headers)

            if result.status_code == 404:
                raise Exception("No data for: {} {} at {}".format(
                    parameter, sensor, timestamp))

            if not result.ok:
                print("No result ok")
                raise Exception("Error {}: {}".format(
                    result.status_code, result.reason))

        except requests.ConnectionError as err:
            raise Exception(
                'Failed to connect to REST API: {}'.format(err)) from err

        except BaseException as err:
            raise Exception(err) from err

        return result.text

    def _send_transaction(self, verb, parameter, value, sensor, timestamp, wait=None):
        payload = cbor.dumps({
            'Verb': verb,
            'Parameter': parameter,
            'Value': value,
            'Sensor': sensor,
            'Timestamp': timestamp
        })

        # Construct the address
        address = _make_weather_address(parameter, sensor, timestamp)

        header = TransactionHeader(
            signer_public_key=self._signer.get_public_key().as_hex(),
            family_name="weather",
            family_version="1.0",
            inputs=[address],
            outputs=[address],
            dependencies=[],
            payload_sha512=_sha512(payload),
            batcher_public_key=self._signer.get_public_key().as_hex(),
            nonce=hex(random.randint(0, 2**64))
        ).SerializeToString()

        signature = self._signer.sign(header)

        transaction = Transaction(
            header=header,
            payload=payload,
            header_signature=signature
        )

        batch_list = self._create_batch_list([transaction])
        batch_id = batch_list.batches[0].header_signature

        if wait and wait > 0:
            wait_time = 0
            start_time = time.time()
            response = self._send_request(
                "batches", batch_list.SerializeToString(),
                'application/octet-stream',
            )
            while wait_time < wait:
                status = self._get_status(
                    batch_id,
                    wait - int(wait_time),
                )
                wait_time = time.time() - start_time

                if status != 'PENDING':
                    return response

            return response

        return self._send_request(
            "batches", batch_list.SerializeToString(),
            'application/octet-stream',
        )

    def _create_batch_list(self, transactions):
        transaction_signatures = [t.header_signature for t in transactions]

        header = BatchHeader(
            signer_public_key=self._signer.get_public_key().as_hex(),
            transaction_ids=transaction_signatures
        ).SerializeToString()

        signature = self._signer.sign(header)

        batch = Batch(
            header=header,
            transactions=transactions,
            header_signature=signature)
        return BatchList(batches=[batch])
