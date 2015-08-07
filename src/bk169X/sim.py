import time


class SerialSim(object):
    def __init__(self, address=b'00', voltage=0.0, current=0.0, pwr=False, remote=False, timeout=1):
        self.address = address
        self.voltage = voltage
        self.current = current
        self.pwr = pwr
        self.remote = remote
        self.timeout = timeout
        self._read_buffer = b''
        self._write_buffer = b''
        self._cmd_reply = b'OK\r'
        self._eol = b'\r'
        self._cmd_len = 4
        self._gmax_v = 20.1
        self._gmax_c = 9.99
        self.limit = self._gmax_v
        self._gmax_val = b'201999\r'
        self._cmds = {
            b'SOUT': self._power,
            b'GMAX': self._gmax,
            b'SESS': self._remote,
            b'ENDS': self._local,
            b'GETS': self._setpoint,
            b'GETD': self._reading,
            b'VOLT': self._volt,
            b'CURR': self._curr,
            b'GOVP': self._govp,
            b'SOVP': self._sovp,
        }

    def write(self, cmd):
        self._write_buffer += cmd
        length_eol = len(self._eol)
        if self._write_buffer[-length_eol:] == self._eol:
            self._process()

    def read(self, chars):
        if self._read_buffer:
            reply = self._read_buffer[:chars]
            self._read_buffer = self._read_buffer[chars:]
            return reply
        else:
            time.sleep(self.timeout)
            return self._read_buffer

    def close(self):
        self._read_buffer = b''
        self._write_buffer = b''

    def _gmax(self, value):
        if value == b'':
            self._read_buffer += self._gmax_val
            return True
        else:
            return False

    def _local(self, value):
        if value == b'':
            self.remote = False
            return True
        else:
            return False

    def _remote(self, value):
        if value == b'':
            self.remote = True
            return True
        else:
            return False

    def _power(self, value):
        if value == b'1':
            self.pwr = False
        elif value == b'0':
            self.pwr = True
        return True

    def _setpoint(self, value):
        if value != b'':
            return False
        else:
            reply = '{v:03.0f}{c:03.0f}\r'.format(v=self.voltage*10, c=self.current*100)
            self._read_buffer += reply.encode('ascii', 'ignore')
            return True

    def _volt(self, value):
        if value == b'':
            return False
        else:
            voltage = float(value)/10.0
            self.voltage = min(voltage, self.limit, self._gmax_v)
            return True

    def _curr(self, value):
        if value == b'':
            return False
        else:
            current = float(value)/100.0
            self.current = min(current, self.limit, self._gmax_c)
            return True

    def _govp(self, value):
        if value != b'':
            return False
        else:
            reply = '{v:03.0f}\r'.format(v=self.limit*10)
            self._read_buffer += reply.encode('ascii', 'ignore')
            return True

    def _sovp(self, value):
        if value == b'':
            return False
        else:
            self.limit = float(value)/10.0
            return True

    def _reading(self, value):
        if value != b'':
            return False
        else:
            if self.pwr:
                reply = '{v:04.0f}{c:04.0f}0\r'.format(v=self.voltage*100, c=self.current*1000)
            else:
                reply = '000000000\r'
            self._read_buffer += reply.encode('ascii', 'ignore')
            return True

    def _process(self):
        msgs = self._write_buffer.splitlines(False)
        for msg in msgs:
            cmd = msg[:self._cmd_len]
            address = msg[self._cmd_len:self._cmd_len + len(self.address)]
            value = msg[self._cmd_len + len(self.address):]
            if address == self.address:
                func = self._cmds.get(cmd)
                if func is not None:
                    if func(value):
                        self._read_buffer += self._cmd_reply
        self._write_buffer = b''
