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

      * - Off
        - * Front light is off
          * Rear light is off
          * The brake lights come on during braking
          * Turn signals are enabled upon user request
          * High beams also turn on upon user request

      * - Standard
        - * Front light is on at the safety setting
          * Rear light is on
          * Brake lights come on during braking
          * Turn signals are enabled upon user request
          * High beams also turn on upon user request

      * - Adaptive
        - * Front light is on, level is set according to ambient light level
          * Rear light is on, level is set according to ambient light level
          * Brake lights come on during braking
          * Turn signals are enabled upon user request
          * High beams also turn on upon user request

      * - Emergency
        - * Front light is on at the lowest permitted brightness
          * Rear light is on at the lowest permitted brightness
          * Brake lights are disabled
          * Turn signals are disabled
          * High beams are disabled
          * Wide beams are disabled

Off
---

Off generally turns everything off, but user request might override this in case of turn signals,
high beams and the brake light can activate.

Standard and adaptive mode
--------------------------

Selectable by the user or the body computer, the main difference is that standard mode is on during
daylight conditions. This is achieved by a minimum set brightness, whereas adaptive doesn't have this
so the lights might be completely off for some setpoints.

Emergency mode
--------------

Selectable by the body computer, this mode is used in case of a low battery or other power delivery
issue. All lights reduce their brightness to the minimum legal level, features that would consume
additional power such as high beam and brake light are disabled.

In case of a communication loss the lights stay in emergency mode, because otherwise the safety
setting might drain the batteries further.

Loss of communication
---------------------

In all modes except emergency the behavior in case the communication is lost is:

* Front light is set to safety level and strobe settings, high beam is off, turn signal is disabled
* Rear light is set to safety level and strobe settings, brake light reverts to internal source,
  turn signal is disabled
