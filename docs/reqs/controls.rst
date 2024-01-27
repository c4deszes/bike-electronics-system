User control
============

Lights
------

.. req:: Light behavior controls
  :id: REQ_LIGHT_CONTROL_BEHAVIOR_TABLE
  :status: draft

  .. list-table::
    :header-rows: 1

    * - Item
      - Purpose
      - Control

    * - Signals
      - Indicates the intended turning direction
      - 2 buttons or 1 lever, globally enabled/disabled based on lighting mode

    * - Main lights
      - Indicates ride direction
      - Autonomously by the body computer and based on lighting mode

    * - High beams
      - Indicates the area around and above the bicycle
      - 1 button and automatically by the body computer

    * - Beamforming
      - Smooths out the front light direction, following corners
      - Automatically based on the lighting mode, configurable

    * - Warning lights
      - Indicates stand still state
      - 1 button

  .. image:: assets/light-controls.svg

Battery
-------

.. req:: Battery status LED indication
  :id: REQ_BATTERY_STATUS_LED
  :status: draft

  There should be an LED indication on the battery management system showing that:

  * the battery is connected and good, by a solid red color
  * the battery is connected but has a low charge, by a slowly blinking red color
  * the battery is connected but has a very low charge, by a a rapidly blinking red color

.. req:: Battery removal intent
  :id: REQ_BATTERY_PARKING_BUTTON
  :status: draft

  There should be a button on the battery management system that when pressed, indicates the battery
  is going to be removed. After pressing it the whole electronics system goes to shutdown mode, the
  operation is coordinated by the cycle computer and can be rejected by it.

  When rejecting the park the LED should blink twice within 1 second and the user will have to press
  it again to attempt parking.

  When shutdown happened successfully the LED should turn off.

  If the shutdown happened but the battery was not removed then the LED should remain off until bus
  activity which is ideally initiated by the cycle computer or one of the peripherals sensing
  movement.

  .. image:: assets/battery.svg
