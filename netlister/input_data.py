from netlister.registry import RegistryMixin, Registry
from loguru import logger
import json

class InputData(RegistryMixin):
    def __init__(self, registry: Registry) -> None:
        super().__init__(registry)

        self.modules = {}

    '''
    Determines the top-level module in the verilog hierarchy
    '''
    def get_top_module(self):
        for type, module in self.modules.items():
            if module.is_top():
                return module

        # If it can't find a module marked as 'top', fail
        logger.error("Could not find top module. Maybe add 'hierarchy -top <modulname>' to your yosys script.")
        quit()

    def get_module_for_type(self, type):
        if type not in self.modules:
            logger.error("Could not find module {} in input data", type)
            quit()

        return self.modules[type]


    def has_module(self, module):
        return module in self.modules


    def load(self, path):
        logger.info("Loading input data from {}", path)
        with open(path) as f:
            self.__parse(json.load(f))


    def __parse(self, data):
        for type, information in data['modules'].items():
            module = ModuleTemplate(type)

            module.set_attributes(information['attributes'])

            logger.warning("{}", module.attributes)


            for label, portinfo in information['ports'].items():
                port = Port(label)
                port.set_direction(portinfo['direction'])
                port.set_bits(portinfo['bits'])

                module.add_port(port)

            for label, cellinfo in information['cells'].items():
                cell = CellTemplate(label)
                cell.set_type(cellinfo['type'])
                cell.set_attributes(cellinfo['attributes'])
                if 'port_directions' in cellinfo:
                    cell.set_port_directions(cellinfo['port_directions'])
                cell.set_connections(cellinfo['connections'])

                module.add_cell(cell)

            for label, netnameinfo in information['netnames'].items():
                netname = NetName(label)
                netname.set_bits(netnameinfo['bits'])

            self.modules[type] = module







class Port:
    def __init__(self, label) -> None:
        self.label = label

    def set_direction(self, direction):
        self.direction = direction

    def set_bits(self, bits):
        self.bits = bits

class CellTemplate:
    def __init__(self, label) -> None:
        self.label = label

        self.attributes = {}
        self.port_directions = {}
        self.attributes = {}

    def set_type(self, type):
        self.type = type

    def set_attributes(self, attributes):
        self.attributes = attributes

    def set_port_directions(self, port_directions):
        self.port_directions = port_directions

    def set_connections(self, connections):
        self.connections = connections

class NetName:
    def __init__(self, label) -> None:
        self.label = label

    def set_bits(self, bits):
        self.bits = bits
        
    
        


class ModuleTemplate:
    def __init__(self, type) -> None:
        self.type = type
        self.ports = []
        self.cells = []
        self.netnames = []
        self.attributes = {}

    def set_attributes(self, attributes):
        self.attributes = attributes

    def is_top(self):
        if "top" in self.attributes and self.attributes['top'] == "00000000000000000000000000000001":
            return True

        return False


    def is_blackbox(self):
        if 'blackbox' in self.attributes and self.attributes['blackbox'] == "00000000000000000000000000000001":
            return True

        return False

    def add_port(self, port):
        self.ports.append(port)

    def add_cell(self, cell):
        self.cells.append(cell)

    def add_netnames(self, netname):
        self.netnames.append(netname)








    




        
        
