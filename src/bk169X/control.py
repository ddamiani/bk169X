import serial


class PSCommError(Exception):
    pass


class PowerSupply(object):
    def __init__(
            self,
            device,
            baud=9600,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            address='00',
            timeout=1
    ):
        self.device = device
        self.baud = baud
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.address = address
        self.timeout = timeout
        self._ser = None
        self._cmd_rep = 'OK'
        self._cmd_rep_fail = ''

    def connect(self):
        if self._ser is None:
            self._ser = serial.Serial(
                self.device,
                self.baud,
                bytesize=self.bytesize,
                parity=self.parity,
                stopbits=self.stopbits,
                timeout=self.timeout
            )

    def close(self):
        self._ser.close()
        self._ser = None

    @staticmethod
    def _float_to_fmt(value, order, digits):
        return '{value:0>{digits:d}.0f}'.format(value=value*10**order, digits=digits)

    @staticmethod
    def _fmt_to_float(valstr, order):
        return float(valstr)/10**order

    def _write(self, str_val):
        str_val += '\r'
        byte_val = str_val.encode('ascii', 'ignore')
        self._ser.write(byte_val)

    def _readline(self):
        eol = b'\r'
        leneol = len(eol)
        line = bytearray()
        while True:
            c = self._ser.read(1)
            if c:
                line += c
                if line[-leneol:] == eol:
                    break
            else:
                break
        return line.decode('ascii', 'ignore').rstrip('\r')

    def remote(self):
        self.cmd('SESS')

    def local(self):
        self.cmd('ENDS')

    def off(self):
        self.cmd('SOUT', '1')

    def on(self):
        self.cmd('SOUT', '0')

    def voltage(self, voltage=None):
        if voltage is None:
            resp = self.cmd('GETD')
            return self._fmt_to_float(resp[:4], 2)
        else:
            self.cmd('VOLT', self._float_to_fmt(voltage, 1, 3))

    def current(self, current=None):
        if current is None:
            resp = self.cmd('GETD')
            return self._fmt_to_float(resp[4:-1], 3)
        else:
            self.cmd('CURR', self._float_to_fmt(current, 2, 3))

    def reading(self):
        resp = self.cmd('GETD')
        return self._fmt_to_float(resp[:4], 2), self._fmt_to_float(resp[4:-1], 3), bool(int(resp[-1]))

    def setpoint(self, voltage=None, current=None):
        digits = 3
        if voltage is None and current is None:
            resp = self.cmd('GETS')
            return self._fmt_to_float(resp[:digits], 1), self._fmt_to_float(resp[digits:], 2)
        else:
            if voltage is not None:
                self.cmd('VOLT', self._float_to_fmt(voltage, 1, digits))
            if current is not None:
                self.cmd('CURR', self._float_to_fmt(current, 2, digits))

    def getd(self):
        return self.cmd('GETD')

    def cmd(self, cmd, value=None):
        if self._ser is None:
            self.connect()

        cmd += self.address
        if value is not None:
            cmd += value
        self._write(cmd)

        output = None
        while True:
            line = self._readline()
            if line == self._cmd_rep:
                break
            elif line == self._cmd_rep_fail:
                raise PSCommError(
                    "No command 'OK' response returned by power supply within {0:.1f} s".format(self.timeout)
                )
            else:
                if output is None:
                    output = line
                else:
                    raise PSCommError("More than one line output returned by power supply")

        return output

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, type, value, traceback):
        self.close()
