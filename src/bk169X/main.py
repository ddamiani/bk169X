import sys
import argparse

import serial
import IPython

import os
import bk169X.control as _bkcont
import bk169X.calib as _bkcal


def __parse_cli():
    parser = argparse.ArgumentParser(
        description='A tool for control and calibration of BK Precision 169X Series DC power supplies'
    )

    settle = 1.5
    if os.name == 'nt':
        serial_port = 'COM3'
    elif os.name == 'posix':
        serial_port = 'ttyS0'
    else:
        serial_port = None

    parser.add_argument(
        '-p',
        '--port',
        metavar='PORT',
        default=serial_port,
        help='the serial port the power supply is attached to (default: {})'.format(serial_port)
    )

    subparser = parser.add_subparsers(dest='mode', help='The mode choice of the tool')
    subparser.required = True

    control_parser = subparser.add_parser('control', help='Control mode of the tool')

    calib_parser = subparser.add_parser('calib', help='Calibrtion mode of the tool')

    calib_parser.add_argument(
        'vstart',
        metavar='VSTART',
        type=float,
        help='the starting voltage for calibration scans'
    )

    calib_parser.add_argument(
        'vend',
        metavar='VEND',
        type=float,
        help='the ending voltage for calibration scans'
    )

    calib_parser.add_argument(
        'vstep',
        metavar='VSTEP',
        type=float,
        help='the voltage step size for the calibration scans'
    )

    calib_parser.add_argument(
        '-s',
        '--settle',
        metavar='SETTLE',
        type=float,
        default=settle,
        help='the settling time before reading back the voltage (default {time:.2f} s)'.format(time=settle)
    )

    return parser.parse_args()


def main():
    try:
        __args = __parse_cli()
        __bkps = _bkcont.PowerSupply(__args.port)
        try:
            __bkps.connect()
            __banner_base = '*  {mode} tool for BK Precision 169X Series DC power supplies  *'
            if __args.mode == 'calib':
                __banner = __banner_base.format(mode='Calibration')
                calib = _bkcal.PowerSupplyCalib(__bkps, __args.vstart, __args.vend, __args.vstep, __args.settle)
            elif __args.mode == 'control':
                __banner = __banner_base.format(mode='Control')
                bkps = __bkps
            else:
                print('Unknown tool mode: {mode}'.format(mode=__args.mode))
                sys.exit(1)
            __banner = '\n{0}\n{1}\n{0}\n'.format('*'*len(__banner), __banner)
            IPython.embed(banner1=__banner)
        except serial.SerialException as ser_ex:
            print('Problem connecting to power supply:', ser_ex)
            sys.exit(1)
        finally:
            __bkps.close()
    except KeyboardInterrupt:
        print('\nExitting tool!')


if __name__ == '__main__':
    main()
