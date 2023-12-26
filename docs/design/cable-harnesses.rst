Cable harnesses
===============

Front devices
-------------

.. kroki::
    :type: wireviz

    connectors:
        LIN_LockoutActuator:
            type: JWPF
            subtype: male
            pinlabels: [Vbat, -, LIN, GND]
        LIN_FrontLight:
            type: JWPF
            subtype: male
            pinlabels: [Vbat, -, LIN, GND]
        LIN_CycleComputer:
            type: JWPF
            subtype: male
            pinlabels: [Vbat, LIN2, LIN1, GND]
        BMS_RearConnector:
            type: JWPF
            subtype: male
            pinlabels: [Vbat, -, LIN, GND, Vbat, -, LIN, GND]

    cables:
        W1:
            gauge: 0.25 mm2
            length: 0.2
            color_code: DIN
            wirecount: 8

    connections:
        -
            - BMS_RearConnector: [1-8]
            - W1: [1-8]
        -
            - W1: [1-4]
            - LIN_FrontLight: [1-4]
        -
            - W1: [5-8]
            - LIN_CycleComputer: [1-4]
        -
            - W1: [5-8]
            - LIN_LockoutActuator: [1-4]

Rear devices
------------

.. kroki::
    :type: wireviz

    connectors:
        LIN_RotorSensor:
            type: JWPF
            subtype: male
            pinlabels: [Vbat, -, LIN, GND]
        LIN_RearLight:
            type: JWPF
            subtype: male
            pinlabels: [Vbat, -, LIN, GND]
        BMS_RearConnector:
            type: JWPF
            subtype: male
            pinlabels: [Vbat, -, LIN, GND, Vbat, -, LIN, GND]

    cables:
        W1:
            gauge: 0.25 mm2
            length: 0.2
            color_code: DIN
            wirecount: 8

    connections:
        -
            - LIN_RotorSensor: [1-4]
            - W1: [1-4]
            - BMS_RearConnector: [1-4]
        -
            - LIN_RearLight: [1-4]
            - W1: [5-8]
            - BMS_RearConnector: [5-8]

Sensor cables
-------------

.. kroki::
    :type: wireviz

    connectors:
        RotorSensor_Input1:
            type: JWPF
            subtype: male
            pinlabels: [In+, In-]
        RotorSensor_Input2:
            type: JWPF
            subtype: male
            pinlabels: [In+, In-]
        FrontSensor:
            type: 2pin
            subtype: soldered
            pinlabels: [V+, GND]
        RearSensor:
            type: 2pin
            subtype: soldered
            pinlabels: [V+, GND]

    cables:
        W1:
            gauge: 0.25 mm2
            length: 0.2 cm
            color_code: DIN
            wirecount: 2
        W2:
            gauge: 0.25 mm2
            length: 0.2
            color_code: DIN
            wirecount: 2

    connections:
        -
            - RotorSensor_Input1: [1-2]
            - W1: [1-2]
            - FrontSensor: [1-2]
        -
            - RotorSensor_Input2: [1-2]
            - W2: [1-2]
            - RearSensor: [1-2]