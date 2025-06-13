Speed signals
=============

Speed status
------------

.. req:: Global speed signal
    :id: REQ_SIGNAL_GLOBAL_SPEED
    :status: draft

    The speed signal shall be in the following value range:

    - 0: Stand still ``0 km/h``
    - 1-65535: Speed in ``0.1 km/h`` per increment

.. req:: Global speed state
    :id: REQ_SIGNAL_GLOBAL_SPEED_STATE
    :status: draft
    
    - Ok (0): When the speed signal is good
    - Slow response (1): When the speed and related signals update slower than the required reaction
                         time for critical events
    - Unreliable (2): When the speed signal is likely incorrect
    - Error (3): When the speed cannot be determined

.. req:: Channel speed state
    :id: REQ_SIGNAL_CHANNEL_SPEED_STATE
    :status: draft

    The speed state shall have the following values:

    - Ok (0) - when the output channel is fine and a valid speed signal is available
    - Unused (1) - not used
    - Sensor warning (2) - when the speed sensor reports back a measurement warning (airgap)
    - Speed unreliable (3) - when the speed signal is inconsistent
    - Sensor error (4) - when the speed sensor reports back a measurement error or no data is available
    - Output open (5) - when the output channel has no sensor connected
    - Output shorted/error (6) - when the output channel is shorted or generally has a physical error
    - Off (7) - when the corresponding output stage is off

    The values here also denote priority, the highest being the output turned off, the idea being
    that lower values correspond to a usable speed signal while high ones above sensor error mean
    that the speed is incorrect.

.. req:: Brake signal
    :id: REQ_SIGNAL_BRAKE
    :status: draft

    The brake signal shall have the following values:

    - Disabled (0)
    - Not braking (1)
    - Braking (2)
    - Unused (3)

.. req:: Wheel slip signal
    :id: REQ_SIGNAL_WHEEL_SLIP
    :status: draft

    The wheel slip signal shall have the following values:
    
    - Not active (0) - when the wheel isn't slipping
    - Slip (1) - when the wheel is detected to be slipping

.. req:: Wheel lockup signal
    :id: REQ_SIGNAL_WHEEL_LOCKUP
    :status: draft

    The wheel slip signal shall have the following values:
    
    - Not active (0) - when the wheel isn't locked up
    - Lockup (1) - when the wheel is detected to be locked up

Distance
--------

.. req:: Distance signal
    :id: REQ_SIGNAL_DISTANCE
    :status: draft

    The distance signal shall be in the following range:

    - Distance (0 - 2^32-1): Distance rode since power up in meters

Road surface
------------

.. req:: Road quality signal
    :id: REQ_SIGNAL_ROAD_QUALITY
    :status: draft

    The road quality signal shall have the following values:

    - Not measured (0)
    - Flat (1)
    - Rough (2)
    - Very rough (3)

.. req:: Gradient signal
    :id: REQ_SIGNAL_GRADIENT
    :status: draft

    The road surface gradient shall have the following values:

    - Angle (0-63): ``1.4°`` per increment

iTPMS
-----

.. req:: iTPMS signal
    :id: REQ_SIGNAL_ITPMS_STATE
    :status: draft

    The iTPMS signal shall have the following values:

    - Stopped (0): when the measurement has been stopped with no definite result
    - Running (1): when a measurement is in progress
    - Front pressure low (2): measurement has concluded, front tire is underinflated
    - Rear pressure low (3): measurement has concluded, rear tire is underinflated
    - Ok (4): measurement has concluded, tire pressures are good
    - Invalid (5-7): unused signal value range
