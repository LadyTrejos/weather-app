import argparse
import getpass
import logging
import pkg_resources
import os
import sys
import traceback
from datetime import datetime
from colorlog import ColoredFormatter
from client.client import Client

DISTRIBUTION_NAME = 'sawtooth-weather'
DEFAULT_URL = 'http://rest-api:8008'


def create_console_handler(verbose_level):
    clog = logging.StreamHandler()
    formatter = ColoredFormatter(
        "%(log_color)s[%(asctime)s %(levelname)-8s%(module)s]%(reset)s "
        "%(white)s%(message)s",
        datefmt="%H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        })

    clog.setFormatter(formatter)
    clog.setLevel(logging.DEBUG)
    return clog

def setup_loggers(verbose_level):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(create_console_handler(verbose_level))

def create_parent_parser(prog_name):
    parent_parser = argparse.ArgumentParser(prog=prog_name, add_help=False)
    parent_parser.add_argument(
        '-v', '--verbose',
        action='count',
        help='enable more verbose output')

    try:
        version = pkg_resources.get_distribution(DISTRIBUTION_NAME).version
    except pkg_resources.DistributionNotFound:
        version = 'UNKNOWN'

    parent_parser.add_argument(
        '-V', '--version',
        action='version',
        version=(DISTRIBUTION_NAME + ' (Hyperledger Sawtooth) version {}')
        .format(version),
        help='display version information')

    return parent_parser


def create_parser(prog_name):
    parent_parser = create_parent_parser(prog_name)

    parser = argparse.ArgumentParser(
        parents=[parent_parser],
        description="Provides subcommands to manage weather application",
        formatter_class=argparse.RawDescriptionHelpFormatter)

    subparsers = parser.add_subparsers(title='subcommands', dest='command')

    add_set_parser(subparsers, parent_parser)
    add_show_parser(subparsers, parent_parser)
    add_list_parser(subparsers, parent_parser)

    return parser


def valid_datetime_type(arg_datetime_str):
    """custom argparse type for user datetime values given from the command line"""
    try:
        return datetime.strptime(arg_datetime_str, "%d/%m/%Y %H:%M:%S").isoformat()
    except ValueError:
        msg = "Given datetime ({0}) not valid. Expected format 'DD/MM/AAAA HH:mm:ss'".format(
            arg_datetime_str)
        raise argparse.ArgumentTypeError(msg)


def add_set_parser(subparsers, parent_parser):
    message = 'Sends a weather transaction to set <parameter> to <value> from <sensor> at <timestamp>.'

    parser = subparsers.add_parser(
        'set',
        parents=[parent_parser],
        description=message,
        help='Sets a parameter to value from a sensor at a timestamp')

    parser.add_argument(
        'parameter',
        type=str,
        help='type of measure to set')

    parser.add_argument(
        'value',
        type=float,
        help='amount to set')

    parser.add_argument(
        'sensor',
        type=str,
        help='sensor that recorded the measurement')

    parser.add_argument(
        'timestamp',
        type=valid_datetime_type,
        help='date and time the measurement was taken')

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API')

    parser.add_argument(
        '--username',
        type=str,
        help="identify name of user's private key file")

    parser.add_argument(
        '--keyfile',
        type=str,
        help="identify file containing user's private key")

    parser.add_argument(
        '--wait',
        nargs='?',
        const=sys.maxsize,
        type=int,
        help='set time, in seconds, to wait for transaction to commit')


def do_set(args):
    parameter, value, sensor, timestamp, wait = args.parameter, args.value, args.sensor, args.timestamp, args.wait
    client = _get_client(args)
    response = client.set(parameter, value, sensor, timestamp, wait)
    print(response)


def add_show_parser(subparsers, parent_parser):
    message = 'Shows the value of the <parameter> at a optional <sensor> and <timestamp>.'

    parser = subparsers.add_parser(
        'show',
        parents=[parent_parser],
        description=message,
        help='Displays the specified parameter value')

    parser.add_argument(
        'parameter',
        type=str,
        help='name of parameter to show')

    parser.add_argument(
        'sensor',
        type=str,
        help='name of sensor that recorded the measurement')

    parser.add_argument(
        'timestamp',
        type=valid_datetime_type,
        help='date and hour to show')

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API')


def do_show(args):
    parameter, sensor, timestamp = args.parameter, args.sensor, args.timestamp

    client = _get_client(args, False)
    value = client.show(parameter, sensor, timestamp)
    print('-'*55)
    print('{:<15} {:<8} {:<10} {:<20}'.format(
        'Parameter', 'Value', 'Sensor', 'Timestamp'))
    print('-'*55)
    date = datetime.strptime(
            timestamp, "%Y-%m-%dT%H:%M:%S").strftime("%d/%m/%Y %H:%M:%S")
    print('{:<15} {:<8} {:<10} {:<20}'.format(parameter, value, sensor, date))


def add_list_parser(subparsers, parent_parser):
    message = 'Shows the values of all sensor data.'

    parser = subparsers.add_parser(
        'list',
        parents=[parent_parser],
        description=message,
        help='Displays all sensor values')

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API')


def do_list(args):
    client = _get_client(args, False)
    results = client.list()
    print('-'*55)
    print('{:<15} {:<8} {:<10} {:<20}'.format(
        'Parameter', 'Value', 'Sensor', 'Timestamp'))
    print('-'*55)
    for data in results:
        date = datetime.strptime(
            data['Timestamp'], "%Y-%m-%dT%H:%M:%S").strftime("%d/%m/%Y %H:%M:%S")
        print('{:<15} {:<8} {:<10} {:<20}'.format(
            data['Parameter'], data['Value'], data['Sensor'], date))


def _get_client(args, read_key_file=True):
    return Client(
        url=DEFAULT_URL if args.url is None else args.url,
        keyfile=_get_keyfile(args) if read_key_file else None)


def _get_keyfile(args):
    try:
        if args.keyfile is not None:
            return args.keyfile
    except AttributeError:
        return None

    real_user = getpass.getuser() if args.username is None else args.username
    home = os.path.expanduser("~")
    key_dir = os.path.join(home, ".sawtooth", "keys")

    return '{}/{}.priv'.format(key_dir, real_user)


def main(prog_name=os.path.basename(sys.argv[0]), args=None):
    if args is None:
        args = sys.argv[1:]
    parser = create_parser(prog_name)
    args = parser.parse_args(args)

    verbose_level = 0
    setup_loggers(verbose_level=verbose_level)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Get the commands from cli args and call corresponding handlers
    if args.command == 'set':
        do_set(args)
    elif args.command == 'show':
        do_show(args)
    elif args.command == 'list':
        do_list(args)
    else:
        raise Exception("invalid command: {}".format(args.command))


def main_wrapper():
    # pylint: disable=bare-except
    try:
        main()
    except Exception as err:
        print("Error: {}".format(err), file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        pass
    except SystemExit as e:
        raise e
    except:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main_wrapper()
