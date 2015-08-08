import sys
import argparse

import serial
import IPython

import os
import glob
import bk169X.control as _bkcont
import bk169X.calib as _bkcal


def __parse_cli():
    parser = argparse.ArgumentParser(
        description='A tool for control and calibration of BK Precision 169X Series DC power supplies'
    )

    settle = 1.5
    serial_port_linux = '/dev/ttyUSB0'
    serial_port_osx = '/dev/cu.usbserial-*'
    serial_port = None
    if os.name == 'nt':
        serial_port = 'COM3'
    elif os.name == 'posix':
        if os.path.exists(serial_port_linux):
            serial_port = serial_port_linux
        else:
            # Possible dev name on OSX
            devs = glob.glob(serial_port_osx)
            if devs:
                serial_port = devs[0]

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

    control_parser.add_argument(
        '-s',
        '--simulate',
        action='store_true',
        help='run the control software with a simulated serial device'
    )

    calib_parser = subparser.add_parser('calib', help='Calibrtion mode of the tool')
    calib_parser.set_defaults(simulate=False)

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
        __port = __args.port
        __banner_base = '*  {mode} tool for BK Precision 169X Series DC power supplies  *'
        __banner_stp = 'Power supply settings: {volt:4.1f} V, {curr:5.2f} A\n'
        __banner_read = 'Power supply readings: {volt:4.1f} V, {curr:5.2f} A\n'
        # prompt user for input if no serial port was specified
        if __port is None:
            __port = input('Please specify a serial port to use (e.g. COM3, /dev/ttyUSB0): ')
        with _bkcont.PowerSupply(__port, simulated=__args.simulate) as __bkps:
            if __args.mode == 'calib':
                __banner = __banner_base.format(mode='Calibration')
                calib = _bkcal.PowerSupplyCalib(__bkps, __args.vstart, __args.vend, __args.vstep, __args.settle)
                __stp_v, __stp_c = calib.ps.setpoint()
                __status = __banner_stp.format(volt=__stp_v, curr=__stp_c)
                __status += __banner_read.format(volt=calib.ps.voltage(), curr=calib.ps.current())
            elif __args.mode == 'control':
                ps = __bkps
                __banner = __banner_base.format(mode='Control')
                __stp_v, __stp_c = ps.setpoint()
                __status = __banner_stp.format(volt=__stp_v, curr=__stp_c)
                __status += __banner_read.format(volt=ps.voltage(), curr=ps.current())
            else:
                print('Unknown tool mode: {mode}'.format(mode=__args.mode))
                sys.exit(1)
            __banner = '\n{0}\n{1}\n{0}\n'.format('*'*len(__banner), __banner)
            IPython.embed(banner1=__banner, banner2=__status)
    except serial.SerialException as ser_ex:
        print('Problem connecting to power supply:', ser_ex)
        sys.exit(1)
    except KeyboardInterrupt:
        print('\nExiting tool!')


if __name__ == '__main__':
    main()
