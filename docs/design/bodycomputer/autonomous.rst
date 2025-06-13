Autonomous Behavior
===================

It's important that the system is able to work standalone with minimal user intervention.

Cold start
----------

The system starts up when the battery is inserted.

* Lights are initially at minimum brightness

Operation
---------

While in operating mode the front light status is polled, as the button is pressed the body computer
cycles through different light modes. If the front light is disconnected then the mode should still
be kept, only valid single increments should cycle the modes.

Speed status and ride status are continuously polled.

When the ride status is Idle the brightness in the current mode is decreased, the brightness goes
back to normal if the ride status is Active, or if the mode is changed.

Parking (long)
--------------

Parking is initiated by the user, pressing a button on the body computer activates it. It can only
be activated when the bicycle is in Idle, Paused or NotStarted ride state.

When parking is accepted the body computer will send an Shutdown request on the network, every
device goes into low power state.

The system can wakeup at the request of the body computer, either pressing the park button again
or via other detection methods (accelerometer, dynamo, etc.)

Park (short)
------------

Similar to long parking, except Idle request is sent at the end, devices may have specific low
power modes.

The system can wakeup at the request of any node that's capable of detecting activity.
