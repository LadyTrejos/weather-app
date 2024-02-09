import argparse
import sys

import pkg_resources
from sawtooth_sdk.processor.config import get_log_config
from sawtooth_sdk.processor.config import get_log_dir
from sawtooth_sdk.processor.core import TransactionProcessor
from sawtooth_sdk.processor.log import init_console_logging
from sawtooth_sdk.processor.log import log_configuration

from weather.processor.tp_handler import WeatherHandler
from weather.utils import WEATHER_NAMESPACE

DISTRIBUTION_NAME = "sawtooth-weather"
DEFAULT_URL = "tcp://localhost:4004"


def parse_args(args):
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(
        "-C",
        "--connect",
        default=DEFAULT_URL,
        help="Endpoint for the validator connection",
    )

    parser.add_argument(
        "-vv",
        "--verbose",
        action="count",
        default=0,
        help="Increase output sent to stderr",
    )

    try:
        version = pkg_resources.get_distribution(DISTRIBUTION_NAME).version
    except pkg_resources.DistributionNotFound:
        version = "UNKNOWN"

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=(DISTRIBUTION_NAME + " (Hyperledger Sawtooth) version {}").format(
            version
        ),
        help="print version information",
    )

    return parser.parse_args(args)


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    opts = parse_args(args)
    processor = None
    try:
        processor = TransactionProcessor(url=opts.connect)
        log_config = get_log_config(filename="weather_log_config.toml")

        init_console_logging(verbose_level=opts.verbose)

        # The prefix should eventually be looked up from the
        # validator's namespace registry.
        handler = WeatherHandler(WEATHER_NAMESPACE)

        processor.add_handler(handler)
        print("Starting processor...")
        processor.start()
    except KeyboardInterrupt:
        pass
    except Exception as e:  # pylint: disable=broad-except
        print("Error: {}".format(e), file=sys.stderr)
    finally:
        if processor is not None:
            processor.stop()


if __name__ == "__main__":
    main()
