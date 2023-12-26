Radar
=====

Rear radar requirements
-----------------------

.. req:: Rear radar range
  :id: REQ_REAR_RADAR_RANGE
  :status: draft

  The radar shall have a maximum range of ``10m``, and a minimum range of ``0.5m``.

  The radar angle should be off center to the left to enhance the detection area to where traffic
  most likely will be approaching from. This angle should be ``3.5°``, but can be mounted straight
  if the sensitivity of the radar is good at this angle.

.. req:: Rear radar speed range
  :id: REQ_REAR_RADAR_SPEED_RANGE
  :status: draft

  The radar shall be able to measure the relative speed of the target in the range of:

  * -5km/h (departure)
  * 40km/h (approaching)

  *The Vra=40km/h requirement comes from the usual cycling speed being 25km/h and cars in standard
  traffic going 50-60km/h, anything above this would likely not be detected within the maximum
  distance.*
