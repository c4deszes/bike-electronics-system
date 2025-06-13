Power lifecycle
===============

Cold start
----------

Cold start is when there's no power available, then suddenly it is. It may happen in two ways:

* Battery is inserted
* Dynamo hub starts generating power

All peripherals turn on as power is available.

Idle mode
----------

Idle mode is used to conserve battery life. It is entered under two conditions:

* Master requests idle mode, no further requests are sent after
* Voltage drops below 9V and no communication is active for 1sec

Idle mode is exited if:

* Any traffic occurs on the bus
* the voltage goes back above 9V

Product specific behavior:

* Rotor sensor: none, sensors may be turned off but only if it can determine when the bicycle starts
                going again. while the system is idle the device may send a wakeup request if it
                detects movement
* Rear light: emergency brightness
* Front light: emergency brightness

Shutdown
--------

Shutdown mode is used to converse battery life even more, it is entered when:

* Master requests shutdown mode, no further requests are sent after

Shutdown mode is exited if:

* Traffic on the bus

Product specific behavior:

* Rotor sensor: configuration is saved, ride is stopped and logs are saved, turned off
* Rear light: configuration is saved, turned off
* Front light: configuration is saved, turned off
