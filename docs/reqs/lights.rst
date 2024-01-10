Lights
======

Modes
-----

.. req:: Lighting mode
  :id: REQ_LIGHTING_MODES
  :status: draft

  .. list-table::
    :header-rows: 1

    * - Mode
      - Description
      - During bus failure

    * - Off
      - * Front light is off
        * Rear light is off
        * The brake lights come on during braking
        * Turn signals are enabled upon user request
        * High beams also turn on upon user request, but they do timeout after 5 seconds.
      - The lights switch to standard mode

    * - Standard
      - * Front light is on at the safety setting
        * Rear light is on
        * Brake lights come on during braking
        * Turn signals are enabled upon user request
        * High beams also turn on upon user request
      - * High beams should be off
        * Turn signals should be off
        * Brake light is enabled but only if the rear light can determine the condition on it's own

    * - Adaptive
      - * Front light is on, level is set according to ambient light level (optionally enabled daytime running lights)
        * Rear light is on, level is set according to ambient light level (optionally enabled daytime running lights)
        * Brake lights come on during braking
        * Turn signals are enabled upon user request
        * High beams also turn on upon user request
      - The lights switch to standard mode

    * - Emergency
      - * Front light is on at the lowest permitted brightness
        * Rear light is on at the lowest permitted brightness
        * Brake lights are disabled
        * Turn signals are disabled
        * High beams are disabled
        * Wide beams are disabled
      - The lights stay in emergency mode
