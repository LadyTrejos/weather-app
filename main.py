from tp_handler import WeatherHandler
from sawtooth_sdk.processor.core import TransactionProcessor
from state import WEATHER_NAMESPACE

if __name__ == '__main__':
    try:
        URL = 'tcp://localhost:4004'
        print("antes")
        processor = TransactionProcessor(url=URL)
        print("despues", processor)
        handler = WeatherHandler(WEATHER_NAMESPACE)
        print("handler", handler.family_name, processor._handlers)
        processor.add_handler(handler)
        print("añadir handler", processor._handlers)
        processor.start()
        print("Starting processor...")
        print("Connecting to Sawtooth Validator at {}".format(URL))
    except KeyboardInterrupt:
        print("Key interrupt")
    except Exception as e:  # pylint: disable=broad-except
        print("Error: {}".format(e))
    finally:
        if processor is not None:
            print("Stop processor")
            processor.stop()
