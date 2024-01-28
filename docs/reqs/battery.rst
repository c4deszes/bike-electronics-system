Battery
=======

.. req:: Battery voltage
  :id: REQ_BATTERY_VOLTAGE
  :status: draft

  The operating battery voltage shall be within ``6.8V`` and ``12V``.

.. req:: Battery current
  :id: REQ_BATTERY_CURRENT
  :status: draft

  The battery shall be able to provide ``5A`` peak current and ``2A`` contiuously.

.. req:: Battery capacity
  :id: REQ_BATTERY_CAPACITY
  :status: draft

  The battery shall be able to operate for ``6h`` under the following assumptions:

  * Front light is on at 75%  of it's peak power, beam forming is on
  * Rear light is on at 100% brightness with brake lights enabled, radar is also enabled
  * Cycle computer is operational and is wirelessly connected to a phone, display is 30% backlit
  * Rotor sensor is operational with all sensors
  * Lockout actuator is idle with 4 actuations every hour
  * BMS is on, generator power not available
