bk169X
=======

BK Precision 169X Series control and calibration

A simple Python library for interacting with BK Precision 169X Series DC power supplies. Communicates with the supplies
over an RS-232 connection. Also has the ability to read and update the voltage and current calibration constants of the
supply in the unit's eeprom.

Example where the supply is attached to COM3:

    from bk169X import control
    
    ps = control.PowerSupply('COM3')
    # set the voltage to 5 V
    ps.voltage(5.0)
    # turn on the supplies output
    ps.on()
    # readout the sense voltage, current draw, and mode (constant voltage or current)
    volt, curr, mode = ps.reading()


Also includes a small IPython based terminal app *bkterm* for controlling/calibrating the supply interactively. 

Requirements
------------

  * Python 3.x
  * NumPy
  * PySerial
  * IPython
