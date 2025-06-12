# Bicycle electronics system

## Hardware

[Rotor sensor](https://github.com/c4deszes/bike-rotor-sensor) (or wheel speed sensor) measures wheel
speed, detects braking, flat tire and road inclination.

[Rear Light](https://github.com/c4deszes/bike-rear-light) is a tail light with brake light
capabilities.

[Front light](https://github.com/c4deszes/bike-front-light) is a front light, that synchronizes
modes to the rest of the system.

[Battery Management System](https://github.com/c4deszes/bike-battery-management) is the power source
of the system, it also acts the master on the bus handling communication.

---

[Lockout actuator](https://github.com/c4deszes/bike-lockout-actuator) rotates the front suspension
lockout valve to either open (free moving) or closed position which affect the shock absorbing
capability of the fork.

## Communication & Utility

[LINE protocol](https://github.com/c4deszes/bike-line-protocol) is used for communication between
nodes.

[Flash tool](https://github.com/c4deszes/bike-flash-tool) extends diagnostics with standard
interfaces for flashing.

[UDS tool](https://github.com/c4deszes/bike-uds-tool) adds standard interfaces for reading and
writing product properties and calling services.

## Low-level libraries

[SAMD21 HAL](https://github.com/c4deszes/samd21-hal) is a Hardware Abstraction Layer for SAMD21
devices written in C.

[SAMD21 LINE Bootloader](https://github.com/c4deszes/samd21-line-bootloader) is a bootloader using
LINE protocol for SAMD21 devices.
