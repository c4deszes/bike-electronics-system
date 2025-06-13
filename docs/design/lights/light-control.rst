

The lights are controlled by the BMS.

To ensure that the lights are on when needed and but also don't distract others by their behavior
the control system must have multiple protections. Some of these protections will be part of the
lights themselves, others will be how the

Mode control
------------

Lights have 4 controlled modes of which 2 are up to the user's preference, adaptive and standard.
This preference is stored by the BMS and upon startup must be validated, any other default mode
should be considered invalid.

The mode "Off" must only be selected by the user, this selection might be automatic for example
based on the phone's internal clock, the failure of that is highly unlikely and if that occurs the
phone can be disconnected, this action should prompt the BMS to revert to the default mode.

The mode "Emergency" must only be selected by the body computer under specific circumstances. A
failure in determining this mode would either cause the battery to drain faster than it should or
it would cause a lower than expected brightness. Both of these have severe consequences but they're
within the expectations of the rider, e.g.: bringing multiple batteries, keeping them charged or
being able to navigate with no lights.

Brightness control
------------------

Brightness is controlled by a single signal that affects all lights.

In standard mode it's up to the individual lights to ensure that they're daylight visible. Since
these values are configurable the lights should validate this setting and revert to safe known values
should a configuration failure occur.

In adaptive mode the lights might be off if the target level is low. No safety mechanism is expected
regarding adaptive mode as the user can switch to standard mode should the adaptive configuration
provide no output.

.. TODO: turn signal, strobe, antistrobe

Special options
---------------

All lights have separate controls to enable or disable certain functions and to enable or disable
blinking.

Rear light:

* Behavior: blinking and solid behavior is controlled by user preference and external signals
* BrakeLight enable/disable: no special caution needed, up to user preference
* TurnSignal enable/disable: no special caution needed, up to user preference, masks turn indicator

Front light:

* Behavior: blinking and solid behavior is controlled by user preference and external signals
* BeamForming enable/disable: user preference, the unit has to detect when beamforming could be faulty
* TurnSignal enable/disable: no special caution needed
* HighBeam: caution needed, unintended high beam on could blind oncoming traffic, must be off unless
  controls explicitly enable it

Failures
--------

Individual light failures are detected and the user would be notified, the front light is always seen
so there's no special detection feature expected. The rear light is expected to detect it's own
light element failures as the user would not see it.

Light segments failing may cause other segments to be disabled, for example if the rear right turn
light is shorted then the front turn indicators may be disabled. This is all optional and depedent
on no other failures occuring.

An entire light unit's failure is also detected, the remaining lights should remain on.

When a light is disconnected from the rest of the network the light goes into safety mode, the light
should make sure that the safety minimum brightness is valid. The body computer should consider the
whole light unit to have failed (e.g.: no turn signals, brake light)

Blink and blink control failure can affect the lights drastically. External blink signals must be
validated by the lights so that they conform to some minimum timing requirements. Blinking mode might
be unintentionally set, this is not a huge problem if the internal blink signals operate correctly.
