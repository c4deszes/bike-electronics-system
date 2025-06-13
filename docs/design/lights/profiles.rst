Light profiles
==============

A light profile describes how the lights will behave given system inputs. In every profile
two operations have to be described, an automatic and a manual mode. The profile can choose
to disable either one.

For manual operation a list of modes is needed, the user can cycle through the modes and a mode
can override all light specific signals. There are some automatics that can be enabled in manual
operation.

In automatic operation the light stays in one mode which is dynamic based on certain inputs, like
the ambient light. Then there are a couple of automatic behaviors that can be enabled.

Automatic behaviors
-------------------

Idle derate
~~~~~~~~~~~

when the bicycle is idle the lights' brightness is reduced, the derating is a slope, in standard
mode it derates around the minimum brightness, in adaptive it can derate down to 0

Idle blinking
~~~~~~~~~~~~~

when the bicycle is idle the lights go into blinking mode

.. note:: the brake lights are not automatic behavior, those are standard in every mode if the
    rear light has braking enabled and the rotor sensor can sense braking

Parameters
----------

{
    "manual": {
        "enabled": true
        "modes": [
            {
                "name": "Minimum-Brightness",
                "brightness": 10,
                "mode": "adaptive"
            }
        ],
        "automatics": {
            "idle-derate": {
                "enabled": true,
                "derate": "50%"
            },
            "idle-blink": {
                "enabled": false
            }
        }
    },
    "auto": {
        "enabled": true,
        "automatics": {
            "idle-derate": {
                "enabled": true,
                "derate": "50%"
            },
            "idle-blink": {
                "enabled": false
            }
        }
    }
}
