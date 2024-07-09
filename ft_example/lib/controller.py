import fischertechnik.factories as txt_factory

txt_factory.init()
txt_factory.init_motor_factory()
txt_factory.init_servomotor_factory()

controller = txt_factory.controller_factory.create_graphical_controller()

txt_factory.initialized()
servo = txt_factory.servomotor_factory.create_servomotor(controller, 1)
motor = txt_factory.motor_factory.create_encodermotor(controller, 1)