import fischertechnik.factories as txt_factory

txt_factory.init()

controller = txt_factory.controller_factory.create_graphical_controller()

txt_factory.initialized()