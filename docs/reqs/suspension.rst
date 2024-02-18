Suspension
==========

Modes
-----

.. req:: Suspension modes
  :id: REQ_SUSPENSION_MODES
  :status: draft

  * Automatic: actuators go to the commanded position but will go automatically to the open
               position if the road surface quality worsens
  * Command: actuators go the commanded position
  * Open: actuators stay in the open position, ignoring all commands
  * Manual: actuator movement is disabled, only manual adjustments work

.. req:: Actuation speed
  :id: REQ_SUSPENSION_CONTROL
  :status: draft

  The actuators shall be able to go from their open to their closed position within ``4 seconds``.
