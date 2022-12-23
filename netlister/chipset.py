from skidl import *
import skidl
from netlister.registry import RegistryMixin, Registry
from netlister.functions import abort
from loguru import logger


import json

# class Device(RegistryMixin):
#     def __init__(self, registry, name, properties) -> None:
#         super().__init__(registry)
#         self.name = name
#         self.raw_pins = properties["pins"]
#         self.footprint = "Package_DIP:DIP-%s_W7.62mm" % len(self.raw_pins)
#         self.__parse_pins()

#     # This function extracts buses from the pins, and converts the pin information into a useful
#     # format.
#     def __parse_pins(self):
#         self.bussed_pins = {}
#         for pinnr, label in self.raw_pins.items():
#             pinnr = int(pinnr)
#             # See if we're dealing with a bus-pin
#             match = re.findall("(.*)\[(\d*)\]", label)
#             if match:
#                 label, idx = match[0]
#                 idx = int(idx)
#                 if label not in self.bussed_pins:
#                     self.bussed_pins[label] = {}
#                 self.bussed_pins[label][idx] = pinnr
#             else:
#                 # Not dealing with a bus pin
#                 if label not in self.bussed_pins:
#                     self.bussed_pins[label] = []
#                 self.bussed_pins[label].append(pinnr)

#         # Now we have a list that looks like this:
#         # {
#         #  'A': {0: 1, 1: 4, 2: 9, 3: 12}, 
#         #  'B': {0: 2, 1: 5, 2: 10, 3: 13}, 
#         #  'Y': {0: 3, 1: 6, 2: 8, 3: 11}, 
#         #  'GND': [7], 
#         #  'VCC': [14]
#         # }

#     def add_to_netlist(self):
#         self.part = skidl.Part('74xx', self.name, footprint=self.footprint, tool_version="kicad_v6")

#     # The connections parameter takes the following format:
#     # The letters are the labels of the device as known in yosys
#     # The numbers are the netnumbers as provided by yosys
#     # {
#     #         "A": [ 2, 3 ],
#     #         "B": [ 4, 5 ],
#     #         "Y": [ 6, 7 ]
#     # }
#     def connect(self, connections):
#         self.__connect_signal(connections)
#         self.__connect_gnd()
#         self.__connect_power()
#         self.__handle_unconnected_pins()


#     # If unconnected pins are inputs, they will be pulled to GND
#     # If they are outputs, they will be left floating
#     def __handle_unconnected_pins(self):
#         for pin in self.part.get_pins():
#             if not pin.is_connected():
#                 if pin.func == Pin.types.INPUT:
#                     pin += self.netlist.GND
#                 elif pin.func == Pin.types.OUTPUT:
#                     pin += NC
#                 else:
#                     abort("Unkown pin type: %s" % pin.func)


#     def __connect_gnd(self):
#         for pin_nr in self.bussed_pins["GND"]:
#             self.__connect_pin_to_net(pin_nr, 0, "VCC")

#     def __connect_power(self):
#         for pin_nr in self.bussed_pins["VCC"]:
#             self.__connect_pin_to_net(pin_nr, 1, "VCC")

#     def __connect_signal(self, connections):
#         for port_label, net_nrs in connections.items():
#             pins_for_port = self.bussed_pins[port_label]
#             for idx, net_nr in enumerate(net_nrs):
#                 pin_nr = pins_for_port[idx]
#                 pin_label = self.raw_pins[str(pin_nr)]
            
#                 self.__connect_pin_to_net(pin_nr, net_nr, pin_label)

#     def __connect_pin_to_net(self, pin_nr, net_nr, pin_label):
#         net = self.netlist.get_net(net_nr)
#         logger.info("Connecting pin {}({}) of {}({}) to net {}({})", pin_nr, pin_label, self.part.ref, self.part.name, net_nr, net.name)

#         self.part[pin_nr] += net

# class Module:
#     def __init__(self, name, device:Device) -> None:
#         self.name = name
#         self.device = device

class DeviceTemplate():
    type : str
    pins: dict
    kicad_library : str
    ports : list
    footprint : str

    def __init__(self, type) -> None:
        self.type = type
        self.ports = []
        
    def set_pins(self, pins):
        self.pins = pins
        self.footprint = "Package_DIP:DIP-%s_W7.62mm" % len(self.pins)
        self.__parse_ports()

    def __parse_ports(self):
        ports = {}
        for pinnr, label in self.pins.items():
            pinnr = int(pinnr)
            # See if we're dealing with a bus-pin
            match = re.findall("(.*)\[(\d*)\]", label)
            if match:
                label, idx = match[0]
                idx = int(idx)
                if label not in ports:
                    ports[label] = {}
                ports[label][idx] = pinnr
            else:
                # Not dealing with a bus pin
                if label not in self.ports:
                    ports[label] = {}
                ports[label][0] = pinnr

        self.ports = ports

class ChipSet(RegistryMixin):
    device_templates : dict

    def __init__(self, registry: Registry) -> None:
        super().__init__(registry)

        self.device_templates = {}

    '''
    The method loads the chipset that is used to map devices typed by YoSYS to devices that
    are part of the KiCAD library
    '''
    def load(self, path):
        logger.info("Loading chipset from {}", path)

        with open(path) as f:
            self.chipset = json.load(f)

        self.__validate()
        self.__parse()

    def __parse(self):
        for type, device_data in self.chipset['devices'].items():
            device_template = DeviceTemplate(type)
            device_template.kicad_library = device_data['kicad_library']
            device_template.set_pins(device_data['pins'])
            self.device_templates[device_template.type] = device_template

    def get_device_template_for_module(self,module_name) -> DeviceTemplate:
        if module_name not in self.chipset["mapping"]:
            abort("No mapping for %s in self.chipset file" % module_name)

        device_type = self.chipset["mapping"][module_name]

        if device_type not in self.chipset["devices"]:
            abort("%s not in devices in self.chipset file" % device_type)

        return self.device_templates[device_type]


      

        


    def __validate(self):
        if "devices" not in self.chipset or len(self.chipset["devices"]) == 0:
            abort("Supplied self.chipset file has no devices")

        if "package" not in self.chipset and self.chipset["package"] not in ["DIP"]:
            abort("package not specified or invalid")

        if "mapping" not in self.chipset or len(self.chipset["mapping"]) == 0:
            abort("Supplied self.chipset file has no mapping")

        # Check for obvious pin configuration errors
        for name, device in self.chipset["devices"].items():
            pins = device["pins"]
            for label in pins.values():
                if list(pins.values()).count(label) > 1:
                    logger.warning("Pin-label {} of device {} occurs more than once", label, name)






    def __getattr__(self, attr):
        return self.chipset[attr]
        