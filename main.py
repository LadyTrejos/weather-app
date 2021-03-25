from tp_handler import WeatherHandler
from sawtooth_sdk.processor.core import TransactionProcessor
from state import WEATHER_NAMESPACE

if __name__ == '__main__':
    try:
        URL = 'tcp://validator:4004'
        processor = TransactionProcessor(url=URL)
        handler = WeatherHandler(WEATHER_NAMESPACE)
        processor.add_handler(handler)
        print("Starting processor...")
        processor.start()
    except KeyboardInterrupt:
        print("Key interrupt")
    except Exception as e:  # pylint: disable=broad-except
        print("Error: {}".format(e))
    finally:
        if processor is not None:
            print("Stop processor")
            processor.stop()
