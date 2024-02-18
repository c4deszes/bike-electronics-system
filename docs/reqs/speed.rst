Speed
=====

.. req:: Speed range
  :id: REQ_SPEED_RANGE
  :status: final

  The rotor sensor shall be capable of measuring speeds up to ``70km/h``.

.. req:: Speed Resolution
  :id: REQ_SPEED_RESOLUTION
  :status: draft

  The rotor sensor shall be able to measure speeds with a resolution of:

    * ``0.1 km/h`` in the range of ``0-30km/h``
    * ``0.5 km/h`` in the range of ``30-70km/h``

.. req:: Distance range
  :id: REQ_DISTANCE_RANGE
  :status: final

  The rotor sensor shall be capable of measuring distance rode in a session up to ``200km``.

.. req:: Acceleration range
  :id: REQ_ACCELERATION_RANGE
  :status: final

  The rotor sensor shall be capable of measuring accelerations from ``-1.5g`` to ``1.5g``.
  
  During standard operation the expected accelerations will be within ``-0.5g`` to ``0.5g``.

.. req:: Brake detection
  :id: REQ_BRAKE_DETECTION
  :status: draft

  When the sensed deceleration is above ``2.5 m/s^2`` then the rotor sensor shall report braking,
  the condition can be cleared once the deceleration stops.

.. req:: Wheel lockup
  :id: REQ_WHEEL_LOCKUP
  :status: draft

  When the sensed speed of a wheel suddenly goes below ``0.5 m/s`` the wheel should be reported as
  locked up.

.. req:: Wheel slip
  :id: REQ_WHEEL_SLIP
  :status: draft

  When the sensed speed of a wheel suddenly goes above the other wheel's speed by more than ``10%``
  and that wheel is not locked up the wheel should be reported as slipping.

.. req:: Sensor error detection
  :id: REQ_SPEED_SENSOR_ERROR_DETECTION
  :status: final

  The rotor sensor shall report when an error occurs in any of it's sensors, 

.. req:: Tire Pressure monitoring
  :id: REQ_TIRE_PRESSURE_MONITOR
  :status: draft

  The rotor sensor shall be able to distinguish tire circumferences based on speed and then indicate
  whether a tire is low pressure.
