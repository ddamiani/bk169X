import time
import configparser

import numpy as np

import re


class PowerSupplyCalib(object):
    def __init__(self, ps, vstart, vend, vstep, scan_speed=1.5):
        self.vstart = vstart
        self.vend = vend
        self.vstep = vstep
        self.scan_vals = np.arange(self.vstart, self.vend+(0.5*self.vstep), self.vstep)
        self.ps = ps
        self.scan_speed = scan_speed
        self._scans = {}
        self._volt_key = 'VoltCalib'
        self._curr_key = 'CurrCalib'
        self._key_regex = re.compile('address\.([0-9]{3})')
        self._min_volt_addr = 59
        self._max_volt_addr = 84
        self._start_volt_val = 8
        self._volt_per_addr = 8
        self._min_curr_addr = 110
        self._max_curr_addr = 142
        self._start_curr_val = 0
        self._curr_per_addr = 32
        self._calib_types = {
            self._volt_key: range(self._min_volt_addr, self._max_volt_addr, 1),
            self._curr_key: range(self._min_curr_addr, self._max_curr_addr, 1),
        }
        self.prntstr = '{0:.1f}: {1:.2f}'

    def scan(self, name=None, residual=False):
        scan_result = []
        if self.ps.voltage() < 0.01:
            self.ps.on()
        for val in self.scan_vals:
            self.ps.voltage(val)
            time.sleep(self.scan_speed)
            if residual:
                setp, _ = self.ps.setpoint()
                result = self.ps.voltage() - setp
            else:
                result = self.ps.voltage()
            scan_result.append(result)
        if name is None:
            return scan_result
        else:
            self._scans[name] = scan_result

    def dump(self, filename):
        config = configparser.ConfigParser()
        for k, v in self._calib_types.items():
            config.add_section(k)
            for addr in v:
                config[k]['address.{:0>3d}'.format(addr)] = self.address(addr)
        with open(filename, 'w') as configfile:
            config.write(configfile)

    def load(self, filename):
        config = configparser.ConfigParser()
        config.read(filename)
        for calib_type in self._calib_types.keys():
            for addr_key, value in config[calib_type].items():
                match = self._key_regex.match(addr_key)
                if match:
                    self.address(int(match.group(1)), value)

    @property
    def volt_addr(self):
        return self._calib_types[self._volt_key]

    @property
    def curr_addr(self):
        return self._calib_types[self._curr_key]

    def set_scan(self, vstart, vend, vstep, scan_speed=None):
        self._scans = {}
        self.vstart = vstart
        self.vend = vend
        self.vstep = vstep
        self.scan_vals = np.arange(self.vstart, self.vend+(0.5*self.vstep), self.vstep)
        if scan_speed is not None:
            self.scan_speed = scan_speed

    def set_scan_address(self, address):
        voltages = self.get_voltages(address)
        self.set_scan(voltages[0], voltages[-1], 0.1)

    def get_scan(self, name, show=False):
        if show and name in self._scans:
            print('\n'.join(self.prntstr.format(setp, res) for setp, res in zip(self.scan_vals, self._scans[name])))
        else:
            return self._scans.get(name)

    def residual(self, name1, name2, show=False):
        avals = self.get_scan(name1)
        bvals = self.get_scan(name2)
        residuals = [a-b for a, b in zip(avals, bvals)]
        if show:
            print('\n'.join(self.prntstr.format(setp, res) for setp, res in zip(self.scan_vals, residuals)))
        else:
            return residuals

    def address(self, addr, val=None):
        if val is None:
            return self.ps.cmd('GEEP', '{:0>3d}'.format(addr))
        else:
            self.ps.cmd('SEEP', '{addr:0>3d}{val}'.format(addr=addr, val=val))

    def get_volt_address(self, voltage):
        return (int(voltage*10) - self._start_volt_val) // self._volt_per_addr + self._min_volt_addr

    def get_curr_address(self, current):
        return (int(current*100) - self._start_curr_val) // self._curr_per_addr + self._min_curr_addr

    def get_voltages(self, address):
        voltint = self._volt_per_addr * (address - self._min_volt_addr) + self._start_volt_val
        return [volt/10.0 for volt in range(voltint, voltint+self._volt_per_addr, 1)]

    def get_currents(self, address):
        currint = self._curr_per_addr * (address - self._min_curr_addr) + self._start_curr_val
        return [curr/100.0 for curr in range(currint, currint+self._curr_per_addr, 1)]
