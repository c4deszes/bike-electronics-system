Products
========

Rotor sensor
------------

* Measuring speed of front and rear wheel
* Measuring number of rotations of boths wheels
* Detection of slipping wheels
* Detection of locked up wheels
* Detection of flat tire (iTPMS)
* Measuring acceleration of the bicycle frame
* Measuring road steepness

**Target:**

* Microcontroller: ATSAMD21x
* Communication: LINE / LIN PHY
* Power consumption: 100mA

Lockout actuator
----------------

* Open/close the lockout valve head
* Report back position of valve head
* Measuring acceleration and movement of the fork
* Automatically reacting to road conditions to change lockout setting

**Target:**

* Microcontroller: ATSAMD21x
* Communication: LINE / LIN PHY
* Power consumption: 100mA idle, 3.0A peak

Rear light
----------

* Indicate bicycle location clearly
* Indicate when braking
* Indicate turning direction
* Detecting vehicles coming from the rear

**Target:**

* Microcontroller: ATSAMD21x or ATTINY826
* Communication: LINE / LIN PHY
* Power consumption: 500mA max. continuous

Front light
-----------

* Brighten the road in a 60-90° cone in front of the bicycle
* Beamform the light, removing slight shakes from the output and provide better coverage during
  steering, the beam should also follow inclines and declines.
* Indicate turning direction

**Target:**

* Microcontroller: ATSAMD21x
* Communication: LINE / LIN PHY
* Power consumption: 2.0A max. continuous

Battery manager
---------------

* Provide power to all other products
* Measure available energy in the battery
* Provide measurements to BCM
* Ability to quick change batteries

**Target:**

* Microcontroller: ATSAMD21x or ATTINY826
* Communication: LINE / LIN PHY
* Power consumption: 100mA max. internal, 5.0A supplied, 500mA generator input

Cycle computer
--------------

* Displaying information like speed, distance
* Allows controlling the other products like lights, suspension control
* Automatic lockout activation and remote control
* Automatic light control, turn indication

**Target:**

* Microcontroller: ESP32-S2/S3
* Communication: LINE / LIN PHY
* Power consumption: 300mA max. continuous

More ideas
----------

* Electronic bell
* Frontal collision detection, road quality monitoring
* Monitoring gear selection and actual gear
* Stick shaker
